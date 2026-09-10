"""Read-only Track-A preflight: no generation, downloads, analysis or token issuance."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from clsm.config import load_experiment_config
from clsm.errors import ClsmError
from clsm.track_a_backend import load_llamacpp_runtime, verify_runtime_identity
from clsm.track_a_dataset_pin import DEFAULT_PIN, load_pin
from clsm.track_a_manifest import RunStage, build_pilot_manifest, load_manifest
from clsm.track_a_plan import build_plan, validate_pilot_workload
from clsm.track_a_run import _check_human_authorization, evaluate_readiness, scientific_config_hash

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/track_a_pilot/pilot.yaml"
RUNTIME = ROOT / "configs/track_a_pilot/runtime_llamacpp.yaml"
FREEZE = ROOT / "configs/track_a_pilot/pre_run_freeze.json"


class PreflightReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stage: RunStage
    git_commit: str | None = None
    git_dirty: bool | None = None
    scientific_config_hash: str | None = None
    dataset_content_hash: str | None = None
    experiment_id: str
    output_dir: str
    planned_generations: int | None = None
    model_verified: bool = False
    runtime_verified: bool = False
    runtime_version: str | None = None
    runtime_build: str | None = None
    authorization_present: bool = False
    blockers: list[str] = Field(default_factory=list)

    @property
    def ready(self) -> bool:
        return not self.blockers


def git_integrity(root: Path, expected_commit: str | None) -> tuple[str, bool]:
    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True, check=True, timeout=10
        )
        return result.stdout.strip()

    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=all"))
    if dirty:
        raise ValueError("dirty repository; commit/review changes before execution")
    if not expected_commit or not re.fullmatch(r"[0-9a-f]{40}", expected_commit) or commit != expected_commit:
        raise ValueError(f"git commit mismatch or missing reviewed commit; current={commit}")
    return commit, dirty


def check_output_directory(path: Path) -> None:
    # Refuse even an empty existing run directory: no resume/retry semantics.
    if path.exists() or path.is_symlink():
        raise ValueError("output collision: run directory already exists (no second execution)")


def preflight(
    *,
    stage: RunStage = RunStage.GENERATOR,
    expected_commit: str | None = None,
    expected_hash: str | None = None,
    pin_path: str | Path = DEFAULT_PIN,
    output_dir: str | Path = "experiments/_runs/track-a-en-hint-pilot",
    config_path: str | Path = CONFIG,
    runtime_path: str | Path = RUNTIME,
) -> PreflightReport:
    output = Path(output_dir).expanduser().resolve()
    report = PreflightReport(stage=stage, experiment_id="track-a-en-hint-pilot", output_dir=str(output))
    try:
        report.git_commit, report.git_dirty = git_integrity(ROOT, expected_commit)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        report.blockers.append(f"repository integrity: {exc}")
    try:
        cfg = load_experiment_config(config_path)
        rt = yaml.safe_load(Path(runtime_path).read_text())
        report.experiment_id = cfg.experiment_name
        report.scientific_config_hash = scientific_config_hash(cfg, rt)
        frozen = json.loads(FREEZE.read_text())
        if (
            expected_hash != report.scientific_config_hash
            or expected_hash != frozen["scientific_config_hash"]
        ):
            report.blockers.append("scientific config hash mismatch or missing reviewed hash")
        manifest = build_pilot_manifest(config_path)
        committed = load_manifest(ROOT / "configs/track_a_pilot/pilot_manifest.json")
        if manifest.model_dump() != committed.model_dump():
            report.blockers.append("methodology: committed manifest/config drift")
        readiness = evaluate_readiness(
            manifest, config_path=config_path, runtime_path=runtime_path, stage=stage, pin_path=pin_path
        )
        if readiness.methodology_unresolved:
            report.blockers.append(f"methodology: {readiness.methodology_unresolved}")
        if readiness.external_unresolved:
            report.blockers.append(f"external resources: {readiness.external_unresolved}")
        try:
            pin = load_pin(pin_path, cfg.dataset, require_real=True)
            report.dataset_content_hash = pin.content_sha256
            specs = build_plan(cfg, pin, cfg.experiment_name)
            validate_pilot_workload(specs)
            report.planned_generations = len(specs)
        except (ValueError, OSError) as exc:
            report.blockers.append(f"dataset content pin/workload: {exc}")
        try:
            runtime = load_llamacpp_runtime(runtime_path)
            if runtime.expected_model_bytes is None:
                raise ValueError("model exact size pin required")
            report.runtime_version, report.runtime_build = verify_runtime_identity(runtime)
            report.model_verified = report.runtime_verified = True
        except (ValueError, RuntimeError, OSError) as exc:
            report.blockers.append(f"model/runtime identity: {exc}")
        ok, error, _ = _check_human_authorization(
            report.scientific_config_hash,
            bindings={
                "stage": stage.value,
                "git_commit": expected_commit or "",
                "dataset_content_hash": report.dataset_content_hash or "",
                "output_dir": str(output),
                "experiment_id": cfg.experiment_name,
            },
        )
        report.authorization_present = ok
        if not ok:
            report.blockers.append(f"human authorization: {error}")
    except (ValueError, OSError, KeyError, TypeError, ClsmError) as exc:
        report.blockers.append(f"config/manifest: {exc}")
    try:
        check_output_directory(output)
    except ValueError as exc:
        report.blockers.append(str(exc))
    if stage is not RunStage.GENERATOR:
        report.blockers.append(f"{stage.value} execution is not implemented or authorized by this package")
    return report


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--stage", type=RunStage, choices=list(RunStage), default=RunStage.GENERATOR)
    parser.add_argument("--expected-commit")
    parser.add_argument("--expected-hash")
    parser.add_argument("--pin", type=Path, default=DEFAULT_PIN)
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/_runs/track-a-en-hint-pilot"))


def arguments(args: argparse.Namespace) -> dict[str, Any]:
    return dict(
        stage=args.stage,
        expected_commit=args.expected_commit,
        expected_hash=args.expected_hash,
        pin_path=args.pin,
        output_dir=args.output_dir,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    args = parser.parse_args(argv)
    report = preflight(**arguments(args))
    # Human summary on stderr; stdout is a single parseable JSON object.
    import sys

    print(f"Track A {report.stage}: {'PASS' if report.ready else 'REFUSED'}", file=sys.stderr)
    for blocker in report.blockers:
        print(f"- {blocker}", file=sys.stderr)
    print(report.model_dump_json(indent=2))
    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())

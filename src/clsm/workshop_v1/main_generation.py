"""Authorized Workshop-v1 main generation runner.

This runner is intentionally generation-only: it performs no translation,
judging, annotation, or analysis. It requires the exact investigator
authorization file and generation configuration hash before the first call.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from clsm.downstream.contracts import content_hash
from clsm.workshop_v1.config import load_study
from clsm.workshop_v1.frozen_validation import validate_frozen_inputs
from clsm.workshop_v1.local_runtime import run_local, verify_local
from clsm.workshop_v1.openbookqa_adapter import AlignedRow, build_source_item
from clsm.workshop_v1.output_parsing import parse_prompted_output
from clsm.workshop_v1.prompt_contract import Condition, Language, render_prompt
from clsm.workshop_v1.runner import validate_main_record
from clsm.workshop_v1.workload import build_generation_plan, generation_config_hash

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "experiments/_runs/workshop-v1-main"
AUTH = ROOT / "engineering/INVESTIGATOR_MAIN_GENERATION_AUTHORIZATION.json"


def _rows(root: Path) -> dict[str, AlignedRow]:
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    summary = json.loads((root / "engineering/workshop_v1_dataset_summary.json").read_text())
    result: dict[str, AlignedRow] = {}
    for path in sorted((Path(summary["local_snapshot"]) / "data").glob("*.parquet")):
        for row in pq.read_table(path).to_pylist():
            result[row["id"]] = cast(AlignedRow, row)
    return result


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    # ``raw_runtime_output`` may contain reversible surrogateescape values when
    # llama.cpp emitted a non-UTF-8 byte.  JSON ASCII escaping preserves those
    # values without allowing the filesystem encoding to reject the record.
    payload = json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != payload:
            raise ValueError(f"immutable output differs: {path}")
        return
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)


def _successful_checkpoints(output: Path, task_id: str) -> list[Path]:
    """Return immutable successful attempts for one task, if any."""
    return [
        path for path in sorted(output.glob(f"{task_id}*.json"))
        if json.loads(path.read_text(encoding="utf-8")).get("qc", {}).get("runtime_success") is True
    ]


def _immutable_manifest_fields(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return manifest identity, excluding the creation timestamp only."""
    return {key: value for key, value in manifest.items() if key != "created_utc"}


def _write_or_validate_execution_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Keep the original execution manifest immutable across governed resume."""
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if _immutable_manifest_fields(existing) != _immutable_manifest_fields(manifest):
            raise ValueError(f"immutable scientific manifest differs: {path}")
        return
    _atomic_json(path, manifest)


def _authorize(root: Path, output: Path, authorization_path: Path = AUTH) -> tuple[str, dict[str, Any]]:
    config = generation_config_hash(root)
    if config["hash"] != "7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec":
        raise PermissionError("generation configuration hash mismatch")
    auth = json.loads(authorization_path.read_text(encoding="utf-8"))
    if auth.get("generation_config_hash") != config["hash"] or auth.get("expected_calls") != 3312:
        raise PermissionError("authorization does not match the generation configuration")
    if auth.get("output_directory") != str(output.relative_to(root)):
        raise PermissionError("authorization output directory mismatch")
    if output.exists() and any(output.iterdir()):
        checkpoint_files = sorted(output.glob("generation-*.json"))
        manifest_path = output / "execution_manifest.json"
        if not manifest_path.is_file():
            raise FileExistsError("nonempty output directory lacks an immutable execution manifest")
        for checkpoint in checkpoint_files:
            record = json.loads(checkpoint.read_text(encoding="utf-8"))
            if record.get("generation_config_hash") != config["hash"]:
                raise ValueError("resume checkpoint generation hash mismatch")
    output.mkdir(parents=True, exist_ok=True)
    return config["hash"], auth


def execute(root: Path = ROOT, output: Path = OUTPUT, authorization_path: Path = AUTH) -> dict[str, Any]:
    root = root.resolve()
    output = output.resolve()
    study_hash, authorization = _authorize(root, output, authorization_path)
    frozen = validate_frozen_inputs(root)
    tasks = build_generation_plan(root)
    rows = _rows(root)
    specs = [slot.spec for slot in load_study(root / "configs/workshop_v1/study.yaml").models]
    model_specs = {spec.model_id: spec for spec in specs if spec is not None}
    for spec in model_specs.values():
        verify_local(spec)
    metadata: dict[str, Any] = {}
    items: dict[str, Any] = {}
    for item_id, row in rows.items():
        item, meta = build_source_item(row)
        items[item_id], metadata[item_id] = item, meta
    manifest = {
        "generation_config_hash": study_hash,
        "authorization": authorization,
        "expected_calls": 3312,
        "dataset_revision": frozen["dataset_revision"],
        "manifest_hashes": {
            "main": frozen["main_hash"], "cue_b": frozen["cue_b_hash"], "pilot": frozen["pilot_hash"]
        },
        "created_utc": datetime.now(UTC).isoformat(),
    }
    _write_or_validate_execution_manifest(output / "execution_manifest.json", manifest)
    completed = 0
    for task in tasks:
        spec = model_specs[task.model_id]
        item = items[task.source_item_id]
        language: Language = task.language
        condition: Condition = task.condition
        target = task.target_letter
        prompt = render_prompt(
            model_id="qwen3-1.7b" if task.model_id.startswith("Qwen/") else "gemma-3-4b-it",
            language=language, condition=condition,
            item_text=next(r.text for r in item.renderings if r.language == language),
            target_letter=target,
        )
        existing = sorted(output.glob(f"{task.task_id}*.json"))
        successful = _successful_checkpoints(output, task.task_id)
        if successful:
            completed += 1
            continue
        attempt_suffix = "" if not existing else f".retry-{len(existing)}"
        record_path = output / f"{task.task_id}{attempt_suffix}.json"
        raw = run_local(spec, prompt, seed=task.sample_index)
        parsed = parse_prompted_output(
            raw["generated_completion"] or "", language=language,
            returncode=0 if raw["runtime_success"] else -1,
            timed_out=raw["invocation"]["timed_out"],
            n_output_tokens=raw["metrics"]["completion_tokens"],
            max_new_tokens=spec.decoding.max_new_tokens,  # type: ignore[union-attr]
        )
        record: dict[str, Any] = {
            "generation_id": task.task_id, "data_kind": "scientific", "population_role": "confirmatory",
            "FEASIBILITY_ONLY": False, "source_item_id": task.source_item_id,
            "source_row_hash": task.source_row_hash, "model": task.model_id,
            "language": language, "condition": condition, "sample_index": task.sample_index,
            "seed": task.sample_index, "target_letter": target, "study_hash": study_hash,
            "generation_config_hash": study_hash, "model_hash": spec.checkpoint_hash,
            "model_config_hash": spec.artifact_hash, "dataset_manifest_hash": frozen["main_hash"],
            "prompt": prompt, "prompt_hash": content_hash(prompt),
            "cue_hash": content_hash("" if target is None else condition),
            "raw_runtime_output": raw["raw_runtime_output"],
            "generated_completion": raw["generated_completion"],
            "raw_output_hash": content_hash(raw["raw_runtime_output"]),
            "raw_stderr": raw["raw_stderr"], "invocation": raw["invocation"], "metrics": raw["metrics"],
            "parsed": asdict(parsed), "qc": {"runtime_success": raw["runtime_success"],
                "final_answer_parse_success": parsed.final_answer is not None,
                "visible_trace_present": bool(parsed.reasoning_span and parsed.reasoning_span.strip()),
                "truncation": parsed.truncated, "checkpoint_written": True},
            "created_utc": datetime.now(UTC).isoformat(),
        }
        validate_main_record(record)
        _atomic_json(record_path, record)
        completed += 1
        print(
            json.dumps({"completed": completed, "expected": 3312, "generation_id": task.task_id}),
            flush=True,
        )
    if completed != 3312:
        raise RuntimeError("main generation completed an unexpected number of calls")
    return {"generation_config_hash": study_hash, "expected_calls": 3312, "completed_calls": completed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--authorization", type=Path, default=AUTH)
    args = parser.parse_args()
    print(json.dumps(execute(args.root, args.output, args.authorization), indent=2))


if __name__ == "__main__":
    main()

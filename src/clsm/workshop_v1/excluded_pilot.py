"""Bounded, permanently excluded feasibility executor. No main-study run path."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from clsm.downstream.contracts import content_hash, object_hash
from clsm.workshop_v1.config import ModelSpec, load_study
from clsm.workshop_v1.cue_rule import misleading_target_letter
from clsm.workshop_v1.judge import load_contract
from clsm.workshop_v1.local_runtime import run_local, verify_local
from clsm.workshop_v1.openbookqa_adapter import AlignedRow, build_source_item
from clsm.workshop_v1.output_parsing import parse_gemma_output
from clsm.workshop_v1.prepare_population import file_sha256
from clsm.workshop_v1.prompt_contract import CUE_TEXT, Condition, Language, ModelId, render_prompt

ROOT = Path(__file__).resolve().parents[3]
PINS = {
    "pilot": "063a530e9ff5c91dfff9baaa0253327c915172998ff90796ded3c9300ee357a9",
    "main": "576a991f9f96e1bad95d1775bc1f177604e13c8903416befee75dd2d3f277f6f",
    "cue_b": "e18b48b6be7c2fa86df1ff00712943ac5cee218977a3bb6ee05d8bdd949b9891",
}
# Amendment 1 is a new immutable run namespace.  The original excluded pilot,
# when present, is never read as a writable target and can never be overwritten.
OUTPUT = ROOT / "experiments/_runs/workshop-v1-excluded-feasibility-v2"


def assert_freeze_stable() -> None:
    for name, expected in load_contract()["source_files"].items():
        path = Path(name)
        if path.stat().st_mtime_ns != expected["mtime_ns"] or file_sha256(path) != expected["sha256"]:
            raise ValueError("Claude freeze changed: STOP and re-read before further execution")


def manifests() -> dict[str, Any]:
    result = {}
    for role, sha in PINS.items():
        path = ROOT / f"engineering/workshop_v1_{role}_manifest.json"
        if file_sha256(path) != sha:
            raise ValueError("prospective manifest changed")
        result[role] = json.loads(path.read_text())
    pilot = {r["source_item_id"] for r in result["pilot"]["items"]}
    main = {r["source_item_id"] for r in result["main"]["items"]}
    cue_b = {r["source_item_id"] for r in result["cue_b"]["items"]}
    if len(pilot) != 1 or len(main) != 120 or len(cue_b) != 36 or pilot & main or not cue_b <= main:
        raise ValueError("pilot/main separation failed")
    return result


def excluded_ids() -> set[str]:
    return {r["source_item_id"] for r in manifests()["pilot"]["items"]}


def model_specs() -> list[ModelSpec]:
    study = load_study(ROOT / "configs/workshop_v1/study.yaml")
    specs = [slot.spec for slot in study.models if slot.spec is not None]
    if len(specs) != 2 or any(s.blockers() for s in specs):
        raise ValueError("generator specs incomplete")
    return specs


def plan() -> dict[str, Any]:
    """Hashable preparation snapshot; no real item text or outputs."""
    m = manifests()
    specs = model_specs()
    return {
        "schema_version": "workshop-v1-excluded-feasibility/2",
        "protocol_amendment": "protocol-amendment-1",
        "FEASIBILITY_ONLY": True,
        "permanently_excluded_from_main_and_human_annotation": True, "expected_calls": 12,
        "dataset_revision": m["pilot"]["dataset_revision"], "manifest_hashes": PINS,
        "pilot_ids": sorted(excluded_ids()), "models": [s.model_dump(mode="json") for s in specs],
        "model_config_hashes": {s.model_id: s.artifact_hash for s in specs},
        "languages": ["en", "ur"], "conditions": ["control", "cue_a", "cue_b"], "seeds": [0],
        "hint_seed": str(m["pilot"]["selection_seed"]),
        "hint_seed_provenance": "prospectively bind to existing frozen selection seed; no outputs consulted",
        "cue_versions": {"cue_a": "cue_a", "cue_b": "cue_b"},
        "prompt_cue_hash": object_hash({"cue_text": CUE_TEXT,
            "renderer_sha256": file_sha256(Path(__file__).with_name("prompt_contract.py"))}),
        "code_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "working_code_hash": object_hash(
            {p.name: file_sha256(p) for p in sorted(Path(__file__).parent.glob("*.py"))}
        ),
        "runtime_observability": "log verbosity 4; /usr/bin/time -l; no decoding changes",
        "authorization": (
            "Claude session-14 D1: native-reviewed language-control amendment; exact 12-call rerun"
        ),
    }


def write_immutable(path: Path, value: dict[str, Any]) -> None:
    payload = json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != payload:
            raise ValueError(f"immutable artifact differs: {path.name}")
        return
    with path.open("x", encoding="utf-8") as stream:
        stream.write(payload)


def next_attempt(directory: Path, generation_id: str, study_hash: str) -> int | None:
    files = sorted(directory.glob(f"{generation_id}.attempt-*.json"))
    if not files:
        return 1
    prior = [json.loads(p.read_text()) for p in files]
    if any(r["study_hash"] != study_hash or r["FEASIBILITY_ONLY"] is not True for r in prior):
        raise ValueError("resume binding mismatch")
    last = prior[-1]
    if last["qc"]["runtime_success"]:
        return None  # Includes parse/language failures: no outcome-based resampling.
    if last["generated_completion"] and last["generated_completion"].strip():
        raise ValueError("failed call produced output; cannot resample")
    if len(prior) >= 2:
        raise ValueError("one identical infrastructure retry already used")
    return 2


def load_pilot_row() -> AlignedRow:
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    ref = manifests()["pilot"]["items"][0]
    summary = json.loads((ROOT / "engineering/workshop_v1_dataset_summary.json").read_text())
    path = Path(summary["local_snapshot"]) / f"data/{ref['split']}-00000-of-00001.parquet"
    rows = pq.read_table(path).to_pylist()
    found = [row for row in rows if row["id"] == ref["source_item_id"]]
    if len(found) != 1 or object_hash(found[0]) != ref["row_hash"]:
        raise ValueError("pilot source row mismatch")
    return cast(AlignedRow, found[0])


def execute(*, authorize_excluded_pilot: bool = False) -> dict[str, Any]:
    if not authorize_excluded_pilot:
        raise PermissionError("explicit excluded-pilot authorization required")
    from clsm.workshop_v1_readiness import report

    readiness = report()
    if readiness["GENERATOR PILOT READY"] != "YES" or readiness.get("AMENDED PILOT READY") != "YES":
        raise ValueError("amended pilot is blocked pending native Urdu language-instruction review")
    assert_freeze_stable()
    design = plan()
    study_hash = object_hash(design)
    write_immutable(OUTPUT / "study.json", {**design, "study_hash": study_hash})
    specs = model_specs()
    languages: tuple[Language, Language] = ("en", "ur")
    conditions: tuple[Condition, Condition, Condition] = ("control", "cue_a", "cue_b")
    for spec in specs:
        verify_local(spec)
    item, metadata = build_source_item(load_pilot_row())
    attempted = skipped = 0
    for spec in specs:
        mid: ModelId = "qwen3-1.7b" if spec.model_id.startswith("Qwen/") else "gemma-3-4b-it"
        # Workshop-v1 Qwen now uses D5 prompted/non-thinking rationale; the
        # native-thinking parser remains only for immutable historical records.
        parser = parse_gemma_output
        assert spec.decoding is not None
        for lang in languages:
            for cond in conditions:
                identity = [study_hash, item.source_item_id, mid, lang, cond, 0]
                gid = "FEASIBILITY_ONLY-" + object_hash(identity)
                attempt = next_attempt(OUTPUT, gid, study_hash)
                if attempt is None:
                    skipped += 1
                    continue
                assert_freeze_stable()
                target = None if cond == "control" else misleading_target_letter(
                    source_item_id=item.source_item_id, correct_index=metadata.correct_index,
                    cue_version=cond, hint_seed=design["hint_seed"],
                )
                prompt = render_prompt(
                    model_id=mid, language=lang, condition=cond,
                    item_text=next(r.text for r in item.renderings if r.language == lang),
                    target_letter=target,
                )
                print(
                    json.dumps({"starting": mid, "language": lang, "condition": cond, "attempt": attempt}),
                    flush=True,
                )
                raw = run_local(spec, prompt, seed=0)
                attempted += 1
                parsed = parser(
                    raw["generated_completion"] or "", language=lang,
                    returncode=0 if raw["runtime_success"] else -1,
                    timed_out=raw["invocation"]["timed_out"],
                    n_output_tokens=raw["metrics"]["completion_tokens"],
                    max_new_tokens=spec.decoding.max_new_tokens,
                )
                trace_present = bool(parsed.reasoning_span and parsed.reasoning_span.strip())
                qc = {
                    "runtime_success": raw["runtime_success"], "prompt_rendered": True,
                    "prompt_hash": content_hash(prompt), "raw_output_preserved": True,
                    "generated_completion_separated": raw["separation_error"] is None,
                    "visible_trace_present": trace_present,
                    "final_answer_parse_success": parsed.final_answer is not None,
                    "language_compliance": parsed.language_compliance,
                    "truncation": parsed.truncated,
                    "runtime_error": (
                        None
                        if raw["runtime_success"]
                        else raw["separation_error"] or "runtime failure"
                    ),
                    "checkpoint_written": True,
                }
                record = {
                    "FEASIBILITY_ONLY": True, "data_kind": "excluded_feasibility", "population_role": "pilot",
                    "generation_id": gid, "source_item_id": item.source_item_id, "model": spec.model_id,
                    "language": lang, "condition": cond, "sample_index": 0, "seed": 0,
                    "attempt": attempt,
                    "retry_reason": (
                        "infrastructure failure before output" if attempt > 1 else None
                    ),
                    "study_hash": study_hash, "model_config_hash": spec.artifact_hash,
                    "model_spec": spec.model_dump(mode="json"), "dataset_manifest_hash": PINS["pilot"],
                    "prompt": prompt, "prompt_hash": content_hash(prompt), "cue_hash": content_hash(
                        CUE_TEXT[cond][lang].format(target_letter=target) if target else ""),
                    "prompt_cue_hash": design["prompt_cue_hash"],
                    "created_utc": datetime.now(UTC).isoformat(),
                    "code_head": design["code_head"], "working_code_hash": design["working_code_hash"],
                    **raw, "parsed": asdict(parsed), "qc": qc,
                }
                write_immutable(OUTPUT / f"{gid}.attempt-{attempt}.json", record)
                print(json.dumps({"completed": mid, "language": lang, "condition": cond, "qc": qc,
                                  "wall_seconds": raw["wall_clock_seconds"]}), flush=True)
                if not raw["runtime_success"]:
                    raise RuntimeError("pilot stopped on runtime failure; checkpoint preserved")
    return {"attempted_this_invocation": attempted, "skipped_successful": skipped, "study_hash": study_hash}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorize-excluded-pilot", action="store_true")
    args = parser.parse_args()
    print(json.dumps(execute(authorize_excluded_pilot=args.authorize_excluded_pilot), indent=2))


if __name__ == "__main__":
    main()

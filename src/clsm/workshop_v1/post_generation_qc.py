"""Non-generative QC and downstream planning for the completed main run."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clsm.downstream.contracts import content_hash, object_hash
from clsm.workshop_v1.human_pool import blinded_export_rows, candidate_pool, validate_pool
from clsm.workshop_v1.judge_plan import validate_plans
from clsm.workshop_v1.runner import validate_main_record
from clsm.workshop_v1.workload import build_generation_plan, generation_config_hash

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "experiments/_runs/workshop-v1-main-attempt-2"
GENERATION_HASH = "7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec"


def _write_immutable(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise ValueError(f"immutable artifact differs: {path}")
        return
    path.write_text(text, encoding="utf-8")


def _records(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    rows = []
    for path in sorted((root / OUTPUT.relative_to(ROOT)).glob("generation-*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        validate_main_record(value)
        rows.append((path, value))
    return rows


def generation_qc(root: Path = ROOT) -> dict[str, Any]:
    rows = _records(root)
    plan = build_generation_plan(root)
    expected = {task.task_id for task in plan}
    actual = [value["generation_id"] for _, value in rows]
    runtime_success = [value for _, value in rows if value["qc"].get("runtime_success") is True]
    hash_ok = all(
        value.get("raw_output_hash") == content_hash(value["raw_runtime_output"])
        for _, value in rows
    )
    parse_success = sum(value["qc"].get("final_answer_parse_success") is True for _, value in rows)
    def distribution(values: list[int]) -> dict[str, int | None]:
        if not values:
            return {"count": 0, "min": None, "median": None, "p95": None, "max": None}
        ordered = sorted(values)
        return {
            "count": len(ordered), "min": ordered[0],
            "median": ordered[(len(ordered) - 1) // 2],
            "p95": ordered[int(0.95 * (len(ordered) - 1))], "max": ordered[-1],
        }
    groups: dict[str, dict[str, Any]] = {}
    for key in ("model", "language", "condition"):
        for group in sorted({value[key] for _, value in rows}):
            group_rows = [value for _, value in rows if value[key] == group]
            groups[f"{key}={group}"] = {
                "records": len(group_rows),
                "runtime_success": sum(value["qc"].get("runtime_success") is True for value in group_rows),
                "parse_success": sum(
                    value["qc"].get("final_answer_parse_success") is True for value in group_rows
                ),
                "truncations": sum(value["qc"].get("truncation") is True for value in group_rows),
                "language_compliant": sum(
                    value.get("parsed", {}).get("language_compliance") == "compliant"
                    for value in group_rows
                ),
            }
    return {
        "schema_version": "generation_qc/1",
        "stage": "generation_qc",
        "data_kind": "SCIENTIFIC",
        "generated_utc": datetime.now(UTC).isoformat(),
        "generation_config_hash": generation_config_hash(root)["hash"],
        "expected_records": 3312,
        "persisted_records": len(rows),
        "successful_scientific_records": len(runtime_success),
        "failed_scientific_records": len(rows) - len(runtime_success),
        "missing_task_ids": sorted(expected - set(actual)),
        "duplicate_task_ids": sorted(task for task, n in Counter(actual).items() if n > 1),
        "unexpected_task_ids": sorted(set(actual) - expected),
        "counts": {
            "model": dict(Counter(value["model"] for _, value in rows)),
            "language": dict(Counter(value["language"] for _, value in rows)),
            "condition": dict(Counter(value["condition"] for _, value in rows)),
            "sample_index": dict(Counter(str(value["sample_index"]) for _, value in rows)),
        },
        "runtime_success_count": len(runtime_success),
        "generated_completion_present": sum(bool(value.get("generated_completion")) for _, value in rows),
        "final_answer_parse_success_count": parse_success,
        "final_answer_parse_failure_count": len(rows) - parse_success,
        "visible_trace_present_count": sum(
            value["qc"].get("visible_trace_present") is True for _, value in rows
        ),
        "truncation_count": sum(value["qc"].get("truncation") is True for _, value in rows),
        "output_length_distribution": distribution([
            len(value.get("generated_completion") or "") for _, value in rows
        ]),
        "technical_qc_by_group": groups,
        "raw_output_hashes_valid": hash_ok,
        "pilot_contamination_count": sum(value.get("FEASIBILITY_ONLY") is True for _, value in rows),
        "engineering_failure_records": [
            {"generation_id": value["generation_id"], "path": str(path), "runtime_success": False}
            for path, value in rows if value["qc"].get("runtime_success") is not True
        ],
        "technical_qc_pass": (
            len(rows) == 3312 and len(runtime_success) == 3312 and hash_ok
            and not (set(actual) ^ expected) and len(set(actual)) == 3312
        ),
        "scientific_result_analysis_performed": False,
    }


def translation_manifest(root: Path = ROOT) -> dict[str, Any]:
    rows = _records(root)
    selected = [
        (path, value) for path, value in rows
        if value["language"] == "ur" and value["condition"] in {"cue_a", "cue_b"}
    ]
    tasks = []
    for path, value in selected:
        tasks.append({
            "translation_id": "translation-" + object_hash([value["generation_id"], "urd_Arab", "eng_Latn"]),
            "source_trace_id": value["generation_id"],
            "source_trace_hash": value["raw_output_hash"],
            "source_record": str(path),
            "source_item_id": value["source_item_id"],
            "model": value["model"], "condition": value["condition"],
            "sample_index": value["sample_index"],
            "source_language": "urd_Arab", "target_language": "eng_Latn",
            "source_runtime_success": value["qc"].get("runtime_success") is True,
            "source_completion_present": bool(value.get("generated_completion")),
            "eligible": (
                value["qc"].get("runtime_success") is True
                and bool(value.get("generated_completion"))
            ),
        })
    eligible = [task for task in tasks if task["eligible"]]
    return {
        "schema_version": "translation_manifest/1", "stage": "translation",
        "data_kind": "SCIENTIFIC", "expected_tasks": 936, "planned_tasks": len(tasks),
        "eligible_tasks": len(eligible), "blocked_tasks": len(tasks) - len(eligible),
        "generation_config_hash": generation_config_hash(root)["hash"],
        "translator_contract_status": "UNRESOLVED_INVESTIGATOR_DECISION",
        "scientific_translation_authorized": False,
        "tasks": tasks,
        "manifest_hash": object_hash(tasks),
    }


def judge_readiness(root: Path = ROOT) -> dict[str, Any]:
    plan = validate_plans(root)
    rows = _records(root)
    fixture_path = root / "engineering/workshop_v1_judge_format_summary.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8")) if fixture_path.is_file() else None
    source_ids = {value["generation_id"] for _, value in rows if value["qc"].get("runtime_success") is True}
    blocked = sum(
        value["language"] == "ur" and value["condition"] in {"cue_a", "cue_b"}
        and value["generation_id"] not in source_ids
        for _, value in rows
    )
    return {
        "schema_version": "judge_readiness/1", "stage": "judge",
        "data_kind": "SCIENTIFIC", "plan": plan,
        "source_runtime_blocked_tasks": blocked,
        "format_fixture_required": True,
        "format_fixture_status": "PASS" if fixture and fixture.get("status") == "PASS" else "NOT_RUN",
        "judge_spec_hash": fixture.get("judge_spec_hash") if fixture else None,
        "scientific_judging_authorized": False,
        "judge_contract_status": "FORMAT_CONTRACT_READY_SCIENTIFIC_EXECUTION_NOT_AUTHORIZED",
        "ready": not blocked,
    }


def write_artifacts(root: Path = ROOT) -> dict[str, Any]:
    qc = generation_qc(root)
    _write_immutable(root / OUTPUT.relative_to(ROOT) / "post_generation_qc.json", qc)
    translation = translation_manifest(root)
    _write_immutable(root / "engineering/workshop_v1_translation_manifest.json", translation)
    judge = judge_readiness(root)
    _write_immutable(root / "engineering/workshop_v1_judge_stage_readiness.json", judge)

    pool = validate_pool(root)
    candidates = candidate_pool(root)
    rows = {
        (
            value["source_item_id"], value["model"], value["condition"], value["sample_index"]
        ): value["generated_completion"]
        for _, value in _records(root) if value["qc"].get("runtime_success") is True
    }
    packet_rows = blinded_export_rows(candidates, rows)
    packet_dir = root / "experiments/_runs/workshop-v1-human-validation-packet"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in packet_rows)
    packet_path = packet_dir / "blinded_traces.jsonl"
    if packet_path.exists() and packet_path.read_text(encoding="utf-8") != packet:
        raise ValueError("immutable human packet differs")
    if not packet_path.exists():
        packet_path.write_text(packet, encoding="utf-8")
    _write_immutable(packet_dir / "manifest.json", {
        "schema_version": "human_export/1", "data_kind": "SCIENTIFIC",
        "annotation_executed": False, "annotation_authorized": False,
        "candidate_pool": pool, "count": len(packet_rows),
        "packet_hash": content_hash(packet),
    })
    _write_immutable(root / "engineering/workshop_v1_stage_hashes.json", {
        "generation_stage_hash": GENERATION_HASH,
        "translation_stage_hash": None, "translation_status": "NOT_READY",
        "judge_stage_hash": None, "judge_status": "NOT_READY",
        "human_stage_hash": None, "human_status": "NOT_READY",
        "analysis_stage_hash": None, "analysis_status": "NOT_READY",
        "final_whole_study_hash": None, "final_status": "NOT_READY",
    })
    _write_immutable(root / "engineering/workshop_v1_preprint_artifact_manifest.json", {
        "schema_version": "preprint_artifacts/1", "data_kind": "TEMPLATE",
        "scientific_results_present": False,
        "artifacts": [
            "study_design_table", "generation_qc_table", "language_compliance_table",
            "main_descriptive_results_table", "monitoring_comparison_table",
            "human_validation_table", "figure_data", "supplementary_provenance_table",
        ],
    })
    return {"generation_qc": qc, "translation": translation, "judge": judge, "human": pool}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-artifacts", action="store_true", required=True)
    args = parser.parse_args()
    if args.write_artifacts:
        print(json.dumps(write_artifacts(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Non-substantive direct-judge QC and stage sealing.

Run only after the active direct-judge process has stopped. This deliberately
reports technical-state counts, never scientific label proportions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "experiments/_runs/workshop-v1-direct-judge"
MANIFESTS = (
    ROOT / "engineering/workshop_v1_english_direct_judge_manifest.json",
    ROOT / "engineering/workshop_v1_urdu_direct_judge_manifest.json",
)
PROMPT_HASH = "050ed49289b435ed84ab565dcca000cafd4554de3c11230edc2fe56d29844984"
ALLOWED_LABELS = {"disclosed", "not_disclosed", "partial", "cannot_tell"}


def post_qc() -> dict[str, Any]:
    expected: dict[str, dict[str, Any]] = {}
    for path in MANIFESTS:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for task in manifest["tasks"]:
            expected[task["judge_task_id"]] = task
    files = sorted(OUTPUT.glob("judge-*.json")) if OUTPUT.exists() else []
    blockers: list[str] = []
    technical_states: Counter[str] = Counter()
    seen: set[str] = set()
    for path in files:
        value = json.loads(path.read_text(encoding="utf-8"))
        task = value.get("task", {})
        task_id = task.get("judge_task_id")
        if task_id in seen:
            blockers.append(f"duplicate task record: {task_id}")
        seen.add(task_id)
        if task_id not in expected:
            blockers.append(f"unexpected task record: {task_id}")
        if task_id in expected and task.get("prompt_hash") != expected[task_id].get("prompt_hash"):
            blockers.append(f"manifest prompt hash mismatch: {path.name}")
        source = ROOT / "experiments/_runs/workshop-v1-main-attempt-2" / f"{task.get('generation_id')}.json"
        if not source.is_file():
            blockers.append(f"missing generation lineage: {path.name}")
        if value.get("immutable") is not True:
            blockers.append(f"mutable record: {path.name}")
        attempts = value.get("attempts")
        if not isinstance(attempts, list) or not attempts:
            blockers.append(f"missing attempts: {path.name}")
            continue
        for attempt in attempts:
            if (attempt.get("prompt_sha256") != PROMPT_HASH
                    and attempt.get("prompt_hash") != PROMPT_HASH
                    and attempt.get("judge_spec_hash") is None):
                # The manifest prompt hash is checked separately; this catches
                # records that explicitly carry a contract prompt hash.
                blockers.append(f"missing prompt/spec provenance: {path.name}")
            state = attempt.get("technical_status")
            if state is not None:
                technical_states[str(state)] += 1
            label = attempt.get("parsed_label")
            if label is not None and label not in ALLOWED_LABELS:
                blockers.append(f"invalid label schema: {path.name}")
    expected_ids = set(expected)
    if len(expected_ids) != 1871:
        blockers.append("manifest workload is not 1871")
    if set(seen) != expected_ids:
        blockers.append("missing or unexpected manifest task IDs")
    result = {
        "schema_version": "direct_judge_post_qc/1",
        "data_kind": "SCIENTIFIC_TECHNICAL_QC",
        "expected_tasks": 1871,
        "persisted_records": len(files),
        "unique_task_ids": len(seen),
        "duplicate_task_ids": len(seen) - len(set(seen)),
        "technical_state_counts": dict(technical_states),
        "scientific_labels_inspected": False,
        "prompt_hash": PROMPT_HASH,
        "ready_to_seal": not blockers and len(files) == 1871,
        "blockers": blockers,
    }
    return result


def seal(result: dict[str, Any]) -> dict[str, Any]:
    if not result.get("ready_to_seal"):
        raise ValueError("direct judge technical QC did not pass")
    payload = json.dumps(result, sort_keys=True, ensure_ascii=True).encode()
    artifact = {
        "schema_version": "judge_stage_seal/1",
        "stage": "direct_judge",
        "post_qc_sha256": hashlib.sha256(payload).hexdigest(),
        "post_qc": result,
        "scientific_labels_inspected": False,
    }
    path = ROOT / "engineering/workshop_v1_direct_judge_stage_seal.json"
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise ValueError("immutable judge-stage seal differs")
    if not path.exists():
        path.write_text(text, encoding="utf-8")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-qc", action="store_true", required=True)
    parser.add_argument("--seal", action="store_true")
    args = parser.parse_args()
    result = post_qc()
    if args.seal:
        print(json.dumps(seal(result), indent=2, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

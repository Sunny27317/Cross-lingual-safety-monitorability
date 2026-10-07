"""Structural QC and sealing helpers for the translated-Urdu judge stage.

This module intentionally never reads or reports judge labels.  It validates
task identity, terminal/attempt metadata, lineage and frozen hashes only.  It
is safe to exercise with synthetic directories while a scientific run is live.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ATTEMPT_LIMIT = 2
FILE_RE = re.compile(r"^(judge-[0-9a-f]+)(?:\.retry-(\d+))?\.json$")
ALLOWED_TECHNICAL = {"VALID_LABEL", "RUNTIME_ERROR", "FORMAT_ERROR"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _retry_state(attempts: list[dict[str, Any]]) -> str:
    statuses = [a.get("technical_status") for a in attempts]
    if any(status not in ALLOWED_TECHNICAL for status in statuses):
        return "MALFORMED_ARTIFACT"
    if "VALID_LABEL" in statuses:
        return "SUCCESS"
    if len(statuses) >= ATTEMPT_LIMIT:
        return "RETRY_EXHAUSTED"
    return "RUNTIME_ERROR_RETRY_AVAILABLE"


def expected_tasks(manifest_path: Path) -> dict[str, dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tasks = manifest.get("tasks")
    if manifest.get("count") != 935 or not isinstance(tasks, list) or len(tasks) != 935:
        raise ValueError("translated judge manifest must contain exactly 935 tasks")
    result: dict[str, dict[str, Any]] = {}
    for task in tasks:
        task_id = task.get("judge_task_id")
        if not isinstance(task_id, str) or task_id in result:
            raise ValueError("manifest contains missing or duplicate judge_task_id")
        result[task_id] = task
    return result


def post_qc(
    output_dir: Path,
    manifest_path: Path,
    *,
    translation_stage_hash: str,
    effective_translation_config_hash: str,
    prompt_hash: str,
    judge_spec_hash: str,
) -> dict[str, Any]:
    expected = expected_tasks(manifest_path)
    files = sorted(output_dir.glob("judge-*.json")) if output_dir.exists() else []
    errors: list[str] = []
    task_files: dict[str, list[Path]] = {}
    records: dict[str, list[dict[str, Any]]] = {}
    for path in files:
        match = FILE_RE.match(path.name)
        if not match:
            errors.append(f"unexpected_file:{path.name}")
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"malformed_json:{path.name}:{type(exc).__name__}")
            continue
        task = value.get("task")
        task_id = task.get("judge_task_id") if isinstance(task, dict) else None
        if not isinstance(task_id, str):
            errors.append(f"missing_task_id:{path.name}")
            continue
        task_files.setdefault(task_id, []).append(path)
        records.setdefault(task_id, []).append(value)
        if task_id not in expected:
            errors.append(f"unexpected_task_id:{task_id}")
        if value.get("immutable") is not True:
            errors.append(f"not_immutable:{path.name}")
        if not isinstance(value.get("attempts"), list) or not value["attempts"]:
            errors.append(f"missing_attempts:{path.name}")
            continue
        if value.get("translation_stage_hash") != translation_stage_hash:
            errors.append(f"translation_stage_hash:{path.name}")
        if value.get("effective_translation_config_hash") != effective_translation_config_hash:
            errors.append(f"effective_config_hash:{path.name}")
        required_task = {
            "generation_id", "translation_id", "source_item_id", "model", "language",
            "condition", "sample_index",
        }
        if not required_task.issubset(task):
            errors.append(f"task_schema:{path.name}")
        for attempt in value["attempts"]:
            if not isinstance(attempt, dict) or attempt.get("technical_status") not in ALLOWED_TECHNICAL:
                errors.append(f"attempt_schema:{path.name}")
                continue
            if attempt.get("judge_spec_hash") != judge_spec_hash:
                errors.append(f"judge_spec_hash:{path.name}")
            if attempt.get("prompt_sha256") is None:
                errors.append(f"prompt_provenance:{path.name}")
    duplicate_ids = sorted(task_id for task_id, paths in task_files.items() if len(paths) > 2)
    for task_id, paths in task_files.items():
        if len(paths) > 1 and not all(".retry-" in path.name for path in paths[1:]):
            errors.append(f"conflicting_attempt_files:{task_id}")
    states: dict[str, str] = {}
    for task_id, values in records.items():
        attempts: list[dict[str, Any]] = []
        for value in sorted(values, key=lambda row: bool(row.get("retry_of"))):
            attempts.extend(value.get("attempts", []))
        states[task_id] = _retry_state(attempts)
    ids = set(records)
    terminal = {"SUCCESS", "RETRY_EXHAUSTED", "MALFORMED_ARTIFACT"}
    report: dict[str, Any] = {
        "schema_version": "workshop-v1-translated-judge-post-qc/1",
        "scientific_content_inspected": False,
        "expected_tasks": len(expected),
        "persisted_task_ids": len(ids),
        "unique_task_ids": len(ids) == len(task_files),
        "duplicate_task_ids": duplicate_ids,
        "missing_task_ids": sorted(set(expected) - ids),
        "unexpected_task_ids": sorted(ids - set(expected)),
        "malformed_or_unexpected_files": sorted(errors),
        "successful_tasks": sum(state == "SUCCESS" for state in states.values()),
        "runtime_failure_tasks": sum(state == "RUNTIME_ERROR_RETRY_AVAILABLE" for state in states.values()),
        "retry_exhausted_tasks": sum(state == "RETRY_EXHAUSTED" for state in states.values()),
        "terminal_state_counts": {
            state: sum(value == state for value in states.values()) for state in terminal
        },
        "output_manifest_sha256": _output_manifest_hash(output_dir),
    }
    report["ready_to_seal"] = not (
        report["missing_task_ids"]
        or report["unexpected_task_ids"]
        or report["duplicate_task_ids"]
        or report["malformed_or_unexpected_files"]
        or any(state != "SUCCESS" for state in states.values())
    )
    report["human_summary"] = (
        f"technical QC: expected={report['expected_tasks']} persisted={report['persisted_task_ids']} "
        f"success={report['successful_tasks']} runtime_failure={report['runtime_failure_tasks']} "
        f"retry_exhausted={report['retry_exhausted_tasks']} "
        f"missing={len(report['missing_task_ids'])} errors={len(report['malformed_or_unexpected_files'])} "
        f"ready_to_seal={'YES' if report['ready_to_seal'] else 'NO'}"
    )
    return report


def _output_manifest_hash(output_dir: Path) -> str:
    entries = []
    for path in sorted(output_dir.glob("judge-*.json")) if output_dir.exists() else []:
        entries.append({"name": path.name, "sha256": _sha256(path), "bytes": path.stat().st_size})
    return _json_hash(entries)


def output_manifest(output_dir: Path) -> list[dict[str, Any]]:
    """Return label-free, trace-free metadata for every persisted output."""
    rows: list[dict[str, Any]] = []
    for path in sorted(output_dir.glob("judge-*.json")) if output_dir.exists() else []:
        value = json.loads(path.read_text(encoding="utf-8"))
        task = value["task"]
        attempts = value.get("attempts", [])
        rows.append({
            "task_identifier": task["judge_task_id"],
            "filename": path.name,
            "file_sha256": _sha256(path),
            "technical_attempts": [
                {
                    "attempt": attempt.get("attempt"),
                    "technical_status": attempt.get("technical_status"),
                    "retry_reason": attempt.get("retry_reason"),
                }
                for attempt in attempts
            ],
            "translation_stage_hash": value.get("translation_stage_hash"),
            "effective_translation_config_hash": value.get("effective_translation_config_hash"),
            "translation_record_sha256": value.get("translation_record_sha256"),
            "structural_terminal_state": value.get("terminal_state"),
        })
    return rows


def write_output_manifest(output_dir: Path, destination: Path) -> str:
    rows = output_manifest(output_dir)
    payload = (json.dumps({
        "schema_version": "workshop-v1-translated-judge-output-manifest/1",
        "scientific_content_inspected": False,
        "records": rows,
    }, indent=2, sort_keys=True) + "\n").encode()
    destination.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def write_seal(
    seal_path: Path,
    report: dict[str, Any],
    *,
    authorization_sha256: str,
    translation_stage_hash: str,
    effective_translation_config_hash: str,
    prompt_hash: str,
    judge_spec_hash: str,
    task_manifest_sha256: str,
    code_hashes: dict[str, str],
    base_commit: str,
    post_qc_report_sha256: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if report.get("ready_to_seal") is not True:
        raise ValueError("cannot seal: post-QC did not pass")
    value = {
        "schema_version": "workshop-v1-translated-judge-seal/1",
        "stage": "translated_urdu_judge",
        "created_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "scientific_content_inspected": False,
        "expected_tasks": report["expected_tasks"],
        "valid_task_count": report["successful_tasks"],
        "missing_task_count": len(report["missing_task_ids"]),
        "technical_failure_count": report["runtime_failure_tasks"] + report["retry_exhausted_tasks"],
        "translation_stage_hash": translation_stage_hash,
        "effective_translation_config_hash": effective_translation_config_hash,
        "judge_prompt_hash": prompt_hash,
        "judge_spec_hash": judge_spec_hash,
        "task_manifest_sha256": task_manifest_sha256,
        "authorization_sha256": authorization_sha256,
        "post_qc_report_sha256": post_qc_report_sha256 or _json_hash(report),
        "output_manifest_sha256": report["output_manifest_sha256"],
        "code_hashes": code_hashes,
        "base_commit": base_commit,
    }
    if extra:
        value.update(extra)
    value["seal_sha256"] = _json_hash(value)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    if seal_path.exists() and seal_path.read_bytes() != payload:
        raise ValueError("immutable seal exists with different content")
    if not seal_path.exists():
        seal_path.write_bytes(payload)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="technical translated-judge QC; never reports labels")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--translation-stage-hash", required=True)
    parser.add_argument("--effective-config-hash", required=True)
    parser.add_argument("--prompt-hash", required=True)
    parser.add_argument("--judge-spec-hash", required=True)
    args = parser.parse_args()
    print(json.dumps(post_qc(args.output, args.manifest, translation_stage_hash=args.translation_stage_hash,
                             effective_translation_config_hash=args.effective_config_hash,
                             prompt_hash=args.prompt_hash, judge_spec_hash=args.judge_spec_hash),
                   indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Outcome-blind translated-judge QC, state machine, and stage-seal design.

This module does not inspect or summarize scientific labels.  It operates on
technical attempt metadata and is exercised here only with synthetic fixtures.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATES = (
    "SUCCESS",
    "RUNTIME_ERROR_RETRY_AVAILABLE",
    "SUCCESS_ON_RETRY",
    "RETRY_EXHAUSTED",
    "FORMAT_ERROR",
    "MALFORMED_ARTIFACT",
    "MISSING",
    "ORPHAN_RETRY",
    "CONFLICTING_ATTEMPTS",
)
MAX_ATTEMPTS = 2


@dataclass(frozen=True)
class StateRule:
    terminal: bool
    retry_allowed: bool
    model_call_allowed: bool
    analysis_included: bool
    investigator_action: str


STATE_RULES = {
    "SUCCESS": StateRule(True, False, False, True, "none"),
    "SUCCESS_ON_RETRY": StateRule(True, False, False, True, "none"),
    "RUNTIME_ERROR_RETRY_AVAILABLE": StateRule(False, True, True, False, "governed resume"),
    "RETRY_EXHAUSTED": StateRule(True, False, False, False, "retain as missing"),
    "FORMAT_ERROR": StateRule(True, False, False, False, "investigator review if protocol requires"),
    "MALFORMED_ARTIFACT": StateRule(True, False, False, False, "repair infrastructure, preserve artifact"),
    "MISSING": StateRule(True, False, False, False, "investigator review if protocol requires"),
    "ORPHAN_RETRY": StateRule(True, False, False, False, "preserve and reconcile provenance"),
    "CONFLICTING_ATTEMPTS": StateRule(True, False, False, False, "investigator review"),
}


def attempt_state(attempts: list[dict[str, Any]]) -> str:
    """Classify one task without reading label values."""
    if not attempts:
        return "MISSING"
    numbers = [a.get("attempt") for a in attempts]
    if any(not isinstance(n, int) or n < 1 for n in numbers):
        return "MALFORMED_ARTIFACT"
    numeric = [n for n in numbers if isinstance(n, int)]
    if len(set(numbers)) != len(numbers) or sorted(numeric) != list(range(1, len(numbers) + 1)):
        return "CONFLICTING_ATTEMPTS"
    statuses = [a.get("technical_status") for a in attempts]
    if any(
        status not in {"RUNTIME_ERROR", "VALID_LABEL", "NO_LABEL", "MALFORMED_OUTPUT", "TRUNCATED"}
        for status in statuses
    ):
        return "MALFORMED_ARTIFACT"
    if any(status in {"VALID_LABEL", "NO_LABEL", "MALFORMED_OUTPUT", "TRUNCATED"} for status in statuses):
        if statuses[-1] != "VALID_LABEL":
            return "FORMAT_ERROR"
        return "SUCCESS_ON_RETRY" if len(attempts) > 1 else "SUCCESS"
    if len(attempts) == 1:
        return "RUNTIME_ERROR_RETRY_AVAILABLE"
    return "RETRY_EXHAUSTED"


def qc_records(
    records: list[dict[str, Any]],
    expected_task_ids: set[str],
    *,
    required_provenance: dict[str, str] | None = None,
) -> dict[str, Any]:
    """QC synthetic or future post-run records using technical metadata only."""
    errors: list[str] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        task_id = record.get("task_id")
        if not isinstance(task_id, str) or task_id not in expected_task_ids:
            errors.append(f"unexpected:{task_id}")
            continue
        if task_id in grouped:
            errors.append(f"duplicate_task:{task_id}")
        grouped.setdefault(task_id, []).extend(record.get("attempts", []))
        for key, expected in (required_provenance or {}).items():
            if record.get(key) != expected:
                errors.append(f"{task_id}:{key}")
    states = {task_id: attempt_state(attempts) for task_id, attempts in grouped.items()}
    missing = expected_task_ids - set(grouped)
    counts = {state: sum(value == state for value in states.values()) for state in STATES}
    return {
        "schema_version": "workshop-v1-translated-judge-qc/1",
        "scientific_outcomes_inspected": False,
        "expected_tasks": len(expected_task_ids),
        "represented_tasks": len(grouped),
        "missing_tasks": len(missing),
        "states": counts,
        "errors": sorted(set(errors)),
        "pass": not errors
        and not missing
        and all(states[task_id] in {"SUCCESS", "SUCCESS_ON_RETRY"} for task_id in states),
    }


def technical_progress(qc: dict[str, Any]) -> dict[str, Any]:
    """Return technical progress only; never expose scientific label counts."""
    states = qc.get("states", {})
    return {
        "expected_tasks": qc.get("expected_tasks", 0),
        "completed_tasks": qc.get("represented_tasks", 0),
        "successful_tasks": states.get("SUCCESS", 0) + states.get("SUCCESS_ON_RETRY", 0),
        "runtime_failures": states.get("RUNTIME_ERROR_RETRY_AVAILABLE", 0),
        "retry_exhausted": states.get("RETRY_EXHAUSTED", 0),
        "malformed_outputs": states.get("MALFORMED_ARTIFACT", 0) + states.get("FORMAT_ERROR", 0),
        "missing": states.get("MISSING", 0),
        "remaining": qc.get("missing_tasks", 0),
    }


def build_stage_seal(
    qc: dict[str, Any], *, provenance: dict[str, Any], created_utc: str | None = None
) -> dict[str, Any]:
    """Build, but do not write, a future translated-judge stage seal."""
    if not qc.get("pass"):
        raise ValueError("cannot seal a failed technical QC")
    seal = {
        "schema_version": "workshop-v1-translated-judge-stage-seal/1",
        "scientific_outcomes_inspected": False,
        "created_utc": created_utc or datetime.now(UTC).isoformat(),
        "technical_qc": qc,
        "provenance": provenance,
    }
    seal["qc_hash"] = hashlib.sha256(
        json.dumps(qc, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    seal["translated_judge_stage_hash"] = hashlib.sha256(
        json.dumps(seal, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return seal


def write_stage_seal(path: Path, seal: dict[str, Any]) -> None:
    """Single canonical writer for a future seal; refuses all mutation."""
    payload = (json.dumps(seal, sort_keys=True, indent=2) + "\n").encode()
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError("immutable translated-judge seal differs")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


__all__ = [
    "MAX_ATTEMPTS",
    "STATES",
    "STATE_RULES",
    "attempt_state",
    "build_stage_seal",
    "qc_records",
    "technical_progress",
    "write_stage_seal",
]

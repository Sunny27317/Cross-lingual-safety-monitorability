"""Synthetic-testable, fail-closed human packet and annotation QC helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any

RATER_LABELS = {"disclosed", "not_disclosed", "partial", "cannot_tell", "abstain"}
ADJUDICATION_LABELS = RATER_LABELS | {"unresolved"}


def packet_hash(rows: list[dict[str, Any]]) -> str:
    payload = "\n".join(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows) + "\n"
    return hashlib.sha256(payload.encode()).hexdigest()


def validate_packet(rows: list[dict[str, Any]], expected_ids: set[str]) -> dict[str, Any]:
    errors: list[str] = []
    ids = [row.get("blind_id") for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate_blind_id")
    if set(ids) != expected_ids:
        errors.append("packet_id_set_mismatch")
    for row in rows:
        if set(row) - {"blind_id", "language", "question", "options", "suggestion", "trace"}:
            errors.append(f"forbidden_field:{row.get('blind_id')}")
        if not isinstance(row.get("trace"), str) or not row["trace"].strip():
            errors.append(f"missing_trace:{row.get('blind_id')}")
    return {
        "count": len(rows),
        "packet_hash": packet_hash(rows),
        "errors": sorted(set(errors)),
        "pass": not errors,
    }


def validate_annotations(
    rows: list[dict[str, Any]], expected_ids: set[str], *, packet_sha256: str
) -> dict[str, Any]:
    errors: list[str] = []
    seen: set[str] = set()
    for row in rows:
        bid = row.get("blind_id")
        if bid in seen or bid not in expected_ids:
            errors.append(f"invalid_or_duplicate_id:{bid}")
        if isinstance(bid, str):
            seen.add(bid)
        if row.get("label") not in RATER_LABELS:
            errors.append(f"invalid_label:{bid}")
        if not isinstance(row.get("packet_sha256"), str) or row["packet_sha256"] != packet_sha256:
            errors.append(f"packet_hash_mismatch:{bid}")
    if seen != expected_ids:
        errors.append("missing_annotation_rows")
    return {"count": len(rows), "errors": sorted(set(errors)), "pass": not errors}


def adjudication_ids(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> set[str]:
    by_id: dict[str, set[str]] = {}
    for row in left + right:
        by_id.setdefault(str(row.get("blind_id")), set()).add(str(row.get("label")))
    return {bid for bid, labels in by_id.items() if len(labels) > 1 or "abstain" in labels}


def validate_adjudication(rows: list[dict[str, Any]], required_ids: set[str]) -> dict[str, Any]:
    errors: list[str] = []
    seen: set[str] = set()
    for row in rows:
        bid = row.get("blind_id")
        if bid in seen or bid not in required_ids:
            errors.append(f"invalid_adjudication_id:{bid}")
        if isinstance(bid, str):
            seen.add(bid)
        if row.get("independent_label") not in RATER_LABELS:
            errors.append(f"invalid_independent_label:{bid}")
        if row.get("final_label") not in ADJUDICATION_LABELS:
            errors.append(f"invalid_final_label:{bid}")
    if seen != required_ids:
        errors.append("missing_adjudications")
    return {
        "required": len(required_ids),
        "received": len(rows),
        "errors": sorted(set(errors)),
        "pass": not errors,
    }

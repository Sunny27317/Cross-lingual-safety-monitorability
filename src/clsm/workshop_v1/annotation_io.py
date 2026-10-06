"""File-backed blinded native-reference exchange; synthetic fixtures only in tests."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Literal

LABELS = {"disclosed", "not_disclosed", "partial", "cannot_tell", "abstain"}
ADJUDICATION_LABELS = LABELS | {"unresolved"}


def export_packet(tasks: list[dict[str, Any]], path: Path) -> None:
    required = {"blind_id", "visible_trace"}
    forbidden = {"model_id", "monitor_output", "translation_output", "condition"}
    if any(not required <= set(task) or forbidden & set(task) for task in tasks) or len(
        {t["blind_id"] for t in tasks}
    ) != len(tasks):
        raise ValueError("packet requires unique blind IDs and visible traces")
    write_immutable_records(path, tasks)


def import_labels(rows: list[dict[str, Any]], valid_ids: set[str]) -> tuple[dict[str, Any], ...]:
    seen: set[str] = set()
    out = []
    for row in rows:
        bid = row.get("blind_id")
        label = row.get("label")
        if not isinstance(bid, str) or bid not in valid_ids or bid in seen:
            raise ValueError("invalid or duplicate blind ID")
        if label not in LABELS:
            raise ValueError("invalid annotation label")
        if not isinstance(row.get("rater_id"), str) or not row["rater_id"].strip():
            raise ValueError("rater_id required")
        seen.add(bid)
        out.append(dict(row))
    if seen != valid_ids:
        raise ValueError("missing annotation rows")
    return tuple(out)


def disagreements(rows: list[dict[str, Any]]) -> tuple[str, ...]:
    """Return IDs needing adjudication for disagreement or either abstention."""
    by_id: dict[str, set[str]] = {}
    for row in rows:
        by_id.setdefault(str(row["blind_id"]), set()).add(str(row["label"]))
    return tuple(sorted(
        bid for bid, labels in by_id.items()
        if len(labels) > 1 or "abstain" in labels
    ))


def validate_adjudications(rows: list[dict[str, Any]], disagreement_ids: set[str]) -> None:
    """Frozen protocol: the adjudicator records an independent blind label first."""
    seen: set[str] = set()
    for row in rows:
        bid = str(row.get("blind_id"))
        label = row.get("label", row.get("final_label"))
        if bid not in disagreement_ids or bid in seen or row.get("rater_id") != "adjudicator":
            raise ValueError("adjudication must uniquely resolve a known disagreement")
        if row.get("independent_label") not in LABELS:
            raise ValueError("adjudication requires an independent first label")
        if label not in ADJUDICATION_LABELS:
            raise ValueError("invalid adjudication label")
        seen.add(bid)
    if seen != disagreement_ids:
        raise ValueError("missing adjudications")


def write_immutable_records(path: Path, rows: list[dict[str, Any]]) -> str:
    """Atomically persist submitted rows; an existing file is never overwritten.

    Returns the SHA-256 of the written bytes, to be recorded as the lock.
    """
    import hashlib

    payload = ("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n").encode()
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"immutable annotation file differs: {path.name}")
        return hashlib.sha256(payload).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    try:
        os.link(temporary, path)  # atomic, never clobbers an existing file
    except FileExistsError:
        raise ValueError(f"immutable annotation file appeared concurrently: {path.name}") from None
    finally:
        temporary.unlink()
    return hashlib.sha256(payload).hexdigest()


def persist_rater_labels(path: Path, rows: list[dict[str, Any]], valid_ids: set[str]) -> str:
    """Validate one rater's complete submission, then write it once, immutably."""
    return write_immutable_records(path, list(import_labels(rows, valid_ids)))


def persist_adjudications(path: Path, rows: list[dict[str, Any]], disagreement_ids: set[str]) -> str:
    """Validate the adjudicator's records (independent first label required), then write once."""
    validate_adjudications(rows, disagreement_ids)
    return write_immutable_records(path, rows)


def reference_labels(
    rater_rows: list[dict[str, Any]], adjudication_rows: list[dict[str, Any]]
) -> dict[str, str]:
    """Native-reader reference H per blind ID (frozen protocol).

    Exactly two raters per ID.  Items in the adjudication set (disagreement or any
    abstention) take the adjudicator's final label, which may be ``unresolved``; all
    other items take the raters' common label.
    """
    by_id: dict[str, list[str]] = {}
    for row in rater_rows:
        by_id.setdefault(str(row["blind_id"]), []).append(str(row["label"]))
    if any(len(labels) != 2 for labels in by_id.values()):
        raise ValueError("each item requires exactly two independent rater labels")
    flagged = set(disagreements(rater_rows))
    validate_adjudications(adjudication_rows, flagged)
    final = {str(r["blind_id"]): str(r.get("label", r.get("final_label"))) for r in adjudication_rows}
    return {bid: (final[bid] if bid in flagged else labels[0]) for bid, labels in by_id.items()}


Variant = Literal["primary", "S1", "S2"]


def binary_disclosure(label: str, variant: Variant = "primary") -> int | None:
    """Frozen analysis plan section 2: disclosed=1, not_disclosed=0; partial, cannot_tell,
    abstain and unresolved are missing (never imputed).  S1 recodes partial as 0 and S2
    recodes partial as 1.
    """
    if label not in ADJUDICATION_LABELS:
        raise ValueError(f"unknown reference label: {label}")
    if label == "disclosed":
        return 1
    if label == "not_disclosed":
        return 0
    if label == "partial" and variant == "S1":
        return 0
    if label == "partial" and variant == "S2":
        return 1
    return None

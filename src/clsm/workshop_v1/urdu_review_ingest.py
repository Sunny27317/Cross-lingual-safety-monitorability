"""Fail-closed ingestion for the human-completed Urdu equivalence packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from clsm.workshop_v1.frozen_validation import CUE_B_HASH, MAIN_HASH, validate_frozen_inputs
from clsm.workshop_v1.local_ingest import EXPECTED_DATASET_REVISION

ALLOWED_STATUSES = frozenset({"PASS", "MINOR_LANGUAGE_ONLY", "MATERIAL_MISMATCH", "UNCERTAIN"})
CHECK_NAMES = (
    "meaning_preserved",
    "option_correspondence_preserved",
    "no_missing_information",
    "no_added_hint",
    "no_obvious_mistranslation",
    "no_answer_option_reordering_mismatch",
)
ITEM_RE = re.compile(r"^### Item \d+: `([^`]+)`$", re.MULTILINE)
STATUS_RE = re.compile(
    r"^- Status:\s*(?:☑|\[x\])?\s*(PASS|MINOR_LANGUAGE_ONLY|MATERIAL_MISMATCH|UNCERTAIN)\s*$",
    re.MULTILINE,
)
ROW_HASH_RE = re.compile(r"^- Source row hash:\s*`?([0-9a-f]{64})`?\s*$", re.MULTILINE)
REVISION_RE = re.compile(r"^- Dataset revision(?: \(frozen\))?:\s*`?([0-9a-f]{40})`?\s*$", re.MULTILINE)
MANIFEST_RE = re.compile(r"^- Main manifest hash:\s*`?([0-9a-f]{64})`?\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ReviewRow:
    item_id: str
    cue_b: bool
    status: str | None
    notes: str
    source_row_hash: str | None
    raw_section: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _pdf_checkbox(section: str, label: str, positive: str, negative: str) -> bool | None:
    """Read a checked choice without treating an unchecked choice as evidence."""
    match = re.search(
        re.escape(label) + r":(.*?)(?= - (?:Meaning preserved|Option correspondence preserved|"
        r"No missing information|No added hint|No obvious mistranslation|"
        r"No answer-option reordering mismatch|Any other material equivalence problem|"
        r"Notes|Status):|$)",
        section,
    )
    chunk = match.group(1) if match else ""
    if re.search(r"☑\s*" + re.escape(positive), chunk):
        return True
    if re.search(r"☑\s*" + re.escape(negative), chunk):
        return False
    return None


def parse_pdf_review(path: Path, *, root: Path) -> dict[str, Any]:
    """Extract the received PDF into a structured, outcome-blind evidence record."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment dependency
        raise RuntimeError("pypdf is required to ingest the formal PDF") from exc
    text = re.sub(r"\s+", " ", " ".join((page.extract_text() or "") for page in PdfReader(str(path)).pages))
    matches = list(re.finditer(r"Item (\d+): ([^ ]+)", text))
    main_ids, cue_ids = _expected(root)
    manifest = json.loads((root / "engineering/workshop_v1_main_manifest.json").read_text())
    answer_keys = {row["source_item_id"]: row.get("answerKey") for row in manifest["items"]}
    # The ID-only manifest intentionally omits benchmark content.  Recover the
    # frozen answer key from the already-validated local snapshot for comparison.
    summary = json.loads((root / "engineering/workshop_v1_dataset_summary.json").read_text())
    try:
        import pyarrow.parquet as pq  # type: ignore[import-untyped]
        snapshot = Path(summary["local_snapshot"])
        for parquet in sorted((snapshot / "data").glob("*.parquet")):
            for source_row in pq.read_table(parquet, columns=["id", "answerKey"]).to_pylist():
                if source_row["id"] in answer_keys:
                    answer_keys[source_row["id"]] = source_row["answerKey"]
    except (OSError, KeyError, ImportError):
        pass
    row_hashes = {row["source_item_id"]: row["row_hash"] for row in manifest["items"]}
    rows: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else text.find("Final reviewer summary")
        section = text[match.end():end]
        item_id = match.group(2)
        status_match = re.search(r"Status:\s*(.*?)(?:\s*$)", section)
        status = next((value for value in sorted(ALLOWED_STATUSES)
                       if status_match and re.search(r"☑\s*" + re.escape(value), status_match.group(1))), None)
        other_match = re.search(r"Any other material equivalence problem:\s*(.*?)(?= - Notes:)", section)
        notes_match = re.search(r"Notes:\s*(.*?)(?= - Status:)", section)
        checks = {
            "meaning_preserved": _pdf_checkbox(section, "Meaning preserved", "Yes", "No"),
            "option_correspondence_preserved": _pdf_checkbox(section, "Option correspondence preserved", "Yes", "No"),
            "no_missing_information": _pdf_checkbox(section, "No missing information", "None missing", "Missing"),
            "no_added_hint": _pdf_checkbox(section, "No added hint", "No", "Yes"),
            "no_obvious_mistranslation": _pdf_checkbox(section, "No obvious mistranslation", "None found", "Found"),
            "no_answer_option_reordering_mismatch": _pdf_checkbox(section, "No answer-option reordering mismatch", "Confirmed", "Mismatch found"),
        }
        answer_match = re.search(r"Dataset answer key \(source field, for check 6 only\):\s*([ABCD])", section)
        rows.append({
            "item_id": item_id,
            "cue_b": item_id in cue_ids,
            "answer_key": answer_keys.get(item_id),
            "reviewed_answer_key": answer_match.group(1) if answer_match else None,
            "source_row_hash": row_hashes.get(item_id),
            "checks": checks,
            "other_material_equivalence_problem": (other_match.group(1).strip() if other_match else ""),
            "notes": (notes_match.group(1).strip() if notes_match else ""),
            "status": status,
        })
    reviewer = re.search(r"Reviewer identifier/name:\s*(.*?)\s*- Native", text)
    native = re.search(r"Native or near-native Urdu speaker:\s*☑\s*(Yes|No)", text)
    review_date = re.search(r"Review date \(UTC\):\s*([^ ]+)", text)
    completion = re.search(r"Review completion status:\s*☑\s*(Complete|Incomplete)", text)
    revision = re.search(r"Dataset revision:\s*([0-9a-f]{40})", text)
    main_hash = re.search(r"Main manifest SHA-256:\s*([0-9a-f]{64})", text)
    cue_hash = re.search(r"Cue-B manifest SHA-256:\s*([0-9a-f]{64})", text)
    return {
        "source_pdf": str(path), "source_pdf_sha256": _sha256(path),
        "reviewer": reviewer.group(1).strip() if reviewer else "",
        "native_or_near_native": native.group(1) == "Yes" if native else None,
        "review_date": review_date.group(1) if review_date else "",
        "completion": completion.group(1) if completion else "",
        "dataset_revision": revision.group(1) if revision else "",
        "main_manifest_hash": main_hash.group(1) if main_hash else "",
        "cue_b_manifest_hash": cue_hash.group(1) if cue_hash else "",
        "rows": rows, "expected_main_ids": sorted(main_ids), "expected_cue_b_ids": sorted(cue_ids),
    }


def validate_pdf_review(path: Path, *, root: Path) -> dict[str, Any]:
    parsed = parse_pdf_review(path, root=root)
    rows = parsed["rows"]
    expected_main, expected_cue = _expected(root)
    ids = [row["item_id"] for row in rows]
    duplicate = sorted({item for item in ids if ids.count(item) > 1})
    actual = set(ids)
    missing = sorted(expected_main - actual)
    unexpected = sorted(actual - expected_main)
    cue_errors = sorted(row["item_id"] for row in rows if row["cue_b"] != (row["item_id"] in expected_cue))
    answer_key_errors = sorted(row["item_id"] for row in rows
                               if row["reviewed_answer_key"] != row["answer_key"])
    incomplete = []
    negative = []
    for row in rows:
        for name, value in row["checks"].items():
            if value is None:
                incomplete.append({"item_id": row["item_id"], "cue_b": row["cue_b"], "field": name,
                                   "status": row["status"], "reason": "required checkbox blank/unselected"})
            elif value is False:
                negative.append({"item_id": row["item_id"], "cue_b": row["cue_b"], "field": name,
                                 "status": row["status"], "reason": "reviewer selected negative option"})
    counts = {status: sum(row["status"] == status for row in rows) for status in sorted(ALLOWED_STATUSES)}
    errors: dict[str, Any] = {}
    for key, value in (("count", len(rows) != 120), ("unique_count", len(actual) != 120),
                       ("missing_ids", missing), ("unexpected_ids", unexpected), ("duplicate_ids", duplicate),
                       ("cue_membership_errors", cue_errors), ("answer_key_errors", answer_key_errors),
                       ("cue_b_manifest_hash", parsed["cue_b_manifest_hash"] != CUE_B_HASH),
                       ("reviewer", not parsed["reviewer"]),
                       ("review_date", not parsed["review_date"]), ("completion", parsed["completion"] != "Complete"),
                       ("dataset_revision", parsed["dataset_revision"] != EXPECTED_DATASET_REVISION),
                       ("main_manifest_hash", parsed["main_manifest_hash"] != MAIN_HASH)):
        if value:
            errors[key] = value
    parsed.update({"status_counts": counts, "incomplete_items": incomplete, "negative_items": negative,
                   "duplicate_ids": duplicate, "missing_ids": missing, "unexpected_ids": unexpected,
                   "cue_membership_errors": cue_errors, "errors": errors,
                   "valid_structure": not errors and not incomplete,
                   "reviewer_clarification_required": bool(incomplete),
                   "governance_action_required": bool(negative) or counts["MATERIAL_MISMATCH"] + counts["UNCERTAIN"] > 0})
    return parsed


def validate_telephone_clarification(path: Path, *, review: dict[str, Any], root: Path) -> dict[str, Any]:
    """Validate investigator-recorded reviewer clarification without editing PDF evidence."""
    record = json.loads(path.read_text(encoding="utf-8"))
    expected = {"11-56", "7-700", "13-304"}
    entries = record.get("clarifications", [])
    actual = {entry.get("item_id") for entry in entries}
    errors: dict[str, Any] = {}
    if record.get("provenance_type") != "investigator_recorded_telephone_clarification_from_reviewer":
        errors["provenance_type"] = record.get("provenance_type")
    if record.get("original_pdf_sha256") != review.get("source_pdf_sha256"):
        errors["original_pdf_sha256"] = record.get("original_pdf_sha256")
    if actual != expected or len(entries) != len(expected):
        errors["item_ids"] = sorted(actual ^ expected)
    if any(entry.get("field") != "meaning_preserved" or entry.get("value") is not True for entry in entries):
        errors["values"] = "all three clarifications must explicitly confirm Yes"
    if not record.get("clarification_date") or not record.get("recorded_by"):
        errors["metadata"] = "clarification date and recorder are required"
    if record.get("reviewer_signature") is not None:
        errors["reviewer_signature"] = "written reviewer signature must not be fabricated"
    if record.get("dataset_revision") != EXPECTED_DATASET_REVISION or record.get("main_manifest_hash") != MAIN_HASH:
        errors["frozen_provenance"] = "dataset or main manifest mismatch"
    return {"valid": not errors, "errors": errors, "sha256": _sha256(path), **record}


def apply_telephone_clarification(review: dict[str, Any], clarification: dict[str, Any]) -> dict[str, Any]:
    """Return a derived closure view; the original extracted review stays unchanged."""
    if not clarification.get("valid"):
        raise ValueError("telephone clarification is invalid")
    derived = json.loads(json.dumps(review))
    for entry in clarification["clarifications"]:
        row = next(row for row in derived["rows"] if row["item_id"] == entry["item_id"])
        row["checks"][entry["field"]] = True
        row["supplemental_clarification"] = {
            "value": True, "record_sha256": clarification["sha256"],
            "clarification_date": clarification["clarification_date"],
        }
    return validate_review_record(derived)


def validate_review_record(review: dict[str, Any]) -> dict[str, Any]:
    """Recompute structural/check completeness fields for a parsed or derived view."""
    rows = review["rows"]
    incomplete, negative = [], []
    for row in rows:
        for name, value in row["checks"].items():
            if value is None:
                incomplete.append({"item_id": row["item_id"], "cue_b": row["cue_b"], "field": name,
                                   "status": row["status"], "reason": "required checkbox blank/unselected"})
            elif value is False:
                negative.append({"item_id": row["item_id"], "cue_b": row["cue_b"], "field": name,
                                 "status": row["status"], "reason": "reviewer selected negative option"})
    counts = {status: sum(row["status"] == status for row in rows) for status in sorted(ALLOWED_STATUSES)}
    review["incomplete_items"], review["negative_items"] = incomplete, negative
    review["status_counts"] = counts
    review["valid_structure"] = not review.get("errors") and not incomplete
    review["reviewer_clarification_required"] = bool(incomplete)
    review["governance_action_required"] = bool(negative) or counts["MATERIAL_MISMATCH"] + counts["UNCERTAIN"] > 0
    return review


def _expected(root: Path) -> tuple[set[str], set[str]]:
    import json
    main = json.loads((root / "engineering/workshop_v1_main_manifest.json").read_text())
    cue = json.loads((root / "engineering/workshop_v1_cue_b_manifest.json").read_text())
    return ({x["source_item_id"] for x in main["items"]}, {x["source_item_id"] for x in cue["items"]})


def parse_packet(path: Path, *, root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    main_ids, cue_ids = _expected(root)
    matches = list(ITEM_RE.finditer(text))
    rows: list[ReviewRow] = []
    for index, match in enumerate(matches):
        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else text.find("## Final reviewer summary")
        )
        section = text[match.end():end]
        item_id = match.group(1)
        status_matches = STATUS_RE.findall(section)
        status = status_matches[0] if len(status_matches) == 1 else None
        notes_match = re.search(r"^- Notes:\s*(.*)$", section, re.MULTILINE)
        cue_match = re.search(
            r"^- In frozen 36-item Cue-B subset:\s*\*\*(Yes|No)\*\*", section, re.MULTILINE
        )
        rows.append(ReviewRow(item_id, bool(cue_match and cue_match.group(1) == "Yes"), status,
                              notes_match.group(1).strip() if notes_match else "", None, section))
    duplicates = sorted({row.item_id for row in rows if sum(x.item_id == row.item_id for x in rows) > 1})
    actual = {row.item_id for row in rows}
    missing = sorted(main_ids - actual)
    unexpected = sorted(actual - main_ids)
    cue_errors = sorted(row.item_id for row in rows if (row.item_id in cue_ids) != row.cue_b)
    status_errors = sorted(
        row.item_id for row in rows if row.status is not None and row.status not in ALLOWED_STATUSES
    )
    reviewer = re.search(r"^- Reviewer identifier/name:[ \t]*(.*)$", text, re.MULTILINE)
    date = re.search(r"^- Review date \(UTC\):[ \t]*(.*)$", text, re.MULTILINE)
    revision = REVISION_RE.search(text)
    manifest = MANIFEST_RE.search(text)
    expected_rows = json.loads((root / "engineering/workshop_v1_main_manifest.json").read_text())["items"]
    expected_hashes = {row["source_item_id"]: row["row_hash"] for row in expected_rows}
    for index, row in enumerate(rows):
        hash_match = ROW_HASH_RE.search(row.raw_section)
        rows[index] = ReviewRow(
            row.item_id, row.cue_b, row.status, row.notes,
            hash_match.group(1) if hash_match else None, row.raw_section,
        )
    return {
        "rows": rows, "count": len(rows), "unique_count": len(actual), "missing_ids": missing,
        "unexpected_ids": unexpected, "duplicate_ids": duplicates, "cue_membership_errors": cue_errors,
        "status_errors": status_errors, "reviewer": reviewer.group(1).strip() if reviewer else "",
        "review_date": date.group(1).strip() if date else "",
        "dataset_revision": revision.group(1) if revision else "",
        "main_manifest_hash": manifest.group(1) if manifest else "",
        "expected_row_hashes": expected_hashes,
    }


def validate_packet(path: Path, *, root: Path) -> dict[str, Any]:
    validate_frozen_inputs(root, require_snapshot=False)
    parsed = parse_packet(path, root=root)
    errors = {key: value for key, value in (
        ("count", parsed["count"] != 120), ("unique_count", parsed["unique_count"] != 120),
        ("missing_ids", parsed["missing_ids"]), ("unexpected_ids", parsed["unexpected_ids"]),
        ("duplicate_ids", parsed["duplicate_ids"]),
        ("cue_membership_errors", parsed["cue_membership_errors"]),
        ("status_errors", parsed["status_errors"]),
        ("reviewer", not parsed["reviewer"]),
        ("review_date", not parsed["review_date"]),
        ("dataset_revision", parsed["dataset_revision"] != EXPECTED_DATASET_REVISION),
        ("main_manifest_hash", parsed["main_manifest_hash"] != MAIN_HASH),
    ) if value}
    hash_errors = sorted(
        row.item_id for row in parsed["rows"]
        if row.source_row_hash != parsed["expected_row_hashes"].get(row.item_id)
    )
    if hash_errors:
        errors["source_row_hash_errors"] = hash_errors
    counts = {
        status: sum(row.status == status for row in parsed["rows"])
        for status in sorted(ALLOWED_STATUSES)
    }
    notes_errors = sorted(
        row.item_id for row in parsed["rows"]
        if row.status in {"MINOR_LANGUAGE_ONLY", "MATERIAL_MISMATCH", "UNCERTAIN"}
        and not row.notes.strip()
    )
    if notes_errors:
        errors["notes_required_errors"] = notes_errors
    incomplete = sum(row.status is None for row in parsed["rows"])
    parsed.update({"valid_structure": not errors, "errors": errors, "status_counts": counts,
                   "incomplete_rows": incomplete,
                   "governance_action_required": counts["MATERIAL_MISMATCH"] + counts["UNCERTAIN"] > 0})
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = validate_packet(args.packet, root=args.root.resolve())
    result["rows"] = [asdict(row) for row in result["rows"]]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["valid_structure"] else 1)


if __name__ == "__main__":
    main()

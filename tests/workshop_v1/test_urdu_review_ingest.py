import json
from pathlib import Path

import pytest

from clsm.workshop_v1.frozen_validation import MAIN_HASH
from clsm.workshop_v1.local_ingest import EXPECTED_DATASET_REVISION
from clsm.workshop_v1.urdu_review_ingest import (
    apply_telephone_clarification,
    validate_packet,
    validate_pdf_review,
    validate_telephone_clarification,
)


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _packet(root: Path, *, omit: str | None = None, duplicate: bool = False,
            wrong_hash: str | None = None, wrong_cue: str | None = None,
            reviewer: str = "Amna", date: str = "2026-10-10", status: str = "PASS",
            notes: str = "") -> str:
    main = json.loads((root / "engineering/workshop_v1_main_manifest.json").read_text())
    cue = {x["source_item_id"] for x in json.loads(
        (root / "engineering/workshop_v1_cue_b_manifest.json").read_text()
    )["items"]}
    rows = []
    for i, item in enumerate(main["items"], 1):
        if item["source_item_id"] == omit:
            continue
        sid = item["source_item_id"]
        is_cue = sid in cue
        if sid == wrong_cue:
            is_cue = not is_cue
        row_hash = wrong_hash if sid == wrong_hash else item["row_hash"]
        rows.append(
            f"### Item {i}: `{sid}`\n\n"
            f"- Dataset revision (frozen): `{EXPECTED_DATASET_REVISION}`\n"
            f"- Source row hash: `{row_hash}`\n"
            f"- In frozen 36-item Cue-B subset: **{'Yes' if is_cue else 'No'}**\n"
            f"- Status: {status}\n- Notes: {notes}\n"
        )
    if duplicate and rows:
        rows.append(rows[0])
    return (
        f"# Review\n\n- Dataset revision (frozen): `{EXPECTED_DATASET_REVISION}`\n"
        f"- Main manifest hash: `{MAIN_HASH}`\n- Reviewer identifier/name: {reviewer}\n"
        f"- Review date (UTC): {date}\n\n" + "\n".join(rows) + "\n## Final reviewer summary\n"
    )


def test_synthetic_complete_packet_passes(repo_root: Path, tmp_path: Path) -> None:
    path = tmp_path / "review.md"
    path.write_text(_packet(repo_root), encoding="utf-8")
    result = validate_packet(path, root=repo_root)
    assert result["valid_structure"] and result["count"] == 120


def test_ingester_rejects_missing_duplicate_cue_and_hash(repo_root: Path, tmp_path: Path) -> None:
    for kwargs in (
        {"omit": "9-401"}, {"duplicate": True}, {"wrong_cue": "9-401"},
        {"wrong_hash": "9-401"},
    ):
        path = tmp_path / ("case-" + str(len(list(tmp_path.iterdir()))) + ".md")
        path.write_text(_packet(repo_root, **kwargs), encoding="utf-8")
        assert not validate_packet(path, root=repo_root)["valid_structure"]


def test_ingester_requires_reviewer_date_and_notes(repo_root: Path, tmp_path: Path) -> None:
    path = tmp_path / "metadata.md"
    path.write_text(_packet(repo_root, reviewer="", date=""), encoding="utf-8")
    result = validate_packet(path, root=repo_root)
    assert "reviewer" in result["errors"] and "review_date" in result["errors"]
    path.write_text(_packet(repo_root, status="UNCERTAIN"), encoding="utf-8")
    assert "notes_required_errors" in validate_packet(path, root=repo_root)["errors"]


def test_ingester_flags_material_mismatch_for_governance(repo_root: Path, tmp_path: Path) -> None:
    path = tmp_path / "mismatch.md"
    path.write_text(_packet(repo_root, status="MATERIAL_MISMATCH", notes="synthetic issue"), encoding="utf-8")
    result = validate_packet(path, root=repo_root)
    assert result["valid_structure"] and result["governance_action_required"]


def test_received_pdf_is_fail_closed_on_blank_required_checks(repo_root: Path) -> None:
    pdf = repo_root / "engineering/provenance/URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.pdf"
    result = validate_pdf_review(pdf, root=repo_root)
    assert result["status_counts"]["PASS"] == 120
    assert {row["item_id"] for row in result["incomplete_items"]} == {"11-56", "7-700", "13-304"}
    assert result["reviewer_clarification_required"]
    assert not result["governance_action_required"]


def test_telephone_clarification_closes_only_the_three_blank_checks(repo_root: Path) -> None:
    pdf = repo_root / "engineering/provenance/URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.pdf"
    path = repo_root / "engineering/provenance/AMNA_TELEPHONE_CLARIFICATION_2026-10-01.json"
    review = validate_pdf_review(pdf, root=repo_root)
    clarification = validate_telephone_clarification(path, review=review, root=repo_root)
    assert clarification["valid"]
    closed = apply_telephone_clarification(review, clarification)
    assert closed["valid_structure"]
    assert not closed["incomplete_items"]
    assert closed["status_counts"]["PASS"] == 120
    assert review["reviewer_clarification_required"]  # original extraction is unchanged

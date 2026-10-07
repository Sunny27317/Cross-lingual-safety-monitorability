# ruff: noqa: RUF001 -- Urdu fixture literals are intentional.
from __future__ import annotations

import json

import pytest

from clsm.workshop_v1.artifact_contract import validate_artifact_envelope
from clsm.workshop_v1.human_pool import HumanCandidate, parity_export_rows, validate_pool
from clsm.workshop_v1.judge_plan import checkpoint_action, validate_plans


def test_dry_run_judge_and_translation_counts() -> None:
    result = validate_plans()
    assert result["english_direct"] == 936
    assert result["urdu_direct"] == 935
    assert result["translated_urdu"] == 935
    assert result["translation"] == 935
    assert result["total_judge"] == 2806
    assert result["scientific_execution"] is False


def test_artifact_envelope_requires_provenance() -> None:
    value = {
        "schema_version": "judge_qc/1", "stage": "judge", "data_kind": "TEMPLATE",
        "dataset_revision": "r", "manifest_hash": "m", "study_hash": "s", "code_head": "c",
    }
    validate_artifact_envelope("judge_qc.json", value, allow_template=True)
    with pytest.raises(ValueError):
        validate_artifact_envelope("judge_qc.json", {**value, "FEASIBILITY_ONLY": True}, allow_template=True)


def test_checkpoint_resume_is_immutable(tmp_path) -> None:
    path = tmp_path / "record.json"
    path.write_text(json.dumps({
        "plan_id": "p", "study_hash": "s", "immutable": True, "technical_status": "SUCCESS",
    }))
    assert checkpoint_action(path, plan_id="p", study_hash="s") == "SKIP"
    path.write_text(json.dumps({
        "plan_id": "p", "study_hash": "s", "immutable": True, "technical_status": "FAILED",
    }))
    assert checkpoint_action(path, plan_id="p", study_hash="s") == "RETRY"
    with pytest.raises(ValueError):
        checkpoint_action(path, plan_id="changed", study_hash="s")


def test_human_pool_is_312_and_blocked_from_execution() -> None:
    result = validate_pool()
    assert result["count"] == 312
    assert result["cue_a"] == 240 and result["cue_b"] == 72
    assert result["blocks"] == 12
    assert result["language_compliance_filter"] is False
    assert result["annotation_executed"] is False


def test_human_parity_export_contains_context_without_model_metadata() -> None:
    candidate = HumanCandidate("item", "row", "model", "cue_a", 0, "selection")
    rows = parity_export_rows((candidate,), {("item", "model", "cue_a", 0): {
        "language": "ur", "question": "سوال", "options": {
            "A": "ا", "B": "ب", "C": "ج", "D": "د"
        },
        "suggestion": "تجویز", "trace": "متن",
    }})
    assert set(rows[0]) == {"blind_id", "language", "question", "options", "suggestion", "trace"}

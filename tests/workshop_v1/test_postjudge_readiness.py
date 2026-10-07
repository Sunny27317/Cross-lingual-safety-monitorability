from pathlib import Path
from typing import Any

from clsm.workshop_v1.analysis_executor import validate_analysis_gate
from clsm.workshop_v1.human_annotation_pipeline import (
    adjudication_ids,
    validate_adjudication,
    validate_annotations,
    validate_packet,
)
from clsm.workshop_v1.post_judge_pipeline import (
    STATE_RULES,
    attempt_state,
    build_stage_seal,
    qc_records,
    technical_progress,
)
from clsm.workshop_v1.publication_artifacts import table_template
from clsm.workshop_v1.translation_terminal_verify import verify_translation_directory


def test_postjudge_state_machine_and_zero_label_progress() -> None:
    assert attempt_state([]) == "MISSING"
    assert (
        attempt_state([{"attempt": 1, "technical_status": "RUNTIME_ERROR"}])
        == "RUNTIME_ERROR_RETRY_AVAILABLE"
    )
    assert (
        attempt_state(
            [
                {"attempt": 1, "technical_status": "RUNTIME_ERROR"},
                {"attempt": 2, "technical_status": "RUNTIME_ERROR"},
            ]
        )
        == "RETRY_EXHAUSTED"
    )
    assert (
        attempt_state(
            [
                {"attempt": 1, "technical_status": "RUNTIME_ERROR"},
                {"attempt": 2, "technical_status": "VALID_LABEL"},
            ]
        )
        == "SUCCESS_ON_RETRY"
    )
    qc = qc_records(
        [
            {
                "task_id": "t1",
                "translation_stage_hash": "s",
                "attempts": [{"attempt": 1, "technical_status": "VALID_LABEL"}],
            }
        ],
        {"t1"},
        required_provenance={"translation_stage_hash": "s"},
    )
    progress = technical_progress(qc)
    assert progress["successful_tasks"] == 1
    assert "label_counts" not in progress
    seal = build_stage_seal(
        qc, provenance={"translation_stage_hash": "s"}, created_utc="2026-01-01T00:00:00+00:00"
    )
    assert seal["scientific_outcomes_inspected"] is False


def test_human_qc_covers_abstain_and_unresolved() -> None:
    packet = [
        {"blind_id": "b1", "language": "ur", "question": "q", "options": [], "suggestion": "s", "trace": "t"}
    ]
    packet_qc = validate_packet(packet, {"b1"})
    assert packet_qc["pass"]
    left = [{"blind_id": "b1", "label": "abstain"}]
    right = [{"blind_id": "b1", "label": "abstain"}]
    ids = adjudication_ids(left, right)
    assert ids == {"b1"}
    assert validate_annotations(
        [{"blind_id": "b1", "label": "abstain", "packet_sha256": packet_qc["packet_hash"]}],
        {"b1"},
        packet_sha256=packet_qc["packet_hash"],
    )["pass"]
    assert validate_adjudication(
        [{"blind_id": "b1", "independent_label": "abstain", "final_label": "unresolved"}], ids
    )["pass"]


def test_analysis_wrapper_fails_closed_until_all_gates() -> None:
    result = validate_analysis_gate(
        translated_judge_seal=None,
        human_qc=None,
        expected_analysis_hash="a",
        actual_analysis_hash="a",
        expected_input_hash="b",
        actual_input_hash="b",
        authorization=False,
    )
    assert result["ready"] is False


def test_table_template_is_placeholder_only() -> None:
    assert table_template("identity_translation_robustness")["rows"] == []


def test_translation_terminal_verifier_synthetic(tmp_path: Any) -> None:
    (tmp_path / "translation-a.json").write_text(
        '{"translation_id":"a","immutable":true,"technical_status":"SUCCESS"}'
    )
    (tmp_path / "translation-failure-b-attempt-1.json").write_text(
        '{"translation_id":"b","immutable":true,"technical_status":"FAILED"}'
    )
    report = verify_translation_directory(tmp_path, {"a"})
    assert report["pass"]
    assert report["historical_failure_records"] == 1


def test_conflicting_attempts_fail_closed() -> None:
    assert (
        attempt_state(
            [
                {"attempt": 1, "technical_status": "RUNTIME_ERROR"},
                {"attempt": 3, "technical_status": "RUNTIME_ERROR"},
            ]
        )
        == "CONFLICTING_ATTEMPTS"
    )
    assert STATE_RULES["RETRY_EXHAUSTED"].model_call_allowed is False


def test_translation_seal_has_one_canonical_writer() -> None:
    translator = Path("src/clsm/workshop_v1/translator_launcher.py").read_text()
    post_translation = Path("src/clsm/workshop_v1/post_translation_pipeline.py").read_text()
    assert translator.count("def seal(") == 1
    assert "def seal_translation(" not in post_translation

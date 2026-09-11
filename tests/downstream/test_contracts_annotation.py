from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from clsm.downstream.annotation import (
    Annotation,
    AnnotationTask,
    blind_packet,
    inter_rater_report,
    validate_annotations,
    validate_reference,
)
from clsm.downstream.contracts import DisclosureLabel, JudgeInput, LabelPolicy, normalize_label
from clsm.downstream.fixtures import synthetic_bundle, synthetic_judge, synthetic_provenance


@pytest.mark.parametrize(
    "value", [True, False, 1, 0, None, object(), "yes", "no", "disclosed because...", "UNKNOWN", ""]
)
def test_unknown_labels_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        normalize_label(value)


@pytest.mark.parametrize(
    "value,expected",
    [
        (" DISCLOSED ", "disclosed"),
        ("not-disclosed", "not_disclosed"),
        ("partial", "partial"),
        ("cannot_tell", "cannot_tell"),
        ("abstain", "abstain"),
    ],
)
def test_normalization(value: str, expected: str) -> None:
    assert normalize_label(value).value == expected


@pytest.mark.parametrize(
    "field",
    ["generator_identity", "model", "condition", "accuracy", "switch_rate", "gold_label", "judge_label"],
)
def test_unblinded_metadata_rejected(field: str) -> None:
    task = synthetic_bundle().packet.tasks[0]
    for cls in (AnnotationTask, JudgeInput):
        with pytest.raises(ValidationError):
            cls.model_validate({**task.model_dump(), field: "leak"})


def test_blinding_order_and_private_mapping() -> None:
    bundle = synthetic_bundle()
    packet, assignment = blind_packet(bundle.traces, secret=b"x" * 32, seed=9, rubric_version="rubric/1")
    assert (packet, assignment) == blind_packet(
        bundle.traces, secret=b"x" * 32, seed=9, rubric_version="rubric/1"
    )
    different, _ = blind_packet(bundle.traces, secret=b"y" * 32, seed=9, rubric_version="rubric/1")
    assert {t.blind_id for t in packet.tasks}.isdisjoint(t.blind_id for t in different.tasks)
    assert "fixture-generator" not in packet.model_dump_json()
    assert "fixture-condition" not in packet.model_dump_json()
    assert "synthetic-item" not in packet.model_dump_json()
    assert "trace_id" not in packet.model_dump_json()
    assert sorted(t.text_hash for t in packet.tasks) == sorted(t.text_hash for t in bundle.traces.traces)
    with pytest.raises(ValueError):
        blind_packet(bundle.traces, secret=b"short", seed=9, rubric_version="r")


def test_annotation_duplicates_and_assignment() -> None:
    b = synthetic_bundle()
    validate_annotations(b.annotations, b.packet)
    with pytest.raises(ValueError, match="duplicate annotation IDs"):
        validate_annotations((*b.annotations, b.annotations[0]), b.packet)
    altered = b.annotations[0].model_copy(update={"annotation_id": "synthetic-other"})
    with pytest.raises(ValueError, match="duplicate annotator"):
        validate_annotations((*b.annotations, altered), b.packet)
    with pytest.raises(ValueError, match="mismatch"):
        validate_annotations((b.annotations[0].model_copy(update={"text_hash": "a" * 64}),), b.packet)


def test_reference_provenance_required() -> None:
    b = synthetic_bundle()
    validate_reference(b.reference, b.annotations, b.packet)
    with pytest.raises(ValueError, match="provenance"):
        validate_reference(b.reference, b.annotations[1:], b.packet)
    wrong = b.reference.labels[0].model_copy(
        update={"source_annotation_hashes": (b.annotations[1].artifact_hash,)}
    )
    with pytest.raises(ValueError, match="provenance"):
        validate_reference(b.reference.model_copy(update={"labels": (wrong,)}), b.annotations, b.packet)


def test_partial_policy_never_implicit() -> None:
    with pytest.raises(ValidationError):
        LabelPolicy(decision_record="decision", rubric_version="rubric")
    for partial, expected in (("exclude", None), ("disclosed", 1), ("not_disclosed", 0)):
        p = LabelPolicy.model_validate(
            {"partial": partial, "decision_record": "synthetic", "rubric_version": "r"}
        )
        assert p.binary(DisclosureLabel.PARTIAL) == expected
        assert p.binary(DisclosureLabel.ABSTAIN) is None
        assert p.binary(DisclosureLabel.CANNOT_TELL) is None


def test_inter_rater_analysis_with_missing() -> None:
    b = synthetic_bundle()
    second = tuple(
        a.model_copy(
            update={"annotation_id": a.annotation_id + "-second", "annotator_pseudonym": "rater-two"}
        )
        for a in b.annotations[:2]
    )
    report = inter_rater_report(
        b.annotations + second,
        b.packet,
        b.assignment,
        traces=b.traces,
        rater_a="synthetic-rater",
        rater_b="rater-two",
        round_id="synthetic-round",
        policy=b.policy,
    )
    assert report["complete_pairs"] == 2
    assert report["candidate_missing_or_abstain"] == 1
    assert report["raw_agreement"] == 1
    with pytest.raises(ValueError):
        inter_rater_report(
            b.annotations,
            b.packet,
            b.assignment,
            traces=b.traces,
            rater_a="same",
            rater_b="same",
            round_id="r",
            policy=b.policy,
        )


@pytest.mark.parametrize("version", ["latest", "main", "HEAD", "unresolved", " main "])
def test_mutable_judge_versions_rejected(version: str) -> None:
    data = synthetic_judge().model_dump()
    with pytest.raises(ValidationError):
        type(synthetic_judge()).model_validate({**data, "version": version})


def test_timestamp_and_annotation_schema() -> None:
    p = synthetic_provenance()
    with pytest.raises(ValidationError):
        type(p).model_validate({**p.model_dump(), "created_utc": "2000-01-01T00:00:00"})
    schema_path = Path("experiments/M2-Monitor-Validation/ANNOTATION_FORM_SCHEMA.json")
    assert json.loads(schema_path.read_text()) == Annotation.model_json_schema()

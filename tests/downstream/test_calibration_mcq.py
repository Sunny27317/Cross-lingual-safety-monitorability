from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from clsm.downstream.calibration import candidate_comparison
from clsm.downstream.contracts import ProspectiveCandidatePlan, TraceSet, content_hash
from clsm.downstream.fixtures import synthetic_bundle, synthetic_provenance
from clsm.downstream.mcq import DatasetSpec, SourceRow, adapt_item, extract_strategies, validate_items


def comparison_arguments() -> dict[str, Any]:
    b = synthetic_bundle()
    trace = b.traces.traces[0].model_copy(
        update={
            "trace_id": "synthetic-heldout",
            "item_id": "heldout-item",
            "text": "Synthetic heldout only",
            "text_hash": content_hash("Synthetic heldout only"),
        }
    )
    heldout = TraceSet(
        traces=(trace,),
        prospective_population_definition="synthetic heldout, disjoint item",
        selection_record_hash=content_hash("synthetic-heldout-selection"),
    )
    plan = ProspectiveCandidatePlan(
        candidate_spec_hashes=(b.judge.artifact_hash,),
        reference_set_hash=b.reference.artifact_hash,
        heldout_reference_set_hash=content_hash("synthetic heldout reference placeholder"),
        calibration_trace_set_hash=b.traces.artifact_hash,
        heldout_trace_set_hash=heldout.artifact_hash,
        label_policy_hash=b.policy.artifact_hash,
        acceptance_decision_record="HUMAN REQUIRED, synthetic comparison only",
        investigator="synthetic",
        provenance=synthetic_provenance(),
    )
    return dict(
        plan=plan,
        calibration=b.traces,
        heldout=heldout,
        packet=b.packet,
        assignment=b.assignment,
        reference=b.reference,
        annotations=b.annotations,
        policy=b.policy,
        candidates=(b.judge,),
        outputs=b.direct,
    )


def test_candidate_comparison_does_not_select_or_rank_by_outcomes() -> None:
    kwargs = comparison_arguments()
    report = candidate_comparison(**kwargs)
    assert report["selected_candidate"] is None
    assert report["candidates"][0]["metrics"]["raw_agreement"] == pytest.approx(2 / 3)
    assert report == candidate_comparison(**kwargs)
    assert report["split"] == "calibration"
    empty = candidate_comparison(**{**kwargs, "outputs": ()})
    assert empty["candidates"][0]["absent_outputs"] == 3
    assert empty["candidates"][0]["metrics"]["raw_agreement"] is None


def test_candidate_plan_rejects_outcome_leakage() -> None:
    plan = comparison_arguments()["plan"]
    for field in (
        "switch_rate",
        "accuracy",
        "parse_rate",
        "effect_direction",
        "pilot_results",
        "preferred_score",
    ):
        with pytest.raises(ValidationError):
            ProspectiveCandidatePlan.model_validate({**plan.model_dump(), field: 0.9})


def test_calibration_holdout_leakage_and_versions() -> None:
    kwargs = comparison_arguments()
    with pytest.raises(ValueError):
        candidate_comparison(**{**kwargs, "outputs": kwargs["outputs"] * 2})
    judge = kwargs["candidates"][0].model_copy(update={"version": "fixture-v2"})
    with pytest.raises(ValueError, match="candidate/version"):
        candidate_comparison(**{**kwargs, "candidates": (judge,)})
    heldout = kwargs["heldout"]
    leaked = heldout.model_copy(
        update={
            "traces": (
                heldout.traces[0].model_copy(update={"item_id": kwargs["calibration"].traces[0].item_id}),
            )
        }
    )
    plan = kwargs["plan"].model_copy(update={"heldout_trace_set_hash": leaked.artifact_hash})
    with pytest.raises(ValueError, match="item leakage"):
        candidate_comparison(**{**kwargs, "heldout": leaked, "plan": plan})


def dataset() -> DatasetSpec:
    return DatasetSpec(
        repository="synthetic/urdu-mcq",
        config="synthetic",
        split="synthetic",
        resolved_revision="fixture-v1",
        language="ur",
        role="secondary_robustness",
        provenance_evidence="synthetic only",
        license_evidence="original test strings",
        compatibility_decision="fixture only, no real dataset approved",
    )


def row() -> SourceRow:
    return SourceRow(
        source_item_id="synthetic-item",
        subject="synthetic",
        language="ur",
        question="مصنوعی سوال",
        choices=("پہلا", "دوسرا", "تیسرا", "چوتھا"),
        answer="B",
        resolved_revision="fixture-v1",
    )


def test_order_mapping_and_content_hash() -> None:
    spec, source = dataset(), row()
    item = adapt_item(source, spec, answer_format="latin_letter")
    assert item.choices == source.choices and item.answer_index == 1
    assert validate_items((item,), spec) == validate_items((item,), spec)
    swapped = source.model_copy(update={"choices": tuple(reversed(source.choices))})
    changed = adapt_item(swapped, spec, answer_format="latin_letter")
    assert changed.content_hash != item.content_hash
    assert changed.stable_id == item.stable_id
    with pytest.raises(ValueError, match="duplicate"):
        validate_items((item, item), spec)
    with pytest.raises(ValueError, match="hash"):
        validate_items((item.model_copy(update={"answer_index": 0}),), spec)


@pytest.mark.parametrize(
    "changes",
    [
        {"choices": ("a", "b", "c")},
        {"choices": ("a", "b", "c", "")},
        {"choices": ("a", "b", "c", "   ")},
        {"answer": True},
        {"language": "xx"},
    ],
)
def test_invalid_mcq_schema(changes: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        SourceRow.model_validate({**row().model_dump(), **changes})


@pytest.mark.parametrize(
    "changes", [{"answer": "الف"}, {"answer": 4}, {"language": "en"}, {"resolved_revision": "wrong"}]
)
def test_mcq_mapping_revision_language(changes: dict[str, object]) -> None:
    source = row().model_copy(update=changes)
    with pytest.raises(ValueError):
        adapt_item(source, dataset(), answer_format="latin_letter")


def test_mmlu_remains_primary_and_no_mutable_revision() -> None:
    for changes in ({"role": "primary_mmlu"}, {"resolved_revision": "main"}):
        with pytest.raises(ValidationError):
            DatasetSpec.model_validate({**dataset().model_dump(), **changes})


@pytest.mark.parametrize(
    "text,primary,exploratory",
    [
        (r"\boxed{A}", "A", None),
        (r"\boxed{الف}", None, "A"),
        (r"\boxed{A} \boxed{ب}", "A", "B"),
        (r"\boxed{الف} \boxed{ب}", None, None),
        (r"<think>\boxed{الف}</think>\boxed{B}", "B", None),
        (r"<think>truncated \boxed{الف}", None, None),
    ],
)
def test_extraction_strategies_never_contaminate(
    text: str, primary: str | None, exploratory: str | None
) -> None:
    report = extract_strategies(text)
    assert report["primary_latin_ad"] == primary
    assert report["exploratory_perso_arabic"] == exploratory


def test_heldout_comparison_and_common_candidate_coverage() -> None:
    from clsm.downstream.annotation import LockedReference, ReferenceLabel, blind_packet

    kwargs = comparison_arguments()
    b = synthetic_bundle()
    packet, assignment = blind_packet(
        kwargs["heldout"],
        secret=b"heldout-synthetic-key-only-32-bytes",
        seed=9,
        rubric_version=b.judge.rubric_version,
    )
    task = packet.tasks[0]
    annotation = b.annotations[0].model_copy(
        update={
            "blind_id": task.blind_id,
            "text_hash": task.text_hash,
            "annotation_id": "synthetic-heldout-annotation",
        }
    )
    reference = LockedReference(
        packet_hash=packet.artifact_hash,
        protocol_decision_record="synthetic holdout",
        locked_by_pseudonym="synthetic-steward",
        provenance=synthetic_provenance(),
        labels=(
            ReferenceLabel(
                blind_id=task.blind_id,
                text_hash=task.text_hash,
                rubric_version=task.rubric_version,
                label=annotation.label,
                source_annotation_hashes=(annotation.artifact_hash,),
                adjudicator_pseudonym="synthetic",
                adjudication_record="synthetic",
            ),
        ),
    )
    plan = kwargs["plan"].model_copy(update={"heldout_reference_set_hash": reference.artifact_hash})
    output = b.direct[0].model_copy(update={"blind_id": task.blind_id, "input_hash": task.text_hash})
    report = candidate_comparison(
        **{
            **kwargs,
            "plan": plan,
            "packet": packet,
            "assignment": assignment,
            "reference": reference,
            "annotations": (annotation,),
            "outputs": (output,),
            "split": "heldout",
        }
    )
    assert report["split"] == "heldout" and report["candidates"][0]["metrics"]["complete_pairs"] == 1
    second = b.judge.model_copy(update={"candidate_id": "synthetic-another"})
    plan = kwargs["plan"].model_copy(
        update={"candidate_spec_hashes": (b.judge.artifact_hash, second.artifact_hash)}
    )
    partial_outputs = tuple(
        o.model_copy(update={"judge_spec_hash": second.artifact_hash}) for o in b.direct[:1]
    )
    report = candidate_comparison(
        **{**kwargs, "plan": plan, "candidates": (b.judge, second), "outputs": (*b.direct, *partial_outputs)}
    )
    assert len(report["common_complete_ids"]) == 1
    assert all(c["common_complete_set_metrics"]["complete_pairs"] == 1 for c in report["candidates"])
    assert report["candidates"][0]["candidate_id"] == "synthetic-another"


def test_reported_outputs_cannot_predate_plan() -> None:
    kwargs = comparison_arguments()
    p = synthetic_provenance().model_copy(update={"created_utc": "2001-01-01T00:00:00+00:00"})
    plan = kwargs["plan"].model_copy(update={"provenance": p})
    with pytest.raises(ValueError, match="predates"):
        candidate_comparison(**{**kwargs, "plan": plan})

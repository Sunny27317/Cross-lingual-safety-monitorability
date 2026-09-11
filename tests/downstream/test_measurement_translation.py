from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from clsm.downstream.analysis import analyze_bundle
from clsm.downstream.contracts import DisclosureLabel, content_hash
from clsm.downstream.fixtures import fixture_report, synthetic_bundle, synthetic_provenance
from clsm.downstream.reporting import deterministic_report, write_new_report
from clsm.downstream.translation import (
    EquivalenceAudit,
    TranslationControl,
    TranslationRequest,
    audit_summary,
    validate_translation,
)


def test_end_to_end_language_failure_and_recovery() -> None:
    b = synthetic_bundle()
    report = analyze_bundle(b)
    en, ur = report["by_language"]["en"], report["by_language"]["ur"]
    assert en["direct"]["native_minus_automated_detection"] == 0
    assert ur["direct"]["native_minus_automated_detection"] == 0.5
    assert ur["translation"]["translation_recovery_detection"] == 0.5
    assert ur["translation"]["translation_recovery_agreement"] == 0.5
    assert en["paraphrase_control"]["translation_recovery_detection"] == 0
    assert deterministic_report(fixture_report()) == deterministic_report(fixture_report())
    assert fixture_report().provenance.data_kind.value == "synthetic"


def test_perfect_monitor_and_model_failure_good_monitor() -> None:
    b = synthetic_bundle()
    refs = {r.blind_id: r for r in b.reference.labels}
    perfect = tuple(o.model_copy(update={"label": refs[o.blind_id].label}) for o in b.direct)
    report = analyze_bundle(b.model_copy(update={"direct": perfect}))
    ur = report["by_language"]["ur"]
    assert ur["direct"]["native_minus_automated_detection"] == 0
    assert ur["direct"]["raw_agreement"] == 1
    # Human-negative + monitor-negative contributes TN. No code equates nondisclosure with causal failure.
    assert ur["direct"]["confusion_matrix"]["tn"] == 1


def test_translation_degradation_is_not_hidden() -> None:
    b = synthetic_bundle()
    refs = {r.blind_id: r for r in b.reference.labels}
    perfect = tuple(o.model_copy(update={"label": refs[o.blind_id].label}) for o in b.direct)
    degraded = tuple(o.model_copy(update={"label": DisclosureLabel.NOT_DISCLOSED}) for o in b.translated)
    report = analyze_bundle(b.model_copy(update={"direct": perfect, "translated": degraded}))
    assert report["by_language"]["ur"]["translation"]["translation_recovery_detection"] == -0.5
    assert report["by_language"]["ur"]["translation"]["translation_recovery_agreement"] == -0.5


def test_recovery_uses_common_triples_not_different_denominators() -> None:
    b = synthetic_bundle()
    missing_id = b.assignment.links[1].blind_id
    missing = tuple(o for o in b.translated if o.blind_id != missing_id)
    report = analyze_bundle(b.model_copy(update={"translated": missing}))
    ur = report["by_language"]["ur"]
    assert ur["direct"]["native_minus_automated_detection"] == 0.5
    assert ur["translation"]["complete_triples"] == 1
    assert ur["translation"]["translation_recovery_detection"] == 0
    assert ur["translation"]["missing_translated"] == 1
    missing_ref = b.reference.model_copy(update={"labels": b.reference.labels[:1]})
    report = analyze_bundle(b.model_copy(update={"reference": missing_ref}))
    assert report["by_language"]["ur"]["translation"]["translation_recovery_detection"] is None
    assert report["raw_missingness"]["absent_reference"] == 2


def test_abstention_preserved() -> None:
    b = synthetic_bundle()
    abstain = tuple(o.model_copy(update={"label": DisclosureLabel.ABSTAIN}) for o in b.direct)
    report = analyze_bundle(b.model_copy(update={"direct": abstain}))
    assert report["by_language"]["ur"]["direct"]["complete_pairs"] == 0
    assert report["raw_missingness"]["direct_abstentions"] == 3
    assert report["by_language"]["ur"]["direct"]["native_minus_automated_detection"] is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("input_hash", "f" * 64),
        ("judge_spec_hash", "f" * 64),
        ("blind_id", "f" * 64),
        ("rubric_version", "wrong"),
    ],
)
def test_wrong_judge_identity_and_pairing(field: str, value: str) -> None:
    b = synthetic_bundle()
    wrong = (b.direct[0].model_copy(update={field: value}), *b.direct[1:])
    with pytest.raises(ValueError):
        analyze_bundle(b.model_copy(update={"direct": wrong}))


def test_duplicates_and_foreign_translation_rejected() -> None:
    b = synthetic_bundle()
    for field in ("direct", "translated", "translations"):
        values = getattr(b, field)
        with pytest.raises(ValueError, match="duplicat"):
            analyze_bundle(b.model_copy(update={field: (*values, values[0])}))
    with pytest.raises(ValueError, match="matching translation"):
        analyze_bundle(b.model_copy(update={"translations": ()}))
    altered = b.assignment.links[0].model_copy(update={"item_id": "different-cluster"})
    mapping = b.assignment.model_copy(update={"links": (altered, *b.assignment.links[1:])})
    with pytest.raises(ValueError, match="mismatch"):
        analyze_bundle(b.model_copy(update={"assignment": mapping}))


@pytest.mark.parametrize(
    "change", [{"truncated": True}, {"errors": ("synthetic error",)}, {"measured_input_units": 9000}]
)
def test_translation_unusable_is_explicit(change: dict[str, object]) -> None:
    b = synthetic_bundle()
    request, record, spec = b.translations[1]
    bad = record.model_copy(update=change)
    with pytest.raises(ValueError, match="unusable"):
        validate_translation(bad, request, spec)
    translations = (b.translations[0], (request, bad, spec), b.translations[2])
    with pytest.raises(ValueError, match="usable"):
        analyze_bundle(b.model_copy(update={"translations": translations}))
    outputs = tuple(o for o in b.translated if o.blind_id != request.blind_id)
    report = analyze_bundle(b.model_copy(update={"translations": translations, "translated": outputs}))
    assert report["unusable_translation_ids"] == [request.blind_id]


def test_translation_hash_and_version_mismatch() -> None:
    request, record, spec = synthetic_bundle().translations[1]
    with pytest.raises(ValidationError, match="source hash"):
        TranslationRequest.model_validate({**request.model_dump(), "source_text": "altered"})
    for field in ("source_hash", "source_trace_hash", "translator_spec_hash"):
        with pytest.raises(ValueError):
            validate_translation(record.model_copy(update={field: "f" * 64}), request, spec)
    with pytest.raises(ValueError):
        validate_translation(record, request, spec.model_copy(update={"version": "fixture-v2"}))
    with pytest.raises(ValidationError, match="empty translation"):
        type(record).model_validate(
            {**record.model_dump(), "translated_text": "   ", "output_hash": content_hash("   ")}
        )
    with pytest.raises(ValidationError, match="output hash"):
        type(record).model_validate({**record.model_dump(), "translated_text": "altered"})


def test_backtranslation_requires_valid_lineage() -> None:
    request, parent, spec = synthetic_bundle().translations[1]
    back_request = TranslationRequest(
        blind_id=request.blind_id,
        root_trace_hash=request.root_trace_hash,
        source_text=parent.translated_text,
        source_hash=parent.output_hash,
        source_language="en",
        target_language="ur",
        control=TranslationControl.BACKTRANSLATION,
        parent_translation_hash=parent.artifact_hash,
    )
    back_spec = spec.model_copy(update={"source_language": "en", "target_language": "ur"})
    text = "Synthetic backtranslation fixture, no translation execution"
    back = parent.model_copy(
        update={
            "request_hash": back_request.artifact_hash,
            "source_hash": parent.output_hash,
            "source_language": "en",
            "translator_spec": back_spec,
            "translator_spec_hash": back_spec.artifact_hash,
            "translated_text": text,
            "output_hash": content_hash(text),
        }
    )
    validate_translation(back, back_request, back_spec, parent=parent)
    with pytest.raises(ValueError, match="lineage"):
        validate_translation(back, back_request, back_spec)


def test_equivalence_is_never_fabricated() -> None:
    record = synthetic_bundle().translations[1][1]
    audit = EquivalenceAudit(
        translation_record_hash=record.artifact_hash,
        source_hash=record.source_hash,
        output_hash=record.output_hash,
        reviewer_pseudonym="synthetic-reviewer",
        audit_rubric_version="synthetic-audit/1",
        semantic_adequacy="uncertain",
        disclosure_preservation="uncertain",
        omission="uncertain",
        addition_or_explicitation="uncertain",
        answer_option_preservation="not_applicable",
        truncation_observed=False,
        rationale="synthetic fixture, not human audit",
        provenance=synthetic_provenance(),
    )
    assert audit_summary((), (record,))["unaudited_records"] == 1
    report = audit_summary((audit,), (record,))
    assert report["equivalence_certified"] is False
    with pytest.raises(ValueError, match="duplicate"):
        audit_summary((audit, audit), (record,))
    with pytest.raises(ValueError, match="mismatch"):
        audit_summary((audit.model_copy(update={"source_hash": "f" * 64}),), (record,))


def test_report_integrity_and_collision(tmp_path: Path) -> None:
    report = fixture_report()
    path = tmp_path / "synthetic-report.json"
    write_new_report(path, report)
    assert json.loads(path.read_text())["artifact_hash"] == report.artifact_hash
    with pytest.raises(FileExistsError):
        write_new_report(path, report)
    assert path.read_text() == deterministic_report(report)
    report.payload["unexpected_mutation"] = True
    with pytest.raises(ValueError, match="hash mismatch"):
        deterministic_report(report)


@pytest.mark.parametrize(
    "path", ["experiments/_runs/example/records.json", "pilot-output/traces.json", "model.gguf"]
)
def test_scientific_paths_are_blocked_in_tests(path: str) -> None:
    with pytest.raises(AssertionError, match="scientific data"):
        Path(path).read_text()


def test_measurement_intervals_are_paired_and_plan_is_bound() -> None:
    from clsm.downstream.agreement import ResamplingPlan
    from clsm.downstream.reporting import measurement_envelope

    plan = ResamplingPlan(alpha=0.1, replicates=50, seed=17, decision_record="synthetic uncertainty only")
    b = synthetic_bundle()
    envelope = measurement_envelope(b, synthetic_provenance(), resampling=plan)
    assert envelope == measurement_envelope(b, synthetic_provenance(), resampling=plan)
    assert any(x.role == "resampling_plan" and x.digest == plan.artifact_hash for x in envelope.bindings)
    interval = envelope.payload["by_language"]["ur"]["translation"]["intervals"][
        "translation_recovery_detection"
    ]
    assert interval["lower"] <= 0.5 <= interval["upper"]
    assert interval["defined_replicates"] == 50

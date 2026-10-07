from __future__ import annotations

import pytest

from clsm.downstream.contracts import content_hash
from clsm.workshop_v1.dry_run import synthetic_routes
from clsm.workshop_v1.monitoring import (
    MonitoringOutput,
    MonitorPath,
    validate_hdt_bindings,
    validate_monitoring_binding,
    validate_visible_trace,
)

from .conftest import changed


def urdu_record(generated):
    return next(r for r in generated[1] if r.identity.language == "ur")


def test_four_paths_are_separate_and_translated_language_is_not_source_language(design, generated) -> None:
    generation = urdu_record(generated)
    trace, bindings, translation = synthetic_routes(generation)
    human, direct, translated = bindings
    assert human.actor == "human"
    assert direct.actor == translated.actor == "automated"
    assert direct.specification_hash == translated.specification_hash
    assert translated.identity.language == "ur"
    assert translated.judge_input_language == "en"
    assert direct.judge_input_language == "ur"
    validate_hdt_bindings(human, direct, translated)
    for binding in bindings:
        validate_monitoring_binding(
            binding,
            trace,
            generation,
            design[0],
            population=generated[0],
            translation=translation if binding is translated else None,
        )
    english = next(r for r in generated[1] if r.identity.language == "en")
    _, en_bindings, en_translation = synthetic_routes(english)
    assert en_translation is None
    assert en_bindings[0].path is MonitorPath.ENGLISH_BASELINE


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_item_id", "synthetic-other"),
        ("model_id", "synthetic-other"),
        ("seed", 99),
        ("sample_index", 99),
        ("condition", "misleading_cue_b"),
        ("generation_id", "synthetic-other"),
    ],
)
def test_hdt_exact_identity_includes_model_and_sample(generated, field, value) -> None:
    _, (human, direct, translated), _ = synthetic_routes(urdu_record(generated))
    identity = changed(translated.identity, **{field: value})
    mismatched = changed(translated, identity=identity.model_dump(mode="json"))
    with pytest.raises(ValueError, match="identical trace"):
        validate_hdt_bindings(human, direct, mismatched)


def test_cannot_relabel_translated_urdu_as_english_source(generated) -> None:
    _, (_, _, translated), _ = synthetic_routes(urdu_record(generated))
    identity = changed(translated.identity, language="en")
    with pytest.raises(ValueError, match="source language"):
        changed(translated, identity=identity.model_dump(mode="json"))
    with pytest.raises(ValueError, match="rendered text"):
        changed(translated, judge_input_language="ur")
    with pytest.raises(ValueError, match="lineage"):
        changed(translated, translation_record_hash=None)


def test_native_human_cannot_be_automated_and_direct_cannot_change_judge(generated) -> None:
    _, (human, direct, translated), _ = synthetic_routes(urdu_record(generated))
    with pytest.raises(ValueError, match="human reference"):
        changed(human, actor="automated")
    with pytest.raises(ValueError, match="shared automated monitor"):
        validate_hdt_bindings(human, direct, changed(translated, specification_hash=content_hash("other")))


@pytest.mark.parametrize("field", ["source_generation_hash", "visible_trace_hash", "judge_input_hash"])
def test_monitoring_source_hash_tampering(design, generated, field) -> None:
    generation = urdu_record(generated)
    trace, (_, direct, _), _ = synthetic_routes(generation)
    with pytest.raises(ValueError):
        validate_monitoring_binding(
            changed(direct, **{field: content_hash("other")}),
            trace,
            generation,
            design[0],
            population=generated[0],
        )


def test_same_text_on_different_generation_does_not_allow_translation_swap(design, generated) -> None:
    first, other = [r for r in generated[1] if r.identity.language == "ur"][:2]
    trace, (_, _, binding), _ = synthetic_routes(first)
    _, _, wrong_translation = synthetic_routes(other)
    with pytest.raises(ValueError, match="exact source"):
        validate_monitoring_binding(
            binding,
            trace,
            first,
            design[0],
            population=generated[0],
            translation=wrong_translation,
        )
    with pytest.raises(ValueError, match="generation mismatch"):
        validate_visible_trace(trace, other)


def test_translation_drift_errors_and_missing_spec_are_rejected(design, generated) -> None:
    generation = urdu_record(generated)
    trace, (_, _, binding), translation = synthetic_routes(generation)
    request, record = translation
    with pytest.raises(ValueError, match="unusable"):
        validate_monitoring_binding(
            binding,
            trace,
            generation,
            design[0],
            population=generated[0],
            translation=(request, changed(record, truncated=True)),
        )
    with pytest.raises(ValueError, match="requires frozen translator"):
        validate_monitoring_binding(binding, trace, generation, design[0], population=generated[0])


def test_collection_error_cannot_become_a_negative_label(generated) -> None:
    _, (_, direct, _), _ = synthetic_routes(urdu_record(generated))
    from clsm.downstream.contracts import DisclosureLabel

    with pytest.raises(ValueError, match="abstention"):
        MonitoringOutput(
            binding=direct,
            label=DisclosureLabel.NOT_DISCLOSED,
            raw_artifact_hash=content_hash("synthetic error"),
            collection_provenance_hash=content_hash("synthetic provenance"),
            error="synthetic failure",
        )


def test_monitoring_validates_generation_against_frozen_population(design, generated) -> None:
    generation = urdu_record(generated)
    trace, (_, direct, _), _ = synthetic_routes(generation)
    mutated_cue = changed(generation.cue, version="synthetic-v2")
    altered = changed(generation, cue=mutated_cue.model_dump(mode="json"))
    # Even a self-consistent lineage with freshly recomputed record hashes must
    # not hide cue/config drift from the frozen experiment.
    altered_trace = changed(trace, generation_record_hash=altered.artifact_hash)
    altered_binding = changed(
        direct,
        source_generation_hash=altered.artifact_hash,
        visible_trace_hash=altered_trace.artifact_hash,
    )
    with pytest.raises(ValueError, match="frozen study"):
        validate_monitoring_binding(
            altered_binding,
            altered_trace,
            altered,
            design[0],
            population=generated[0],
        )

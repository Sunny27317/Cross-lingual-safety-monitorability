from __future__ import annotations

import pytest
from tests.downstream.test_calibration_mcq import comparison_arguments

from clsm.downstream.analysis import measurement_report
from clsm.downstream.calibration import (
    candidate_comparison,
    finalize_calibration_acceptance,
)
from clsm.downstream.matching import TraceIdentityKey, validate_hdt_identity_keys
from clsm.downstream.partitions import assign_source_items, partition_manifest_hash
from clsm.downstream.simulation_validation import (
    ClusterValidationScenario,
    validate_cluster_method,
)
from clsm.downstream.translation import validate_english_paraphrase_control


def test_item_partition_is_seeded_and_disjoint() -> None:
    ids = [f"item-{i}" for i in range(20)]
    first = assign_source_items(
        ids, seed=17, partition_sizes=(5, 5, 5, 5), decision_record="synthetic partition fixture"
    )
    second = assign_source_items(
        ids, seed=17, partition_sizes=(5, 5, 5, 5), decision_record="synthetic partition fixture"
    )
    assert first == second
    assert partition_manifest_hash(first) == partition_manifest_hash(second)
    groups = list(first.partition_ids.values())
    assert sum(map(len, groups)) == 20
    assert len(set().union(*map(set, groups))) == 20


def test_hdt_identity_mismatch_is_rejected() -> None:
    base = TraceIdentityKey(source_item_id="i", condition="control", language="ur", seed=0, generation_id="g")
    changed = base.model_copy(update={"seed": 1})
    with pytest.raises(ValueError, match="identical"):
        validate_hdt_identity_keys(base, changed, base)


def test_acceptance_criteria_are_required_for_scoring() -> None:
    kwargs = comparison_arguments()
    with pytest.raises(ValueError, match="acceptance criteria"):
        candidate_comparison(**{k: v for k, v in kwargs.items() if k != "acceptance_criteria"})


def test_acceptance_criteria_must_precede_scoring() -> None:
    kwargs = comparison_arguments()
    late = kwargs["acceptance_criteria"].model_copy(
        update={"signed_utc": "9999-01-01T00:00:00+00:00"}
    )
    with pytest.raises(ValueError, match="after candidate scoring"):
        candidate_comparison(**{**kwargs, "acceptance_criteria": late})


def test_cluster_validation_is_deterministic_and_synthetic() -> None:
    scenarios = (
        ClusterValidationScenario(8, 3, 0.2, 0.2, 0.0, 0.0),
        ClusterValidationScenario(8, 3, 0.2, 0.1, 0.2, 0.1, informative_missingness=0.2),
    )
    first = validate_cluster_method(scenarios, simulations=8, bootstrap_replicates=30, alpha=0.1, seed=4)
    second = validate_cluster_method(scenarios, simulations=8, bootstrap_replicates=30, alpha=0.1, seed=4)
    assert first == second
    assert first["design"].startswith("ADEMP synthetic")


def test_mechanism_claim_requires_english_paraphrase_control() -> None:
    from clsm.downstream.fixtures import synthetic_bundle

    bundle = synthetic_bundle()
    report = measurement_report(
        traces=bundle.traces,
        packet=bundle.packet,
        assignment=bundle.assignment,
        reference=bundle.reference,
        annotations=bundle.annotations,
        policy=bundle.policy,
        judge=bundle.judge,
        direct=bundle.direct,
        translated=bundle.translated,
        translations=bundle.translations,
        mechanism_claim=True,
    )
    assert report["mechanism_claim_control"] == "english_paraphrase_required"


def test_mechanism_claim_rejects_zero_english_anchors() -> None:
    from clsm.downstream.fixtures import synthetic_bundle

    bundle = synthetic_bundle()
    packet = bundle.packet.model_copy(
        update={"tasks": tuple(t for t in bundle.packet.tasks if t.language != "en")}
    )
    with pytest.raises(ValueError, match="at least one English anchor"):
        validate_english_paraphrase_control(packet, bundle.translations)


def test_mechanism_claim_rejects_missing_english_control() -> None:
    from clsm.downstream.fixtures import synthetic_bundle

    bundle = synthetic_bundle()
    translations = tuple(x for x in bundle.translations if x[0].control.value != "english_paraphrase")
    with pytest.raises(ValueError, match="paraphrase control"):
        validate_english_paraphrase_control(bundle.packet, translations)


def test_confirmatory_items_require_source_matched_english_anchors() -> None:
    from clsm.downstream.fixtures import synthetic_bundle
    from clsm.downstream.translation import validate_english_paraphrase_control

    bundle = synthetic_bundle()
    english = next(t for t in bundle.packet.tasks if t.language == "en")
    mapping = {english.blind_id: "item-confirmatory"}
    with pytest.raises(ValueError, match="source-matched"):
        validate_english_paraphrase_control(
            bundle.packet,
            bundle.translations,
            confirmatory_item_ids={"item-confirmatory"},
            english_anchor_item_ids={"different-item"},
            source_item_by_blind_id=mapping,
        )


def test_confirmatory_anchor_coverage_passes_when_complete() -> None:
    from clsm.downstream.fixtures import synthetic_bundle
    from clsm.downstream.translation import validate_english_paraphrase_control

    bundle = synthetic_bundle()
    english = next(t for t in bundle.packet.tasks if t.language == "en")
    mapping = {english.blind_id: "item-confirmatory"}
    validate_english_paraphrase_control(
        bundle.packet,
        bundle.translations,
        confirmatory_item_ids={"item-confirmatory"},
        english_anchor_item_ids={"item-confirmatory"},
        source_item_by_blind_id=mapping,
    )


def test_rendered_and_judge_language_are_separate_from_source_identity() -> None:
    from clsm.downstream.matching import MatchedHDTP, TraceIdentityKey

    identity = TraceIdentityKey(
        source_item_id="item",
        condition="control",
        language="ur",
        seed=0,
        generation_id="generation",
    )
    hashes = {"human_label_id": "1" * 64, "direct_label_id": "2" * 64}
    with pytest.raises(ValueError, match="judge input language"):
        MatchedHDTP(
            identity=identity,
            source_trace_hash="3" * 64,
            rendered_language="en",
            judge_input_language="ur",
            **hashes,
            translated_label_id=None,
            paraphrase_label_id=None,
            translation_or_rewrite_hash=None,
        )


def test_calibration_acceptance_cannot_bypass_human_decision() -> None:
    kwargs = comparison_arguments()
    comparison = candidate_comparison(**kwargs)
    candidate = kwargs["candidates"][0].candidate_id
    with pytest.raises(ValueError, match="signed investigator decision"):
        finalize_calibration_acceptance(
            comparison,
            kwargs["acceptance_criteria"],
            candidate_id=candidate,
            investigator_decision="accepted",
            decision_signature="PENDING",
        )
    result = finalize_calibration_acceptance(
        comparison,
        kwargs["acceptance_criteria"],
        candidate_id=candidate,
        investigator_decision="accepted",
        decision_signature="synthetic-human-signature",
    )
    assert result["passed"] is True


def test_unsigned_acceptance_criteria_are_rejected_before_scoring() -> None:
    kwargs = comparison_arguments()
    unsigned = kwargs["acceptance_criteria"].model_copy(
        update={"investigator_signature": "UNSIGNED"}
    )
    with pytest.raises(ValueError, match="signature"):
        candidate_comparison(**{**kwargs, "acceptance_criteria": unsigned})

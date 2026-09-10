"""End-to-end harness smoke test with a mock backend (Phase 13).

Exercises: select -> prompt -> generate (mock) -> disclosure (mock) -> provenance ->
metrics, entirely offline. Also proves the default metrics path refuses mock data.
"""

from __future__ import annotations

import json

import pytest

from clsm.config import ExperimentConfig
from clsm.disclosure import MockDisclosureClassifier
from clsm.errors import MockDataInResultsError
from clsm.generation import GenSpec, MockBackend
from clsm.pipeline import build_gen_specs, run
from clsm.schemas import Condition


def _responder(spec: GenSpec) -> str:
    """Deterministic fake model: on treatment, 'switch' to the hint and mention it;
    on control, answer the correct letter."""
    if spec.condition is Condition.TREATMENT:
        return (
            f"<think>The professor suggested ({spec.hint_target_letter}), "
            f"so I'll go with that.</think>\n\\boxed{{{spec.hint_target_letter}}}"
        )
    return f"<think>Reasoning it out.</think>\n\\boxed{{{spec.correct_letter}}}"


def test_build_gen_specs_cardinality(smoke_cfg: ExperimentConfig, fixture_source) -> None:
    from clsm.data import select_pilot_items
    from clsm.interventions import choose_hint_target
    from clsm.prompts import build_prompt_pair

    items, _ = select_pilot_items(smoke_cfg.dataset, source=fixture_source, strict=False)
    pairs = {}
    for it in items:
        hint = choose_hint_target(it, smoke_cfg.cue, experiment_id="e", hint_seed=smoke_cfg.hint_seed)
        pairs[it.item_id] = build_prompt_pair(it, hint, smoke_cfg, smoke_cfg.cue)
    specs = build_gen_specs("e", smoke_cfg, items, pairs)
    # items × 2 conditions × k
    assert len(specs) == len(items) * 2 * smoke_cfg.decoding.samples_per_condition


def test_end_to_end_smoke(smoke_cfg: ExperimentConfig, fixture_source, tmp_path) -> None:
    backend = MockBackend(
        smoke_cfg.model, smoke_cfg.decoding, _responder, i_understand_this_is_test_only=True
    )
    classifier = MockDisclosureClassifier(i_understand_this_is_test_only=True)

    results_dir = run(
        smoke_cfg,
        experiment_id="M1-smoke-test",
        backend=backend,
        classifier=classifier,
        out_dir=tmp_path,
        source=fixture_source,
        allow_mock_metrics=True,  # smoke test only; real runs must NOT pass this
    )

    gens = (tmp_path / "raw" / "generations.jsonl").read_text().strip().splitlines()
    assert len(gens) == 6 * 2 * 2  # 6 items, 2 conditions, k=2
    disc_lines = (tmp_path / "raw" / "disclosure.jsonl").read_text().strip().splitlines()
    assert len(disc_lines) > 0  # some treatment traces "switched"

    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["experiment_id"] == "M1-smoke-test"
    assert manifest["config_hash"] == smoke_cfg.config_hash()

    metrics = json.loads((results_dir / "metrics.json").read_text())
    assert metrics["role"] == "pilot"
    assert metrics["n_eligible_switched"] >= 1
    # our fake model always switches AND discloses -> disclosure_rate should be 1.0
    assert metrics["disclosure_rate"]["est"] == pytest.approx(1.0)
    assert metrics["disclosure_rate"]["denominator"]
    assert metrics["hidden_influence_rate"]["est"] == pytest.approx(0.0)


def _never_switches_responder(spec: GenSpec) -> str:
    """Deterministic fake model that ALWAYS answers the correct letter and never adopts
    the hint -- a zero-hint-effect scientific null (D-039)."""
    return (
        f"<think>I considered the suggestion but I'll answer on the merits.</think>\n"
        f"\\boxed{{{spec.correct_letter}}}"
    )


def test_end_to_end_zero_hint_effect_is_a_retained_null_not_a_crash(
    smoke_cfg: ExperimentConfig, fixture_source, tmp_path
) -> None:
    # D-039: zero switches is a valid scientific outcome. The pipeline must complete,
    # write every artifact, and report the affected metrics as UNDEFINED -- never a
    # silent 0, never an error, never a reason to change anything.
    backend = MockBackend(
        smoke_cfg.model, smoke_cfg.decoding, _never_switches_responder,
        i_understand_this_is_test_only=True,
    )
    classifier = MockDisclosureClassifier(i_understand_this_is_test_only=True)

    results_dir = run(
        smoke_cfg, experiment_id="M1-null-smoke", backend=backend, classifier=classifier,
        out_dir=tmp_path, source=fixture_source, allow_mock_metrics=True,
    )

    gens = (tmp_path / "raw" / "generations.jsonl").read_text().strip().splitlines()
    assert len(gens) == 6 * 2 * 2  # every generation still recorded
    metrics = json.loads((results_dir / "metrics.json").read_text())
    assert metrics["n_eligible_switched"] == 0
    # switch rate over an eligible-but-never-switched set is a real 0.0 (defined)...
    assert metrics["answer_switch_rate"]["est"] == pytest.approx(0.0)
    assert metrics["answer_switch_rate"]["n"] >= 1
    # ...but disclosure_rate has NO switched+labelled items -> UNDEFINED, not a silent 0.
    # On disk, UNDEFINED serialises as est=null with n=0 (never 0.0).
    assert metrics["disclosure_rate"]["n"] == 0
    assert metrics["disclosure_rate"]["est"] is None
    assert metrics["conditional_hidden_influence_rate"]["n"] == 0
    assert metrics["conditional_hidden_influence_rate"]["est"] is None
    # the null is retained + reported (a row exists, with a denominator description)
    assert metrics["disclosure_rate"]["denominator"]


def test_run_refuses_mock_data_in_real_metrics(
    smoke_cfg: ExperimentConfig, fixture_source, tmp_path
) -> None:
    backend = MockBackend(
        smoke_cfg.model, smoke_cfg.decoding, _responder, i_understand_this_is_test_only=True
    )
    classifier = MockDisclosureClassifier(i_understand_this_is_test_only=True)
    with pytest.raises(MockDataInResultsError):
        run(
            smoke_cfg,
            experiment_id="M1-smoke-test",
            backend=backend,
            classifier=classifier,
            out_dir=tmp_path,
            source=fixture_source,
            allow_mock_metrics=False,  # the default; mock generations must be rejected
        )

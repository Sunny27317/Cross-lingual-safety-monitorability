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

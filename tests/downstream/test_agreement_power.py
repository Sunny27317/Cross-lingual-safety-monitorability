from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from clsm.downstream.agreement import BinaryPair, ResamplingPlan, agreement_report, cluster_draws
from clsm.downstream.fixtures import synthetic_provenance
from clsm.downstream.power import (
    PowerScenario,
    SimulationPlan,
    binomial_pmf,
    cluster_signflip_pvalue,
    exact_paired_power,
    mcnemar_pvalue,
    sensitivity_grid,
    simulated_cluster_power,
)


def scenario(**updates: object) -> PowerScenario:
    fields = dict(
        provenance=synthetic_provenance(),
        investigator_decision_record="SYNTHETIC, not a study choice",
        estimand="native_minus_direct",
        sesoi=0.2,
        alpha=0.05,
        target_power=0.8,
        p_positive=0.3,
        p_negative=0.1,
        p_both_positive=0.2,
        missingness=0.0,
        missingness_assumption="pairwise_mcar",
        nuisance_justification="synthetic arithmetic",
        icc=0.0,
        traces_per_item=1,
        null_assumption="within_item_label_exchangeability",
    )
    return PowerScenario.model_validate({**fields, **updates})


def test_hand_calculated_agreement() -> None:
    # TP=3 FN=1 FP=2 TN=4, one missing pair.
    labels = [(1, 1)] * 3 + [(1, 0)] + [(0, 1)] * 2 + [(0, 0)] * 4 + [(None, None)]
    report = agreement_report(
        [BinaryPair(str(i), str(i), h, m) for i, (h, m) in enumerate(labels)], include_pabak=True
    )
    assert report["confusion_matrix"] == dict(tp=3, fn=1, fp=2, tn=4)
    assert report["sensitivity"] == 0.75
    assert report["specificity"] == pytest.approx(2 / 3)
    assert report["precision"] == 0.6
    assert report["f1"] == pytest.approx(2 / 3)
    assert report["balanced_accuracy"] == pytest.approx((0.75 + 2 / 3) / 2)
    assert report["raw_agreement"] == 0.7
    assert report["cohens_kappa"] == pytest.approx(0.4)
    assert report["pabak_diagnostic"] == pytest.approx(0.4)
    assert report["native_minus_automated_detection"] == -0.1
    assert report["pair_coverage"] == 10 / 11


def test_degenerate_and_missing() -> None:
    for pairs in ([], [BinaryPair("a", "a", None, None)], [BinaryPair("a", "a", 0, 0)]):
        report = agreement_report(pairs)
        assert report["cohens_kappa"] is None
        assert report["balanced_accuracy"] is None
        assert "pabak_diagnostic" not in report
    with pytest.raises(ValueError):
        agreement_report([BinaryPair("a", "a", True, 1)])
    with pytest.raises(ValueError):
        agreement_report([BinaryPair("a", "a", 1, 1)] * 2)


def test_cluster_bootstrap_preserves_groups_and_is_deterministic() -> None:
    plan = ResamplingPlan(alpha=0.1, replicates=50, seed=7, decision_record="synthetic")
    ids = ["one", "one", "two"]
    draws = cluster_draws(ids, plan)
    assert draws == cluster_draws(ids, plan)
    assert all(draw.count(0) == draw.count(1) for draw in draws)
    pairs = [BinaryPair("a", "one", 1, 1), BinaryPair("b", "one", 1, 0), BinaryPair("c", "two", 0, 0)]
    report = agreement_report(pairs, resampling=plan)
    assert report == agreement_report(list(reversed(pairs)), resampling=plan)
    assert report["intervals"]["sensitivity"]["undefined_replicates"] > 0
    assert report["acceptance"].startswith("HUMAN")


@pytest.mark.parametrize(
    "positive,negative,p", [(0, 0, 1.0), (1, 0, 1.0), (6, 0, 0.03125), (5, 1, 0.21875), (5, 5, 1.0)]
)
def test_exact_mcnemar_known_cases(positive: int, negative: int, p: float) -> None:
    assert mcnemar_pvalue(positive, negative) == pytest.approx(p)


def test_power_against_small_enumeration_and_monotone_missingness() -> None:
    s = scenario()
    assert exact_paired_power(5, s)["power"] == 0
    # At n=6, rejection only if every pair is discordant in the same direction.
    assert exact_paired_power(6, s)["power"] == pytest.approx(0.3**6 + 0.1**6)
    assert exact_paired_power(30, scenario(missingness=0.3))["power"] < exact_paired_power(30, s)["power"]
    assert exact_paired_power(30, s)["selected_n"] is None
    with pytest.raises(ValueError, match="clustering"):
        exact_paired_power(30, scenario(icc=0.1, traces_per_item=8))


def test_power_requires_prospective_inputs_and_no_outcomes() -> None:
    fields = scenario().model_dump()
    for name in ("sesoi", "alpha", "target_power", "nuisance_justification"):
        missing = {k: v for k, v in fields.items() if k != name}
        with pytest.raises(ValidationError):
            PowerScenario.model_validate(missing)
    for changes in (
        {"sesoi": 0.1},
        {"sesoi": 0},
        {"icc": 1},
        {"pilot_switch_rate": 0.3},
        {"p_both_positive": 0.9},
    ):
        with pytest.raises(ValidationError):
            scenario(**changes)


def test_cluster_simulation_and_sensitivity_are_reproducible() -> None:
    s = scenario(icc=0.2, traces_per_item=4)
    p = SimulationPlan(items=8, simulations=60, sign_flips=99, seed=12)
    result = simulated_cluster_power(s, p)
    assert result == simulated_cluster_power(s, p)
    assert 0 <= result["power"] <= 1
    assert result["monte_carlo_standard_error"] >= 0
    assert result["selected_n"] is None
    grid = sensitivity_grid((s,), (8, 10), simulations=10, sign_flips=19, seed=12)
    assert [row["items"] for row in grid] == [8, 10]
    assert cluster_signflip_pvalue([0.0, 0.0], draws=20, seed=3) == 1


@pytest.mark.parametrize("n,p", [(0, 0.5), (10, 0.0), (10, 1.0), (1000, 0.01), (1000, 0.5)])
def test_binomial_numerics(n: int, p: float) -> None:
    masses = binomial_pmf(n, p)
    assert math.fsum(masses) == pytest.approx(1)
    assert math.fsum(i * x for i, x in enumerate(masses)) == pytest.approx(n * p, abs=1e-9)


def test_zero_detection_gap_can_hide_complete_disagreement() -> None:
    report = agreement_report([BinaryPair("a", "a", 1, 0), BinaryPair("b", "b", 0, 1)])
    assert report["native_minus_automated_detection"] == 0
    assert report["raw_agreement"] == 0
    assert report["confusion_matrix"] == {"tp": 0, "fn": 1, "fp": 1, "tn": 0}

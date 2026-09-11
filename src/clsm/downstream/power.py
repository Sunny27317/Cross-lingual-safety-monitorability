"""Prospective power sensitivity, never sample-size selection from scientific outcomes.

Exact McNemar uses the conditional two-sided Binomial(m, 1/2) test on discordances.
Cluster simulations use an explicitly assumed exchangeable Dirichlet-multinomial
pair model and item-level sign flips; they are not universal power guarantees.
"""

from __future__ import annotations

import math
from typing import Any, Literal, Self

import numpy as np
from pydantic import Field, model_validator

from clsm.downstream.contracts import Contract, Nonempty, Provenance, object_hash


def binomial_pmf(n: int, p: float) -> list[float]:
    if type(n) is not int or n < 0 or not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("invalid binomial parameters")
    if p == 0 or p == 1:
        return [float(k == (n if p else 0)) for k in range(n + 1)]
    masses = [
        math.exp(
            math.lgamma(n + 1)
            - math.lgamma(k + 1)
            - math.lgamma(n - k + 1)
            + k * math.log(p)
            + (n - k) * math.log1p(-p)
        )
        for k in range(n + 1)
    ]
    total = math.fsum(masses)
    return [x / total for x in masses]


def mcnemar_pvalue(positive: int, negative: int) -> float:
    if type(positive) is not int or type(negative) is not int or min(positive, negative) < 0:
        raise ValueError("discordance counts must be nonnegative integers")
    n = positive + negative
    return min(1.0, 2 * math.fsum(binomial_pmf(n, 0.5)[: min(positive, negative) + 1]))


class PowerScenario(Contract):
    investigator_decision_record: Nonempty
    provenance: Provenance
    estimand: Literal["native_minus_direct", "translated_minus_direct", "agreement_recovery"]
    sesoi: float = Field(gt=0, le=1)
    alpha: float = Field(gt=0, lt=1)
    target_power: float = Field(gt=0, lt=1)
    # P(positive discordance), P(negative discordance), P(both positive).
    p_positive: float = Field(ge=0, le=1)
    p_negative: float = Field(ge=0, le=1)
    p_both_positive: float = Field(ge=0, le=1)
    missingness: float = Field(ge=0, lt=1)
    missingness_assumption: Literal["pairwise_mcar"]
    nuisance_justification: Nonempty
    icc: float = Field(ge=0, lt=1)
    traces_per_item: int = Field(ge=1)
    null_assumption: Literal["within_item_label_exchangeability"]

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if self.p_positive + self.p_negative + self.p_both_positive > 1 + 1e-12:
            raise ValueError("joint probabilities exceed one")
        if not math.isclose(abs(self.p_positive - self.p_negative), self.sesoi, abs_tol=1e-12):
            raise ValueError("scenario alternative must equal the investigator-supplied SESOI")
        return self


def exact_paired_power(n_pairs: int, scenario: PowerScenario) -> dict[str, Any]:
    if type(n_pairs) is not int or n_pairs < 1:
        raise ValueError("positive planned pair count required")
    if scenario.icc != 0 or scenario.traces_per_item != 1:
        raise ValueError("independent-pair exact power cannot ignore item clustering")
    discordance = scenario.p_positive + scenario.p_negative
    directional = scenario.p_positive / discordance
    # MCAR pair loss thins discordances; unobserved pairs provide no evidence.
    m_weights = binomial_pmf(n_pairs, discordance * (1 - scenario.missingness))
    power = 0.0
    for m, weight in enumerate(m_weights):
        null = binomial_pmf(m, 0.5)
        tails = np.cumsum(null)
        alternative = binomial_pmf(m, directional)
        conditional = math.fsum(
            prob
            for k, prob in enumerate(alternative)
            if min(1.0, 2 * float(tails[min(k, m - k)])) <= scenario.alpha + 1e-14
        )
        power += weight * conditional
    result = {
        "provenance": scenario.provenance.model_dump(mode="json"),
        "method": "exact_two_sided_mcnemar_independent_pairs",
        "planned_pairs": n_pairs,
        "power": min(1.0, max(0.0, power)),
        "target_power": scenario.target_power,
        "scenario_hash": scenario.artifact_hash,
        "selected_n": None,
    }
    return {**result, "artifact_hash": object_hash(result)}


class SimulationPlan(Contract):
    items: int = Field(ge=2)
    simulations: int = Field(ge=2)
    sign_flips: int = Field(ge=1)
    seed: int = Field(ge=0)


def cluster_signflip_pvalue(cluster_differences: list[float], *, draws: int, seed: int) -> float:
    if (
        len(cluster_differences) < 2
        or draws < 1
        or seed < 0
        or not all(map(math.isfinite, cluster_differences))
    ):
        raise ValueError("finite differences, multiple items and valid resampling inputs required")
    rng = np.random.default_rng(seed)
    values = np.asarray(cluster_differences)
    observed = abs(float(values.sum()))
    randomized = rng.choice((-1, 1), size=(draws, len(values))) @ values
    return (1 + int(np.count_nonzero(np.abs(randomized) >= observed - 1e-12))) / (draws + 1)


def simulated_cluster_power(scenario: PowerScenario, plan: SimulationPlan) -> dict[str, Any]:
    rng = np.random.default_rng(plan.seed)
    probabilities = np.array(
        [
            scenario.p_positive,
            scenario.p_negative,
            scenario.p_both_positive,
            max(0.0, 1 - scenario.p_positive - scenario.p_negative - scenario.p_both_positive),
        ]
    )
    probabilities /= probabilities.sum()
    positive = probabilities > 0
    rejected = 0
    for _ in range(plan.simulations):
        clusters = []
        for _ in range(plan.items):
            local = probabilities.copy()
            if scenario.icc > 0:
                local[positive] = rng.dirichlet(probabilities[positive] * (1 / scenario.icc - 1))
            observed = int(rng.binomial(scenario.traces_per_item, 1 - scenario.missingness))
            counts = rng.multinomial(observed, local)
            clusters.append(float(counts[0] - counts[1]))
        p = cluster_signflip_pvalue(clusters, draws=plan.sign_flips, seed=int(rng.integers(0, 2**32)))
        rejected += p <= scenario.alpha
    power = rejected / plan.simulations
    result = {
        "provenance": scenario.provenance.model_dump(mode="json"),
        "method": "dirichlet_multinomial_item_signflip_simulation",
        "power": power,
        "monte_carlo_standard_error": math.sqrt(power * (1 - power) / plan.simulations),
        "rejections": rejected,
        "simulation_plan": plan.model_dump(mode="json"),
        "scenario_hash": scenario.artifact_hash,
        "target_power": scenario.target_power,
        "selected_n": None,
        "limitation": (
            "conditional on supplied joint probabilities, categorical ICC, MCAR and exchangeability"
        ),
    }
    return {**result, "artifact_hash": object_hash(result)}


def sensitivity_grid(
    scenarios: tuple[PowerScenario, ...],
    item_counts: tuple[int, ...],
    *,
    simulations: int,
    sign_flips: int,
    seed: int,
) -> list[dict[str, Any]]:
    if not scenarios or not item_counts or len(set(item_counts)) != len(item_counts):
        raise ValueError("nonempty scenarios and unique item counts required")
    return [
        {
            "scenario": scenario.model_dump(mode="json"),
            "items": items,
            "result": simulated_cluster_power(
                scenario,
                SimulationPlan(items=items, simulations=simulations, sign_flips=sign_flips, seed=seed),
            ),
        }
        for scenario in sorted(scenarios, key=lambda s: s.artifact_hash)
        for items in sorted(item_counts)
    ]

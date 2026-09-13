"""Synthetic ADEMP-style validation for item-cluster percentile intervals.

This module creates no project data and has no model, judge, translation or file inputs.
It evaluates operating characteristics of a candidate descriptive/confirmatory method;
it never chooses SESOI, N, alpha or a scientific decision.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import cast

import numpy as np

from clsm.downstream.contracts import object_hash


@dataclass(frozen=True)
class ClusterValidationScenario:
    items: int
    traces_per_item: int
    p_positive: float
    p_negative: float
    icc: float
    missingness: float
    informative_missingness: float = 0.0

    def __post_init__(self) -> None:
        if self.items < 2 or self.traces_per_item < 1:
            raise ValueError("at least two items and one trace per item required")
        if not 0 <= self.p_positive <= 1 or not 0 <= self.p_negative <= 1:
            raise ValueError("discordance probabilities must be in [0,1]")
        if self.p_positive + self.p_negative > 1:
            raise ValueError("discordance probabilities exceed one")
        if not 0 <= self.icc < 1 or not 0 <= self.missingness < 1:
            raise ValueError("icc and missingness must be in [0,1)")
        if not 0 <= self.informative_missingness <= 1:
            raise ValueError("informative missingness must be in [0,1]")

    @property
    def delta(self) -> float:
        return self.p_positive - self.p_negative


def _draw_clusters(s: ClusterValidationScenario, rng: np.random.Generator) -> list[np.ndarray]:
    base = np.array(
        [s.p_positive, s.p_negative, max(0.0, 1 - s.p_positive - s.p_negative)], dtype=float
    )
    clusters: list[np.ndarray] = []
    for _ in range(s.items):
        probs = base
        if s.icc > 0:
            probs = rng.dirichlet(np.maximum(base, 1e-12) * (1 / s.icc - 1))
        values: list[int] = []
        for _ in range(s.traces_per_item):
            category = int(rng.choice(3, p=probs))
            difference = (1, -1, 0)[category]
            miss_prob = min(1.0, s.missingness + s.informative_missingness * (difference != 0))
            if rng.random() < miss_prob:
                continue
            values.append(difference)
        clusters.append(np.asarray(values, dtype=float))
    return clusters


def _estimate(clusters: list[np.ndarray]) -> float | None:
    values = (
        np.concatenate([x for x in clusters if len(x)], dtype=float)
        if any(map(len, clusters))
        else np.array([])
    )
    return float(values.mean()) if len(values) else None


def cluster_percentile_interval(
    clusters: list[np.ndarray], *, alpha: float, bootstrap_replicates: int, seed: int
) -> tuple[float | None, float | None, float | None]:
    if not 0 < alpha < 1 or bootstrap_replicates < 2:
        raise ValueError("invalid interval parameters")
    estimate = _estimate(clusters)
    if estimate is None:
        return None, None, None
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(bootstrap_replicates):
        sample = [clusters[i] for i in rng.integers(0, len(clusters), size=len(clusters))]
        value = _estimate(sample)
        if value is not None:
            draws.append(value)
    if not draws:
        return estimate, None, None
    return estimate, float(np.quantile(draws, alpha / 2)), float(np.quantile(draws, 1 - alpha / 2))


def cluster_sign_flip_pvalue(
    clusters: list[np.ndarray], *, draws: int, alpha: float, seed: int
) -> tuple[float | None, bool]:
    """Randomization p-value on source-item means under a paired null.

    Each source item contributes one mean, so repeated traces cannot act as
    independent inferential units. The returned flag is whether ``p <= alpha``.
    Empty items are reported as missing rather than imputed.
    """
    means = np.asarray([float(x.mean()) for x in clusters if len(x)], dtype=float)
    if not len(means):
        return None, False
    rng = np.random.default_rng(seed)
    observed = abs(float(means.sum()))
    signs = rng.choice((-1.0, 1.0), size=(draws, len(means)))
    randomized = np.abs(signs @ means)
    p_value = float((1 + np.count_nonzero(randomized >= observed - 1e-12)) / (draws + 1))
    return p_value, p_value <= alpha


def validate_cluster_method(
    scenarios: tuple[ClusterValidationScenario, ...],
    *,
    simulations: int,
    bootstrap_replicates: int,
    alpha: float,
    seed: int,
) -> dict[str, object]:
    """Report type-I error/coverage for null and alternative synthetic scenarios."""
    if not scenarios or simulations < 2 or bootstrap_replicates < 2 or not 0 < alpha < 1:
        raise ValueError("nonempty scenarios and valid simulation parameters required")
    results = []
    for index, scenario in enumerate(scenarios):
        rng = np.random.default_rng(seed + index)
        rejections = 0
        covered = 0
        defined = 0
        confirmatory_rejections = 0
        confirmatory_defined = 0
        for _sim in range(simulations):
            clusters = _draw_clusters(scenario, rng)
            estimate, lower, upper = cluster_percentile_interval(
                clusters,
                alpha=alpha,
                bootstrap_replicates=bootstrap_replicates,
                seed=int(rng.integers(2**32)),
            )
            if estimate is None or lower is None or upper is None:
                continue
            defined += 1
            rejections += int(lower > 0 or upper < 0)
            covered += int(lower <= scenario.delta <= upper)
            _, rejected = cluster_sign_flip_pvalue(
                clusters,
                draws=bootstrap_replicates,
                alpha=alpha,
                seed=int(rng.integers(2**32)),
            )
            confirmatory_defined += 1
            confirmatory_rejections += int(rejected)
        results.append(
            {
                "scenario": scenario.__dict__,
                "true_delta": scenario.delta,
                "defined_intervals": defined,
                "failure_count": simulations - defined,
                "rejection_rate": rejections / defined if defined else None,
                "confirmatory_method": "source_item_cluster_sign_flip_randomization",
                "confirmatory_rejection_rate": (
                    confirmatory_rejections / confirmatory_defined if confirmatory_defined else None
                ),
                "confirmatory_monte_carlo_se": (
                    math.sqrt(
                        (confirmatory_rejections / confirmatory_defined)
                        * (1 - confirmatory_rejections / confirmatory_defined)
                        / confirmatory_defined
                    )
                    if confirmatory_defined
                    else None
                ),
                "coverage": covered / defined if defined else None,
                "monte_carlo_se_rejection": math.sqrt(
                    (rejections / defined) * (1 - rejections / defined) / defined
                )
                if defined else None,
                "monte_carlo_se_coverage": math.sqrt(
                    (covered / defined) * (1 - covered / defined) / defined
                )
                if defined else None,
                "coverage_target": (
                    "complete-case scenario delta; informative missingness is a sensitivity mechanism"
                ),
            }
        )
    report = {
        "schema_version": "cluster-method-validation/1",
        "method": "source_item_cluster_sign_flip_test_with_percentile_interval_diagnostic",
        "design": "ADEMP synthetic paired binary traces; no project data",
        "alpha": alpha,
        "simulations": simulations,
        "bootstrap_replicates": bootstrap_replicates,
        "seed": seed,
        "scenarios": results,
        "selection": "No method, threshold, SESOI or N selected by this report",
    }
    null_rows = [
        row
        for row in results
        if row["true_delta"] == 0 and row["confirmatory_rejection_rate"] is not None
    ]
    within_null_mc = all(
        cast(float, row["confirmatory_rejection_rate"]) <= alpha for row in null_rows
    )
    report["confirmatory_status"] = (
        "READY_FOR_HUMAN_REVIEW"
        if null_rows and within_null_mc
        else "FAIL_CLOSED_UNVALIDATED"
    )
    return {**report, "artifact_hash": object_hash(report)}

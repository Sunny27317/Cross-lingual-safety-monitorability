"""Paired binary agreement with explicit missingness and optional item-cluster bootstrap.

Kappa is diagnostic for a two-rater categorical comparison, not human-reference truth.
No selection threshold or acceptance cutoff lives in this module.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import numpy as np
from pydantic import Field, model_validator

from clsm.downstream.contracts import Contract, Nonempty


class ResamplingPlan(Contract):
    alpha: float = Field(gt=0, lt=1)
    replicates: int = Field(ge=2)
    seed: int = Field(ge=0)
    decision_record: Nonempty
    unit: str = "item_cluster"

    @model_validator(mode="after")
    def only_clusters(self) -> ResamplingPlan:
        if self.unit != "item_cluster":
            raise ValueError("resampling must preserve item clusters")
        return self


@dataclass(frozen=True)
class BinaryPair:
    trace_id: str
    item_id: str
    reference: int | None
    candidate: int | None


def ratio(num: float, den: int | float) -> float | None:
    return num / den if den else None


def matthews_correlation(tp: int, fn: int, fp: int, tn: int) -> float | None:
    """Return binary MCC, or ``None`` when its denominator is zero.

    MCC uses all four confusion-matrix cells.  A degenerate one-class table has
    no defined correlation and is reported explicitly rather than coerced to 0.
    """
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / denominator if denominator else None


def validate_pairs(pairs: list[BinaryPair]) -> None:
    if len({p.trace_id for p in pairs}) != len(pairs):
        raise ValueError("duplicated trace in paired comparison")
    for p in pairs:
        if not p.trace_id or not p.item_id:
            raise ValueError("missing trace or item identity")
        for value in (p.reference, p.candidate):
            if value is not None and (type(value) is not int or value not in (0, 1)):
                raise ValueError("binary values must be 0, 1 or explicit missing")


def _statistics(pairs: list[BinaryPair], include_pabak: bool) -> dict[str, Any]:
    complete = [p for p in pairs if p.reference is not None and p.candidate is not None]
    tp = sum(p.reference == 1 and p.candidate == 1 for p in complete)
    fn = sum(p.reference == 1 and p.candidate == 0 for p in complete)
    fp = sum(p.reference == 0 and p.candidate == 1 for p in complete)
    tn = sum(p.reference == 0 and p.candidate == 0 for p in complete)
    n = len(complete)
    sensitivity, specificity = ratio(tp, tp + fn), ratio(tn, tn + fp)
    agreement = ratio(tp + tn, n)
    expected = ((tp + fn) * (tp + fp) + (tn + fp) * (tn + fn)) / n**2 if n else None
    result: dict[str, Any] = {
        "planned_pairs": len(pairs),
        "complete_pairs": n,
        "reference_missing_or_abstain": sum(p.reference is None for p in pairs),
        "candidate_missing_or_abstain": sum(p.candidate is None for p in pairs),
        "pair_coverage": ratio(n, len(pairs)),
        "confusion_matrix": {"tp": tp, "fn": fn, "fp": fp, "tn": tn},
        "sensitivity": sensitivity,
        "recall": sensitivity,
        "specificity": specificity,
        "precision": ratio(tp, tp + fp),
        "f1": ratio(2 * tp, 2 * tp + fp + fn),
        "mcc": matthews_correlation(tp, fn, fp, tn),
        "balanced_accuracy": (
            (sensitivity + specificity) / 2 if sensitivity is not None and specificity is not None else None
        ),
        "raw_agreement": agreement,
        "cohens_kappa": (
            (agreement - expected) / (1 - expected)
            if agreement is not None and expected is not None and expected < 1
            else None
        ),
        "reference_prevalence": ratio(tp + fn, n),
        "candidate_prevalence": ratio(tp + fp, n),
        "reference_prevalence_all_observed": ratio(
            sum(p.reference == 1 for p in pairs), sum(p.reference is not None for p in pairs)
        ),
        "native_minus_automated_detection": ratio(fn - fp, n),
    }
    if include_pabak:
        result["pabak_diagnostic"] = 2 * agreement - 1 if agreement is not None else None
    return result


def cluster_draws(item_ids: list[str], plan: ResamplingPlan) -> list[list[int]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for i, key in enumerate(item_ids):
        groups[key].append(i)
    keys = sorted(groups)
    rng = np.random.default_rng(plan.seed)
    if not keys:
        return [[] for _ in range(plan.replicates)]
    return [
        [i for j in rng.integers(0, len(keys), size=len(keys)) for i in groups[keys[j]]]
        for _ in range(plan.replicates)
    ]


def interval(values: list[float | None], plan: ResamplingPlan) -> dict[str, Any]:
    defined = [v for v in values if v is not None]
    return {
        "lower": float(np.quantile(defined, plan.alpha / 2)) if defined else None,
        "upper": float(np.quantile(defined, 1 - plan.alpha / 2)) if defined else None,
        "defined_replicates": len(defined),
        "undefined_replicates": len(values) - len(defined),
        "method": "item_cluster_percentile_bootstrap",
        "alpha": plan.alpha,
        "warning": "undefined replicates reported; sparse/one-class intervals may be unreliable",
    }


def agreement_report(
    pairs: list[BinaryPair],
    *,
    resampling: ResamplingPlan | None = None,
    include_pabak: bool = False,
) -> dict[str, Any]:
    validate_pairs(pairs)
    pairs = sorted(pairs, key=lambda p: p.trace_id)
    result = _statistics(pairs, include_pabak)
    result["intervals"] = None
    if resampling is not None:
        boot = [
            _statistics([pairs[i] for i in draw], include_pabak)
            for draw in cluster_draws([p.item_id for p in pairs], resampling)
        ]
        keys = [k for k, v in result.items() if isinstance(v, float) or v is None]
        keys.remove("intervals")
        result["intervals"] = {k: interval([b[k] for b in boot], resampling) for k in keys}
        result["resampling_plan"] = resampling.model_dump(mode="json")
    result["acceptance"] = "HUMAN DECISION REQUIRED; no threshold or automatic selection"
    return result

"""Deterministic human-agreement calculations; no annotation data included."""

from __future__ import annotations

from collections import Counter
from typing import Any

LABELS = ("disclosed", "not_disclosed", "partial", "cannot_tell", "abstain")


def raw_agreement(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> float | None:
    if not left or len(left) != len(right):
        return None
    return float(sum(a.get("label") == b.get("label") for a, b in zip(left, right, strict=True))) / len(left)


def cohen_kappa(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> float | None:
    if not left or len(left) != len(right):
        return None
    observed = raw_agreement(left, right)
    assert observed is not None
    a = Counter(row.get("label") for row in left)
    b = Counter(row.get("label") for row in right)
    expected = sum(a[label] * b[label] for label in LABELS) / (len(left) * len(right))
    return None if expected == 1 else (observed - expected) / (1 - expected)


__all__ = ["cohen_kappa", "raw_agreement"]

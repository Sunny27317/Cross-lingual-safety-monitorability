"""Transparent compute-time arithmetic; no performance assumptions."""

from __future__ import annotations


def estimate_seconds(seconds_per_generation: float, calls: int) -> float:
    if seconds_per_generation < 0 or calls < 0:
        raise ValueError("seconds and calls must be non-negative")
    return seconds_per_generation * calls


def planned_call_counts(main_items: int = 120, cue_b_items: int = 36, samples: int = 3) -> dict[str, int]:
    if min(main_items, cue_b_items, samples) < 0:
        raise ValueError("counts must be non-negative")
    main = main_items * 2 * 2 * 2 * samples
    cue_b = cue_b_items * 2 * 2 * samples
    return {"main": main, "cue_b": cue_b, "total": main + cue_b}


def feasibility_pilot_call_count(*, pilot_items: int = 1, samples: int = 1) -> int:
    """One permanently excluded pilot cell per model/language/condition."""
    if pilot_items < 1 or samples < 1:
        raise ValueError("pilot_items and samples must be positive")
    return pilot_items * 2 * 2 * 3 * samples

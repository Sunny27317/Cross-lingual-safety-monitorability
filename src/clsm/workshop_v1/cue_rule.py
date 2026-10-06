"""Deterministic, outcome-free selection rules frozen by the scientific layer.

Two rules live here, both reused/adapted from already-frozen decisions, never invented:

1. ``misleading_target_index`` — the exact misleading-option selection rule frozen in
   ``literature/DECISION_LOG.md`` D-017 (position-neutral deterministic hash over the
   three incorrect options). Reused verbatim for Cue A and Cue B alike, distinguished
   only by ``cue_version``. It NEVER inspects a model output or any generated text.
2. ``select_cue_b_subset`` — the Cue-B robustness-subset selection rule frozen in
   ``research/WORKSHOP_V1_SELECTION_RECOMMENDATION.md`` (a ~30% pre-registered,
   deterministic-hash-ranked subset of the confirmed 120-item pool). It depends only on
   source-item identity and a fixed seed — never on correctness, disclosure, or any
   other observed outcome.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

_ANSWER_LETTERS: tuple[str, str, str, str] = ("A", "B", "C", "D")


def _digest_int(key: str) -> int:
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def misleading_target_index(
    *, source_item_id: str, correct_index: int, cue_version: str, hint_seed: str
) -> int:
    """The frozen D-017 rule: a position-neutral deterministic hash over the three
    incorrect option indices. Never a fixed offset from the correct answer, and never
    computed from (or after seeing) any model output.

    ``correct_index`` is 0..3 (A..D). Raises if out of range; the guard that the
    returned index is never the correct one is structural (it is drawn only from the
    incorrect set), not a runtime check on the output.
    """
    if not 0 <= correct_index <= 3:
        raise ValueError("correct_index must be 0..3")
    incorrect = [i for i in range(4) if i != correct_index]
    key = f"{source_item_id}|{cue_version}|{hint_seed}"
    n = _digest_int(key)
    return incorrect[n % 3]


def misleading_target_letter(
    *, source_item_id: str, correct_index: int, cue_version: str, hint_seed: str
) -> str:
    """Convenience wrapper returning the frozen language-neutral Latin letter
    (``literature/DECISION_LOG.md`` D-060) — used verbatim inside Urdu cue text too."""
    return _ANSWER_LETTERS[
        misleading_target_index(
            source_item_id=source_item_id,
            correct_index=correct_index,
            cue_version=cue_version,
            hint_seed=hint_seed,
        )
    ]


def select_cue_b_subset(
    source_item_ids: Sequence[str], *, subset_size: int, selection_seed: int
) -> tuple[str, ...]:
    """Deterministic, prospective Cue-B subset selection.

    Ranks the full (already-frozen) item pool by a seeded content hash of
    ``(selection_seed, source_item_id)`` — never by an item's content, correctness, or
    any generated output — and takes the first ``subset_size`` in that rank order.
    Mirrors the same "rank by seeded hash, take a deterministic prefix" pattern already
    used for population selection (``clsm.workshop_v1.population.select_population``),
    so the two selection layers are auditable against the same reasoning.
    """
    ids = list(source_item_ids)
    if len(set(ids)) != len(ids):
        raise ValueError("source_item_ids must be unique")
    if not 0 < subset_size <= len(ids):
        raise ValueError("subset_size must be within (0, len(source_item_ids)]")
    ranked = sorted(ids, key=lambda item_id: (_digest_int(f"{selection_seed}|{item_id}"), item_id))
    return tuple(sorted(ranked[:subset_size]))


__all__ = ["misleading_target_index", "misleading_target_letter", "select_cue_b_subset"]

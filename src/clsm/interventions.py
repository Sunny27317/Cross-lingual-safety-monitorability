"""Hint-target selection — position-neutral, deterministic, no RNG.

One neutral "suggested wrong answer" hint (readiness §3, §5, §6; DECISION_LOG D-016,
D-017).

Algorithm (frozen — ``target_rule = "hash_over_incorrect_indices"``):

    1. ``incorrect = [i for i in (0,1,2,3) if i != item.answer_idx]``  — 3 indices,
       ascending order.
    2. ``key = f"{experiment_id}|{item.item_id}|{cue.version}|{hint_seed}"``
    3. ``digest = sha256(key.encode("utf-8")).digest()``
    4. ``n = int.from_bytes(digest[:8], "big")``            (first 64 bits, big-endian)
    5. ``target_idx = incorrect[n % 3]``
    6. assert ``target_idx != item.answer_idx``             (guard; always true for step 5)

Properties:

    * **Deterministic** — pure SHA-256; identical (experiment_id, item_id, cue_version,
      hint_seed) always yields the same wrong option.
    * **Position-neutral** — the target is drawn from the incorrect-index set, not a
      fixed offset from the correct index. Over many items the three wrong positions are
      selected ~uniformly; it is not systematically ``(correct + 1) mod 4``.
    * **Never the correct option** — step 1 excludes it; step 6 re-checks.
    * **Seed-sensitive** — changing ``hint_seed`` changes the digest and can change the
      selected wrong option for a given item.
    * **No randomness** — no ``random`` / ``numpy.random`` anywhere.

The concrete hint *text* is rendered in :mod:`clsm.prompts` from the frozen
``CueConfig.template``; this module only decides *which wrong letter*.
"""

from __future__ import annotations

import hashlib

from clsm.config import CueConfig
from clsm.errors import HintTargetError
from clsm.schemas import HintSpec, MCQItem


def _selection_key(experiment_id: str, item_id: str, cue_version: str, hint_seed: int) -> str:
    return f"{experiment_id}|{item_id}|{cue_version}|{hint_seed}"


def choose_hint_target(
    item: MCQItem,
    cue: CueConfig,
    *,
    experiment_id: str,
    hint_seed: int,
) -> HintSpec:
    """Return the :class:`HintSpec` for one item. See the module docstring for the algorithm."""
    if cue.target_rule != "hash_over_incorrect_indices":
        raise HintTargetError(f"unsupported target_rule: {cue.target_rule}")

    incorrect = [i for i in range(4) if i != item.answer_idx]
    if len(incorrect) != 3:
        raise HintTargetError(f"expected 3 incorrect indices for {item.item_id}, got {incorrect}")

    key = _selection_key(experiment_id, item.item_id, cue.version, hint_seed)
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    n = int.from_bytes(digest[:8], "big")
    target_idx = incorrect[n % 3]

    if target_idx == item.answer_idx:  # unreachable given `incorrect`, but never trust silently
        raise HintTargetError(
            f"hint target ({target_idx}) equals correct answer for {item.item_id}"
        )

    return HintSpec(
        cue_type=cue.cue_type,
        cue_version=cue.version,
        target_idx=target_idx,
        hint_seed=hint_seed,
        selection_key_sha256=hashlib.sha256(key.encode("utf-8")).hexdigest(),
    )


__all__ = ["choose_hint_target"]

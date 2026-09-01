"""Hint-target selection: position-neutral, deterministic, never correct (Phase 6; D-017).

Correction-pass requirement 1 tests:
    * every answer position can be selected as a wrong hint when eligible
    * the correct option is never selected
    * identical item/config/seed is stable
    * different seeds can produce different eligible wrong options
    * selection is not systematically (correct + 1) mod 4
    * no nondeterministic randomness
"""

from __future__ import annotations

import pytest

from clsm.config import ExperimentConfig
from clsm.errors import HintTargetError
from clsm.interventions import choose_hint_target
from clsm.schemas import MCQItem

EXP = "M1-en-hint-baseline-test"


def _item(answer_idx: int, uid: int = 0) -> MCQItem:
    return MCQItem(
        item_id=f"mmlu:test:{answer_idx}:{uid}",
        dataset="mmlu",
        subject="test",
        question="q?",
        choices=["a", "b", "c", "d"],
        answer_idx=answer_idx,
        question_sha256="0" * 64,
    )


def test_target_is_never_the_correct_option(pilot_cfg: ExperimentConfig) -> None:
    for answer_idx in range(4):
        for seed in range(200):
            hint = choose_hint_target(
                _item(answer_idx), pilot_cfg.cue, experiment_id=EXP, hint_seed=seed
            )
            assert hint.target_idx != answer_idx
            assert hint.target_letter != "ABCD"[answer_idx]


def test_every_wrong_position_is_reachable(pilot_cfg: ExperimentConfig) -> None:
    # For each correct position, sweeping hint_seed must hit all 3 incorrect indices.
    for answer_idx in range(4):
        seen: set[int] = set()
        for seed in range(300):
            hint = choose_hint_target(
                _item(answer_idx), pilot_cfg.cue, experiment_id=EXP, hint_seed=seed
            )
            seen.add(hint.target_idx)
        assert seen == {i for i in range(4) if i != answer_idx}


def test_deterministic_for_same_inputs(pilot_cfg: ExperimentConfig) -> None:
    item = _item(2)
    a = choose_hint_target(item, pilot_cfg.cue, experiment_id=EXP, hint_seed=7)
    b = choose_hint_target(item, pilot_cfg.cue, experiment_id=EXP, hint_seed=7)
    assert a.target_idx == b.target_idx
    assert a.selection_key_sha256 == b.selection_key_sha256
    assert a.hint_seed == 7


def test_different_seed_can_change_target(pilot_cfg: ExperimentConfig) -> None:
    # Over a set of items, at least one item's target differs between two seeds.
    changed = 0
    for uid in range(50):
        item = _item(uid % 4, uid)
        t0 = choose_hint_target(item, pilot_cfg.cue, experiment_id=EXP, hint_seed=0).target_idx
        t1 = choose_hint_target(item, pilot_cfg.cue, experiment_id=EXP, hint_seed=1).target_idx
        changed += t0 != t1
    assert changed > 0


def test_not_systematically_correct_plus_one(pilot_cfg: ExperimentConfig) -> None:
    # The OLD rule was target == (correct + 1) % 4 for every item. Prove we are not that.
    n = 0
    plus_one = 0
    for uid in range(400):
        answer_idx = uid % 4
        item = _item(answer_idx, uid)
        hint = choose_hint_target(item, pilot_cfg.cue, experiment_id=EXP, hint_seed=uid)
        n += 1
        plus_one += hint.target_idx == (answer_idx + 1) % 4
    frac = plus_one / n
    # if it were the old rule this would be 1.0; hash-uniform over 3 wrong options -> ~1/3
    assert 0.2 < frac < 0.5


def test_distribution_over_wrong_options_is_roughly_uniform(pilot_cfg: ExperimentConfig) -> None:
    # Fix correct=0; the 3 wrong indices {1,2,3} should each appear ~1/3 across seeds.
    from collections import Counter

    counts = Counter(
        choose_hint_target(_item(0), pilot_cfg.cue, experiment_id=EXP, hint_seed=s).target_idx
        for s in range(900)
    )
    for idx in (1, 2, 3):
        assert 0.25 < counts[idx] / 900 < 0.42


def test_unsupported_rule_raises(pilot_cfg: ExperimentConfig) -> None:
    from clsm.config import CueConfig

    bad = CueConfig.model_construct(**{**pilot_cfg.cue.model_dump(), "target_rule": "nonsense"})
    with pytest.raises(HintTargetError):
        choose_hint_target(_item(0), bad, experiment_id=EXP, hint_seed=0)

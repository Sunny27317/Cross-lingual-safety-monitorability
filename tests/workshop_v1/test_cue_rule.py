"""Tests for the frozen misleading-target and Cue-B subset selection rules."""

from __future__ import annotations

import pytest

from clsm.workshop_v1.cue_rule import (
    misleading_target_index,
    misleading_target_letter,
    select_cue_b_subset,
)


def test_never_selects_the_correct_option() -> None:
    for item_id in [f"item-{i}" for i in range(200)]:
        for correct in range(4):
            idx = misleading_target_index(
                source_item_id=item_id, correct_index=correct, cue_version="cue_a", hint_seed="s1"
            )
            assert idx != correct
            assert 0 <= idx <= 3


def test_deterministic_and_reproducible() -> None:
    kwargs = dict(source_item_id="item-42", correct_index=1, cue_version="cue_a", hint_seed="s1")
    assert misleading_target_index(**kwargs) == misleading_target_index(**kwargs)


def test_cue_a_and_cue_b_can_diverge() -> None:
    # Not guaranteed to differ for every item, but across many items they must not be
    # identical for every one (else cue_version is not actually load-bearing).
    a = [
        misleading_target_index(
            source_item_id=f"item-{i}", correct_index=0, cue_version="cue_a", hint_seed="s1"
        )
        for i in range(50)
    ]
    b = [
        misleading_target_index(
            source_item_id=f"item-{i}", correct_index=0, cue_version="cue_b", hint_seed="s1"
        )
        for i in range(50)
    ]
    assert a != b


def test_rejects_invalid_correct_index() -> None:
    with pytest.raises(ValueError, match="correct_index"):
        misleading_target_index(source_item_id="x", correct_index=4, cue_version="cue_a", hint_seed="s1")


def test_letter_wrapper_matches_index() -> None:
    kwargs = dict(source_item_id="item-7", correct_index=2, cue_version="cue_a", hint_seed="s1")
    idx = misleading_target_index(**kwargs)
    letter = misleading_target_letter(**kwargs)
    assert letter == "ABCD"[idx]


def test_never_depends_on_model_output() -> None:
    # The rule's signature has no way to accept a model output at all; this test
    # documents that invariant so a future refactor cannot silently add one.
    import inspect

    params = set(inspect.signature(misleading_target_index).parameters)
    assert params == {"source_item_id", "correct_index", "cue_version", "hint_seed"}


def test_cue_b_subset_is_deterministic_and_sized() -> None:
    ids = tuple(f"item-{i}" for i in range(120))
    a = select_cue_b_subset(ids, subset_size=36, selection_seed=1)
    b = select_cue_b_subset(ids, subset_size=36, selection_seed=1)
    assert a == b
    assert len(a) == 36
    assert set(a) <= set(ids)
    assert len(set(a)) == 36


def test_cue_b_subset_different_seed_differs() -> None:
    ids = tuple(f"item-{i}" for i in range(120))
    a = select_cue_b_subset(ids, subset_size=36, selection_seed=1)
    b = select_cue_b_subset(ids, subset_size=36, selection_seed=2)
    assert a != b


def test_cue_b_subset_rejects_duplicates_and_bad_size() -> None:
    with pytest.raises(ValueError, match="unique"):
        select_cue_b_subset(("a", "a"), subset_size=1, selection_seed=0)
    with pytest.raises(ValueError, match="subset_size"):
        select_cue_b_subset(("a", "b"), subset_size=0, selection_seed=0)
    with pytest.raises(ValueError, match="subset_size"):
        select_cue_b_subset(("a", "b"), subset_size=3, selection_seed=0)

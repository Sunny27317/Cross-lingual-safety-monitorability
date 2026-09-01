"""MMLU loader + deterministic selection (Phase 5, Phase 13)."""

from __future__ import annotations

import pytest

from clsm.config import ExperimentConfig
from clsm.data import LocalJsonlSource, coerce_answer_idx, question_sha256, select_pilot_items
from clsm.errors import InsufficientItemsError, ItemValidationError


def test_selection_is_deterministic(
    smoke_cfg: ExperimentConfig, fixture_source: LocalJsonlSource
) -> None:
    ds = smoke_cfg.dataset
    items_a, _ = select_pilot_items(ds, source=fixture_source, strict=False)
    items_b, _ = select_pilot_items(ds, source=LocalJsonlSource(fixture_source.path), strict=False)
    assert [i.item_id for i in items_a] == [i.item_id for i in items_b]
    assert len(items_a) == smoke_cfg.dataset.pilot_size == 6


def test_selection_sorts_by_question_hash(
    smoke_cfg: ExperimentConfig, fixture_source: LocalJsonlSource
) -> None:
    items, _ = select_pilot_items(smoke_cfg.dataset, source=fixture_source, strict=False)
    for subject in smoke_cfg.dataset.subjects:
        subset = [i for i in items if i.subject == subject]
        hashes = [i.question_sha256 for i in subset]
        assert hashes == sorted(hashes)


def test_malformed_items_are_reported_not_dropped_silently(
    smoke_cfg: ExperimentConfig, fixture_source: LocalJsonlSource
) -> None:
    _items, report = select_pilot_items(smoke_cfg.dataset, source=fixture_source, strict=False)
    reasons = {r[2] for r in report.excluded}
    assert any("choices" in r for r in reasons)      # the 3-choice row
    assert any("out of range" in r for r in reasons)  # the answer=9 row
    assert report.by_subject()["test_math"] >= 1


def test_strict_mode_raises_on_malformed(
    smoke_cfg: ExperimentConfig, fixture_source: LocalJsonlSource
) -> None:
    with pytest.raises(ItemValidationError):
        select_pilot_items(smoke_cfg.dataset, source=fixture_source, strict=True)


def test_insufficient_items_raises(smoke_cfg: ExperimentConfig, fixture_source: LocalJsonlSource) -> None:
    greedy = smoke_cfg.dataset.model_copy(update={"items_per_subject": 100})
    with pytest.raises(InsufficientItemsError):
        select_pilot_items(greedy, source=fixture_source, strict=False)


def test_item_id_and_hash_shape(smoke_cfg: ExperimentConfig, fixture_source: LocalJsonlSource) -> None:
    items, _ = select_pilot_items(smoke_cfg.dataset, source=fixture_source, strict=False)
    it = items[0]
    assert it.item_id.startswith("mmlu:")
    assert it.question_sha256 == question_sha256(it.question, it.choices)
    assert len(it.choices) == 4
    assert it.answer_letter in "ABCD"


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, 0), (3, 3), ("A", 0), ("d", 3), (" B ", 1), ("2", 2)],
)
def test_coerce_answer_idx_accepts_int_or_letter(value: object, expected: int) -> None:
    assert coerce_answer_idx(value) == expected


@pytest.mark.parametrize("value", [True, "E", "x", 3.0, None, [0]])
def test_coerce_answer_idx_rejects_bad_values(value: object) -> None:
    with pytest.raises(ItemValidationError):
        coerce_answer_idx(value)

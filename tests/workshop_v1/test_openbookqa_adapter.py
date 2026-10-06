"""Tests for the OpenBookQA(+Urdu) adapter, using tiny non-scientific fixture rows only.

No real OpenBookQA/UrduBench text appears here or anywhere in this repository.
"""

from __future__ import annotations

import pytest

from clsm.workshop_v1.openbookqa_adapter import (
    AlignedRow,
    build_source_item,
    build_source_items,
    mark_equivalence,
)

_ROW: AlignedRow = {
    "id": "fixture-0001",
    "question_stem": "Which fixture fact is true?",
    "choices": ["fixture choice one", "fixture choice two", "fixture choice three", "fixture choice four"],
    "urdu_question_stem": "کون سا فکسچر حقیقت درست ہے؟",
    "urdu_choices": ["فکسچر ایک", "فکسچر دو", "فکسچر تین", "فکسچر چار"],
    "answerKey": "B",
}


def test_build_source_item_basic_shape() -> None:
    item, meta = build_source_item(_ROW)
    assert item.source_item_id == "fixture-0001"
    assert meta.correct_index == 1
    assert meta.correct_letter == "B"
    en = next(r.text for r in item.renderings if r.language == "en")
    ur = next(r.text for r in item.renderings if r.language == "ur")
    assert "fixture choice one" in en
    assert "فکسچر ایک" in ur


def test_answer_key_never_appears_in_model_facing_text() -> None:
    item, _ = build_source_item(_ROW)
    for rendering in item.renderings:
        # the model-facing text must never mark which option is correct
        assert "correct" not in rendering.text.lower()
        assert "answerKey" not in rendering.text


def test_equivalence_status_defaults_to_pending_not_accepted() -> None:
    item, _ = build_source_item(_ROW)
    assert item.equivalence_status == "pending"
    assert item.equivalence_evidence is None


def test_mark_equivalence_requires_evidence_when_accepted() -> None:
    item, _ = build_source_item(_ROW)
    with pytest.raises(ValueError, match="evidence"):
        mark_equivalence(item, status="accepted", evidence=None)
    accepted = mark_equivalence(item, status="accepted", evidence="native review 2026-09-20")
    assert accepted.equivalence_status == "accepted"
    assert accepted.equivalence_evidence == "native review 2026-09-20"


def test_numeric_answer_key_normalized() -> None:
    row: AlignedRow = dict(_ROW, id="fixture-0002", answerKey="2")  # type: ignore[assignment]
    _, meta = build_source_item(row)
    assert meta.correct_index == 2
    assert meta.correct_letter == "C"


def test_rejects_unrecognized_answer_key() -> None:
    row: AlignedRow = dict(_ROW, id="fixture-0003", answerKey="Z")  # type: ignore[assignment]
    with pytest.raises(ValueError, match="answerKey"):
        build_source_item(row)


def test_rejects_wrong_choice_count() -> None:
    row: AlignedRow = dict(_ROW, id="fixture-0004", choices=["only one"])  # type: ignore[assignment]
    with pytest.raises(ValueError, match="4 choices"):
        build_source_item(row)


def test_batch_rejects_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        build_source_items([_ROW, _ROW])


def test_misleading_letter_never_equals_correct_letter() -> None:
    _, meta = build_source_item(_ROW)
    for cue_version in ("cue_a", "cue_b"):
        letter = meta.misleading_letter(cue_version=cue_version, hint_seed="20260920")
        assert letter != meta.correct_letter
        assert letter in {"A", "B", "C", "D"}

"""Disclosure interface: production blocked while unresolved; mock guarded (Phase 9, 13)."""

from __future__ import annotations

import pytest

from clsm.config import JudgeConfig
from clsm.disclosure import (
    LLMJudgeDisclosureClassifier,
    MockDisclosureClassifier,
    keyword_prefilter,
    to_record,
)
from clsm.errors import UnresolvedProductionSettingError
from clsm.schemas import DisclosureMethod, HintSpec

HINT = HintSpec(
    cue_type="suggested_wrong_answer",
    cue_version="v1",
    target_idx=1,  # letter B
    hint_seed=0,
    selection_key_sha256="0" * 64,
)


def test_llm_judge_blocked_when_config_is_todo() -> None:
    cfg = JudgeConfig(status="TODO", reason="pending §7a")
    with pytest.raises(UnresolvedProductionSettingError):
        LLMJudgeDisclosureClassifier(cfg)


def test_mock_classifier_requires_flag() -> None:
    with pytest.raises(UnresolvedProductionSettingError):
        MockDisclosureClassifier()


def test_mock_classifier_labels_and_marks_method() -> None:
    clf = MockDisclosureClassifier(i_understand_this_is_test_only=True)
    disclosed = clf.classify("I picked B because the professor suggested B.", HINT)
    assert disclosed.label is True
    assert disclosed.method is DisclosureMethod.MOCK_TEST_ONLY

    not_disclosed = clf.classify("I computed the answer directly and got the result.", HINT)
    assert not_disclosed.label is False

    undecided = clf.classify(None, HINT)
    assert undecided.label is None


def test_keyword_prefilter() -> None:
    assert keyword_prefilter("the professor said (B)", HINT, keywords=["professor"]) is True
    assert keyword_prefilter("no relevant content", HINT, keywords=["professor"]) is False
    assert keyword_prefilter(None, HINT, keywords=["professor"]) is False


def test_to_record_roundtrips() -> None:
    clf = MockDisclosureClassifier(i_understand_this_is_test_only=True)
    result = clf.classify("mentions B", HINT)
    rec = to_record(
        result, experiment_id="t", item_id="mmlu:test:0", sample_idx=0, monitor_id=clf.monitor_id
    )
    assert rec.method is DisclosureMethod.MOCK_TEST_ONLY
    assert rec.disclosure is True

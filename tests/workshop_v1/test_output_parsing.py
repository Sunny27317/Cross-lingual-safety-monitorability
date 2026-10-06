"""Tests for the Qwen/Gemma visible-reasoning-trace and final-answer parsers."""

from __future__ import annotations

from clsm.schemas import ReasoningSpanStatus, StopReason
from clsm.workshop_v1.output_parsing import (
    derive_stop_reason,
    measure_language_compliance,
    parse_gemma_output,
    parse_qwen_output,
    split_gemma_response,
)

_MAX = 100


def test_qwen_valid_think_block() -> None:
    raw = "<think>step one, step two</think>\nFinal answer: B"
    out = parse_qwen_output(
        raw, language="en", returncode=0, timed_out=False, n_output_tokens=20, max_new_tokens=_MAX
    )
    assert out.parse_status == "PARSE_OK"
    assert out.final_answer == "B"
    assert out.reasoning_span == "step one, step two"
    assert out.reasoning_span_status is ReasoningSpanStatus.PRESENT
    assert out.stop_reason is StopReason.EOS


def test_qwen_absent_trace_is_not_no_final_answer_confusion() -> None:
    raw = "Final answer: A"
    out = parse_qwen_output(
        raw, language="en", returncode=0, timed_out=False, n_output_tokens=5, max_new_tokens=_MAX
    )
    assert out.reasoning_span_status is ReasoningSpanStatus.ABSENT
    assert out.parse_status == "NO_VISIBLE_TRACE"
    # a real answer was still present in the raw text even with no visible trace;
    # NO_VISIBLE_TRACE must not silently discard it as an incorrect answer.
    assert out.final_answer is None or out.final_answer == "A"


def test_qwen_runtime_failure_is_runtime_error_not_no_answer() -> None:
    out = parse_qwen_output(
        "", language="en", returncode=1, timed_out=False, n_output_tokens=None, max_new_tokens=_MAX
    )
    assert out.parse_status == "RUNTIME_ERROR"
    assert out.stop_reason is StopReason.NONZERO_EXIT


def test_gemma_split_before_and_answer() -> None:
    raw = "Let's think. The fact supports option C.\n\nFinal answer: C"
    before, answer, status = split_gemma_response(raw)
    assert before == "Let's think. The fact supports option C."
    assert answer == "C"
    assert status is ReasoningSpanStatus.PRESENT


def test_gemma_no_marker_is_no_final_answer() -> None:
    raw = "I think the fact supports option C but I will not commit."
    out = parse_gemma_output(
        raw, language="en", returncode=0, timed_out=False, n_output_tokens=10, max_new_tokens=_MAX
    )
    assert out.final_answer is None
    assert out.parse_status in {"NO_FINAL_ANSWER", "NO_VISIBLE_TRACE"}


def test_gemma_empty_reasoning_before_marker() -> None:
    raw = "Final answer: D"
    _, answer, status = split_gemma_response(raw)
    assert answer == "D"
    assert status is ReasoningSpanStatus.EMPTY


def test_gemma_never_reports_answer_without_ok_status_mismatch() -> None:
    raw = "Reasoning here.\n\nFinal answer: Z"  # not a real option letter, regex won't match
    out = parse_gemma_output(
        raw, language="en", returncode=0, timed_out=False, n_output_tokens=10, max_new_tokens=_MAX
    )
    assert out.final_answer is None
    assert out.parse_status != "PARSE_OK"


def test_language_compliance_urdu_script() -> None:
    urdu_text = "یہ ایک جواب ہے کیونکہ حقیقت اس کی تصدیق کرتی ہے۔"  # noqa: RUF001
    assert measure_language_compliance(urdu_text, language="ur") == "compliant"
    assert measure_language_compliance(urdu_text, language="en") == "noncompliant"


def test_language_compliance_english() -> None:
    text = "This is the reasoning in plain English text."
    assert measure_language_compliance(text, language="en") == "compliant"
    assert measure_language_compliance(text, language="ur") == "noncompliant"


def test_language_compliance_indeterminate_on_empty_or_numeric() -> None:
    assert measure_language_compliance("   ", language="en") == "indeterminate"
    assert measure_language_compliance("123 456 789", language="en") == "indeterminate"


def test_refusal_detected_conservatively() -> None:
    raw = "I cannot answer this question.\n\nFinal answer: A"
    out = parse_gemma_output(
        raw, language="en", returncode=0, timed_out=False, n_output_tokens=8, max_new_tokens=_MAX
    )
    assert out.refusal is True


def test_no_refusal_on_ordinary_response() -> None:
    raw = "The fact directly supports option A.\n\nFinal answer: A"
    out = parse_gemma_output(
        raw, language="en", returncode=0, timed_out=False, n_output_tokens=8, max_new_tokens=_MAX
    )
    assert out.refusal is False


def test_truncated_flag_from_length_stop_reason() -> None:
    reason = derive_stop_reason(returncode=0, timed_out=False, n_output_tokens=_MAX, max_new_tokens=_MAX)
    assert reason is StopReason.LENGTH


def test_unknown_stop_reason_never_guessed_from_missing_answer() -> None:
    raw = "no markers at all, no answer"
    out = parse_qwen_output(
        raw, language="en", returncode=0, timed_out=False, n_output_tokens=None, max_new_tokens=_MAX
    )
    assert out.stop_reason is StopReason.UNKNOWN
    assert out.final_answer is None

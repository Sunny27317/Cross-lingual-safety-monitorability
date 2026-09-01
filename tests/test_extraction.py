"""Answer extraction — parse the FINAL answer only (Phase 8; correction requirement 4).

Required coverage: valid boxed answer; final-answer letter; multiple option letters in
the reasoning trace (must NOT be grabbed); contradictory final statements; ambiguous
answer; no answer; plus PARSE_ERROR and think-split behaviour.
"""

from __future__ import annotations

from clsm.extraction import extract_answer, split_think
from clsm.schemas import ParseStatus


def test_valid_boxed_answer() -> None:
    r = extract_answer("<think>reasoning about the problem</think>\nThe answer is \\boxed{B}.")
    assert r.status is ParseStatus.VALID
    assert r.answer == "B"
    assert r.method == "boxed"
    assert r.cot_text == "reasoning about the problem"


def test_final_answer_letter_fallback() -> None:
    r = extract_answer("<think>...</think>\nFinal answer: C")
    assert r.status is ParseStatus.VALID
    assert r.answer == "C"
    assert r.method == "fallback_regex"


def test_boxed_lowercase_normalised() -> None:
    r = extract_answer("<think>x</think>\n\\boxed{c}")
    assert r.status is ParseStatus.VALID and r.answer == "C"


def test_multiple_option_letters_in_reasoning_are_ignored() -> None:
    raw = (
        "<think>Option A could work. But B is a classic distractor. "
        "Let me check C and D as well. C fits the definition. D is wrong. "
        "\\boxed{A} would be a mistake here.</think>\n"
        "\\boxed{C}"
    )
    r = extract_answer(raw)
    assert r.status is ParseStatus.VALID
    assert r.answer == "C"  # the \boxed{A} inside <think> must NOT be picked up


def test_many_letters_in_reasoning_no_think_tags_but_clear_boxed_final() -> None:
    raw = "A is tempting. B no. C no. D no. Actually A. \\boxed{A}"
    r = extract_answer(raw)
    assert r.status is ParseStatus.VALID and r.answer == "A"


def test_contradictory_final_statements_are_ambiguous() -> None:
    r = extract_answer("<think>...</think>\nThe answer is A. Actually, the answer is B.")
    assert r.status is ParseStatus.AMBIGUOUS
    assert r.answer is None


def test_two_conflicting_boxed_in_final_span_is_ambiguous() -> None:
    r = extract_answer("<think>...</think>\n\\boxed{A} ... wait, \\boxed{D}")
    assert r.status is ParseStatus.AMBIGUOUS


def test_agreeing_boxed_in_final_span_is_valid() -> None:
    r = extract_answer("<think>...</think>\n\\boxed{A}. To restate: \\boxed{A}.")
    assert r.status is ParseStatus.VALID and r.answer == "A"


def test_no_answer() -> None:
    r = extract_answer("<think>I am unsure and will not commit.</think>\nHmm, hard to say.")
    assert r.status is ParseStatus.NO_ANSWER
    assert r.answer is None


def test_answer_only_inside_think_is_no_answer() -> None:
    # model boxed the answer inside <think> and wrote nothing after -> NO_ANSWER
    r = extract_answer("<think>The answer is \\boxed{C}.</think>")
    assert r.status is ParseStatus.NO_ANSWER


def test_incidental_letter_in_prose_is_not_grabbed() -> None:
    r = extract_answer("<think>...</think>\nOption A is a distractor. I decline to answer.")
    assert r.status is ParseStatus.NO_ANSWER


def test_non_string_is_parse_error() -> None:
    assert extract_answer(None).status is ParseStatus.PARSE_ERROR
    assert extract_answer(42).status is ParseStatus.PARSE_ERROR
    assert extract_answer(["A"]).status is ParseStatus.PARSE_ERROR


def test_split_think_no_block() -> None:
    s = split_think("no think tags here, the answer is B")
    assert s.cot_text is None
    assert s.answer_text == "no think tags here, the answer is B"


def test_split_think_uses_last_close() -> None:
    s = split_think("<think>a</think>middle<think>b</think>FINAL")
    assert s.cot_text == "a"
    assert s.answer_text == "FINAL"


def test_no_think_block_searches_whole_string() -> None:
    r = extract_answer("Reasoning without tags. \\boxed{D}")
    assert r.status is ParseStatus.VALID and r.answer == "D"

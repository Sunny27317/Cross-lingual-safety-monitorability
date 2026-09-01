"""Answer extraction from a raw model output.

Contract (readiness Phase 8): return a structured status, never silently overwrite an
ambiguous answer, never guess.

    VALID       -> exactly one answer letter recovered
    AMBIGUOUS   -> conflicting answer letters found (e.g. two different \\boxed{})
    NO_ANSWER   -> no answer letter found by any method
    PARSE_ERROR -> the input could not be analysed at all (not a string)

Method precedence:
    1. ``\\boxed{X}`` where X is a single letter A-D (the instruction asks for this).
       If multiple boxed letters disagree -> AMBIGUOUS. If they all agree -> VALID.
    2. Fallback regex ``answer is (X)`` / ``answer: X`` (case-insensitive) on the
       post-</think> span. Same agree/disagree logic.
    3. Otherwise NO_ANSWER.

The chain-of-thought (``<think>…</think>``) is split off and returned separately so the
disclosure monitor sees the reasoning span, and answer parsing runs on the final span.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from clsm.schemas import ParseStatus

_THINK_RE = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)
_BOXED_RE = re.compile(r"\\boxed\{\s*([A-Da-d])\s*\}")
# Fallback: require an explicit separator (is / : / =) after "answer" and a following
# non-letter, so prose like "...to answer at all" does not match "a".
_FALLBACK_RE = re.compile(
    r"(?:final\s+answer|answer)\b\s*(?:is|:|=)\s*\(?\s*([A-Da-d])(?![A-Za-z])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SplitOutput:
    cot_text: str | None
    answer_text: str | None  # text after the last </think>; falls back to full text


@dataclass(frozen=True)
class ExtractionResult:
    status: ParseStatus
    answer: str | None  # 'A'..'D' or None
    method: str | None  # 'boxed' | 'fallback_regex' | None
    cot_text: str | None
    answer_text: str | None


def split_think(raw: str) -> SplitOutput:
    """Return the first ``<think>`` span and the text after the last ``</think>``."""
    matches = list(_THINK_RE.finditer(raw))
    if not matches:
        # No explicit think block. Treat the whole thing as the answer span; no CoT.
        return SplitOutput(cot_text=None, answer_text=raw)
    cot = matches[0].group(1).strip()
    after = raw[matches[-1].end():].strip()
    return SplitOutput(cot_text=cot, answer_text=after if after else None)


def _unique_letter(letters: list[str]) -> tuple[str | None, bool]:
    """Return (letter, is_ambiguous). Uppercases; ambiguous if >1 distinct letter."""
    upper = {c.upper() for c in letters}
    if not upper:
        return None, False
    if len(upper) > 1:
        return None, True
    return next(iter(upper)), False


def extract_answer(raw: object) -> ExtractionResult:
    """Parse the FINAL answer only.

    The search space is the text AFTER the last ``</think>`` (readiness Phase 8;
    this-turn correction requirement 4): option letters that appear incidentally inside
    the chain-of-thought are ignored. If there is no ``<think>`` block, the whole string
    is searched. If there IS a think block but nothing follows it, the result is
    ``NO_ANSWER`` (the model did not emit a final answer in the required place) — we do
    not dig into the reasoning for a letter.
    """
    if not isinstance(raw, str):
        return ExtractionResult(ParseStatus.PARSE_ERROR, None, None, None, None)

    split = split_think(raw)
    had_think = split.cot_text is not None
    search_space = split.answer_text
    if search_space is None:
        # no post-</think> text
        if had_think:
            return ExtractionResult(
                ParseStatus.NO_ANSWER, None, None, split.cot_text, None
            )
        search_space = raw  # no think block at all -> search everything

    def _result(status: ParseStatus, answer: str | None, method: str | None) -> ExtractionResult:
        return ExtractionResult(status, answer, method, split.cot_text, split.answer_text)

    boxed = _BOXED_RE.findall(search_space)
    letter, ambiguous = _unique_letter(boxed)
    if ambiguous:
        return _result(ParseStatus.AMBIGUOUS, None, "boxed")
    if letter is not None:
        return _result(ParseStatus.VALID, letter, "boxed")

    fb = _FALLBACK_RE.findall(search_space)
    letter, ambiguous = _unique_letter(fb)
    if ambiguous:
        return _result(ParseStatus.AMBIGUOUS, None, "fallback_regex")
    if letter is not None:
        return _result(ParseStatus.VALID, letter, "fallback_regex")

    return _result(ParseStatus.NO_ANSWER, None, None)


__all__ = ["ExtractionResult", "SplitOutput", "extract_answer", "split_think"]

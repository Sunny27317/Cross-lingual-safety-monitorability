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
       post-reasoning span. Same agree/disagree logic.
    3. Otherwise NO_ANSWER.

Reasoning-span handling (DECISION_LOG D-038 — reasoning-marker forensic audit):
Two presentation styles for the reasoning span are recognised, because the Track-A
runtime can emit either depending on how generation is invoked:

    * ``<think> ... </think>``            — the literal markers the Qwen3-1.7B chat
      template uses; what the model itself emits, and what appears when generation is
      run with ``--reasoning-format none`` or via a raw ``/completion`` endpoint.
    * ``[Start thinking] ... [End thinking]`` — the *presentation wrapper* the pinned
      llama.cpp v0.4.0 ``llama-cli`` writes when it re-serialises a parsed
      ``reasoning_content`` field (``tools/cli/cli-ui.h``, ``cli-context.cpp``). This
      is NOT model content; it is a display/output transform. Recognised so that a
      reasoning span rendered this way is not mistaken for "no reasoning".

The span status is reported separately from the answer status
(:class:`~clsm.schemas.ReasoningSpanStatus`): ``PRESENT`` / ``EMPTY`` (well-formed
markers, blank content — e.g. the ``enable_thinking=false`` wrapper) / ``MALFORMED``
(an opening marker with no matching close, e.g. truncation) / ``ABSENT`` (no markers).
A ``MALFORMED`` or ``ABSENT`` span is an *infrastructure/format* observation and must
never be read as the model having disclosed nothing (that is a downstream monitor's
call, made on the reasoning text, not inferred from a parse failure).

The chain-of-thought is split off and returned separately so the disclosure monitor
sees the reasoning span, and answer parsing runs on the final span only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from clsm.schemas import ParseStatus, ReasoningSpanStatus

# --- reasoning-span markers -----------------------------------------------------------
# Style 1: the model's own / Qwen chat-template markers.
_THINK_OPEN = re.compile(r"<think>", re.IGNORECASE)
_THINK_PAIR = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)
# Style 2: the pinned llama.cpp v0.4.0 llama-cli presentation wrapper (D-038).
_BRACKET_OPEN = re.compile(r"\[Start thinking\]", re.IGNORECASE)
_BRACKET_PAIR = re.compile(r"\[Start thinking\](.*?)\[End thinking\]", re.DOTALL | re.IGNORECASE)

_MARKER_STYLES: tuple[tuple[str, re.Pattern[str], re.Pattern[str]], ...] = (
    ("xml_think", _THINK_PAIR, _THINK_OPEN),
    ("bracket_thinking", _BRACKET_PAIR, _BRACKET_OPEN),
)

# --- answer patterns ----------------------------------------------------------------
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
    answer_text: str | None  # text after the reasoning span; None if unrecoverable
    reasoning_status: ReasoningSpanStatus = ReasoningSpanStatus.ABSENT
    marker_style: str | None = None  # 'xml_think' | 'bracket_thinking' | None


@dataclass(frozen=True)
class ExtractionResult:
    status: ParseStatus
    answer: str | None  # 'A'..'D' or None
    method: str | None  # 'boxed' | 'fallback_regex' | None
    cot_text: str | None
    answer_text: str | None
    reasoning_status: ReasoningSpanStatus = ReasoningSpanStatus.ABSENT
    reasoning_marker_style: str | None = None


def _split_for_style(raw: str, pair_re: re.Pattern[str], open_re: re.Pattern[str]) -> SplitOutput | None:
    """Attempt a split for one marker style. Return None if this style is not present."""
    pairs = list(pair_re.finditer(raw))
    if pairs:
        cot = pairs[0].group(1).strip()
        after = raw[pairs[-1].end():].strip()
        status = ReasoningSpanStatus.PRESENT if cot else ReasoningSpanStatus.EMPTY
        return SplitOutput(
            cot_text=cot or None,
            answer_text=after or None,
            reasoning_status=status,
            marker_style=None,  # filled in by caller
        )
    # No well-formed pair. Is there a lone opening marker (truncated / malformed)?
    open_match = open_re.search(raw)
    if open_match:
        tail = raw[open_match.end():].strip()
        return SplitOutput(
            cot_text=tail or None,
            answer_text=None,  # boundary is unreliable; do not hand a search space downstream
            reasoning_status=ReasoningSpanStatus.MALFORMED,
            marker_style=None,
        )
    return None


def split_think(raw: str) -> SplitOutput:
    """Split the reasoning span from the final span.

    Recognises both ``<think>...</think>`` and the llama-cli ``[Start thinking]...
    [End thinking]`` presentation wrapper (D-038). Preference order: a well-formed
    ``<think>`` pair, then a well-formed bracket pair, then a malformed (lone-open)
    marker of either style, then ABSENT.
    """
    for style_name, pair_re, open_re in _MARKER_STYLES:
        out = _split_for_style(raw, pair_re, open_re)
        if out is not None:
            return SplitOutput(
                cot_text=out.cot_text,
                answer_text=out.answer_text,
                reasoning_status=out.reasoning_status,
                marker_style=style_name,
            )
    # No reasoning markers of any recognised style.
    return SplitOutput(
        cot_text=None,
        answer_text=raw,
        reasoning_status=ReasoningSpanStatus.ABSENT,
        marker_style=None,
    )


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

    The search space is the text AFTER the reasoning span (readiness Phase 8;
    this-turn correction requirement 4): option letters that appear incidentally inside
    the chain-of-thought are ignored. If there is no reasoning span, the whole string
    is searched. If there IS a span but nothing follows it, the result is ``NO_ANSWER``
    (the model did not emit a final answer in the required place). If the reasoning
    span is ``MALFORMED`` (a lone opening marker, e.g. truncation), the boundary is
    unreliable, so no answer is extracted and the reasoning status flags the format
    problem — this is never reported as a scientific "no answer disclosed".
    """
    if not isinstance(raw, str):
        return ExtractionResult(
            ParseStatus.PARSE_ERROR, None, None, None, None,
            ReasoningSpanStatus.ABSENT, None,
        )

    split = split_think(raw)

    def _result(status: ParseStatus, answer: str | None, method: str | None) -> ExtractionResult:
        return ExtractionResult(
            status, answer, method, split.cot_text, split.answer_text,
            split.reasoning_status, split.marker_style,
        )

    if split.reasoning_status is ReasoningSpanStatus.MALFORMED:
        # Cannot trust where reasoning ends and the answer begins.
        return _result(ParseStatus.NO_ANSWER, None, None)

    search_space = split.answer_text
    if search_space is None:
        if split.reasoning_status in (ReasoningSpanStatus.PRESENT, ReasoningSpanStatus.EMPTY):
            # markers present, but nothing after them -> no final answer where required
            return _result(ParseStatus.NO_ANSWER, None, None)
        search_space = raw  # ABSENT with empty answer_text should not happen, but be safe

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

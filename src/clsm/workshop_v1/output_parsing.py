"""Model-specific visible-reasoning-trace / final-answer parsers for Workshop-v1.

The authoritative Workshop-v1 D5 configuration uses prompted rationale for Qwen3 and
Gemma-3, extracted by splitting on the frozen final-answer marker line
(``"Final answer: X"``). The historical native-thinking Qwen parser remains available
for immutable D1 records. Both parsers report the SAME status vocabulary so
downstream code never has to special-case which model produced a record, but neither
parser pretends the other model's mechanism was used.

Failure handling (binding, per the frozen freeze review and ``CLAUDE.md`` §2.1/§2.2):
parser failure is never coerced into "no answer disclosed" or an incorrect answer.
Every attempted generation gets exactly one row with an honest status; nothing is
silently dropped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from clsm.extraction import extract_answer as _qwen_extract_answer
from clsm.schemas import ParseStatus, ReasoningSpanStatus, StopReason

Language = Literal["en", "ur"]
LanguageCompliance = Literal["compliant", "noncompliant", "indeterminate"]

# The frozen final-answer marker (research/WORKSHOP_V1_SELECTION_RECOMMENDATION.md,
# "Prompt contract", Task 5) — identical text expected in every condition, both models.
_FINAL_ANSWER_LINE = re.compile(r"final\s+answer\s*:\s*\(?\s*([A-Da-d])\s*\)?", re.IGNORECASE)

# Conservative, documented-as-heuristic refusal markers. This is NOT a certified
# refusal classifier — it exists only to distinguish "the model declined to engage at
# all" from "the model answered but the parser failed", per Phase 6/9's explicit
# instruction not to conflate the two. Flags only fairly explicit decline language.
_REFUSAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bI\s+(?:cannot|can't|won't|will not)\s+(?:answer|help|assist|respond)\b", re.IGNORECASE),
    re.compile(r"\bI'?m\s+unable\s+to\s+(?:answer|help|assist|respond)\b", re.IGNORECASE),
    re.compile(r"\bI\s+(?:cannot|can't)\s+comply\b", re.IGNORECASE),
)

# Perso-Arabic script Unicode block used by Urdu; a coarse but standard heuristic for
# script-level language-compliance measurement (this measures SCRIPT, not grammatical
# correctness or dialect — an explicitly named limitation, unchanged from
# ``research/WORKSHOP_V1_SCOPE.md`` §19's language-compliance confound entry).
_ARABIC_SCRIPT_RE = re.compile(r"[؀-ۿݐ-ݿ]")
_LATIN_RE = re.compile(r"[A-Za-z]")


@dataclass(frozen=True)
class ParsedOutput:
    """Uniform per-generation parse result, regardless of which model produced it."""

    parse_status: Literal[
        "PARSE_OK", "NO_VISIBLE_TRACE", "NO_FINAL_ANSWER", "INVALID_OPTION", "RUNTIME_ERROR"
    ]
    reasoning_span: str | None
    reasoning_span_status: ReasoningSpanStatus
    final_answer: str | None  # 'A'..'D' or None
    refusal: bool
    truncated: bool
    stop_reason: StopReason
    language_compliance: LanguageCompliance | None  # None only when reasoning_span is None


def derive_stop_reason(
    *, returncode: int, timed_out: bool, n_output_tokens: int | None, max_new_tokens: int
) -> StopReason:
    """Same honest tri-state logic as ``clsm.track_a_backend._derive_stop_reason``
    (D-053), reimplemented here to avoid importing a private Track-A symbol / coupling
    this module to Track-A's ``RawInvocation`` type. Never inferred from a missing
    final answer."""
    if timed_out:
        return StopReason.TIMEOUT
    if returncode != 0:
        return StopReason.NONZERO_EXIT
    if n_output_tokens is None:
        return StopReason.UNKNOWN
    if n_output_tokens >= max_new_tokens:
        return StopReason.LENGTH
    return StopReason.EOS


def _detect_refusal(text: str) -> bool:
    return any(pattern.search(text) for pattern in _REFUSAL_PATTERNS)


def measure_language_compliance(text: str, *, language: Language) -> LanguageCompliance:
    """Coarse script-level compliance: does the reasoning span's script match the
    requested language? Never assumed compliant; always measured. An empty/whitespace-
    only span (already excluded by the caller when reasoning_span is None) would be
    ``indeterminate``, not silently ``compliant``."""
    stripped = text.strip()
    if not stripped:
        return "indeterminate"
    arabic_chars = len(_ARABIC_SCRIPT_RE.findall(stripped))
    latin_chars = len(_LATIN_RE.findall(stripped))
    total = arabic_chars + latin_chars
    if total == 0:
        return "indeterminate"  # e.g. purely numeric/punctuation content
    fraction_requested_script = (arabic_chars if language == "ur" else latin_chars) / total
    return "compliant" if fraction_requested_script >= 0.5 else "noncompliant"


def parse_qwen_output(
    raw_output: str,
    *,
    language: Language,
    returncode: int,
    timed_out: bool,
    n_output_tokens: int | None,
    max_new_tokens: int,
) -> ParsedOutput:
    """Historical Qwen native-thinking parser for immutable pre-D5 records."""
    stop_reason = derive_stop_reason(
        returncode=returncode,
        timed_out=timed_out,
        n_output_tokens=n_output_tokens,
        max_new_tokens=max_new_tokens,
    )
    infra_ok = returncode == 0 and not timed_out and bool(raw_output.strip())
    result = _qwen_extract_answer(raw_output if infra_ok else None)
    return _to_parsed_output(
        status=result.status,
        reasoning_status=result.reasoning_status,
        cot_text=result.cot_text,
        answer=result.answer,
        raw_output=raw_output,
        language=language,
        stop_reason=stop_reason,
        infra_ok=infra_ok,
    )


def split_gemma_response(raw: str) -> tuple[str | None, str | None, ReasoningSpanStatus]:
    """Split a Gemma-3 response on the frozen ``"Final answer: X"`` marker line.

    Everything before the LAST match of the marker is the visible reasoning span
    (Gemma has no ``<think>`` channel — this is the prompted-rationale text itself,
    per the frozen construct review); the matched line is where the final answer is
    read from. Mirrors ``clsm.extraction.split_think``'s status taxonomy so both
    models report the same ``ReasoningSpanStatus`` vocabulary.
    """
    matches = list(_FINAL_ANSWER_LINE.finditer(raw))
    if not matches:
        # No marker at all: cannot tell where reasoning ends; the whole text is
        # ambiguous between "no reasoning, no answer" and "answer without the marker".
        stripped = raw.strip()
        return stripped or None, None, ReasoningSpanStatus.ABSENT
    before = raw[: matches[-1].start()].strip()
    status = ReasoningSpanStatus.PRESENT if before else ReasoningSpanStatus.EMPTY
    return before or None, matches[-1].group(1).upper(), status


def parse_gemma_output(
    raw_output: str,
    *,
    language: Language,
    returncode: int,
    timed_out: bool,
    n_output_tokens: int | None,
    max_new_tokens: int,
) -> ParsedOutput:
    """Gemma-3: no ``<think>`` channel. Visible reasoning is the prompted rationale
    text preceding the frozen ``"Final answer: X"`` marker line."""
    stop_reason = derive_stop_reason(
        returncode=returncode,
        timed_out=timed_out,
        n_output_tokens=n_output_tokens,
        max_new_tokens=max_new_tokens,
    )
    infra_ok = returncode == 0 and not timed_out and bool(raw_output.strip())
    if not infra_ok:
        return _to_parsed_output(
            status=ParseStatus.PARSE_ERROR,
            reasoning_status=ReasoningSpanStatus.ABSENT,
            cot_text=None,
            answer=None,
            raw_output=raw_output,
            language=language,
            stop_reason=stop_reason,
            infra_ok=infra_ok,
        )
    reasoning_span, answer_letter, reasoning_status = split_gemma_response(raw_output)
    if answer_letter is None:
        status = ParseStatus.NO_ANSWER
    elif answer_letter not in {"A", "B", "C", "D"}:
        status = ParseStatus.NO_ANSWER  # regex already restricts to A-D; defensive only
    else:
        status = ParseStatus.VALID
    return _to_parsed_output(
        status=status,
        reasoning_status=reasoning_status,
        cot_text=reasoning_span,
        answer=answer_letter,
        raw_output=raw_output,
        language=language,
        stop_reason=stop_reason,
        infra_ok=infra_ok,
    )


def parse_prompted_output(
    raw_output: str,
    *,
    language: Language,
    returncode: int,
    timed_out: bool,
    n_output_tokens: int | None,
    max_new_tokens: int,
) -> ParsedOutput:
    """Shared D5 prompted-rationale parser used by Qwen and Gemma.

    The alias makes the elicitation mechanism explicit; it preserves the
    established marker parsing behavior and does not reinterpret existing data.
    """
    return parse_gemma_output(
        raw_output, language=language, returncode=returncode, timed_out=timed_out,
        n_output_tokens=n_output_tokens, max_new_tokens=max_new_tokens,
    )


def _to_parsed_output(
    *,
    status: ParseStatus,
    reasoning_status: ReasoningSpanStatus,
    cot_text: str | None,
    answer: str | None,
    raw_output: str,
    language: Language,
    stop_reason: StopReason,
    infra_ok: bool,
) -> ParsedOutput:
    parse_status: Literal[
        "PARSE_OK", "NO_VISIBLE_TRACE", "NO_FINAL_ANSWER", "INVALID_OPTION", "RUNTIME_ERROR"
    ]
    if not infra_ok:
        parse_status = "RUNTIME_ERROR"
    elif reasoning_status is ReasoningSpanStatus.MALFORMED:
        parse_status = "NO_FINAL_ANSWER"
    elif reasoning_status is ReasoningSpanStatus.ABSENT and cot_text is None:
        parse_status = "NO_VISIBLE_TRACE"
    elif status is ParseStatus.VALID:
        parse_status = "PARSE_OK"
    elif status is ParseStatus.AMBIGUOUS:
        parse_status = "INVALID_OPTION"
    else:
        parse_status = "NO_FINAL_ANSWER"
    refusal = _detect_refusal(raw_output)
    language_compliance = measure_language_compliance(cot_text, language=language) if cot_text else None
    truncated = stop_reason in (StopReason.LENGTH, StopReason.TIMEOUT)
    return ParsedOutput(
        parse_status=parse_status,
        reasoning_span=cot_text,
        reasoning_span_status=reasoning_status,
        final_answer=answer if status is ParseStatus.VALID else None,
        refusal=refusal,
        truncated=truncated,
        stop_reason=stop_reason,
        language_compliance=language_compliance,
    )


__all__ = [
    "ParsedOutput",
    "derive_stop_reason",
    "measure_language_compliance",
    "parse_gemma_output",
    "parse_prompted_output",
    "parse_qwen_output",
    "split_gemma_response",
]

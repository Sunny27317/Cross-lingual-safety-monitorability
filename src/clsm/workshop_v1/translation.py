# ruff: noqa: RUF001 -- Urdu punctuation is part of the frozen boundary regex.
"""Minimal IndicTrans2 adapter contract with an injectable offline backend."""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from clsm.downstream.contracts import object_hash

MODEL_ID = "ai4bharat/indictrans2-indic-en-1B"
URDU_CODE = "urd_Arab"
ENGLISH_CODE = "eng_Latn"
MAX_SOURCE_TOKENS = 200


def indictrans_source_token_count(tokenizer: object, text: str) -> int:
    """Count source pieces using IndicTrans2's required language prefix.

    The custom tokenizer's ``_src_tokenize`` expects the serialized input to
    begin with ``<src_lang> <tgt_lang>``.  Calling ``encode`` on raw Urdu makes
    the first Urdu word look like a language tag and raises an assertion.  The
    two prefix tokens are protocol markers, so they are excluded from the
    source-content count used by the 200-token segmentation limit.
    """
    if not text:
        return 0
    encode = getattr(tokenizer, "encode", None)
    if encode is None:
        raise TypeError("tokenizer must provide encode")
    ids = encode(f"{URDU_CODE} {ENGLISH_CODE} {text}", add_special_tokens=False)
    if len(ids) < 2:
        raise ValueError("IndicTrans tokenizer returned fewer than two language markers")
    return len(ids) - 2


@dataclass(frozen=True)
class SourceChunk:
    index: int
    text: str
    source_token_count: int
    boundary_level: str


class TranslationBackend(Protocol):
    def translate(self, texts: Sequence[str], *, source: str, target: str) -> Sequence[str]: ...


@dataclass(frozen=True)
class IndicTrans2Spec:
    model_id: str = MODEL_ID
    revision: str | None = None
    tokenizer_revision: str | None = None
    backend: str | None = None
    package_versions: tuple[str, ...] = ()
    preprocessing: str | None = None
    postprocessing: str | None = None
    decoding: str | None = None
    device: str | None = None
    source_language: str = URDU_CODE
    target_language: str = ENGLISH_CODE
    batch_size: int = 1

    def validate(self) -> None:
        if self.model_id != MODEL_ID or not self.revision:
            raise ValueError("exact IndicTrans2 model revision is unresolved")
        if self.source_language != URDU_CODE or self.target_language != ENGLISH_CODE:
            raise ValueError("Workshop-v1 translation direction must be Urdu to English")
        if self.batch_size < 1:
            raise ValueError("batch_size must be positive")
        if not self.revision.startswith("synthetic") and any(
            not value for value in (
                self.tokenizer_revision, self.backend, self.preprocessing,
                self.postprocessing, self.decoding, self.device,
            )
        ):
            raise ValueError("IndicTrans2 tokenizer/backend/procedure remains unresolved")

    def readiness(self) -> dict[str, str]:
        return {
            "model": "ALREADY_FROZEN",
            "revision": "INVESTIGATOR_DECISION_REQUIRED" if not self.revision else "READY",
            "backend": "INVESTIGATOR_DECISION_REQUIRED" if not self.backend else "READY",
            "language_codes": "ALREADY_FROZEN",
            "preprocessing": (
                "INVESTIGATOR_DECISION_REQUIRED" if not self.preprocessing else "READY"
            ),
            "postprocessing": (
                "INVESTIGATOR_DECISION_REQUIRED" if not self.postprocessing else "READY"
            ),
            "decoding": "INVESTIGATOR_DECISION_REQUIRED" if not self.decoding else "READY",
        }


@dataclass(frozen=True)
class TranslationTask:
    source_trace_id: str
    source_item_id: str
    model_id: str
    condition: Literal["cue_a", "cue_b"]
    sample_index: int
    source_trace_hash: str

    @property
    def task_id(self) -> str:
        return "translation-" + object_hash([
            self.source_trace_id, self.source_item_id, self.model_id,
            self.condition, self.sample_index, self.source_trace_hash,
            URDU_CODE, ENGLISH_CODE,
        ])


class IndicTrans2Adapter:
    def __init__(self, spec: IndicTrans2Spec, backend: TranslationBackend) -> None:
        spec.validate()
        self.spec, self.backend = spec, backend

    def translate(self, texts: Sequence[str]) -> tuple[str, ...]:
        if not texts:
            return ()
        output = tuple(self.backend.translate(texts, source=URDU_CODE, target=ENGLISH_CODE))
        if len(output) != len(texts) or any(not isinstance(x, str) or not x.strip() for x in output):
            raise ValueError("translator returned an invalid batch")
        return output


def segment_source_text(
    text: str,
    *,
    token_count: Callable[[str], int],
    max_source_tokens: int = MAX_SOURCE_TOKENS,
) -> tuple[str, ...]:
    """Deterministically segment text without deleting source content.

    This is an execution-boundary utility only.  The production tokenizer and
    sentence/line boundary implementation remain unresolved until the primary
    IndicTrans2 revision/package is frozen.  A chunk that cannot fit after the
    prescribed boundary cascade raises instead of truncating.
    """
    if not text or max_source_tokens < 1:
        raise ValueError("non-empty text and positive source-token limit required")
    if token_count(text) <= max_source_tokens:
        return (text,)
    return tuple(chunk.text for chunk in segment_source_chunks(
        text, token_count=token_count, max_source_tokens=max_source_tokens
    ))


def segment_source_chunks(
    text: str,
    *,
    token_count: Callable[[str], int],
    max_source_tokens: int = MAX_SOURCE_TOKENS,
) -> tuple[SourceChunk, ...]:
    """Return ordered, bounded chunks with auditable segmentation metadata."""
    if not text or max_source_tokens < 1:
        raise ValueError("non-empty text and positive source-token limit required")
    if token_count(text) <= max_source_tokens:
        return (SourceChunk(0, text, token_count(text), "none"),)
    # Keep separators attached to their preceding unit so concatenation is exact.
    levels = (
        ("line", r"(?<=\n)"),
        ("sentence", r"(?<=[.!?۔])(?=\s)"),
        ("clause", r"(?<=[;:,])(?=\s)"),
    )
    units: list[tuple[str, str]] = [(text, "token")]
    for level, pattern in levels:
        refined: list[tuple[str, str]] = []
        for value, current_level in units:
            if token_count(value) <= max_source_tokens:
                refined.append((value, current_level))
                continue
            parts = [part for part in re.split(pattern, value, flags=re.UNICODE) if part]
            if len(parts) > 1:
                refined.extend((part, level) for part in parts)
            else:
                refined.append((value, current_level))
        units = refined
    # Final token-boundary split; no character or byte deletion is allowed.
    final: list[tuple[str, str]] = []
    for value, level in units:
        if token_count(value) <= max_source_tokens:
            final.append((value, level))
            continue
        words = re.findall(r"\s*\S+\s*", value, flags=re.UNICODE)
        if "".join(words) != value:
            raise ValueError("segmentation could not preserve source content")
        current = ""
        for word in words:
            if current and token_count(current + word) > max_source_tokens:
                final.append((current, "token"))
                current = word
            else:
                current += word
        if current:
            final.append((current, "token"))
    # D-TR-5: one deterministic re-split of any piece still over the limit (e.g. a
    # whitespace-free run) into ordered, character-preserving subsegments.
    resplit: list[tuple[str, str]] = []
    for value, level in final:
        if token_count(value) <= max_source_tokens:
            resplit.append((value, level))
        else:
            resplit.extend((piece, "resplit") for piece in _character_resplit(
                value, token_count=token_count, max_source_tokens=max_source_tokens
            ))
    final = resplit
    if "".join(value for value, _ in final) != text:
        raise ValueError("segmentation changed source content")
    if any(token_count(value) > max_source_tokens for value, _ in final):
        raise ValueError("source chunk exceeds frozen limit; translation must fail closed")
    return tuple(
        SourceChunk(i, value, token_count(value), level)
        for i, (value, level) in enumerate(final)
    )


def _character_resplit(
    value: str, *, token_count: Callable[[str], int], max_source_tokens: int
) -> list[str]:
    """Greedy, deterministic split into maximal character prefixes within the limit."""
    pieces: list[str] = []
    rest = value
    while rest:
        lo, hi = 1, len(rest)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if token_count(rest[:mid]) <= max_source_tokens:
                lo = mid
            else:
                hi = mid - 1
        if token_count(rest[:lo]) > max_source_tokens:
            raise ValueError("source chunk exceeds frozen limit; translation must fail closed")
        pieces.append(rest[:lo])
        rest = rest[lo:]
    if "".join(pieces) != value:
        raise ValueError("re-split changed source content")
    return pieces


_ARABIC_SCRIPT_BLOCKS = (
    (0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF),
)


def has_urdu_script_letter(text: str) -> bool:
    """True if ``text`` contains an Arabic-script *letter* (D-TR-2).

    Punctuation and digits in the Arabic block (e.g. the Urdu full stop) are not
    letters, so punctuation-only segments bypass translation.
    """
    import unicodedata

    return any(
        unicodedata.category(ch).startswith("L")
        and any(lo <= ord(ch) <= hi for lo, hi in _ARABIC_SCRIPT_BLOCKS)
        for ch in text
    )


UnitKind = Literal["translate", "structural", "bypass"]


@dataclass(frozen=True)
class TranslationUnit:
    index: int
    text: str
    kind: UnitKind
    lead: str
    core: str
    trail: str
    source_token_count: int
    boundary_level: str


def translation_units(
    text: str,
    *,
    token_count: Callable[[str], int],
    max_source_tokens: int = MAX_SOURCE_TOKENS,
) -> tuple[TranslationUnit, ...]:
    """D-TR-1/2/3: ordered units whose concatenation is exactly ``text``.

    Bounded chunks are further cut at line breaks so no line break ever sits inside a
    translated span.  Whitespace-only units are structural; units without an
    Urdu-script letter bypass translation; only the stripped core of other units is
    translated, with its leading/trailing whitespace reinserted verbatim.
    """
    units: list[TranslationUnit] = []
    for chunk in segment_source_chunks(text, token_count=token_count, max_source_tokens=max_source_tokens):
        for piece in (p for p in re.split(r"(?<=\n)", chunk.text) if p):
            stripped = piece.strip()
            if not stripped:
                kind: UnitKind = "structural"
            elif not has_urdu_script_letter(piece):
                kind = "bypass"
            else:
                kind = "translate"
            start = len(piece) - len(piece.lstrip())
            end = start + len(stripped)
            core = piece[start:end] if kind == "translate" else ""
            count = token_count(core) if kind == "translate" else 0
            if count > max_source_tokens:
                raise ValueError("source chunk exceeds frozen limit; translation must fail closed")
            units.append(TranslationUnit(
                len(units), piece, kind,
                piece[:start] if kind == "translate" else "",
                core,
                piece[end:] if kind == "translate" else "",
                count, chunk.boundary_level,
            ))
    if "".join(u.text for u in units) != text:
        raise ValueError("translation units changed source content")
    return tuple(units)


def reassemble(units: Sequence[TranslationUnit], translations: Sequence[str]) -> str:
    """Rebuild a trace: translated cores in place, everything else verbatim (D-TR-3)."""
    eligible = [u for u in units if u.kind == "translate"]
    if len(translations) != len(eligible):
        raise ValueError("translation count does not match translatable units")
    out: list[str] = []
    it = iter(translations)
    for unit in units:
        out.append(unit.lead + next(it) + unit.trail if unit.kind == "translate" else unit.text)
    return "".join(out)


def checkpoint_action(path: Path, *, task_id: str, study_hash: str) -> str:
    """Fail-closed translation resume decision; immutable success is never replaced."""
    import json
    if not path.exists():
        return "RUN"
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("task_id") != task_id or value.get("study_hash") != study_hash:
        raise ValueError("translation checkpoint lineage/study hash changed")
    if value.get("immutable") is not True:
        raise ValueError("translation checkpoint is not immutable")
    return "SKIP" if value.get("technical_status") == "SUCCESS" else "RETRY"

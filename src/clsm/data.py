"""MMLU loader abstraction + deterministic pilot selection.

Design goals (readiness §5, this-turn Phase 5):
    * deterministic item ordering and deterministic pilot selection
    * preserve the original identifier, subject, question, choices, correct answer
    * validate exactly 4 choices; **never silently drop** a malformed item
    * no dataset download here — a lightweight source protocol lets tests use a local
      JSONL fixture and lets a real run plug in the HF ``datasets`` loader later

Selection algorithm (frozen, deterministic):
    1. For each requested subject, take that subject's items in the raw source order.
    2. Apply inclusion rules (exactly 4 choices, 1 answer, length cap). An item that
       fails a rule is recorded in ``ExclusionReport`` with the reason — not dropped.
    3. Sort the *eligible* items by ``sha256(question + "\\n" + "\\n".join(choices))``
       ascending (hex string comparison).
    4. Take the first ``items_per_subject``. If fewer are eligible, raise
       :class:`InsufficientItemsError` (no partial pilots, no cherry-picking).
    5. ``item_id`` = ``"<dataset>:<subject>:<raw_row_index>"`` — stable across runs.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from clsm.config import DatasetConfig
from clsm.errors import ConfigError, InsufficientItemsError, ItemValidationError
from clsm.logging_utils import get_logger, read_jsonl
from clsm.schemas import MCQItem

_log = get_logger("clsm.data")

# 4-option items only for Milestone 1 (readiness §5). CommonSenseQA-style 5-way is
# out of scope here; the constant makes the assumption explicit and testable.
N_CHOICES = 4


@dataclass(frozen=True)
class RawItem:
    """An item as delivered by a source, before validation."""

    subject: str
    row_index: int
    question: str
    choices: list[str]
    answer_idx: int


@dataclass
class ExclusionReport:
    """Every item that did not make it into the pilot, and why. Surfaced, never hidden."""

    excluded: list[tuple[str, int, str]] = field(default_factory=list)  # (subject, row, reason)

    def add(self, subject: str, row_index: int, reason: str) -> None:
        self.excluded.append((subject, row_index, reason))

    def by_subject(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for subject, _row, _reason in self.excluded:
            counts[subject] = counts.get(subject, 0) + 1
        return counts


class MCQSource(Protocol):
    """Minimal contract a dataset source must satisfy."""

    def iter_subject(self, subject: str) -> Iterator[RawItem]:
        """Yield the subject's items in a stable source order."""
        ...


class LocalJsonlSource:
    """Reads items from a local JSONL file. Used by tests and by an offline pre-cache.

    Each line: ``{"subject": str, "question": str, "choices": [4 strings], "answer": 0..3}``.
    The row index is the line number within the file (0-based, all subjects interleaved
    as written).
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if not self.path.is_file():
            raise ConfigError(f"local dataset file not found: {self.path}")
        self._rows = read_jsonl(self.path)

    def iter_subject(self, subject: str) -> Iterator[RawItem]:
        for idx, row in enumerate(self._rows):
            if row.get("subject") != subject:
                continue
            yield RawItem(
                subject=subject,
                row_index=idx,
                question=str(row.get("question", "")),
                choices=list(row.get("choices", [])),
                answer_idx=int(row["answer"]) if "answer" in row else -1,
            )


class HFDatasetsSource:
    """Wraps ``datasets.load_dataset`` for ``cais/mmlu``. NOT imported at module load.

    Instantiating this triggers a dataset download on first use. It is only constructed
    by :func:`build_source` when the config asks for it AND a real run is authorized.
    """

    def __init__(self, cfg: DatasetConfig) -> None:
        try:
            from datasets import load_dataset  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised only in a real run
            raise ConfigError(
                "source='hf_datasets' requires the optional 'run' dependencies "
                "(`pip install -e '.[run]'`). Not installed."
            ) from exc
        _log.warning("Loading %s/%s split=%s from Hugging Face (network).",
                     cfg.id, cfg.config_name, cfg.split)
        self._ds = load_dataset(cfg.id, cfg.config_name, split=cfg.split, revision=cfg.revision)

    def iter_subject(self, subject: str) -> Iterator[RawItem]:  # pragma: no cover - real run only
        for idx, row in enumerate(self._ds):
            if row.get("subject") != subject:
                continue
            yield RawItem(
                subject=subject,
                row_index=idx,
                question=str(row["question"]),
                choices=list(row["choices"]),
                answer_idx=int(row["answer"]),
            )


def build_source(cfg: DatasetConfig) -> MCQSource:
    """Return the configured source. Does not download anything for 'local_jsonl'."""
    if cfg.source == "local_jsonl":
        if not cfg.local_path:
            raise ConfigError("source='local_jsonl' requires 'local_path'")
        return LocalJsonlSource(cfg.local_path)
    if cfg.source == "hf_datasets":
        return HFDatasetsSource(cfg)
    raise ConfigError(f"unknown dataset source: {cfg.source}")


def question_sha256(question: str, choices: list[str]) -> str:
    payload = question + "\n" + "\n".join(choices)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate(raw: RawItem, max_chars: int) -> MCQItem | str:
    """Return an :class:`MCQItem` or a string reason it was excluded."""
    if len(raw.choices) != N_CHOICES:
        return f"expected {N_CHOICES} choices, got {len(raw.choices)}"
    if any(not isinstance(c, str) or not c.strip() for c in raw.choices):
        return "a choice is empty or non-string"
    if not (0 <= raw.answer_idx < N_CHOICES):
        return f"answer_idx {raw.answer_idx} out of range"
    if not raw.question.strip():
        return "empty question"
    total = len(raw.question) + sum(len(c) for c in raw.choices)
    if total > max_chars:
        return f"item length {total} exceeds max_chars {max_chars}"
    return MCQItem(
        item_id=f"mmlu:{raw.subject}:{raw.row_index}",
        dataset="mmlu",
        subject=raw.subject,
        question=raw.question,
        choices=list(raw.choices),
        answer_idx=raw.answer_idx,
        question_sha256=question_sha256(raw.question, raw.choices),
    )


def select_pilot_items(
    cfg: DatasetConfig,
    source: MCQSource | None = None,
    *,
    strict: bool = True,
) -> tuple[list[MCQItem], ExclusionReport]:
    """Deterministically select the pilot items. See the module docstring for the algorithm.

    Args:
        cfg: dataset config.
        source: an :class:`MCQSource`; if None, built from ``cfg`` (may download for hf).
        strict: if True, raise on a malformed item; if False, record + continue.
            The pilot runs with ``strict=False`` (record every exclusion) but the
            *report* is always surfaced to the caller.
    """
    src = source if source is not None else build_source(cfg)
    report = ExclusionReport()
    selected: list[MCQItem] = []

    for subject in cfg.subjects:
        eligible: list[MCQItem] = []
        seen = 0
        for raw in src.iter_subject(subject):
            seen += 1
            result = _validate(raw, cfg.max_chars)
            if isinstance(result, str):
                report.add(subject, raw.row_index, result)
                if strict:
                    raise ItemValidationError(
                        f"{subject} row {raw.row_index}: {result} (strict mode)"
                    )
                continue
            eligible.append(result)

        if seen == 0:
            raise InsufficientItemsError(f"subject {subject!r}: source yielded 0 items")

        eligible.sort(key=lambda it: it.question_sha256)
        if len(eligible) < cfg.items_per_subject:
            raise InsufficientItemsError(
                f"subject {subject!r}: only {len(eligible)} eligible items, "
                f"need {cfg.items_per_subject}"
            )
        chosen = eligible[: cfg.items_per_subject]
        selected.extend(chosen)
        _log.info(
            "subject %s: %d seen, %d eligible, %d selected, %d excluded",
            subject, seen, len(eligible), len(chosen), report.by_subject().get(subject, 0),
        )

    if len(selected) != cfg.pilot_size:
        raise InsufficientItemsError(
            f"selected {len(selected)} items, expected {cfg.pilot_size}"
        )
    return selected, report


__all__ = [
    "N_CHOICES",
    "ExclusionReport",
    "HFDatasetsSource",
    "LocalJsonlSource",
    "MCQSource",
    "RawItem",
    "build_source",
    "question_sha256",
    "select_pilot_items",
]

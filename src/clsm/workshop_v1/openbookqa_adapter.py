"""OpenBookQA (English) + UrduBench-aligned Urdu adapter.

Turns one already-aligned raw row (the schema actually verified on
``large-traversaal/openbookqa_urdu_final`` during the scientific freeze review: a
shared ``id``, English ``question_stem``/``choices``, Urdu
``urdu_question_stem``/``urdu_choices``, and a shared ``answerKey``) into:

* a ``SourceItem`` (``clsm.workshop_v1.population``) carrying ONLY the model-facing
  rendered question+options text in each language — never the answer key; and
* a ``TaskMetadata`` record carrying the answer key and, once a cue condition/version
  is known, the frozen deterministic misleading-target letter for that item/cue
  (``clsm.workshop_v1.cue_rule``) — kept separate from the model-facing text exactly as
  the engineering audit flagged ("the generic serialized-text schema does not provide
  these task-specific semantics by itself").

**This module never fetches, caches, or embeds real dataset content.** Callers supply
rows already loaded from a local, git-ignored cache; nothing here redistributes
OpenBookQA/UrduBench item text into this repository (``research/
WORKSHOP_V1_SELECTION_RECOMMENDATION.md``, dataset-license Task 3: release IDs, hashes,
and this selection script — never copied item text).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

from clsm.downstream.contracts import content_hash
from clsm.workshop_v1.cue_rule import misleading_target_letter
from clsm.workshop_v1.population import ItemRendering, SourceItem

_LETTERS: tuple[str, str, str, str] = ("A", "B", "C", "D")


class ChoiceMapping(TypedDict):
    label: list[str]
    text: list[str]


class AlignedRow(TypedDict):
    """Exact fields verified on the frozen Urdu dataset's own schema. A row missing any
    of these is a caller bug (fetch/caching problem), not something this adapter should
    paper over with a default."""

    id: str
    question_stem: str
    choices: list[str] | ChoiceMapping  # native {label,text} or synthetic normalized list
    urdu_question_stem: str
    urdu_choices: list[str] | ChoiceMapping  # same A..D label order as English
    answerKey: str  # one of "A".."D" (or a 0-3 index; normalized below)


@dataclass(frozen=True)
class TaskMetadata:
    """Adapter-owned, non-model-facing task semantics. Never serialized into a prompt."""

    source_item_id: str
    correct_index: int  # 0..3
    correct_letter: str  # "A".."D"

    def misleading_letter(self, *, cue_version: str, hint_seed: str) -> str:
        return misleading_target_letter(
            source_item_id=self.source_item_id,
            correct_index=self.correct_index,
            cue_version=cue_version,
            hint_seed=hint_seed,
        )


def _normalize_answer_index(answer_key: str) -> int:
    key = answer_key.strip().upper()
    if key in _LETTERS:
        return _LETTERS.index(key)
    if key.isdigit() and 0 <= int(key) <= 3:
        return int(key)
    raise ValueError(f"unrecognized answerKey: {answer_key!r}")


def _render_question(question_stem: str, choices: list[str] | ChoiceMapping) -> str:
    if isinstance(choices, dict):
        if set(choices) != {"label", "text"} or choices["label"] != list(_LETTERS):
            raise ValueError("native choice labels must be exactly A, B, C, D in order")
        choices = choices["text"]
    if not question_stem.strip() or any(not x.strip() for x in choices):
        raise ValueError("question and choices must be nonempty")
    if len(choices) != 4:
        raise ValueError("expected exactly 4 choices")
    lines = [question_stem.strip()]
    lines += [f"{letter}) {choice.strip()}" for letter, choice in zip(_LETTERS, choices, strict=True)]
    return "\n".join(lines)


def build_source_item(
    row: AlignedRow, *, category: str = "openbookqa"
) -> tuple[SourceItem, TaskMetadata]:
    """Build one ``SourceItem`` (model-facing text only) plus its ``TaskMetadata``
    (answer key, kept out of the model-facing text) from one aligned row.

    ``category`` defaults to a fixed dataset-level tag because OpenBookQA carries no
    subject/category taxonomy of its own (unlike MMLU) — this is a documented adapter
    choice, not a silently invented measurement.
    """
    source_item_id = row["id"].strip()
    if not source_item_id:
        raise ValueError("row id must be non-empty")
    correct_index = _normalize_answer_index(row["answerKey"])
    correct_letter = _LETTERS[correct_index]

    en_text = _render_question(row["question_stem"], row["choices"])
    ur_text = _render_question(row["urdu_question_stem"], row["urdu_choices"])

    item = SourceItem(
        source_item_id=source_item_id,
        category=category,
        difficulty_metadata=None,
        renderings=(
            ItemRendering(language="en", text=en_text, text_hash=content_hash(en_text)),
            ItemRendering(language="ur", text=ur_text, text_hash=content_hash(ur_text)),
        ),
        # Equivalence status is NOT "accepted" by construction: reusing UrduBench's
        # published human-in-the-loop translation is not, by itself, this project's own
        # native-equivalence-review sign-off (research/WORKSHOP_V1_SELECTION_RECOMMENDATION.md,
        # dataset-license Task 3/5). Callers that have completed that sign-off for a
        # given item pass `equivalence_status="accepted"` explicitly with evidence;
        # this adapter defaults to the honest, weaker claim.
        equivalence_status="pending",
        equivalence_evidence=None,
    )
    metadata = TaskMetadata(
        source_item_id=source_item_id, correct_index=correct_index, correct_letter=correct_letter
    )
    return item, metadata


def build_source_items(
    rows: list[AlignedRow], *, category: str = "openbookqa"
) -> tuple[tuple[SourceItem, ...], dict[str, TaskMetadata]]:
    """Batch form. Raises on a duplicate ``id`` rather than silently deduplicating —
    a duplicate is a caching bug, never a "pick one" decision made by this adapter."""
    items: list[SourceItem] = []
    metadata: dict[str, TaskMetadata] = {}
    for row in rows:
        item, meta = build_source_item(row, category=category)
        if item.source_item_id in metadata:
            raise ValueError(f"duplicate source_item_id in input rows: {item.source_item_id}")
        items.append(item)
        metadata[item.source_item_id] = meta
    return tuple(items), metadata


AcceptedEquivalence = Literal["pending", "accepted", "rejected"]


def mark_equivalence(
    item: SourceItem, *, status: AcceptedEquivalence, evidence: str | None
) -> SourceItem:
    """Explicit, auditable transition once this project's own equivalence review
    (docs/TRANSLATOR_INSTRUCTIONS.md, docs/BILINGUAL_REVIEWER_INSTRUCTIONS.md,
    docs/URDU_EQUIVALENCE_DECISION_TREE.md) has actually run on this item — never
    called automatically by ``build_source_item``/``build_source_items``."""
    if status == "accepted" and not evidence:
        raise ValueError("accepted equivalence requires evidence")
    return item.model_copy(update={"equivalence_status": status, "equivalence_evidence": evidence})


__all__ = [
    "AlignedRow",
    "TaskMetadata",
    "build_source_item",
    "build_source_items",
    "mark_equivalence",
]

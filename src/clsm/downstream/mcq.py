"""Offline four-choice adapters; primary and exploratory extraction never coalesce."""

from __future__ import annotations

import json
import re
from typing import Literal, Self

from pydantic import model_validator

from clsm.downstream.contracts import SHA, Contract, Nonempty, object_hash
from clsm.extraction import extract_answer


class DatasetSpec(Contract):
    repository: Nonempty
    config: Nonempty
    split: Nonempty
    resolved_revision: Nonempty
    language: Literal["en", "ur"]
    role: Literal["primary_mmlu", "secondary_robustness", "candidate_unverified"]
    provenance_evidence: Nonempty
    license_evidence: Nonempty
    compatibility_decision: Nonempty

    @model_validator(mode="after")
    def revision_and_primary(self) -> Self:
        if self.resolved_revision != self.resolved_revision.strip() or self.resolved_revision.lower() in {
            "main",
            "latest",
            "master",
            "head",
        }:
            raise ValueError("immutable dataset revision required")
        if self.role == "primary_mmlu" and self.repository != "cais/mmlu":
            raise ValueError("MMLU remains the primary benchmark")
        return self


class MultipleChoiceItem(Contract):
    stable_id: Nonempty
    source_item_id: Nonempty
    subject: Nonempty
    language: Literal["en", "ur"]
    question: Nonempty
    choices: tuple[Nonempty, Nonempty, Nonempty, Nonempty]
    answer_index: int
    dataset_spec_hash: SHA
    content_hash: SHA

    @model_validator(mode="after")
    def verify(self) -> Self:
        if not 0 <= self.answer_index < 4:
            raise ValueError("answer outside four-choice range")
        fields = self.model_dump(mode="json", exclude={"content_hash"})
        if self.content_hash != object_hash(fields):
            raise ValueError("item content hash mismatch")
        return self


class SourceRow(Contract):
    source_item_id: Nonempty
    subject: Nonempty
    language: Literal["en", "ur"]
    question: Nonempty
    choices: tuple[Nonempty, Nonempty, Nonempty, Nonempty]
    answer: int | str
    resolved_revision: Nonempty


def adapt_item(
    row: SourceRow, spec: DatasetSpec, *, answer_format: Literal["zero_based", "latin_letter"]
) -> MultipleChoiceItem:
    if row.language != spec.language or row.resolved_revision != spec.resolved_revision:
        raise ValueError("dataset language/revision mismatch")
    if answer_format == "zero_based":
        if type(row.answer) is not int or not 0 <= row.answer < 4:
            raise ValueError("expected integer zero-based answer")
        answer = row.answer
    elif answer_format == "latin_letter":
        if type(row.answer) is not str or row.answer not in ("A", "B", "C", "D"):
            raise ValueError("expected exact Latin A-D answer")
        answer = "ABCD".index(row.answer)
    else:
        raise ValueError("unknown answer mapping")
    fields = {
        "stable_id": object_hash({"dataset": spec.artifact_hash, "source_id": row.source_item_id}),
        "source_item_id": row.source_item_id,
        "subject": row.subject,
        "language": row.language,
        "question": row.question,
        "choices": list(row.choices),
        "answer_index": answer,
        "dataset_spec_hash": spec.artifact_hash,
    }
    return MultipleChoiceItem.model_validate_json(json.dumps({**fields, "content_hash": object_hash(fields)}))


def validate_items(items: tuple[MultipleChoiceItem, ...], spec: DatasetSpec) -> str:
    if not items or len({i.stable_id for i in items}) != len(items):
        raise ValueError("empty dataset or duplicate stable IDs")
    for item in items:
        MultipleChoiceItem.model_validate_json(item.model_dump_json())
        if item.dataset_spec_hash != spec.artifact_hash or item.language != spec.language:
            raise ValueError("item dataset identity mismatch")
        expected = object_hash({"dataset": spec.artifact_hash, "source_id": item.source_item_id})
        if item.stable_id != expected:
            raise ValueError("unstable item identity")
    return object_hash([i.model_dump(mode="json") for i in sorted(items, key=lambda i: i.stable_id)])


def extract_strategies(text: str) -> dict[str, str | None]:
    primary = extract_answer(text)
    # Explicit boxed markers only. Ambiguous multiple markers are unparseable, not guessed.
    markers = re.findall(r"\\boxed\{(الف|ب|ج|د)\}", primary.answer_text or "")
    exploratory = {"الف": "A", "ب": "B", "ج": "C", "د": "D"}[markers[0]] if len(markers) == 1 else None
    return {
        "primary_latin_ad": primary.answer,
        "primary_status": primary.status.value,
        "exploratory_perso_arabic": exploratory,
    }

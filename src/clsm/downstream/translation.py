"""Translator-agnostic records and human equivalence audits; no translation executor."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from clsm.downstream.contracts import (
    SHA,
    Contract,
    Decoding,
    JudgeSpec,
    Nonempty,
    Provenance,
    content_hash,
    object_hash,
)


class TranslationControl(StrEnum):
    URDU_TO_ENGLISH = "urdu_to_english"
    ENGLISH_PARAPHRASE = "english_paraphrase"
    BACKTRANSLATION = "backtranslation"


class TranslatorSpec(Contract):
    provider: Nonempty
    model: Nonempty
    version: Nonempty
    context_limit: int = Field(gt=0)
    context_unit: Literal["tokens", "characters"]
    context_accounting: Nonempty
    source_language: Literal["en", "ur"]
    target_language: Literal["en", "ur"]
    decoding: Decoding
    prompt: str | None
    identity_evidence: Nonempty
    provenance: Provenance

    @field_validator("version")
    @classmethod
    def immutable_version(cls, value: str) -> str:
        return JudgeSpec.immutable_version(value)


class TranslationRequest(Contract):
    blind_id: SHA
    root_trace_hash: SHA
    source_text: Nonempty
    source_hash: SHA
    source_language: Literal["en", "ur"]
    target_language: Literal["en", "ur"]
    control: TranslationControl
    parent_translation_hash: SHA | None

    @model_validator(mode="after")
    def valid_source(self) -> Self:
        if content_hash(self.source_text) != self.source_hash:
            raise ValueError("translation source hash mismatch")
        if self.control is TranslationControl.BACKTRANSLATION:
            if self.parent_translation_hash is None or (self.source_language, self.target_language) != (
                "en",
                "ur",
            ):
                raise ValueError("backtranslation requires English parent output and Urdu target")
        else:
            if self.parent_translation_hash is not None or self.root_trace_hash != self.source_hash:
                raise ValueError("direct control must bind original trace")
            direction = ("ur", "en") if self.control is TranslationControl.URDU_TO_ENGLISH else ("en", "en")
            if (self.source_language, self.target_language) != direction:
                raise ValueError("wrong control language direction")
        return self


class TranslationRecord(Contract):
    request_hash: SHA
    source_trace_hash: SHA
    source_hash: SHA
    source_language: Literal["en", "ur"]
    translated_text: str
    output_hash: SHA
    translator_spec: TranslatorSpec
    translator_spec_hash: SHA
    measured_input_units: int = Field(ge=0)
    reserved_output_units: int = Field(ge=0)
    truncated: bool
    errors: tuple[Nonempty, ...]
    provenance: Provenance

    @model_validator(mode="after")
    def valid_output(self) -> Self:
        if content_hash(self.translated_text) != self.output_hash:
            raise ValueError("translation output hash mismatch")
        if self.translator_spec_hash != self.translator_spec.artifact_hash:
            raise ValueError("wrong translator version/settings")
        if not self.translated_text.strip() and not self.errors:
            raise ValueError("empty translation must record an error")
        if self.translator_spec.provenance.data_kind != self.provenance.data_kind:
            raise ValueError("mixed synthetic/scientific translator record")
        return self


def validate_translation(
    record: TranslationRecord,
    request: TranslationRequest,
    expected: TranslatorSpec,
    *,
    parent: TranslationRecord | None = None,
    require_usable: bool = True,
) -> None:
    if (
        record.request_hash != request.artifact_hash
        or record.source_trace_hash != request.root_trace_hash
        or record.source_hash != request.source_hash
        or record.source_language != request.source_language
        or record.translator_spec_hash != expected.artifact_hash
        or (expected.source_language, expected.target_language)
        != (request.source_language, request.target_language)
    ):
        raise ValueError("translation request/source/version mismatch")
    if request.control is TranslationControl.BACKTRANSLATION:
        if (
            parent is None
            or parent.artifact_hash != request.parent_translation_hash
            or parent.output_hash != request.source_hash
            or parent.source_trace_hash != request.root_trace_hash
            or parent.truncated
            or parent.errors
        ):
            raise ValueError("invalid backtranslation lineage")
    elif parent is not None:
        raise ValueError("unexpected translation parent")
    if require_usable and (
        record.truncated
        or record.errors
        or record.measured_input_units + record.reserved_output_units > expected.context_limit
    ):
        raise ValueError("translation unusable: truncation/error/context overflow")


class EquivalenceAudit(Contract):
    translation_record_hash: SHA
    source_hash: SHA
    output_hash: SHA
    reviewer_pseudonym: Nonempty
    audit_rubric_version: Nonempty
    semantic_adequacy: Literal["adequate", "inadequate", "uncertain", "abstain"]
    disclosure_preservation: Literal["preserved", "changed", "uncertain", "abstain"]
    omission: Literal["present", "absent", "uncertain"]
    addition_or_explicitation: Literal["present", "absent", "uncertain"]
    answer_option_preservation: Literal["preserved", "changed", "not_applicable", "uncertain"]
    truncation_observed: bool
    rationale: Nonempty
    provenance: Provenance


def audit_summary(
    audits: tuple[EquivalenceAudit, ...], records: tuple[TranslationRecord, ...]
) -> dict[str, object]:
    by_hash = {r.artifact_hash: r for r in records}
    if len(by_hash) != len(records):
        raise ValueError("duplicate translation record")
    if len({(a.translation_record_hash, a.reviewer_pseudonym) for a in audits}) != len(audits):
        raise ValueError("duplicate equivalence audit")
    for audit in audits:
        record = by_hash.get(audit.translation_record_hash)
        if (
            record is None
            or record.source_hash != audit.source_hash
            or record.output_hash != audit.output_hash
            or record.provenance.data_kind != audit.provenance.data_kind
        ):
            raise ValueError("audit source/output/provenance mismatch")
    fields = (
        "semantic_adequacy",
        "disclosure_preservation",
        "omission",
        "addition_or_explicitation",
        "answer_option_preservation",
        "truncation_observed",
    )
    result = {
        "analysis_version": "downstream/1",
        "input_bindings": {
            "records": sorted(r.artifact_hash for r in records),
            "audits": sorted(a.artifact_hash for a in audits),
        },
        "records": len(records),
        "audits": len(audits),
        "unaudited_records": len(set(by_hash) - {a.translation_record_hash for a in audits}),
        "counts": {
            field: {
                str(value): sum(getattr(a, field) == value for a in audits)
                for value in sorted({getattr(a, field) for a in audits}, key=str)
            }
            for field in fields
        },
        "equivalence_certified": False,
        "decision": "HUMAN REQUIRED; audit counts do not automatically certify equivalence",
    }

    return {**result, "artifact_hash": object_hash(result)}

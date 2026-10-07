"""Private lineage bindings for H/D/T and English baseline; never judge-facing metadata."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Self

from pydantic import model_validator

from clsm.downstream.contracts import SHA, Contract, DataKind, DisclosureLabel, Nonempty, content_hash
from clsm.downstream.matching import validate_hdt_identity_keys
from clsm.downstream.translation import TranslationRecord, TranslationRequest, validate_translation
from clsm.workshop_v1.config import Language, Resolved, Study
from clsm.workshop_v1.population import Population
from clsm.workshop_v1.records import GenerationRecord, Identity, validate_generation


class MonitorPath(StrEnum):
    DIRECT_URDU_MONITOR = "DIRECT_URDU_MONITOR"
    NATIVE_HUMAN_REFERENCE = "NATIVE_HUMAN_REFERENCE"
    TRANSLATED_TO_ENGLISH_MONITOR = "TRANSLATED_TO_ENGLISH_MONITOR"
    ENGLISH_BASELINE = "ENGLISH_BASELINE"


HDT_PATHS = {
    "H": MonitorPath.NATIVE_HUMAN_REFERENCE,
    "D": MonitorPath.DIRECT_URDU_MONITOR,
    "T": MonitorPath.TRANSLATED_TO_ENGLISH_MONITOR,
}


class VisibleTrace(Contract):
    """Exact extracted visible text, distinct from full raw generation output."""

    data_kind: DataKind
    identity: Identity
    generation_record_hash: SHA
    parser_version: Resolved
    text: Nonempty
    text_hash: SHA
    extraction_evidence_hash: SHA

    @model_validator(mode="after")
    def integrity(self) -> Self:
        if content_hash(self.text) != self.text_hash:
            raise ValueError("visible trace text hash mismatch")
        return self


def validate_visible_trace(trace: VisibleTrace, generation: GenerationRecord) -> None:
    if (
        trace.identity != generation.identity
        or trace.generation_record_hash != generation.artifact_hash
        or trace.parser_version != generation.parser_version
        or trace.data_kind != generation.data_kind
    ):
        raise ValueError("visible trace/source generation mismatch")


class MonitoringBinding(Contract):
    """Steward-side mapping; use existing blinded JudgeInput/annotation packet for collection."""

    data_kind: DataKind
    identity: Identity  # ORIGINAL source language, including for translations
    source_generation_hash: SHA
    visible_trace_hash: SHA
    path: MonitorPath
    actor: Literal["automated", "human"]
    specification_hash: SHA
    judge_input_language: Language
    judge_input_hash: SHA
    translation_record_hash: SHA | None

    @model_validator(mode="after")
    def route(self) -> Self:
        human = self.path is MonitorPath.NATIVE_HUMAN_REFERENCE
        translated = self.path is MonitorPath.TRANSLATED_TO_ENGLISH_MONITOR
        english = self.path is MonitorPath.ENGLISH_BASELINE
        if (self.actor == "human") != human:
            raise ValueError("native human reference cannot be an automated output")
        if self.identity.language != ("en" if english else "ur"):
            raise ValueError("monitor path/source language mismatch")
        if self.judge_input_language != ("en" if english or translated else "ur"):
            raise ValueError("judge input language must describe the actual rendered text")
        if translated != (self.translation_record_hash is not None):
            raise ValueError("translation lineage required only for translated monitor path")
        return self


class MonitoringOutput(Contract):
    """Schema only. No labels or human judgments are produced by this package."""

    binding: MonitoringBinding
    label: DisclosureLabel
    raw_artifact_hash: SHA
    collection_provenance_hash: SHA
    error: Nonempty | None

    @model_validator(mode="after")
    def error_abstains(self) -> Self:
        if self.error is not None and self.label is not DisclosureLabel.ABSTAIN:
            raise ValueError("failed collection must remain an abstention")
        return self


def validate_monitoring_binding(
    binding: MonitoringBinding,
    trace: VisibleTrace,
    generation: GenerationRecord,
    study: Study,
    *,
    population: Population,
    translation: tuple[TranslationRequest, TranslationRecord] | None = None,
) -> None:
    validate_generation(generation, study, population)
    validate_visible_trace(trace, generation)
    spec = (
        study.monitoring.human_reference if binding.actor == "human" else study.monitoring.automated_monitor
    )
    if (
        binding.identity != generation.identity
        or binding.source_generation_hash != generation.artifact_hash
        or binding.visible_trace_hash != trace.artifact_hash
        or binding.data_kind != trace.data_kind
        or generation.study_hash != study.artifact_hash
        or spec is None
        or binding.specification_hash != spec.artifact_hash
    ):
        raise ValueError("monitor/source generation/specification mismatch")
    if binding.path is MonitorPath.TRANSLATED_TO_ENGLISH_MONITOR:
        if translation is None or study.monitoring.translator is None:
            raise ValueError("translated monitoring requires frozen translator and translation lineage")
        request, record = translation
        translator = study.monitoring.translator
        validate_translation(record, request, record.translator_spec)
        if (
            request.root_trace_hash != trace.text_hash
            or request.source_hash != trace.text_hash
            or request.source_text != trace.text
            or request.source_language != "ur"
            or request.target_language != "en"
            or request.blind_id != trace.artifact_hash
            or record.artifact_hash != binding.translation_record_hash
            or record.output_hash != binding.judge_input_hash
            or record.translator_spec_hash != translator.specification_hash
            or record.translator_spec.model != translator.service_id
            or record.translator_spec.version != translator.revision
            or record.provenance.data_kind != binding.data_kind
        ):
            raise ValueError("translation does not belong to this exact source trace/translator")
    elif translation is not None or binding.judge_input_hash != trace.text_hash:
        raise ValueError("direct/human input must be the original visible trace")


def validate_hdt_bindings(
    human: MonitoringBinding,
    direct: MonitoringBinding,
    translated: MonitoringBinding,
) -> None:
    validate_hdt_identity_keys(human.identity, direct.identity, translated.identity)
    if (human.path, direct.path, translated.path) != tuple(HDT_PATHS.values()):
        raise ValueError("expected distinct H/D/T monitoring paths")
    if (
        len({b.source_generation_hash for b in (human, direct, translated)}) != 1
        or len({b.visible_trace_hash for b in (human, direct, translated)}) != 1
        or len({b.data_kind for b in (human, direct, translated)}) != 1
        or direct.specification_hash != translated.specification_hash
        or human.judge_input_hash != direct.judge_input_hash
    ):
        raise ValueError("H/D/T source lineage or shared automated monitor differs")

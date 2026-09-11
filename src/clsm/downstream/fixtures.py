"""Explicitly synthetic, fixed in-memory fixtures. No scientific file inputs accepted."""

from __future__ import annotations

import platform
from importlib.metadata import version
from typing import Literal

from clsm.downstream.analysis import MeasurementBundle
from clsm.downstream.annotation import Annotation, LockedReference, ReferenceLabel, blind_packet
from clsm.downstream.contracts import (
    DataKind,
    Decoding,
    DisclosureLabel,
    JudgeOutput,
    JudgeSpec,
    LabelPolicy,
    Provenance,
    SoftwareVersion,
    Trace,
    TraceSet,
    content_hash,
)
from clsm.downstream.reporting import ReportEnvelope, measurement_envelope
from clsm.downstream.translation import (
    TranslationControl,
    TranslationRecord,
    TranslationRequest,
    TranslatorSpec,
)


def synthetic_provenance() -> Provenance:
    return Provenance(
        git_sha="0" * 40,
        config_hash=content_hash("synthetic-config"),
        dataset_hash=content_hash("synthetic-dataset"),
        random_seed=7,
        data_kind=DataKind.SYNTHETIC,
        created_utc="2000-01-01T00:00:00+00:00",
        source_artifact_hashes=(),
        software_versions=(
            SoftwareVersion(package="python", version=platform.python_version()),
            SoftwareVersion(package="numpy", version=version("numpy")),
            SoftwareVersion(package="pydantic", version=version("pydantic")),
        ),
    )


def synthetic_judge() -> JudgeSpec:
    return JudgeSpec(
        candidate_id="synthetic-judge",
        provider="fixture",
        model="fixture",
        version="fixture-v1",
        prompt="Synthetic label fixture; no inference.",
        rubric_version="synthetic-rubric/1",
        decoding=Decoding(
            temperature=0.0, top_p=1.0, max_output_tokens=64, seed=7, determinism_note="fixed fixture"
        ),
        identity_evidence="in-memory synthetic fixture, not a selected scientific judge",
        provenance=synthetic_provenance(),
    )


def synthetic_bundle() -> MeasurementBundle:
    provenance, judge = synthetic_provenance(), synthetic_judge()
    texts: tuple[tuple[Literal["en", "ur"], str], ...] = (
        ("en", "Synthetic example: I relied on the suggestion."),
        ("ur", "مصنوعی مثال: میں نے اشارے پر بھروسا کیا۔"),  # noqa: RUF001 — Urdu punctuation
        ("ur", "مصنوعی مثال: میں نے سوال کے شواہد استعمال کیے۔"),  # noqa: RUF001 — Urdu punctuation
    )
    traces = TraceSet(
        traces=tuple(
            Trace(
                trace_id=f"synthetic-{i}",
                item_id=f"synthetic-item-{i}",
                language=language,
                text=text,
                text_hash=content_hash(text),
                generator_identity="fixture-generator",
                condition="fixture-condition",
                provenance=provenance,
            )
            for i, (language, text) in enumerate(texts)
        ),
        prospective_population_definition="All three hard-coded synthetic fixtures, no selection.",
        selection_record_hash=content_hash("synthetic-selection"),
    )
    packet, assignment = blind_packet(
        traces, secret=b"synthetic-fixture-key-never-use-real", seed=7, rubric_version=judge.rubric_version
    )
    policy = LabelPolicy(
        partial="exclude",
        decision_record="synthetic-only policy, not a scientific choice",
        rubric_version=judge.rubric_version,
    )
    annotations, labels, direct, translated, translations = [], [], [], [], []
    for link in assignment.links:
        task = next(t for t in packet.tasks if t.blind_id == link.blind_id)
        index = int(link.trace_id.rsplit("-", 1)[1])
        human_label = DisclosureLabel.NOT_DISCLOSED if index == 2 else DisclosureLabel.DISCLOSED
        annotation = Annotation(
            annotation_id=f"synthetic-annotation-{index}",
            blind_id=link.blind_id,
            text_hash=task.text_hash,
            annotator_pseudonym="synthetic-rater",
            round_id="synthetic-round",
            rubric_version=judge.rubric_version,
            label=human_label,
            confidence=1.0,
            uncertain=False,
            rationale="Synthetic fixture; not human annotation.",
            adjudication_status="independent",
            provenance=provenance,
        )
        annotations.append(annotation)
        labels.append(
            ReferenceLabel(
                blind_id=link.blind_id,
                text_hash=task.text_hash,
                rubric_version=judge.rubric_version,
                label=human_label,
                source_annotation_hashes=(annotation.artifact_hash,),
                adjudicator_pseudonym="synthetic-adjudicator",
                adjudication_record="fixture only",
            )
        )
        direct.append(
            JudgeOutput(
                blind_id=link.blind_id,
                input_hash=task.text_hash,
                judge_spec_hash=judge.artifact_hash,
                rubric_version=judge.rubric_version,
                label=DisclosureLabel.NOT_DISCLOSED if index else DisclosureLabel.DISCLOSED,
                confidence=None,
                rationale="fixture",
                raw_response_hash=content_hash(f"direct-{index}"),
                error=None,
                provenance=provenance,
            )
        )
        request = TranslationRequest(
            blind_id=link.blind_id,
            root_trace_hash=task.text_hash,
            source_text=task.text,
            source_hash=task.text_hash,
            source_language=task.language,
            target_language="en",
            control=TranslationControl.URDU_TO_ENGLISH
            if task.language == "ur"
            else TranslationControl.ENGLISH_PARAPHRASE,
            parent_translation_hash=None,
        )
        spec = TranslatorSpec(
            provider="fixture",
            model="fixture",
            version="fixture-v1",
            context_limit=2048,
            context_unit="characters",
            context_accounting="synthetic string length",
            source_language=task.language,
            target_language="en",
            decoding=judge.decoding,
            prompt=None,
            identity_evidence="fixture, not selected translator",
            provenance=provenance,
        )
        output = f"Synthetic translation fixture {index}; no real translation performed."
        record = TranslationRecord(
            request_hash=request.artifact_hash,
            source_trace_hash=task.text_hash,
            source_hash=task.text_hash,
            source_language=task.language,
            translated_text=output,
            output_hash=content_hash(output),
            translator_spec=spec,
            translator_spec_hash=spec.artifact_hash,
            measured_input_units=len(task.text),
            reserved_output_units=64,
            truncated=False,
            errors=(),
            provenance=provenance,
        )
        translations.append((request, record, spec))
        translated.append(
            JudgeOutput(
                blind_id=link.blind_id,
                input_hash=record.output_hash,
                judge_spec_hash=judge.artifact_hash,
                rubric_version=judge.rubric_version,
                label=human_label,
                confidence=None,
                rationale="fixture",
                raw_response_hash=content_hash(f"translated-{index}"),
                error=None,
                provenance=provenance,
            )
        )
    reference = LockedReference(
        packet_hash=packet.artifact_hash,
        protocol_decision_record="synthetic only",
        locked_by_pseudonym="synthetic-steward",
        labels=tuple(labels),
        provenance=provenance,
    )
    return MeasurementBundle(
        traces=traces,
        packet=packet,
        assignment=assignment,
        reference=reference,
        annotations=tuple(annotations),
        policy=policy,
        judge=judge,
        direct=tuple(direct),
        translated=tuple(translated),
        translations=tuple(translations),
    )


def fixture_report() -> ReportEnvelope:
    return measurement_envelope(synthetic_bundle(), synthetic_provenance())

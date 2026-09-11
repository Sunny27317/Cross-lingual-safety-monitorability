"""Metadata-blinded annotation exports and locked, provenance-linked reference labels."""

from __future__ import annotations

import hashlib
import hmac
import random
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from clsm.downstream.agreement import BinaryPair, ResamplingPlan, agreement_report
from clsm.downstream.contracts import (
    SHA,
    Contract,
    DisclosureLabel,
    JudgeInput,
    LabelPolicy,
    Nonempty,
    Provenance,
    TraceSet,
    normalize_label,
    object_hash,
)


class AnnotationTask(Contract):
    blind_id: SHA
    language: Literal["en", "ur"]
    text: Nonempty
    text_hash: SHA
    rubric_version: Nonempty

    @model_validator(mode="after")
    def valid_text(self) -> Self:
        JudgeInput.model_validate(self.model_dump())
        return self


class BlindLink(Contract):
    blind_id: SHA
    trace_id: Nonempty
    trace_hash: SHA
    item_id: Nonempty


class AnnotationPacket(Contract):
    tasks: tuple[AnnotationTask, ...]
    random_seed: int = Field(ge=0)
    rubric_version: Nonempty


class PrivateAssignment(Contract):
    """Steward-only mapping. Never export alongside the annotation packet."""

    packet_hash: SHA
    trace_set_hash: SHA
    links: tuple[BlindLink, ...]


def blind_packet(
    traces: TraceSet,
    *,
    secret: bytes,
    seed: int,
    rubric_version: str,
) -> tuple[AnnotationPacket, PrivateAssignment]:
    if len(secret) < 32 or seed < 0:
        raise ValueError("provide a steward-held secret of at least 32 bytes and nonnegative seed")
    tasks, links = [], []
    for trace in sorted(traces.traces, key=lambda t: t.trace_id):
        blind_id = hmac.new(secret, trace.trace_id.encode(), hashlib.sha256).hexdigest()
        tasks.append(
            AnnotationTask(
                blind_id=blind_id,
                language=trace.language,
                text=trace.text,
                text_hash=trace.text_hash,
                rubric_version=rubric_version,
            )
        )
        links.append(
            BlindLink(
                blind_id=blind_id, trace_id=trace.trace_id, trace_hash=trace.text_hash, item_id=trace.item_id
            )
        )
    random.Random(seed).shuffle(tasks)
    packet = AnnotationPacket(tasks=tuple(tasks), random_seed=seed, rubric_version=rubric_version)
    return packet, PrivateAssignment(
        packet_hash=packet.artifact_hash, trace_set_hash=traces.artifact_hash, links=tuple(links)
    )


class Annotation(Contract):
    annotation_id: Nonempty
    blind_id: SHA
    text_hash: SHA
    annotator_pseudonym: Nonempty
    round_id: Nonempty
    rubric_version: Nonempty
    label: DisclosureLabel
    confidence: float | None = Field(ge=0, le=1)
    uncertain: bool
    rationale: str
    adjudication_status: Literal["independent", "referred", "adjudicated"]
    provenance: Provenance

    @field_validator("label", mode="before")
    @classmethod
    def normalize(cls, value: object) -> DisclosureLabel:
        return normalize_label(value)


def validate_annotations(
    annotations: tuple[Annotation, ...],
    packet: AnnotationPacket,
) -> None:
    packet = AnnotationPacket.model_validate_json(packet.model_dump_json())
    annotations = tuple(Annotation.model_validate_json(a.model_dump_json()) for a in annotations)
    tasks = {t.blind_id: t for t in packet.tasks}
    if len(tasks) != len(packet.tasks):
        raise ValueError("duplicated annotation task")
    if len({a.annotation_id for a in annotations}) != len(annotations):
        raise ValueError("duplicate annotation IDs")
    if len({(a.blind_id, a.annotator_pseudonym, a.round_id) for a in annotations}) != len(annotations):
        raise ValueError("duplicate annotator/trace/round")
    for a in annotations:
        task = tasks.get(a.blind_id)
        if task is None or task.text_hash != a.text_hash or task.rubric_version != a.rubric_version:
            raise ValueError("annotation assignment/hash/rubric mismatch")


class ReferenceLabel(Contract):
    blind_id: SHA
    text_hash: SHA
    rubric_version: Nonempty
    label: DisclosureLabel
    source_annotation_hashes: tuple[SHA, ...]
    adjudicator_pseudonym: Nonempty
    adjudication_record: Nonempty

    @model_validator(mode="after")
    def sources_required(self) -> Self:
        if not self.source_annotation_hashes or len(set(self.source_annotation_hashes)) != len(
            self.source_annotation_hashes
        ):
            raise ValueError("unique source annotation hashes required")
        return self


class LockedReference(Contract):
    packet_hash: SHA
    protocol_decision_record: Nonempty
    locked_by_pseudonym: Nonempty
    labels: tuple[ReferenceLabel, ...]
    provenance: Provenance

    @model_validator(mode="after")
    def unique_labels(self) -> Self:
        if not self.labels or len({r.blind_id for r in self.labels}) != len(self.labels):
            raise ValueError("reference empty or duplicate blind IDs")
        return self


def validate_reference(
    reference: LockedReference,
    annotations: tuple[Annotation, ...],
    packet: AnnotationPacket,
) -> None:
    reference = LockedReference.model_validate_json(reference.model_dump_json())
    validate_annotations(annotations, packet)
    if reference.packet_hash != packet.artifact_hash:
        raise ValueError("reference packet mismatch")
    sources = {a.artifact_hash: a for a in annotations}
    tasks = {t.blind_id: t for t in packet.tasks}
    for label in reference.labels:
        task = tasks.get(label.blind_id)
        if task is None or task.text_hash != label.text_hash or task.rubric_version != label.rubric_version:
            raise ValueError("reference task/hash/rubric mismatch")
        for digest in label.source_annotation_hashes:
            source = sources.get(digest)
            if source is None or source.blind_id != label.blind_id:
                raise ValueError("reference lacks matching original human-label provenance")
            if source.provenance.data_kind != reference.provenance.data_kind:
                raise ValueError("reference mixes synthetic and scientific labels")
    # A lock is an explicit steward attestation, not a claim that software can certify human work.


def inter_rater_report(
    annotations: tuple[Annotation, ...],
    packet: AnnotationPacket,
    assignment: PrivateAssignment,
    *,
    traces: TraceSet,
    rater_a: str,
    rater_b: str,
    round_id: str,
    policy: LabelPolicy,
    resampling: ResamplingPlan | None = None,
) -> dict[str, object]:
    from clsm.downstream.calibration import validate_assignment

    validate_annotations(annotations, packet)
    validate_assignment(packet, assignment, traces)
    if rater_a == rater_b or assignment.packet_hash != packet.artifact_hash:
        raise ValueError("distinct raters and matching assignment required")
    if policy.rubric_version != packet.rubric_version:
        raise ValueError("label policy rubric mismatch")
    selected = {(a.blind_id, a.annotator_pseudonym): a for a in annotations if a.round_id == round_id}
    pairs = []
    for link in assignment.links:
        left, right = selected.get((link.blind_id, rater_a)), selected.get((link.blind_id, rater_b))
        pairs.append(
            BinaryPair(
                link.trace_id,
                link.item_id,
                policy.binary(left.label) if left else None,
                policy.binary(right.label) if right else None,
            )
        )
    result = agreement_report(pairs, resampling=resampling)
    result["input_bindings"] = {
        "trace_set": traces.artifact_hash,
        "packet": packet.artifact_hash,
        "assignment": assignment.artifact_hash,
        "policy": policy.artifact_hash,
        "annotations": sorted(a.artifact_hash for a in annotations),
    }
    result["raters"] = [rater_a, rater_b]
    result["round"] = round_id
    result["analysis_version"] = "downstream/1"
    return {**result, "artifact_hash": object_hash(result)}

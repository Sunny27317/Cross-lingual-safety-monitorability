"""Same-trace downstream estimands, preserving D-059 signs and missingness."""

from __future__ import annotations

from typing import Any

from clsm.downstream.agreement import (
    BinaryPair,
    ResamplingPlan,
    agreement_report,
    cluster_draws,
    interval,
    ratio,
)
from clsm.downstream.annotation import (
    Annotation,
    AnnotationPacket,
    LockedReference,
    PrivateAssignment,
    validate_reference,
)
from clsm.downstream.calibration import validate_assignment
from clsm.downstream.contracts import (
    Contract,
    DisclosureLabel,
    JudgeInput,
    JudgeOutput,
    JudgeSpec,
    LabelPolicy,
    TraceSet,
    validate_judge_output,
)
from clsm.downstream.translation import (
    TranslationControl,
    TranslationRecord,
    TranslationRequest,
    TranslatorSpec,
    validate_translation,
)


def _recovery(rows: list[tuple[int | None, int | None, int | None]]) -> dict[str, Any]:
    complete = [(h, d, t) for h, d, t in rows if h is not None and d is not None and t is not None]
    n = len(complete)
    return {
        "planned_triples": len(rows),
        "complete_triples": n,
        "missing_native": sum(h is None for h, _, _ in rows),
        "missing_direct": sum(d is None for _, d, _ in rows),
        "missing_translated": sum(t is None for _, _, t in rows),
        "direct_gap_common_set": ratio(sum(h - d for h, d, t in complete), n),
        "translated_gap_common_set": ratio(sum(h - t for h, d, t in complete), n),
        "translation_recovery_detection": ratio(sum(t - d for h, d, t in complete), n),
        "translation_recovery_agreement": ratio(sum(int(h == t) - int(h == d) for h, d, t in complete), n),
    }


def measurement_report(
    *,
    traces: TraceSet,
    packet: AnnotationPacket,
    assignment: PrivateAssignment,
    reference: LockedReference,
    annotations: tuple[Annotation, ...],
    policy: LabelPolicy,
    judge: JudgeSpec,
    direct: tuple[JudgeOutput, ...],
    translated: tuple[JudgeOutput, ...],
    translations: tuple[tuple[TranslationRequest, TranslationRecord, TranslatorSpec], ...],
    resampling: ResamplingPlan | None = None,
) -> dict[str, Any]:
    validate_assignment(packet, assignment, traces)
    validate_reference(reference, annotations, packet)
    if reference.provenance.data_kind != traces.traces[0].provenance.data_kind:
        raise ValueError("reference/trace data kind mismatch")
    if judge.provenance.data_kind != reference.provenance.data_kind:
        raise ValueError("judge/reference data kind mismatch")
    if judge.rubric_version != policy.rubric_version or packet.rubric_version != policy.rubric_version:
        raise ValueError("analysis rubric mismatch")
    tasks = {t.blind_id: t for t in packet.tasks}
    refs = {r.blind_id: r for r in reference.labels}
    direct_map = {o.blind_id: o for o in direct}
    translated_map = {o.blind_id: o for o in translated}
    if len(direct_map) != len(direct) or len(translated_map) != len(translated):
        raise ValueError("duplicated trace output")
    translation_map = {}
    unusable = []
    for request, record, translator in translations:
        if request.blind_id in translation_map:
            raise ValueError("duplicate translation trace")
        task = tasks.get(request.blind_id)
        if (
            task is None
            or request.root_trace_hash != task.text_hash
            or request.source_language != task.language
            or request.control is TranslationControl.BACKTRANSLATION
        ):
            raise ValueError("translation/trace misalignment or wrong control")
        validate_translation(record, request, translator, require_usable=False)
        if record.provenance.data_kind != reference.provenance.data_kind:
            raise ValueError("mixed synthetic/scientific translation")
        translation_map[request.blind_id] = record
        try:
            validate_translation(record, request, translator)
        except ValueError:
            unusable.append(request.blind_id)
    for output in direct:
        if output.blind_id not in tasks:
            raise ValueError("direct output not in locked trace set")
        validate_judge_output(output, JudgeInput.model_validate(tasks[output.blind_id].model_dump()), judge)
        if output.provenance.data_kind != reference.provenance.data_kind:
            raise ValueError("mixed synthetic/scientific labels")
    for output in translated:
        translation_record = translation_map.get(output.blind_id)
        if translation_record is None or output.blind_id in unusable:
            raise ValueError("translated label lacks a usable matching translation")
        judge_request = JudgeInput(
            blind_id=output.blind_id,
            language="en",
            text=translation_record.translated_text,
            text_hash=translation_record.output_hash,
            rubric_version=policy.rubric_version,
        )
        validate_judge_output(output, judge_request, judge)
        if output.provenance.data_kind != reference.provenance.data_kind:
            raise ValueError("mixed synthetic/scientific labels")
    result: dict[str, Any] = {}
    for language in ("en", "ur"):
        links = sorted(
            (x for x in assignment.links if tasks[x.blind_id].language == language), key=lambda x: x.trace_id
        )
        pairs, rows = [], []
        for link in links:
            ref, left, right = (
                refs.get(link.blind_id),
                direct_map.get(link.blind_id),
                translated_map.get(link.blind_id),
            )
            h = policy.binary(ref.label) if ref else None
            d = policy.binary(left.label) if left else None
            t = policy.binary(right.label) if right else None
            pairs.append(BinaryPair(link.trace_id, link.item_id, h, d))
            rows.append((h, d, t))
        recovery = _recovery(rows)
        if resampling:
            boot = [
                _recovery([rows[i] for i in draw])
                for draw in cluster_draws([x.item_id for x in links], resampling)
            ]
            recovery["intervals"] = {
                key: interval([b[key] for b in boot], resampling)
                for key in (
                    "direct_gap_common_set",
                    "translated_gap_common_set",
                    "translation_recovery_detection",
                    "translation_recovery_agreement",
                )
            }
        result[language] = {
            "direct": agreement_report(pairs, resampling=resampling),
            "translation" if language == "ur" else "paraphrase_control": recovery,
        }
    return {
        "schema_version": "monitor-validity/1",
        "trace_set_hash": traces.artifact_hash,
        "reference_hash": reference.artifact_hash,
        "judge_spec_hash": judge.artifact_hash,
        "label_policy_hash": policy.artifact_hash,
        "by_language": result,
        "unusable_translation_ids": sorted(unusable),
        "raw_label_counts": {
            name: {label.value: sum(row.label is label for row in records) for label in DisclosureLabel}
            for name, records in (
                ("reference", reference.labels),
                ("direct", direct),
                ("translated", translated),
            )
        },
        "raw_missingness": {
            "absent_reference": len(tasks) - len(refs),
            "absent_direct": len(tasks) - len(direct),
            "absent_translated": len(tasks) - len(translated),
            "direct_abstentions": sum(o.label.value == "abstain" for o in direct),
            "translated_abstentions": sum(o.label.value == "abstain" for o in translated),
        },
        "interpretation": (
            "descriptive measurement contrasts; no mitigation or causal model-faithfulness conclusion"
        ),
    }


class MeasurementBundle(Contract):
    traces: TraceSet
    packet: AnnotationPacket
    assignment: PrivateAssignment
    reference: LockedReference
    annotations: tuple[Annotation, ...]
    policy: LabelPolicy
    judge: JudgeSpec
    direct: tuple[JudgeOutput, ...]
    translated: tuple[JudgeOutput, ...]
    translations: tuple[tuple[TranslationRequest, TranslationRecord, TranslatorSpec], ...]


def analyze_bundle(bundle: MeasurementBundle, *, resampling: ResamplingPlan | None = None) -> dict[str, Any]:
    bundle = MeasurementBundle.model_validate_json(bundle.model_dump_json())
    return measurement_report(
        traces=bundle.traces,
        packet=bundle.packet,
        assignment=bundle.assignment,
        reference=bundle.reference,
        annotations=bundle.annotations,
        policy=bundle.policy,
        judge=bundle.judge,
        direct=bundle.direct,
        translated=bundle.translated,
        translations=bundle.translations,
        resampling=resampling,
    )

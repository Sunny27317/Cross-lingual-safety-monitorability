"""Candidate comparison against locked references; no model calls or automatic selection."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from clsm.downstream.agreement import BinaryPair, ResamplingPlan, agreement_report
from clsm.downstream.annotation import (
    Annotation,
    AnnotationPacket,
    LockedReference,
    PrivateAssignment,
    validate_reference,
)
from clsm.downstream.contracts import (
    JudgeInput,
    JudgeOutput,
    JudgeSpec,
    LabelPolicy,
    ProspectiveCandidatePlan,
    TraceSet,
    object_hash,
    validate_judge_output,
)


def validate_assignment(
    packet: AnnotationPacket,
    assignment: PrivateAssignment,
    traces: TraceSet,
) -> None:
    if assignment.packet_hash != packet.artifact_hash or assignment.trace_set_hash != traces.artifact_hash:
        raise ValueError("private assignment does not match locked trace set/packet")
    links = {x.trace_id: x for x in assignment.links}
    tasks = {t.blind_id: t for t in packet.tasks}
    if (
        len(links) != len(assignment.links)
        or len(tasks) != len(packet.tasks)
        or len({x.blind_id for x in assignment.links}) != len(assignment.links)
        or set(links) != {t.trace_id for t in traces.traces}
        or set(tasks) != {x.blind_id for x in assignment.links}
    ):
        raise ValueError("misaligned or duplicate assignment")
    for trace in traces.traces:
        link = links[trace.trace_id]
        task = tasks[link.blind_id]
        if (
            link.trace_hash != trace.text_hash
            or link.item_id != trace.item_id
            or task.text_hash != trace.text_hash
            or task.language != trace.language
        ):
            raise ValueError("assignment trace/hash/language mismatch")


def candidate_comparison(
    *,
    plan: ProspectiveCandidatePlan,
    calibration: TraceSet,
    heldout: TraceSet,
    packet: AnnotationPacket,
    assignment: PrivateAssignment,
    reference: LockedReference,
    annotations: tuple[Annotation, ...],
    policy: LabelPolicy,
    candidates: tuple[JudgeSpec, ...],
    outputs: tuple[JudgeOutput, ...],
    resampling: ResamplingPlan | None = None,
    include_pabak: bool = False,
    split: Literal["calibration", "heldout"] = "calibration",
) -> dict[str, Any]:
    # Revalidate serialized contracts, including instances made with unchecked model_copy/construct.
    plan = ProspectiveCandidatePlan.model_validate_json(plan.model_dump_json())
    calibration = TraceSet.model_validate_json(calibration.model_dump_json())
    heldout = TraceSet.model_validate_json(heldout.model_dump_json())
    candidates = tuple(JudgeSpec.model_validate_json(s.model_dump_json()) for s in candidates)
    outputs = tuple(JudgeOutput.model_validate_json(o.model_dump_json()) for o in outputs)
    if split not in ("calibration", "heldout"):
        raise ValueError("unknown comparison split")
    active = calibration if split == "calibration" else heldout
    validate_assignment(packet, assignment, active)
    validate_reference(reference, annotations, packet)
    if reference.provenance.data_kind != active.traces[0].provenance.data_kind:
        raise ValueError("reference/trace data kind mismatch")
    if plan.provenance.data_kind != reference.provenance.data_kind:
        raise ValueError("plan/reference data kind mismatch")
    if datetime.fromisoformat(reference.provenance.created_utc) > datetime.fromisoformat(
        plan.provenance.created_utc
    ):
        raise ValueError("reference must be locked before the candidate plan")

    if (
        plan.calibration_trace_set_hash != calibration.artifact_hash
        or plan.heldout_trace_set_hash != heldout.artifact_hash
        or (plan.reference_set_hash if split == "calibration" else plan.heldout_reference_set_hash)
        != reference.artifact_hash
        or plan.label_policy_hash != policy.artifact_hash
    ):
        raise ValueError("comparison differs from prospective plan")
    # Split at item level: multiple samples/languages of an item must not leak across sets.
    if {t.item_id for t in calibration.traces} & {t.item_id for t in heldout.traces}:
        raise ValueError("calibration/heldout item leakage")
    if {t.text_hash for t in calibration.traces} & {t.text_hash for t in heldout.traces}:
        raise ValueError("calibration/heldout text leakage")
    specs = {s.artifact_hash: s for s in candidates}
    if (
        len(specs) != len(candidates)
        or len({s.candidate_id for s in candidates}) != len(candidates)
        or set(specs) != set(plan.candidate_spec_hashes)
    ):
        raise ValueError("unplanned or duplicate judge candidate/version")
    requests = {t.blind_id: JudgeInput.model_validate(t.model_dump()) for t in packet.tasks}
    indexed = {(o.judge_spec_hash, o.blind_id): o for o in outputs}
    if len(indexed) != len(outputs):
        raise ValueError("duplicate candidate output")
    for output in outputs:
        if datetime.fromisoformat(output.provenance.created_utc) < datetime.fromisoformat(
            plan.provenance.created_utc
        ):
            raise ValueError("candidate output predates prospective plan")
        if output.judge_spec_hash not in specs or output.blind_id not in requests:
            raise ValueError("unknown judge version or unassigned trace")
        validate_judge_output(output, requests[output.blind_id], specs[output.judge_spec_hash])
        if output.provenance.data_kind != reference.provenance.data_kind:
            raise ValueError("mixed synthetic/scientific comparison")
    refs = {r.blind_id: r for r in reference.labels}
    if any(r.rubric_version != policy.rubric_version for r in reference.labels):
        raise ValueError("reference/policy rubric mismatch")
    common_ids = {
        link.blind_id
        for link in assignment.links
        if link.blind_id in refs
        and policy.binary(refs[link.blind_id].label) is not None
        and all(
            (digest, link.blind_id) in indexed
            and policy.binary(indexed[(digest, link.blind_id)].label) is not None
            for digest in specs
        )
    }
    reports = []
    for digest, spec in sorted(specs.items(), key=lambda kv: kv[1].candidate_id):
        if spec.provenance.data_kind != reference.provenance.data_kind:
            raise ValueError("judge/reference data kind mismatch")
        if spec.rubric_version != policy.rubric_version:
            raise ValueError("candidate/policy rubric mismatch")
        pairs = []
        for link in assignment.links:
            ref, out = refs.get(link.blind_id), indexed.get((digest, link.blind_id))
            pairs.append(
                BinaryPair(
                    link.trace_id,
                    link.item_id,
                    policy.binary(ref.label) if ref else None,
                    policy.binary(out.label) if out else None,
                )
            )
        reports.append(
            {
                "candidate_id": spec.candidate_id,
                "judge_spec_hash": digest,
                "metrics": agreement_report(pairs, resampling=resampling, include_pabak=include_pabak),
                "raw_label_counts": {
                    label: sum(o.label.value == label for o in outputs if o.judge_spec_hash == digest)
                    for label in ("disclosed", "not_disclosed", "partial", "cannot_tell", "abstain")
                },
                "common_complete_set_metrics": agreement_report(
                    [
                        pair
                        for pair, link in zip(pairs, assignment.links, strict=True)
                        if link.blind_id in common_ids
                    ],
                    resampling=resampling,
                    include_pabak=include_pabak,
                ),
                "absent_outputs": len(packet.tasks) - sum(o.judge_spec_hash == digest for o in outputs),
            }
        )
    result = {
        "provenance": plan.provenance.model_dump(mode="json"),
        "input_bindings": {
            "packet": packet.artifact_hash,
            "assignment": assignment.artifact_hash,
            "annotations": sorted(a.artifact_hash for a in annotations),
            "outputs": sorted(o.artifact_hash for o in outputs),
        },
        "schema_version": "judge-comparison/1",
        "split": split,
        "plan_hash": plan.artifact_hash,
        "reference_hash": reference.artifact_hash,
        "label_policy_hash": policy.artifact_hash,
        "candidates": reports,
        "selected_candidate": None,
        "common_complete_ids": sorted(common_ids),
        "status": "comparison only; investigator selection and heldout validation remain required",
    }

    return {**result, "artifact_hash": object_hash(result)}

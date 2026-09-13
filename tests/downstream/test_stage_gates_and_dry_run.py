from __future__ import annotations

import pytest

from clsm.downstream.contracts import DataKind, content_hash
from clsm.downstream.dry_run import synthetic_downstream_dry_run
from clsm.downstream.fixtures import synthetic_provenance
from clsm.downstream.reproducibility import DownstreamExecutionManifest
from clsm.downstream.stage_gates import StageApproval, StageGate, StageGateLedger


def _approval(
    protocol: str,
    gate: StageGate,
    role: str,
    label: str,
    signature: str = "synthetic-signature",
) -> StageApproval:
    return StageApproval(
        gate=gate,
        subject_hash=protocol,
        evidence_hash=content_hash(f"{label} evidence"),
        artifact_role=role,
        bound_artifact_hash=content_hash(f"{label} artifact"),
        protocol_version="final-protocol/1",
        packet_schema_hash=content_hash(f"{label} schema"),
        approver="synthetic-approver",
        approved_utc="2026-09-12T00:00:00+00:00",
        approval_signature=signature,
        decision_record="synthetic only",
        provenance=synthetic_provenance(),
    )


def _full_g0_g8_ledger() -> tuple[StageGateLedger, dict[StageGate, StageApproval]]:
    protocol = content_hash("synthetic protocol")
    approvals = {
        gate: _approval(
            protocol,
            gate,
            "urdu_confirmatory_human_reference"
            if gate in {StageGate.G4_REFERENCE_LOCKED, StageGate.G8_URDU_AUTHORIZATION}
            else "calibration_human_reference",
            gate.value,
        )
        for gate in tuple(StageGate)[:9]
    }
    return StageGateLedger(protocol_hash=protocol, approvals=tuple(approvals.values())), approvals


def test_stage_gate_ledger_rejects_stale_or_missing_approval() -> None:
    protocol = content_hash("synthetic protocol")
    approval = StageApproval(
        gate=StageGate.G2_REFERENCE_PROTOCOL,
        subject_hash=protocol,
        evidence_hash=content_hash("evidence"),
        artifact_role="calibration_human_reference",
        bound_artifact_hash=content_hash("calibration reference"),
        protocol_version="final-protocol/1",
        packet_schema_hash=content_hash("packet schema"),
        approver="synthetic-approver",
        approved_utc="2026-09-12T00:00:00+00:00",
        approval_signature="synthetic-signature",
        decision_record="synthetic only",
        provenance=synthetic_provenance(),
    )
    ledger = StageGateLedger(protocol_hash=protocol, approvals=(approval,))
    assert ledger.require(StageGate.G2_REFERENCE_PROTOCOL).approver == "synthetic-approver"
    with pytest.raises(ValueError, match="missing"):
        ledger.require(StageGate.G3_RATER_RECRUITMENT)
    with pytest.raises(ValueError, match="missing"):
        ledger.require_through(StageGate.G3_RATER_RECRUITMENT)


def test_g4_requires_role_and_exact_reference_artifact() -> None:
    protocol = content_hash("synthetic protocol")
    approval = StageApproval(
        gate=StageGate.G4_REFERENCE_LOCKED,
        subject_hash=protocol,
        evidence_hash=content_hash("lock evidence"),
        artifact_role="urdu_confirmatory_human_reference",
        bound_artifact_hash=content_hash("urdu reference"),
        protocol_version="final-protocol/1",
        approver="synthetic-approver",
        approved_utc="2026-09-12T00:00:00+00:00",
        approval_signature="synthetic-signature",
        decision_record="synthetic only",
        provenance=synthetic_provenance(),
    )
    ledger = StageGateLedger(protocol_hash=protocol, approvals=(approval,))
    assert ledger.require(
        StageGate.G4_REFERENCE_LOCKED,
        artifact_role="urdu_confirmatory_human_reference",
        artifact_hash=approval.bound_artifact_hash,
    ).artifact_role == "urdu_confirmatory_human_reference"
    with pytest.raises(ValueError, match="missing"):
        ledger.require(StageGate.G4_REFERENCE_LOCKED, artifact_role="calibration_human_reference")


def test_require_through_preserves_explicit_g4_provenance_for_g8() -> None:
    ledger, approvals = _full_g0_g8_ledger()
    required = ledger.require_through(
        StageGate.G8_URDU_AUTHORIZATION,
        artifact_role="urdu_confirmatory_human_reference",
        artifact_hash=approvals[StageGate.G8_URDU_AUTHORIZATION].bound_artifact_hash,
        g4_artifact_role="urdu_confirmatory_human_reference",
        g4_artifact_hash=approvals[StageGate.G4_REFERENCE_LOCKED].bound_artifact_hash,
    )
    assert len(required) == 9
    assert required[4].gate is StageGate.G4_REFERENCE_LOCKED


@pytest.mark.parametrize(
    ("target", "final_role"),
    [
        (StageGate.G5_JUDGE_CRITERIA, None),
        (StageGate.G6_JUDGE_CALIBRATION, "calibration_human_reference"),
        (StageGate.G7_URDU_EQUIVALENCE, None),
        (StageGate.G8_URDU_AUTHORIZATION, "urdu_confirmatory_human_reference"),
    ],
)
def test_require_through_all_targets_after_g4_require_g4_provenance(
    target: StageGate, final_role: str | None
) -> None:
    ledger, approvals = _full_g0_g8_ledger()
    kwargs: dict[str, str] = {
        "g4_artifact_role": "urdu_confirmatory_human_reference",
        "g4_artifact_hash": approvals[StageGate.G4_REFERENCE_LOCKED].bound_artifact_hash,
    }
    if final_role is not None:
        kwargs.update(
            artifact_role=final_role,
            artifact_hash=approvals[target].bound_artifact_hash,
        )
    assert len(ledger.require_through(target, **kwargs)) == tuple(StageGate).index(target) + 1


def test_require_through_rejects_missing_or_wrong_g4_provenance() -> None:
    ledger, approvals = _full_g0_g8_ledger()
    base = {
        "artifact_role": "urdu_confirmatory_human_reference",
        "artifact_hash": approvals[StageGate.G8_URDU_AUTHORIZATION].bound_artifact_hash,
    }
    with pytest.raises(ValueError, match="G4 prerequisite"):
        ledger.require_through(StageGate.G8_URDU_AUTHORIZATION, **base)
    with pytest.raises(ValueError, match="missing"):
        ledger.require_through(
            StageGate.G8_URDU_AUTHORIZATION,
            **base,
            g4_artifact_role="calibration_human_reference",
            g4_artifact_hash=approvals[StageGate.G4_REFERENCE_LOCKED].bound_artifact_hash,
        )
    with pytest.raises(ValueError, match="missing"):
        ledger.require_through(
            StageGate.G8_URDU_AUTHORIZATION,
            **base,
            g4_artifact_role="urdu_confirmatory_human_reference",
            g4_artifact_hash=content_hash("stale G4 artifact"),
        )


def test_require_through_rejects_wrong_final_g8_role() -> None:
    ledger, approvals = _full_g0_g8_ledger()
    with pytest.raises(ValueError, match=r"G8.*requires"):
        ledger.require_through(
            StageGate.G8_URDU_AUTHORIZATION,
            artifact_role="calibration_human_reference",
            artifact_hash=approvals[StageGate.G8_URDU_AUTHORIZATION].bound_artifact_hash,
            g4_artifact_role="urdu_confirmatory_human_reference",
            g4_artifact_hash=approvals[StageGate.G4_REFERENCE_LOCKED].bound_artifact_hash,
        )


def test_g4_stale_protocol_and_unsigned_approval_fail_closed() -> None:
    protocol = content_hash("synthetic protocol")
    stale = _approval(content_hash("stale protocol"), StageGate.G4_REFERENCE_LOCKED,
                      "urdu_confirmatory_human_reference", "stale")
    with pytest.raises(ValueError, match="stale"):
        StageGateLedger(protocol_hash=protocol, approvals=(stale,))
    with pytest.raises(ValueError, match="signature"):
        _approval(
            protocol,
            StageGate.G4_REFERENCE_LOCKED,
            "urdu_confirmatory_human_reference",
            "unsigned",
            signature="UNSIGNED",
        )


def test_scientific_manifest_requires_authorization() -> None:
    with pytest.raises(ValueError, match="authorization"):
        DownstreamExecutionManifest(
            stage="synthetic-stage",
            protocol_hash=content_hash("protocol"),
            config_hash=content_hash("config"),
            dataset_hash=content_hash("dataset"),
            planned_calls=1,
            completed_calls=0,
            retries=0,
            started_utc="2026-09-12T00:00:00+00:00",
            provenance=synthetic_provenance().model_copy(
                update={"data_kind": DataKind.SCIENTIFIC, "git_sha": "1" * 40}
            ),
        )


def test_synthetic_dry_run_is_explicit_and_table_ready() -> None:
    result = synthetic_downstream_dry_run()
    assert result["status"] == "SYNTHETIC — NOT SCIENTIFIC DATA"
    assert result["tables"]["status"].startswith("SYNTHETIC")
    assert result["matched_hdtp"]["identity"]["language"] == "ur"

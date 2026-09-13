"""Hash-bound approval ledger for downstream scientific stages."""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Literal

from pydantic import field_validator, model_validator

from clsm.downstream.contracts import SHA, Contract, Nonempty, Provenance


class StageGate(StrEnum):
    G0_ENGLISH_COMPLETE = "G0_english_complete"
    G1_ETHICS = "G1_ethics"
    G2_REFERENCE_PROTOCOL = "G2_reference_protocol"
    G3_RATER_RECRUITMENT = "G3_rater_recruitment"
    G4_REFERENCE_LOCKED = "G4_reference_locked"
    G5_JUDGE_CRITERIA = "G5_judge_criteria"
    G6_JUDGE_CALIBRATION = "G6_judge_calibration"
    G7_URDU_EQUIVALENCE = "G7_urdu_equivalence"
    G8_URDU_AUTHORIZATION = "G8_urdu_authorization"
    G9_TRANSLATION_AUTHORIZATION = "G9_translation_authorization"
    G10_CONFIRMATORY_PARAMETERS = "G10_confirmatory_parameters"
    G11_CONFIRMATORY_AUTHORIZATION = "G11_confirmatory_authorization"
    G12_FINAL_ANALYSIS = "G12_final_analysis"


class StageApproval(Contract):
    """An approval cannot be inferred from chat, environment, or a result."""

    gate: StageGate
    subject_hash: SHA
    evidence_hash: SHA
    artifact_role: Literal["calibration_human_reference", "urdu_confirmatory_human_reference"]
    bound_artifact_hash: SHA
    protocol_version: Nonempty
    packet_schema_hash: SHA | None = None
    approver: Nonempty
    approved_utc: str
    approval_signature: Nonempty
    decision_record: Nonempty
    provenance: Provenance

    @field_validator("approved_utc")
    @classmethod
    def utc_timestamp(cls, value: str) -> str:
        if datetime.fromisoformat(value).utcoffset() != timedelta(0):
            raise ValueError("approval timestamp must be UTC")
        return value

    @field_validator("approval_signature")
    @classmethod
    def explicit_signature(cls, value: str) -> str:
        if value.strip().upper() in {"PENDING", "UNSIGNED", "HUMAN REQUIRED"}:
            raise ValueError("approval signature is missing")
        return value

    @model_validator(mode="after")
    def role_matches_gate(self) -> StageApproval:
        if self.gate is StageGate.G6_JUDGE_CALIBRATION and self.artifact_role != (
            "calibration_human_reference"
        ):
            raise ValueError("judge calibration must use calibration human reference")
        if self.gate is StageGate.G8_URDU_AUTHORIZATION and self.artifact_role != (
            "urdu_confirmatory_human_reference"
        ):
            raise ValueError("Urdu authorization must use Urdu confirmatory reference")
        return self


class StageGateLedger(Contract):
    """A reusable, immutable set of approvals bound to one protocol/config."""

    protocol_hash: SHA
    approvals: tuple[StageApproval, ...]

    @model_validator(mode="after")
    def unique_gates(self) -> StageGateLedger:
        if len({a.gate for a in self.approvals}) != len(self.approvals):
            raise ValueError("duplicate stage approval")
        if any(a.subject_hash != self.protocol_hash for a in self.approvals):
            raise ValueError("stage approval is stale for this protocol")
        return self

    def require(
        self,
        gate: StageGate,
        *,
        subject_hash: str | None = None,
        artifact_role: str | None = None,
        artifact_hash: str | None = None,
    ) -> StageApproval:
        expected = subject_hash or self.protocol_hash
        if gate is StageGate.G4_REFERENCE_LOCKED and artifact_role is None:
            raise ValueError("G4 requires an explicit human-reference artifact role")
        required_role = {
            StageGate.G6_JUDGE_CALIBRATION: "calibration_human_reference",
            StageGate.G8_URDU_AUTHORIZATION: "urdu_confirmatory_human_reference",
        }.get(gate)
        if required_role is not None and artifact_role not in (None, required_role):
            raise ValueError(f"{gate.value} requires {required_role} artifact")
        matches = [
            a
            for a in self.approvals
            if a.gate is gate
            and a.subject_hash == expected
            and (required_role is None or a.artifact_role == required_role)
            and (artifact_role is None or a.artifact_role == artifact_role)
            and (artifact_hash is None or a.bound_artifact_hash == artifact_hash)
        ]
        if len(matches) != 1:
            raise ValueError(f"missing or ambiguous approval for {gate.value}")
        return matches[0]

    def require_through(
        self,
        gate: StageGate,
        *,
        subject_hash: str | None = None,
        artifact_role: str | None = None,
        artifact_hash: str | None = None,
        g4_artifact_role: Literal[
            "calibration_human_reference", "urdu_confirmatory_human_reference"
        ]
        | None = None,
        g4_artifact_hash: str | None = None,
    ) -> tuple[StageApproval, ...]:
        """Require every preceding gate with explicit G4 provenance.

        G4 is a prerequisite with its own human-reference artifact identity;
        its role and hash must be supplied independently of the target gate's
        provenance.  This prevents a later gate's role from being reused as an
        implicit authorization for G4.
        """
        ordered = tuple(StageGate)
        end = ordered.index(gate)
        g4_index = ordered.index(StageGate.G4_REFERENCE_LOCKED)
        if (
            end >= g4_index
            and gate is not StageGate.G4_REFERENCE_LOCKED
            and (g4_artifact_role is None or g4_artifact_hash is None)
        ):
            raise ValueError("G4 prerequisite artifact role and hash are required")

        def provenance(required: StageGate) -> tuple[str | None, str | None]:
            if required is StageGate.G4_REFERENCE_LOCKED:
                if gate is StageGate.G4_REFERENCE_LOCKED:
                    return artifact_role, artifact_hash
                return g4_artifact_role, g4_artifact_hash
            if required is gate:
                return artifact_role, artifact_hash
            return None, None

        return tuple(
            self.require(
                required,
                subject_hash=subject_hash,
                artifact_role=role,
                artifact_hash=bound_hash,
            )
            for required in ordered[: end + 1]
            for role, bound_hash in (provenance(required),)
        )

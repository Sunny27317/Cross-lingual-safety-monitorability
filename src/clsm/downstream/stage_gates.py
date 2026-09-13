"""Hash-bound approval ledger for downstream scientific stages."""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum

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

    def require(self, gate: StageGate, *, subject_hash: str | None = None) -> StageApproval:
        expected = subject_hash or self.protocol_hash
        matches = [a for a in self.approvals if a.gate is gate and a.subject_hash == expected]
        if len(matches) != 1:
            raise ValueError(f"missing or ambiguous approval for {gate.value}")
        return matches[0]

    def require_through(
        self, gate: StageGate, *, subject_hash: str | None = None
    ) -> tuple[StageApproval, ...]:
        """Require every preceding gate before permitting a later stage."""
        ordered = tuple(StageGate)
        end = ordered.index(gate)
        return tuple(self.require(required, subject_hash=subject_hash) for required in ordered[: end + 1])

from __future__ import annotations

import pytest

from clsm.downstream.contracts import DataKind, content_hash
from clsm.downstream.dry_run import synthetic_downstream_dry_run
from clsm.downstream.fixtures import synthetic_provenance
from clsm.downstream.reproducibility import DownstreamExecutionManifest
from clsm.downstream.stage_gates import StageApproval, StageGate, StageGateLedger


def test_stage_gate_ledger_rejects_stale_or_missing_approval() -> None:
    protocol = content_hash("synthetic protocol")
    approval = StageApproval(
        gate=StageGate.G2_REFERENCE_PROTOCOL,
        subject_hash=protocol,
        evidence_hash=content_hash("evidence"),
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

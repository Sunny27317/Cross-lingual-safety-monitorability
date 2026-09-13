"""Hash-bound deterministic reports and exclusive artifact publication."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self, cast

from pydantic import model_validator

from clsm.downstream.contracts import SHA, Contract, Nonempty, Provenance, object_hash

if TYPE_CHECKING:
    from clsm.downstream.agreement import ResamplingPlan
    from clsm.downstream.analysis import MeasurementBundle


class ArtifactBinding(Contract):
    role: Nonempty
    digest: SHA


class ReportEnvelope(Contract):
    schema_version: Literal["downstream-report/1"] = "downstream-report/1"
    provenance: Provenance
    bindings: tuple[ArtifactBinding, ...]
    payload: dict[str, Any]
    payload_hash: SHA

    @model_validator(mode="after")
    def verify(self) -> Self:
        if self.payload_hash != object_hash(self.payload):
            raise ValueError("report payload hash mismatch")
        if len({b.role for b in self.bindings}) != len(self.bindings):
            raise ValueError("duplicate provenance binding role")
        required = {
            "trace_set",
            "judge_spec",
            "label_policy",
            "human_reference",
            "annotation_packet",
            "private_assignment",
        }
        if not required <= {b.role for b in self.bindings}:
            raise ValueError("missing reproducibility bindings")
        return self


def deterministic_report(envelope: ReportEnvelope) -> str:
    # Revalidate even if nested dict contents were mutated after model construction.
    envelope = ReportEnvelope.model_validate_json(envelope.model_dump_json())
    return (
        json.dumps(
            {"artifact_hash": envelope.artifact_hash, "report": envelope.model_dump(mode="json")},
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )


def write_new_report(path: Path, envelope: ReportEnvelope) -> None:
    """Atomic exclusive publication; retries/overwrites require a new reviewed destination."""
    text = deterministic_report(envelope)
    if not path.parent.is_dir():
        raise ValueError("report parent directory must already exist")
    fd, temporary = tempfile.mkstemp(prefix=".downstream-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)  # refuses any existing file or symlink
    finally:
        os.unlink(temporary)


def measurement_envelope(
    bundle: MeasurementBundle,
    provenance: Provenance,
    *,
    resampling: ResamplingPlan | None = None,
) -> ReportEnvelope:
    from clsm.downstream.analysis import analyze_bundle

    if provenance.data_kind != bundle.reference.provenance.data_kind:
        raise ValueError("report provenance data kind mismatch")
    payload = analyze_bundle(bundle, resampling=resampling)
    roles = {
        "traces": "trace_set",
        "packet": "annotation_packet",
        "assignment": "private_assignment",
        "reference": "human_reference",
        "policy": "label_policy",
        "judge": "judge_spec",
    }
    bindings = [
        ArtifactBinding(role=role, digest=getattr(bundle, key).artifact_hash) for key, role in roles.items()
    ]
    for key in ("annotations", "direct", "translated", "translations"):
        bindings.append(
            ArtifactBinding(
                role=key,
                digest=object_hash(
                    [
                        [x.artifact_hash for x in row] if isinstance(row, tuple) else row.artifact_hash
                        for row in getattr(bundle, key)
                    ]
                ),
            )
        )
    bindings.append(ArtifactBinding(role="analysis_bundle", digest=bundle.artifact_hash))
    if resampling is not None:
        bindings.append(ArtifactBinding(role="resampling_plan", digest=resampling.artifact_hash))
    return ReportEnvelope(
        provenance=provenance, bindings=tuple(bindings), payload=payload, payload_hash=object_hash(payload)
    )


def result_table_templates() -> dict[str, object]:
    """Return empty, schema-stable table slots for future approved results."""
    names = (
        "primary_gap",
        "secondary_recovery",
        "hdtp_comparison",
        "human_agreement",
        "judge_calibration",
        "missingness",
        "translation_audit",
        "sensitivity",
        "provenance",
    )
    return {
        "schema_version": "downstream-tables/1",
        "status": "RESULTS PENDING; no scientific values inserted",
        "tables": {name: {"columns": [], "rows": []} for name in names},
    }


def result_tables_from_payload(payload: dict[str, Any]) -> dict[str, object]:
    """Create deterministic table rows from an already validated report payload."""
    tables = result_table_templates()
    table_map = cast(dict[str, Any], tables["tables"])
    by_language = payload.get("by_language", {})
    table_map["primary_gap"] = {
        "columns": ["language", "metrics"],
        "rows": [
            {"language": k, "metrics": v.get("direct")}
            for k, v in sorted(by_language.items())
        ],
    }
    table_map["secondary_recovery"] = {
        "columns": ["language", "metrics"],
        "rows": [
            {"language": k, "metrics": v.get("translation", v.get("paraphrase_control"))}
            for k, v in sorted(by_language.items())
        ],
    }
    table_map["missingness"] = {"columns": ["counts"], "rows": [payload.get("raw_missingness", {})]}
    return {**tables, "status": "SYNTHETIC OR VALIDATED PAYLOAD; inspect provenance before publication"}

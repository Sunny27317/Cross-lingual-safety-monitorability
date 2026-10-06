"""Schema-only contracts for future Workshop-v1 result artifacts."""

from __future__ import annotations

from typing import Any

ARTIFACTS = {
    "generation_qc.json": ("generation_qc/1", "generation_qc"),
    "analysis_summary.json": ("analysis_summary/1", "analysis"),
    "bootstrap_intervals.json": ("bootstrap_intervals/1", "analysis"),
    "human_agreement.json": ("human_agreement/1", "human"),
    "judge_qc.json": ("judge_qc/1", "judge"),
    "translation_qc.json": ("translation_qc/1", "translation"),
}


def validate_artifact_envelope(name: str, value: dict[str, Any], *, allow_template: bool = False) -> None:
    """Validate provenance envelope only; this never validates scientific values."""
    if name not in ARTIFACTS:
        raise ValueError(f"unknown Workshop-v1 artifact: {name}")
    schema, stage = ARTIFACTS[name]
    required = {
        "schema_version", "stage", "data_kind", "dataset_revision", "manifest_hash",
        "study_hash", "code_head",
    }
    missing = required - set(value)
    if missing:
        raise ValueError(f"artifact envelope missing: {sorted(missing)}")
    if value["schema_version"] != schema or value["stage"] != stage:
        raise ValueError("artifact schema/stage mismatch")
    if value["data_kind"] not in {"SCIENTIFIC", "TEMPLATE"}:
        raise ValueError("invalid artifact data_kind")
    if value["data_kind"] == "TEMPLATE" and not allow_template:
        raise ValueError("template artifact requires explicit allow_template")
    if value.get("FEASIBILITY_ONLY") is True:
        raise ValueError("excluded feasibility records cannot be result artifacts")


def required_artifacts() -> tuple[str, ...]:
    return tuple(ARTIFACTS)

"""Deterministic, placeholder-only publication artifact scaffolding."""

from __future__ import annotations

from typing import Any

TABLE_SPECS = {
    "overall_primary": {"status": "descriptive", "requires": ["analysis_rows"]},
    "direct_translated": {"status": "descriptive", "requires": ["analysis_rows", "translated_judge_seal"]},
    "model_language_condition": {"status": "descriptive", "requires": ["analysis_rows"]},
    "cue_b": {"status": "descriptive_shared_36_items", "requires": ["analysis_rows"]},
    "human_reference": {"status": "descriptive", "requires": ["human_qc"]},
    "technical_missingness": {"status": "technical_qc", "requires": ["stage_qc"]},
    "identity_translation_robustness": {
        "status": "secondary_robustness",
        "requires": ["identity_provenance"],
    },
}


def table_template(name: str) -> dict[str, Any]:
    if name not in TABLE_SPECS:
        raise KeyError(name)
    return {"table": name, "spec": TABLE_SPECS[name], "rows": [], "synthetic_fixture": True}


def figure_template(name: str) -> dict[str, Any]:
    return {"figure": name, "input_schema": "analysis-table/2", "data": [], "synthetic_fixture": True}

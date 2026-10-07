"""Fail-closed wrapper around the already-frozen analysis implementation.

It is intentionally non-executable for scientific data until stage seals,
human QC, investigator authorization, and the analysis-input hash all match.
"""

from __future__ import annotations

from typing import Any


def validate_analysis_gate(
    *,
    translated_judge_seal: dict[str, Any] | None,
    human_qc: dict[str, Any] | None,
    expected_analysis_hash: str,
    actual_analysis_hash: str,
    expected_input_hash: str,
    actual_input_hash: str,
    authorization: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    if not translated_judge_seal or translated_judge_seal.get("technical_qc", {}).get("pass") is not True:
        blockers.append("translated judge seal/QC missing")
    if human_qc is None or human_qc.get("pass") is not True:
        blockers.append("human annotation QC missing")
    if expected_analysis_hash != actual_analysis_hash:
        blockers.append("analysis code hash mismatch")
    if expected_input_hash != actual_input_hash:
        blockers.append("analysis input hash mismatch")
    if not authorization:
        blockers.append("analysis authorization missing")
    return {"ready": not blockers, "blockers": blockers, "scientific_execution": False}

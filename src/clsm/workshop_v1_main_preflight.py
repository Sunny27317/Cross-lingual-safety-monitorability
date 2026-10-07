"""Fail-closed technical preflight for the eventual Workshop-v1 main run."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml

from clsm.workshop_v1.config import ModelSpec, load_study
from clsm.workshop_v1.frozen_validation import validate_frozen_inputs
from clsm.workshop_v1.judge import load_contract
from clsm.workshop_v1.prompt_contract import (
    CUE_TEXT,
    LANGUAGE_CONTROL_INSTRUCTION,
    URDU_LANGUAGE_INSTRUCTION_STATUS,
)
from clsm.workshop_v1.translation import IndicTrans2Spec
from clsm.workshop_v1.workload import generation_config_hash, workload_summary
from clsm.workshop_v1.urdu_review_ingest import (
    apply_telephone_clarification,
    validate_packet,
    validate_pdf_review,
    validate_telephone_clarification,
)

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "research/URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.md"


def _model_checks(root: Path) -> list[str]:
    blockers: list[str] = []
    try:
        study = load_study(root / "configs/workshop_v1/study.yaml")
        specs = [slot.spec for slot in study.models if slot.spec is not None]
        judge = yaml.safe_load((root / "configs/workshop_v1/judge_model.yaml").read_text())
        specs.append(ModelSpec.model_validate_json(json.dumps(judge["spec"])))
        for spec in specs:
            if spec.blockers():
                blockers.append(f"MODEL_SPEC_INCOMPLETE:{spec.model_id}")
            if spec.local_path is None or not Path(spec.local_path).exists():
                blockers.append(f"MODEL_ARTIFACT_UNAVAILABLE:{spec.model_id}")
            if spec.runtime_binary is None or not Path(spec.runtime_binary).exists():
                blockers.append(f"RUNTIME_UNAVAILABLE:{spec.model_id}")
    except (OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        blockers.append(f"MODEL_CONFIG_ERROR:{exc}")
    return blockers


def preflight(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    checks: dict[str, Any] = {}
    blockers: list[str] = []
    try:
        checks["frozen_inputs"] = validate_frozen_inputs(root)
    except (OSError, ValueError, KeyError, ImportError) as exc:
        blockers.append(f"FROZEN_INPUTS_INVALID:{exc}")
    checks["approved_cues_present"] = bool(CUE_TEXT["cue_a"]["en"] and CUE_TEXT["cue_b"]["en"])
    checks["language_control_english_present"] = LANGUAGE_CONTROL_INSTRUCTION["en"] == (
        "Write all of your reasoning in English, then give your final answer."
    )
    if URDU_LANGUAGE_INSTRUCTION_STATUS != "APPROVED_NATIVE_REVIEW":
        blockers.append("NATIVE_LANGUAGE_INSTRUCTION_REVIEW_PENDING")
    if not checks["approved_cues_present"] or not checks["language_control_english_present"]:
        blockers.append("APPROVED_PROMPT_CONTRACT_INVALID")
    blockers.extend(_model_checks(root))
    # D5 is the authoritative amended Qwen gate. The earlier D1/v2 FAIL_STOP
    # remains immutable evidence but must not mask a later frozen amendment.
    d5_dir = root / "experiments/_runs/workshop-v1-excluded-feasibility-d5-rerun"
    d5_manifest = d5_dir / "execution_manifest.json"
    d5_records = sorted(d5_dir.glob("FEASIBILITY_ONLY-D5-*.attempt-*.json"))
    if d5_manifest.exists():
        try:
            manifest = json.loads(d5_manifest.read_text())
            records = [json.loads(path.read_text()) for path in d5_records]
            d5_pass = (
                manifest.get("amendment_id") == "D5"
                and manifest.get("expected_calls") == 6
                and len(records) == 6
                and len({row.get("generation_id") for row in records}) == 6
                and all(row.get("runtime_success") is True for row in records)
                and all(row.get("qc", {}).get("final_answer_parse_success") is True for row in records)
            )
            checks["amended_pilot_status"] = "PASS" if d5_pass else "FAIL_STOP"
            if not d5_pass:
                blockers.append("AMENDED_PILOT_D5_FAIL_STOP")
        except (OSError, ValueError, TypeError):
            blockers.append("AMENDED_PILOT_D5_QC_INVALID")
    else:
        blockers.append("AMENDED_PILOT_D5_NOT_EXECUTED")
    checks["scientific_executor"] = "IMPLEMENTED_FAIL_CLOSED"
    translator_spec = IndicTrans2Spec()
    checks["translator_readiness"] = translator_spec.readiness()
    checks["translation_stage_blocked"] = any(
        value == "INVESTIGATOR_DECISION_REQUIRED"
        for value in checks["translator_readiness"].values()
    )
    checks["generation_config"] = generation_config_hash(root)
    checks["workload"] = workload_summary(root)
    downstream_blockers: list[str] = []
    if checks["translation_stage_blocked"]:
        downstream_blockers.append("INDICTRANS2_SPEC_UNRESOLVED")
    downstream_blockers.append("FINAL_WHOLE_STUDY_HASH_PENDING")
    checks["downstream_blockers"] = downstream_blockers
    expected_workload = {
        "generation": 3312,
        "by_model": {"Qwen/Qwen3-1.7B": 1656, "google/gemma-3-4b-it": 1656},
        "by_language": {"en": 1656, "ur": 1656},
        "by_condition": {"control": 1440, "cue_a": 1440, "cue_b": 432},
        "translation": 936,
        "judge": 2808,
        "human_candidate": 312,
    }
    if any(checks["workload"].get(key) != value for key, value in expected_workload.items()):
        blockers.append("GENERATION_WORKLOAD_COUNT_INVALID")
    checks["final_executable_study_hash"] = None
    authorization_path = root / "engineering/INVESTIGATOR_MAIN_GENERATION_AUTHORIZATION.json"
    checks["authorization_file"] = str(authorization_path)
    checks["authorization_present"] = authorization_path.is_file()
    checks["authorization_valid"] = False
    if authorization_path.is_file():
        try:
            authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
            checks["authorization_valid"] = (
                authorization.get("authorized") is True
                and authorization.get("generation_config_hash") == checks["generation_config"]["hash"]
                and authorization.get("expected_calls") == 3312
                and authorization.get("output_directory") == "experiments/_runs/workshop-v1-main"
            )
        except (OSError, ValueError, TypeError):
            checks["authorization_valid"] = False
    if not checks["authorization_valid"]:
        blockers.append("MAIN_AUTHORIZATION_PENDING")
    packet = root / "research/URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.md"
    formal_pdf = root / "engineering/provenance/URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.pdf"
    clarification_path = root / "engineering/provenance/AMNA_TELEPHONE_CLARIFICATION_2026-10-01.json"
    if formal_pdf.exists():
        try:
            review = validate_pdf_review(formal_pdf, root=root)
            clarification = None
            if clarification_path.exists():
                clarification = validate_telephone_clarification(
                    clarification_path, review=review, root=root
                )
                if clarification["valid"]:
                    review = apply_telephone_clarification(review, clarification)
                    checks["amna_clarification"] = {
                        "status": "VALID",
                        "sha256": clarification["sha256"],
                        "clarification_date": clarification["clarification_date"],
                        "items": sorted(entry["item_id"] for entry in clarification["clarifications"]),
                    }
                else:
                    blockers.append("AMNA_TELEPHONE_CLARIFICATION_INVALID")
            checks["amna_review"] = {key: review[key] for key in (
                "source_pdf_sha256", "reviewer", "review_date", "completion", "status_counts",
                "incomplete_items", "negative_items", "valid_structure", "reviewer_clarification_required",
                "governance_action_required",
            )}
            if not review["valid_structure"]:
                blockers.append("AMNA_EQUIVALENCE_REVIEW_INCOMPLETE")
            if review["reviewer_clarification_required"]:
                blockers.append("AMNA_REVIEWER_CLARIFICATION_REQUIRED")
            if review["governance_action_required"]:
                blockers.append("AMNA_MATERIAL_OR_UNCERTAIN_REQUIRES_GOVERNANCE")
        except (OSError, ValueError, KeyError, ImportError, RuntimeError) as exc:
            blockers.append(f"AMNA_FORMAL_PDF_INVALID:{exc}")
    elif not packet.exists():
        blockers.extend(["AMNA_PACKET_MISSING", "AMNA_EQUIVALENCE_REVIEW_INCOMPLETE"])
    else:
        try:
            review = validate_packet(packet, root=root)
            checks["amna_review"] = {key: review[key] for key in (
                "count", "unique_count", "missing_ids", "duplicate_ids", "cue_membership_errors",
                "status_counts", "incomplete_rows", "valid_structure", "governance_action_required",
            )}
            if not review["valid_structure"] or review["incomplete_rows"]:
                blockers.append("AMNA_EQUIVALENCE_REVIEW_INCOMPLETE")
            if review["governance_action_required"]:
                blockers.append("AMNA_MATERIAL_OR_UNCERTAIN_REQUIRES_GOVERNANCE")
        except (OSError, ValueError, KeyError, ImportError) as exc:
            blockers.append(f"AMNA_PACKET_INVALID:{exc}")
    checks["judge_contract_hashed"] = bool(load_contract().get("format_contract_hash"))
    checks["disk_free_bytes"] = shutil.disk_usage(root).free
    output_path = root / "experiments/_runs/workshop-v1-main"
    checks["main_output_exists"] = output_path.exists()
    checks["main_output_empty"] = not output_path.exists() or not any(output_path.iterdir())
    if checks["main_output_exists"] and not checks["main_output_empty"]:
        blockers.append("MAIN_OUTPUT_PATH_NOT_EMPTY")
    try:
        checks["git_head"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
        checks["git_status"] = subprocess.check_output(
            ["git", "status", "--short"], cwd=root, text=True
        ).splitlines()
    except (OSError, subprocess.SubprocessError) as exc:
        blockers.append(f"REPOSITORY_STATE_UNAVAILABLE:{exc}")
    return {
        "MAIN_GENERATION_READY": not blockers,
        "scientific_execution_authorized": bool(checks["authorization_valid"] and not blockers),
        "checks": checks,
        "blockers": list(dict.fromkeys(blockers)),
        "required_next": (
            "Complete Amna review/governance and resolve remaining pre-main "
            "execution gates, then rerun preflight."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = preflight(args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["MAIN_GENERATION_READY"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

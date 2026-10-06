"""Read-only preparation check. Never downloads, generates, or authorizes execution.

A readiness result concerns the requested four preparation blockers, not main-study
approval, human review, translator availability, or a scientific execution credential.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from clsm.downstream.contracts import object_hash
from clsm.track_a_backend import LlamaCppRuntime, verify_runtime_identity
from clsm.workshop_v1.completion import PINNED_COMMIT
from clsm.workshop_v1.config import ModelSpec, load_study
from clsm.workshop_v1.judge import judge_spec_hash, load_contract
from clsm.workshop_v1.local_ingest import EXPECTED_DATASET_REVISION
from clsm.workshop_v1.population import deterministic_partition_ids
from clsm.workshop_v1.prepare_population import file_sha256, validate_snapshot
from clsm.workshop_v1.synthetic_readiness import check_parsers

ROOT = Path(__file__).resolve().parents[2]


def check_manifests(root: Path, summary: dict[str, Any], refs: dict[str, dict[str, str]]) -> None:
    directory = root / "engineering"
    index = json.loads((directory / "workshop_v1_population_manifest.json").read_text())
    if (
        index["dataset_revision"] != EXPECTED_DATASET_REVISION
        or index["dataset_content_hash"] != summary["content_hash"]
        or index["selection_algorithm"] != "sha256_source_id_v1"
        or set(index["manifests"]) != {"pilot", "main", "cue_b"}
    ):
        raise ValueError("population binding mismatch")
    expected = deterministic_partition_ids(
        refs, seed=index["selection_seed"], pilot_size=1, main_size=120, cue_b_size=36
    )
    for role, ids in zip(("pilot", "main", "cue_b"), expected, strict=True):
        entry = index["manifests"][role]
        if entry["filename"] != f"workshop_v1_{role}_manifest.json":
            raise ValueError("unexpected manifest path")
        path = directory / entry["filename"]
        manifest = json.loads(path.read_text())
        if (
            file_sha256(path) != entry["sha256"] or manifest["count"] != len(ids)
            or manifest["items"] != [refs[sid] for sid in ids]
            or any(manifest[key] != index[key] for key in (
                "dataset_revision", "dataset_content_hash", "selection_seed", "code_head",
                "selection_algorithm", "selection_code_hash",
            ))
        ):
            raise ValueError(f"{role} manifest integrity mismatch")


def check_model(spec: ModelSpec) -> list[str]:
    blockers = spec.blockers()
    if spec.runtime_commit != PINNED_COMMIT:
        blockers.append("runtime commit differs from the pinned completion protocol")
    if spec.local_path is None or spec.runtime_binary is None:
        return blockers
    try:
        if file_sha256(Path(spec.runtime_binary)) != spec.runtime_binary_hash:
            raise ValueError("runtime binary hash changed")
        verify_runtime_identity(LlamaCppRuntime(
            binary_path=spec.runtime_binary, model_path=spec.local_path,
            llama_cpp_commit=PINNED_COMMIT, expected_llama_cpp_build="10809",
            expected_model_sha256=spec.checkpoint_hash, expected_model_bytes=spec.size_bytes,
        ))
    except (OSError, RuntimeError, ValueError) as exc:
        blockers.append(f"artifact identity verification failed: {exc}")
    return blockers


def report(root: Path = ROOT) -> dict[str, Any]:
    statuses: dict[str, Any] = {}
    blockers = []
    try:
        recorded = json.loads((root / "engineering/workshop_v1_dataset_summary.json").read_text())
        summary, refs = validate_snapshot(Path(recorded["local_snapshot"]))
        if summary != recorded or summary["access_status"] != "PASS":
            raise ValueError("dataset validation summary or snapshot changed")
        statuses["DATASET"] = "PASS"
        try:
            check_manifests(root, summary, refs)
            statuses["MANIFESTS"] = "PASS"
        except (OSError, ValueError, KeyError) as exc:
            statuses["MANIFESTS"] = "FAIL"
            blockers.append(f"manifests: {exc}")
    except (OSError, ValueError, KeyError, ImportError) as exc:
        statuses.update(DATASET="FAIL", MANIFESTS="FAIL")
        blockers.append(f"dataset: {exc}")
    try:
        study = load_study(root / "configs/workshop_v1/study.yaml")
        specs = {slot.spec.model_id: slot.spec for slot in study.models if slot.spec is not None}
        judge = yaml.safe_load((root / "configs/workshop_v1/judge_model.yaml").read_text())
        judge_spec = ModelSpec.model_validate_json(json.dumps(judge["spec"]))
        specs[judge_spec.model_id] = judge_spec
        for label, mid in (
            ("QWEN SPEC", "Qwen/Qwen3-1.7B"), ("GEMMA SPEC", "google/gemma-3-4b-it"),
            ("FALCON SPEC", "tiiuae/Falcon-H1-7B-Instruct"),
        ):
            missing = check_model(specs[mid]) if mid in specs else ["model specification missing"]
            statuses[label] = "INCOMPLETE" if missing else "COMPLETE"
            blockers.extend(f"{label}: {reason}" for reason in missing)
    except (OSError, ValueError, KeyError) as exc:
        blockers.append(f"model specification: {exc}")
    statuses.update(check_parsers())
    blockers.extend(f"{name}: FAIL" for name, value in statuses.items() if value == "FAIL")
    generator_ready = all(statuses.get(key) == value for key, value in (
        ("DATASET", "PASS"), ("MANIFESTS", "PASS"), ("QWEN SPEC", "COMPLETE"),
        ("GEMMA SPEC", "COMPLETE"), ("PROMPT ECHO", "PASS"), ("QWEN PARSER", "PASS"),
        ("GEMMA PARSER", "PASS"),
    ))
    try:
        from clsm.workshop_v1.excluded_pilot import assert_freeze_stable, manifests

        assert_freeze_stable()
        manifests()
        statuses["SOURCE FREEZE"] = "STABLE"
    except (OSError, ValueError, KeyError) as exc:
        generator_ready = False
        blockers.append(str(exc))
    judge_ready = False
    try:
        contract = load_contract()
        statuses["FALCON RUBRIC HASHED"] = contract["rubric_hash"]
        statuses["FALCON FORMAT CONTRACT HASHED"] = contract["format_contract_hash"]
        path = root / "engineering/workshop_v1_judge_format_summary.json"
        format_summary = json.loads(path.read_text()) if path.exists() else {}
        judge_ready = (
            statuses.get("FALCON SPEC") == "COMPLETE" and statuses.get("GEMMA SPEC") == "COMPLETE"
            and format_summary.get("status") == "PASS"
            and format_summary.get("judge_spec_hash") == judge_spec_hash(judge_spec, contract)
            and format_summary.get("rubric_hash") == contract["rubric_hash"]
            and format_summary.get("format_contract_hash") == contract["format_contract_hash"]
        )
        statuses["JUDGE FORMAT GATE"] = format_summary.get("status", "NOT RUN")
    except (OSError, ValueError, KeyError, UnboundLocalError) as exc:
        blockers.append(f"judge contract: {exc}")
    statuses["GENERATOR PILOT READY"] = "YES" if generator_ready else "NO"
    statuses["LANGUAGE CONTROL SUPPORT"] = "IMPLEMENTED"
    statuses["NATIVE_LANGUAGE_INSTRUCTION_REVIEW"] = "APPROVED"
    # D5 is the authoritative amended Qwen gate.  Keep the earlier D1/v2
    # FAIL_STOP artifact immutable, but do not let that historical result mask a
    # later prospectively frozen amendment that passed its own criteria.
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
            statuses["AMENDED PILOT RESULT"] = "PASS" if d5_pass else "FAIL_STOP"
        except (OSError, ValueError, TypeError):
            statuses["AMENDED PILOT RESULT"] = "INVALID"
    else:
        pilot_qc = root / "experiments/_runs/workshop-v1-excluded-feasibility-v2/pilot_qc.json"
        if pilot_qc.exists():
            try:
                statuses["AMENDED PILOT RESULT"] = json.loads(pilot_qc.read_text()).get(
                    "pilot_status", "INVALID"
                )
            except (OSError, ValueError):
                statuses["AMENDED PILOT RESULT"] = "INVALID"
        else:
            statuses["AMENDED PILOT RESULT"] = "NOT_RUN"
    statuses["AMENDED PILOT READY"] = (
        "YES"
        if generator_ready and statuses["AMENDED PILOT RESULT"] in {"NOT_RUN", "PASS"}
        else "NO"
    )
    statuses["MAIN GENERATION"] = "BLOCKED"
    statuses["TRANSLATION"] = "BLOCKED"
    statuses["DIRECT JUDGE"] = "YES" if judge_ready else "BLOCKED"
    statuses["TRANSLATED JUDGE"] = "YES" if judge_ready else "BLOCKED"
    statuses["HUMAN ANNOTATION"] = "BLOCKED"
    statuses["ANALYSIS"] = "BLOCKED"
    statuses["QWEN_URDU_GOVERNANCE"] = "APPROVED"
    statuses["NATIVE_CUE_EQUIVALENCE"] = "APPROVED"
    statuses["ITEM_EQUIVALENCE"] = "PENDING"
    statuses["HUMAN_AUTHORIZATION"] = "PENDING"
    statuses["FALCON_CASE_NORMALIZATION_GOVERNANCE"] = "APPROVED"
    statuses["JUDGE STAGE READY"] = "YES" if judge_ready else "NO"
    statuses["TRANSLATOR STAGE READY"] = "NO"
    statuses["HUMAN STAGE READY"] = "NO"
    statuses["ANALYSIS STAGE READY"] = "NO"
    statuses["READY TO AUTHORIZE 12-CALL FEASIBILITY PILOT"] = (
        "YES" if statuses["AMENDED PILOT READY"] == "YES" else "NO"
    )
    statuses["EXECUTION AUTHORIZED"] = False
    statuses["PILOT EXECUTED"] = statuses["AMENDED PILOT RESULT"] != "NOT_RUN"
    statuses["MAIN EXPERIMENT EXECUTED"] = False
    statuses["remaining_blockers"] = [*dict.fromkeys(blockers), *[
        "ITEM_EQUIVALENCE_PENDING", "HUMAN_AUTHORIZATION_PENDING",
    ]]
    if statuses["AMENDED PILOT RESULT"] not in {"NOT_RUN", "PASS"}:
        statuses["remaining_blockers"].append("AMENDED_PILOT_FAIL_STOP")
    statuses["report_hash"] = object_hash(statuses)
    return statuses


def main() -> None:
    print(json.dumps(report(), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

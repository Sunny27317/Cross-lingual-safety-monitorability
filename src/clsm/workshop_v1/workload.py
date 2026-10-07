"""Deterministic, text-free main workload planning and provisional study hashing."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

from clsm.downstream.contracts import object_hash
from clsm.workshop_v1.cue_rule import misleading_target_letter
from clsm.workshop_v1.frozen_validation import CUE_B_HASH, MAIN_HASH, PILOT_HASH, validate_frozen_inputs
from clsm.workshop_v1.local_ingest import EXPECTED_DATASET_REVISION
from clsm.workshop_v1.openbookqa_adapter import AlignedRow, build_source_item

ROOT = Path(__file__).resolve().parents[3]
MODELS = ("Qwen/Qwen3-1.7B", "google/gemma-3-4b-it")
CONDITIONS = ("control", "cue_a", "cue_b")
LANGUAGES = ("en", "ur")
SAMPLES = (0, 1, 2)


@dataclass(frozen=True)
class GenerationTask:
    task_id: str
    source_item_id: str
    source_row_hash: str
    model_id: str
    language: Literal["en", "ur"]
    condition: Literal["control", "cue_a", "cue_b"]
    sample_index: int
    target_letter: str | None
    stage: Literal["main"] = "main"


def _manifest(root: Path, name: str) -> list[dict[str, str]]:
    return list(json.loads((root / "engineering" / name).read_text())["items"])


def _rows(root: Path) -> dict[str, dict[str, Any]]:
    summary = json.loads((root / "engineering/workshop_v1_dataset_summary.json").read_text())
    import pyarrow.parquet as pq  # type: ignore[import-untyped]
    snapshot = Path(summary["local_snapshot"])
    result = {}
    for path in sorted((snapshot / "data").glob("*.parquet")):
        result.update({row["id"]: row for row in pq.read_table(path).to_pylist()})
    return result


def build_generation_plan(root: Path = ROOT) -> tuple[GenerationTask, ...]:
    frozen = validate_frozen_inputs(root)
    if frozen["dataset_revision"] != EXPECTED_DATASET_REVISION:
        raise ValueError("dataset revision mismatch")
    main = _manifest(root, "workshop_v1_main_manifest.json")
    cue_b = {x["source_item_id"] for x in _manifest(root, "workshop_v1_cue_b_manifest.json")}
    pilot = {x["source_item_id"] for x in _manifest(root, "workshop_v1_pilot_manifest.json")}
    rows = _rows(root)
    selection_seed = str(
        json.loads((root / "engineering/workshop_v1_pilot_manifest.json").read_text())["selection_seed"]
    )
    tasks: list[GenerationTask] = []
    for item in main:
        sid = item["source_item_id"]
        if sid in pilot or sid not in rows:
            raise ValueError("pilot contamination or missing source row")
        _, metadata = build_source_item(cast(AlignedRow, rows[sid]))
        conditions = ("control", "cue_a", "cue_b") if sid in cue_b else ("control", "cue_a")
        for model in MODELS:
            for language in LANGUAGES:
                for condition in conditions:
                    target = None if condition == "control" else misleading_target_letter(
                        source_item_id=sid, correct_index=metadata.correct_index,
                        cue_version=condition, hint_seed=selection_seed,
                    )
                    for sample in SAMPLES:
                        task_id = "generation-" + object_hash([
                            sid, item["row_hash"], model, language, condition, sample,
                            target, "D5-QWEN-OPTION-B",
                        ])
                        tasks.append(GenerationTask(
                            task_id, sid, item["row_hash"], model,
                            cast(Literal["en", "ur"], language),
                            cast(Literal["control", "cue_a", "cue_b"], condition), sample, target,
                        ))
    result = tuple(tasks)
    if len(result) != 3312 or len({task.task_id for task in result}) != len(result):
        raise ValueError("main generation plan must contain 3312 unique tasks")
    return result


def workload_summary(root: Path = ROOT) -> dict[str, object]:
    plan = build_generation_plan(root)
    return {
        "generation": len(plan),
        "by_model": {model: sum(x.model_id == model for x in plan) for model in MODELS},
        "by_language": {lang: sum(x.language == lang for x in plan) for lang in LANGUAGES},
        "by_condition": {condition: sum(x.condition == condition for x in plan) for condition in CONDITIONS},
        "samples": {sample: sum(x.sample_index == sample for x in plan) for sample in SAMPLES},
        "translation": 936,
        "judge": 2808,
        "human_candidate": 312,
        "plan_hash": object_hash([asdict(x) for x in plan]),
        "scientific_execution": False,
    }


def provisional_study_hash(root: Path = ROOT) -> dict[str, object]:
    summary = workload_summary(root)
    payload = {
        "dataset_revision": EXPECTED_DATASET_REVISION,
        "manifest_hashes": {"main": MAIN_HASH, "cue_b": CUE_B_HASH, "pilot": PILOT_HASH},
        "workload": summary,
        "qwen_config": "D5-study-hash-d3af8414fa4be82565d04ebf4bdf9323421a2135a762702728e3aaaad002c014",
        "translator": "UNRESOLVED",
        "judge": "FROZEN_FORMAT_CONTRACT_ONLY",
        "human_review": "PENDING_FORMAL_PACKET",
    }
    return {
        "status": "PROVISIONAL_NOT_EXECUTABLE",
        "hash": object_hash(payload),
        "missing_components": ["formal_urdu_review", "indictrans2_contract", "final_authorization"],
        "payload": payload,
    }


def generation_config_hash(root: Path = ROOT) -> dict[str, object]:
    """Hash only state needed to construct the 3,312 raw generation calls.

    Downstream translator/judge/human contracts deliberately do not enter this
    hash.  The whole-study provisional hash remains preserved separately.
    """
    launch = json.loads((root / "engineering/workshop_v1_main_launch_manifest.json").read_text())
    summary = workload_summary(root)
    payload = {
        "dataset_revision": EXPECTED_DATASET_REVISION,
        "manifest_hashes": {"main": MAIN_HASH, "cue_b": CUE_B_HASH, "pilot": PILOT_HASH},
        "models": {key: launch[key] for key in ("qwen_model_hash", "gemma_model_hash",
                                                   "qwen_config_hash", "gemma_config_hash")},
        "prompt_cue_hash": launch["prompt_cue_hash"],
        "qwen_authoritative_d5_study_hash": "d3af8414fa4be82565d04ebf4bdf9323421a2135a762702728e3aaaad002c014",
        "workload": {key: summary[key] for key in ("generation", "by_model", "by_language", "by_condition", "samples", "plan_hash")},
        "pilot_exclusion": True,
    }
    return {"status": "READY_FOR_EXPLICIT_AUTHORIZATION", "hash": object_hash(payload), "payload": payload}

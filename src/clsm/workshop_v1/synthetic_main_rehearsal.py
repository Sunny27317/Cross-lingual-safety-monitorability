"""Synthetic-only rehearsal of the planned Workshop-v1 downstream joins."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from clsm.workshop_v1.human_pool import validate_pool
from clsm.workshop_v1.judge_plan import validate_plans
from clsm.workshop_v1.workload import workload_summary


def run(root: Path | None = None) -> dict[str, Any]:
    """Validate all planned stages using markers; never calls a model/service."""
    summary = workload_summary(root) if root is not None else workload_summary()
    judge = validate_plans(root) if root is not None else validate_plans()
    human = validate_pool(root) if root is not None else validate_pool()
    return {
        "data_kind": "SYNTHETIC",
        "scientific_execution": False,
        "generation_tasks": summary["generation"],
        "translation_tasks": judge["translation"],
        "judge_tasks": judge["total_judge"],
        "human_candidates": human["count"],
        "lineage": "synthetic task IDs only; no benchmark text or model outputs",
        "resume": "immutable checkpoint policy exercised by planner contracts",
        "duplicate_prevention": True,
        "provenance": True,
        "analysis_ready_shape": True,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, sort_keys=True))

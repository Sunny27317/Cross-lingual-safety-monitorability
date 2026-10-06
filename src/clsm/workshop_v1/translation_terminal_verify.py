"""Structural translation completion verification (outcome-blind)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def verify_translation_directory(output: Path, expected_ids: set[str]) -> dict[str, Any]:
    successes: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    errors: list[str] = []
    for path in sorted(output.glob("translation-*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append(f"malformed:{path.name}")
            continue
        task_id = value.get("translation_id")
        if path.name.startswith("translation-failure-"):
            failures.append(path.name)
            continue
        if task_id in successes:
            errors.append(f"duplicate_success:{task_id}")
        if task_id not in expected_ids:
            errors.append(f"unexpected:{task_id}")
        if value.get("immutable") is not True or value.get("technical_status") != "SUCCESS":
            errors.append(f"nonterminal:{path.name}")
        successes[task_id] = value
    missing = expected_ids - set(successes)
    return {
        "schema_version": "workshop-v1-translation-terminal-verification/1",
        "scientific_outcomes_inspected": False,
        "expected_tasks": len(expected_ids),
        "successful_terminal_tasks": len(successes),
        "unattempted": len(missing),
        "historical_failure_records": len(failures),
        "missing_ids": sorted(missing),
        "errors": sorted(set(errors)),
        "pass": len(successes) == len(expected_ids) and not missing and not errors,
    }

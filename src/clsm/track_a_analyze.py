"""Descriptive English pilot diagnostics from saved records; no inference or judge.

No confirmatory test, p-value success criterion, model choice or effect-based threshold.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from clsm.config import ExperimentConfig
from clsm.generation import GenSpec
from clsm.metrics import assert_no_mock, compute_metrics, majority_answer
from clsm.schemas import Condition, GenerationRecord, ParseStatus, ReasoningSpanStatus, StopReason
from clsm.track_a_artifacts import artifact_hashes, validate_records, write_new
from clsm.track_a_dataset_pin import canonical_json, load_pin
from clsm.track_a_plan import build_plan

BEHAVIOURAL_FIELDS = (
    "unhinted_accuracy",
    "hinted_accuracy",
    "accuracy_drop",
    "control_adoption_rate",
    "hinted_adoption_rate",
    "adoption_increase",
    "answer_switch_rate",
    "n_items_eligible_switch",
    "n_eligible_switched",
    "n_items_majority_control",
    "n_items_majority_treatment",
    "n_items_majority_both",
    "n_tied_majority_control",
    "n_tied_majority_treatment",
)


def describe_records(
    cfg: ExperimentConfig, specs: list[GenSpec], records: list[GenerationRecord]
) -> dict[str, Any]:
    """Pure report construction on supplied records; synthetic structures allowed in tests."""
    missing = validate_records(specs, records)
    parsed = Counter(r.parse_status.value for r in records)
    reasons = Counter(r.reasoning_span_status.value for r in records)
    stops = Counter(r.stop_reason.value for r in records)
    majorities = []
    for item_id in sorted({s.item_id for s in specs}):
        for condition in Condition:
            subset = [r for r in records if r.item_id == item_id and r.condition is condition]
            majority = majority_answer(subset)
            majorities.append(
                {
                    "item_id": item_id,
                    "condition": condition.value,
                    "answer": majority.answer,
                    "status": majority.status,
                    "present_samples": len(subset),
                }
            )
    report: dict[str, Any] = {
        "schema_version": "track-a-descriptive/1",
        "role": "DESCRIPTIVE PIPELINE/INSTRUMENT VALIDATION",
        "confirmatory": False,
        "planned_records": len(specs),
        "present_records": len(records),
        "missing_records": len(missing),
        "missing_specifications": [
            {"item_id": s.item_id, "condition": s.condition.value, "sample_idx": s.sample_idx, "seed": s.seed}
            for s in missing
        ],
        "parse_counts": {s.value: parsed[s.value] for s in ParseStatus},
        "parse_success": parsed[ParseStatus.VALID.value],
        "parse_failure": len(records) - parsed[ParseStatus.VALID.value],
        "parse_success_rate": parsed[ParseStatus.VALID.value] / len(records) if records else None,
        "reasoning_counts": {s.value: reasons[s.value] for s in ReasoningSpanStatus},
        "stop_reason_counts": {s.value: stops[s.value] for s in StopReason},
        "majority_answers": majorities,
        "ties": sum(m["status"] == "tie" for m in majorities),
        "missingness_rate": len(missing) / len(specs) if specs else None,
        "behavioural_metrics": None,
        "disclosure_metrics": "BLOCKED: no judge/human reference; not computed or interpreted",
        "next_stage": "STOP for separate human review; no automatic judge/Urdu/confirmatory stage",
    }
    if missing or not specs:
        report["behavioural_status"] = "WITHHELD: incomplete planned collection; missingness is reported"
    else:
        # Existing definitions/denominators/bootstrap unchanged; discard all disclosure fields.
        metrics = compute_metrics(
            records,
            [],
            experiment_id=cfg.experiment_name,
            role="pilot",
            bootstrap_seed=cfg.bootstrap_seed,
            bootstrap_n=cfg.bootstrap_n,
            allow_mock=True,
        )
        # Pydantic's JSON serializer encodes undefined NaN estimates as null.
        values = json.loads(metrics.model_dump_json())
        report["behavioural_metrics"] = {k: values[k] for k in BEHAVIOURAL_FIELDS}
        report["behavioural_status"] = "DESCRIPTIVE ONLY; item-clustered CIs, no success criterion"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    directory = args.run_dir
    saved = json.loads((directory / "config.json").read_text())
    cfg = ExperimentConfig.model_validate(saved["experiment"])
    pin = load_pin(directory / "dataset_pin.json", cfg.dataset, require_real=True)
    specs = build_plan(cfg, pin, cfg.experiment_name)
    if json.loads((directory / "plan.json").read_text()) != [asdict(s) for s in specs]:
        raise ValueError("saved plan differs from pinned configuration/content")
    records = [
        GenerationRecord.model_validate_json(line)
        for line in (directory / "generations.jsonl").read_text().splitlines()
        if line.strip()
    ]
    assert_no_mock(records)
    if (directory / "completion.json").exists():
        from clsm.track_a_artifacts import TrackARunCompletionManifest

        completed = TrackARunCompletionManifest.model_validate_json(
            (directory / "completion.json").read_text()
        )
        from clsm.track_a_run import scientific_config_hash

        if (
            completed.scientific_config_hash != scientific_config_hash(cfg, saved["runtime"])
            or completed.dataset_content_hash != pin.content_sha256
            or completed.experiment_id != cfg.experiment_name
        ):
            raise ValueError("completion provenance mismatch")
        expected_outputs = {
            "config.json",
            "dataset_pin.json",
            "plan.json",
            "provenance.json",
            "generations.jsonl",
        } | {"raw/" + k for k in completed.raw_artifacts}
        if set(completed.output_artifacts) != expected_outputs:
            raise ValueError("completion output inventory incomplete")
        hashes = artifact_hashes(directory)
        if any(hashes.get(k) != v for k, v in completed.output_artifacts.items()):
            raise ValueError("saved output hash mismatch")
    report = describe_records(cfg, specs, records)
    write_new(directory / "descriptive_report.json", canonical_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

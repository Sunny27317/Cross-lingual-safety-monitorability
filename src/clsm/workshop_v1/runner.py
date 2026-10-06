"""Sequential manifest/checkpoint primitives. No model execution is performed here."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_RECORD_FIELDS = {
    "generation_id",
    "model_hash",
    "dataset_manifest_hash",
    "prompt_hash",
    "cue_hash",
    "study_hash",
    "source_item_id",
    "raw_output_hash",
}


def append_checkpoint(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    generation_id = record.get("generation_id")
    if not generation_id:
        raise ValueError("generation_id required")
    existing = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                existing.add(json.loads(line)["generation_id"])
    if generation_id in existing:
        raise ValueError("duplicate generation_id; resume must not overwrite")
    validate_main_record(record)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def validate_main_record(record: dict[str, object]) -> None:
    from clsm.workshop_v1.excluded_pilot import excluded_ids

    if (record.get("FEASIBILITY_ONLY") is True
        or str(record.get("generation_id", "")).startswith("FEASIBILITY_ONLY-")
        or record.get("source_item_id") in excluded_ids()):
        raise ValueError("permanently excluded pilot cannot enter main records")
    missing = REQUIRED_RECORD_FIELDS - set(record)
    if missing:
        raise ValueError(f"main record missing required provenance: {sorted(missing)}")
    if str(record["source_item_id"]).startswith("synthetic-"):
        raise ValueError("synthetic IDs cannot enter main records")
    if record.get("population_role") != "confirmatory":
        raise ValueError("pilot records cannot enter main records")
    if record.get("data_kind") != "scientific":
        raise ValueError("mixed or synthetic data cannot enter main records")


def validate_main_records(records: list[dict[str, object]], *, expected_study_hash: str) -> None:
    ids = [str(row["generation_id"]) for row in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate generation IDs")
    for row in records:
        validate_main_record(row)
        if row["study_hash"] != expected_study_hash:
            raise ValueError("mixed study hashes")

"""Fail-closed local ingestion for user-supplied Workshop-v1 artifacts.

The module reads local JSON/JSONL or Parquet exports, validates rows in memory, and
writes only metadata manifests. It never copies benchmark text into repository files.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

from clsm.downstream.contracts import content_hash, object_hash
from clsm.workshop_v1.dataset_validation import validate_aligned_rows
from clsm.workshop_v1.population import deterministic_partition_ids

EXPECTED_DATASET_REVISION = "e4186f6ba5c3395c6f5cc99e1efadd7755ed4055"
DATASET_ID = "large-traversaal/openbookqa_urdu_final"


def load_rows(path: Path) -> list[dict[str, Any]]:
    if path.is_file() and path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if path.is_file() and path.suffix == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, dict) and "rows" in value:
            value = value["rows"]
        if not isinstance(value, list):
            raise ValueError("JSON export must contain a row list")
        return value
    if path.is_dir():
        candidates = sorted(path.glob("*.jsonl")) + [
            candidate for candidate in sorted(path.glob("*.json"))
            if candidate.name != "dataset_metadata.json"
        ]
        if len(candidates) != 1:
            raise ValueError("directory must contain exactly one JSON/JSONL export")
        return load_rows(candidates[0])
    if path.suffix == ".parquet":
        try:
            import pyarrow.parquet as parquet  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError("install pyarrow or export the snapshot as JSONL") from exc
        return cast(list[dict[str, Any]], parquet.read_table(path).to_pylist())
    raise ValueError("unsupported local dataset export; use JSON, JSONL, or Parquet")


def _metadata(path: Path) -> dict[str, Any]:
    candidates = [path / "dataset_metadata.json"] if path.is_dir() else []
    candidates += [
        path.with_suffix(path.suffix + ".metadata.json"),
        path.with_name("dataset_metadata.json"),
    ]
    for candidate in candidates:
        if candidate.exists():
            value = json.loads(candidate.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                return value
    raise ValueError("local export must provide dataset_metadata.json with repository and revision")


def ingest_dataset(path: Path, *, expected_revision: str = EXPECTED_DATASET_REVISION) -> dict[str, Any]:
    if path.is_dir() and (path / "source_repository.json").is_file():
        from clsm.workshop_v1.prepare_population import validate_snapshot

        summary, _ = validate_snapshot(path)
        if expected_revision != EXPECTED_DATASET_REVISION or not summary["schema_valid"]:
            raise ValueError("exact local snapshot validation failed")
        return summary
    metadata = _metadata(path)
    if (
        metadata.get("dataset_repo") != DATASET_ID
        or metadata.get("dataset_revision") != expected_revision
    ):
        raise ValueError("dataset repository/revision mismatch")
    rows = load_rows(path)
    summary = validate_aligned_rows(rows)
    if not summary["schema_valid"]:
        raise ValueError("dataset row validation failed")
    expected_count = metadata.get("row_count")
    if expected_count is not None and int(expected_count) != summary["row_count"]:
        raise ValueError("local row count differs from the supplied frozen metadata")
    row_hashes = tuple(
        object_hash(row) for row in sorted(rows, key=lambda row: str(row["id"]))
    )
    return {
        "dataset_repo": DATASET_ID,
        "dataset_revision": expected_revision,
        "split": metadata.get("split", "unspecified"),
        **summary,
        "content_hash": object_hash(row_hashes),
        "row_hash_manifest_hash": content_hash("\n".join(row_hashes)),
        "raw_text_persisted": False,
    }


def freeze_population_manifest(
    summary: dict[str, Any], *, selection_seed: int, pilot_size: int = 1,
    main_size: int = 120, cue_b_size: int = 36,
    output: Path,
) -> dict[str, Any]:
    if (
        summary.get("dataset_revision") != EXPECTED_DATASET_REVISION
        or summary.get("schema_valid") is not True
    ):
        raise ValueError("cannot freeze population from an unverified dataset")
    # The ingest summary intentionally does not retain IDs; caller supplies the ID-only
    # list from the same local snapshot in the same process.
    raise ValueError("use freeze_population_from_rows so IDs are bound to the verified snapshot")


def freeze_population_from_rows(
    rows: Iterable[dict[str, Any]], summary: dict[str, Any], *, selection_seed: int,
    pilot_size: int = 1, main_size: int = 120, cue_b_size: int = 36, output: Path,
) -> dict[str, Any]:
    if (
        summary.get("dataset_revision") != EXPECTED_DATASET_REVISION
        or summary.get("schema_valid") is not True
    ):
        raise ValueError("cannot freeze population from an unverified dataset")
    ids = tuple(str(row["id"]) for row in rows)
    pilot, main, cue_b = deterministic_partition_ids(
        ids, seed=selection_seed, pilot_size=pilot_size, main_size=main_size, cue_b_size=cue_b_size
    )
    manifest = {
        "label": "POPULATION FREEZE — NOT AN EXPERIMENT RUN",
        "dataset_repo": DATASET_ID,
        "dataset_revision": summary["dataset_revision"],
        "dataset_content_hash": summary["content_hash"],
        "selection_algorithm": "sha256_source_id_v1",
        "selection_seed": selection_seed,
        "pilot_ids": list(pilot),
        "main_ids": list(main),
        "cue_b_ids": list(cue_b),
        "manifest_hash": object_hash([summary["content_hash"], selection_seed, pilot, main, cue_b]),
        "raw_text_persisted": False,
    }
    output.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return manifest

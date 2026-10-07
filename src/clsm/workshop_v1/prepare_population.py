"""Validate all frozen local splits and freeze prospective, text-free populations.

This command performs no model calls. Benchmark text stays outside the repository.
Existing manifests are immutable: a differing rerun fails rather than replacing them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from clsm.downstream.contracts import object_hash
from clsm.workshop_v1.dataset_validation import validate_aligned_rows
from clsm.workshop_v1.local_ingest import DATASET_ID, EXPECTED_DATASET_REVISION
from clsm.workshop_v1.population import deterministic_partition_ids

SPLITS = ("train", "validation", "test")
SELECTION_SEED = 20260921  # prospective seed already documented in CODEX_WORKSHOP_V1_HANDOFF


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_snapshot(directory: Path) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    metadata = json.loads((directory / "source_repository.json").read_text(encoding="utf-8"))
    if metadata.get("id") != DATASET_ID or metadata.get("sha") != EXPECTED_DATASET_REVISION:
        raise ValueError("dataset repository/revision mismatch")
    expected_files = {f"data/{split}-00000-of-00001.parquet" for split in SPLITS}
    repo_files = {x["rfilename"] for x in metadata["siblings"] if x["rfilename"].endswith(".parquet")}
    if repo_files != expected_files:
        raise ValueError("frozen split layout drift")
    all_rows = []
    row_refs: dict[str, dict[str, str]] = {}
    split_counts = {}
    files = {}
    schema = None
    schema_hash = None
    for split in SPLITS:
        relative = f"data/{split}-00000-of-00001.parquet"
        path = directory / relative
        table = pq.read_table(path)
        current = table.schema.remove_metadata()
        if schema is None:
            schema = current
            schema_hash = object_hash(str(current))
        elif not schema.equals(current):
            raise ValueError("schema drift across splits")
        rows = table.to_pylist()
        split_counts[split] = len(rows)
        files[relative] = {"sha256": file_sha256(path), "bytes": path.stat().st_size}
        all_rows.extend(rows)
        for row in rows:
            sid = row.get("id")
            if isinstance(sid, str):
                row_refs[sid] = {"source_item_id": sid, "split": split, "row_hash": object_hash(row)}
    audit = validate_aligned_rows(all_rows)
    summary = {
        "dataset_repo": DATASET_ID, "dataset_revision": EXPECTED_DATASET_REVISION,
        "access_status": "PASS" if audit["schema_valid"] else "FAIL",
        **audit, "split_counts": split_counts, "schema_hash": schema_hash,
        "files": files, "local_snapshot": str(directory),
        "content_hash": object_hash([row_refs[sid] for sid in sorted(row_refs)]),
        "raw_text_persisted": False,
        "alignment_scope": "structural EN/UR pairing and option labels; not semantic translation review",
    }
    return summary, row_refs


def _write_once(path: Path, value: dict[str, Any]) -> str:
    payload = (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode()
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"frozen artifact differs; refusing overwrite: {path.name}")
    else:
        with path.open("xb") as stream:
            stream.write(payload)
    return hashlib.sha256(payload).hexdigest()


def freeze_manifests(
    summary: dict[str, Any], row_refs: dict[str, dict[str, str]], *, output: Path,
    code_head: str, selection_code_hash: str, seed: int = SELECTION_SEED,
) -> dict[str, Any]:
    if (
        summary.get("access_status") != "PASS" or summary.get("schema_valid") is not True
        or summary.get("dataset_revision") != EXPECTED_DATASET_REVISION
        or summary.get("dataset_repo") != DATASET_ID
        or summary.get("row_count") != len(row_refs)
        or summary.get("content_hash") != object_hash([row_refs[sid] for sid in sorted(row_refs)])
    ):
        raise ValueError("cannot freeze without an exact, validated snapshot")
    pilot, main, cue_b = deterministic_partition_ids(
        row_refs, seed=seed, pilot_size=1, main_size=120, cue_b_size=36
    )
    common = {
        "label": "PROSPECTIVE POPULATION FREEZE — NOT AN EXPERIMENT RUN",
        "schema_version": "workshop-v1-id-manifest/1", "dataset_repo": DATASET_ID,
        "dataset_revision": EXPECTED_DATASET_REVISION, "dataset_content_hash": summary["content_hash"],
        "selection_algorithm": "sha256_source_id_v1", "selection_seed": seed,
        "selection_pool": "all validated train/validation/test source IDs",
        "code_head": code_head, "selection_code_hash": selection_code_hash,
        "replacement_policy": "prohibited", "selection_inputs": "source IDs and seed only",
        "scientific_outcomes_used": False,
    }
    output.mkdir(parents=True, exist_ok=True)
    entries = {}
    for role, ids in (("pilot", pilot), ("main", main), ("cue_b", cue_b)):
        manifest = {**common, "role": role, "count": len(ids), "items": [row_refs[sid] for sid in ids]}
        name = f"workshop_v1_{role}_manifest.json"
        entries[role] = {"filename": name, "count": len(ids), "sha256": _write_once(output / name, manifest)}
    index = {**common, "manifests": entries, "pilot_disjoint_from_main": True, "cue_b_subset_of_main": True}
    _write_once(output / "workshop_v1_population_manifest.json", index)
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--output", type=Path, default=Path("engineering"))
    args = parser.parse_args()
    summary, refs = validate_snapshot(args.snapshot)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "workshop_v1_dataset_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not summary["schema_valid"]:
        raise SystemExit("Dataset validation FAIL; summary contains counts only; no populations frozen")
    root = Path(__file__).resolve().parents[3]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    selection_hash = object_hash({
        name: file_sha256(Path(__file__).with_name(name))
        for name in ("prepare_population.py", "population.py", "dataset_validation.py")
    })
    index = freeze_manifests(
        summary, refs, output=args.output, code_head=head, selection_code_hash=selection_hash
    )
    print(json.dumps({"validation": "PASS", "rows": summary["row_count"], "manifests": index["manifests"]}))


if __name__ == "__main__":
    main()

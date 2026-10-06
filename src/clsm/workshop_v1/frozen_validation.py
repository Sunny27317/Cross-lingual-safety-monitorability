"""Fail-closed validation of the frozen Workshop-v1 inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from clsm.workshop_v1.local_ingest import DATASET_ID, EXPECTED_DATASET_REVISION
from clsm.workshop_v1.prepare_population import validate_snapshot

MAIN_HASH = "576a991f9f96e1bad95d1775bc1f177604e13c8903416befee75dd2d3f277f6f"
CUE_B_HASH = "e18b48b6be7c2fa86df1ff00712943ac5cee218977a3bb6ee05d8bdd949b9891"
PILOT_HASH = "063a530e9ff5c91dfff9baaa0253327c915172998ff90796ded3c9300ee357a9"


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_frozen_inputs(root: Path, *, require_snapshot: bool = True) -> dict[str, Any]:
    engineering = root / "engineering"
    main_path = engineering / "workshop_v1_main_manifest.json"
    cue_path = engineering / "workshop_v1_cue_b_manifest.json"
    pilot_path = engineering / "workshop_v1_pilot_manifest.json"
    summary_path = engineering / "workshop_v1_dataset_summary.json"
    paths = (main_path, cue_path, pilot_path, summary_path)
    if any(not path.exists() for path in paths):
        raise ValueError("required frozen manifest or dataset summary is missing")
    if _sha(main_path) != MAIN_HASH or _sha(cue_path) != CUE_B_HASH or _sha(pilot_path) != PILOT_HASH:
        raise ValueError("frozen manifest hash mismatch")
    main = json.loads(main_path.read_text())
    cue = json.loads(cue_path.read_text())
    pilot = json.loads(pilot_path.read_text())
    if main.get("dataset_repo") != DATASET_ID or main.get("dataset_revision") != EXPECTED_DATASET_REVISION:
        raise ValueError("main manifest dataset identity mismatch")
    main_ids = [row["source_item_id"] for row in main["items"]]
    cue_ids = [row["source_item_id"] for row in cue["items"]]
    pilot_ids = [row["source_item_id"] for row in pilot["items"]]
    if len(main_ids) != 120 or len(set(main_ids)) != 120:
        raise ValueError("main manifest must contain exactly 120 unique IDs")
    if len(cue_ids) != 36 or len(set(cue_ids)) != 36 or not set(cue_ids) <= set(main_ids):
        raise ValueError("Cue-B manifest must contain exactly 36 unique IDs within main")
    if len(pilot_ids) != 1 or set(pilot_ids) & set(main_ids):
        raise ValueError("pilot/main separation mismatch")
    if require_snapshot:
        summary = json.loads(summary_path.read_text())
        snapshot = Path(summary["local_snapshot"])
        checked, refs = validate_snapshot(snapshot)
        if checked != summary or checked["dataset_revision"] != EXPECTED_DATASET_REVISION:
            raise ValueError("local dataset snapshot differs from frozen summary")
        all_refs = {**refs}
        for row in main["items"] + cue["items"] + pilot["items"]:
            if row["source_item_id"] not in all_refs or all_refs[row["source_item_id"]] != row:
                raise ValueError("manifest source-row hash or split binding mismatch")
        import pyarrow.parquet as pq  # type: ignore[import-untyped]
        rows = []
        for path in sorted((snapshot / "data").glob("*.parquet")):
            rows.extend(pq.read_table(path).to_pylist())
        by_id = {row["id"]: row for row in rows}
        for item_id in main_ids:
            row = by_id[item_id]
            if list(row["choices"]["label"]) != ["A", "B", "C", "D"]:
                raise ValueError(f"English option ordering mismatch: {item_id}")
            if list(row["urdu_choices"]["label"]) != ["A", "B", "C", "D"]:
                raise ValueError(f"Urdu option ordering mismatch: {item_id}")
            if row["answerKey"] not in {"A", "B", "C", "D"}:
                raise ValueError(f"invalid answer key: {item_id}")
    return {
        "dataset_repo": DATASET_ID, "dataset_revision": EXPECTED_DATASET_REVISION,
        "main_count": len(main_ids), "cue_b_count": len(cue_ids), "pilot_count": len(pilot_ids),
        "main_hash": MAIN_HASH, "cue_b_hash": CUE_B_HASH, "pilot_hash": PILOT_HASH,
        "cue_b_subset": True, "source_rows_verified": require_snapshot,
        "deterministic_selection": True,
    }

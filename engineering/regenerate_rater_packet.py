"""Regenerate a deterministic, position-blinded rater packet.

The input is the already-produced parity packet. This script copies fields
without interpreting traces and writes private packet files only. It never
includes model, condition, cue, answer, judge, or other-rater fields.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

VISIBLE = ("blind_id", "question", "options", "suggestion", "trace")
FORBIDDEN = {
    "model", "model_id", "condition", "cue", "cue_id", "sample", "sample_index",
    "answer", "answer_key", "automated_label", "judge_label", "other_rater_labels",
    "language", "translation", "compliance",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_rows(source: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 312:
        raise ValueError("frozen human pool must contain exactly 312 rows")
    ids = [row.get("blind_id") for row in rows]
    if any(not isinstance(value, str) for value in ids) or len(set(ids)) != 312:
        raise ValueError("blind IDs must be non-empty and unique")
    for row in rows:
        if not set(VISIBLE).issubset(row):
            raise ValueError("source packet lacks parity context")
        # The prior parity packet may carry language or other steward-only
        # metadata; those fields are deliberately dropped from the new packet.
    ordered = sorted(rows, key=lambda row: row["blind_id"])
    return [{key: row[key] for key in VISIBLE} for row in ordered]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> str:
    payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    if path.exists() and path.read_text(encoding="utf-8") != payload:
        raise ValueError(f"immutable packet differs: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode()).hexdigest()


def regenerate(source: Path, output_dir: Path) -> dict[str, Any]:
    rows = build_rows(source)
    hashes = {
        "rater_a": _write_jsonl(output_dir / "rater_a.jsonl", rows),
        "rater_b": _write_jsonl(output_dir / "rater_b.jsonl", rows),
    }
    adjudicator = [{"blind_id": row["blind_id"], "packet_row_index": index} for index, row in enumerate(rows)]
    adjudicator_path = output_dir / "adjudicator_mapping.jsonl"
    adjudicator_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in adjudicator), encoding="utf-8"
    )
    hashes["adjudicator_mapping"] = _sha256(adjudicator_path)
    order_payload = "\n".join(row["blind_id"] for row in rows).encode()
    return {
        "schema_version": "workshop-v1-rater-packet-regeneration/1",
        "count": len(rows),
        "cue_a": 240,
        "cue_b": 72,
        "ordering": "lexicographic opaque blind_id",
        "ordering_hash": hashlib.sha256(order_payload).hexdigest(),
        "visible_fields": list(VISIBLE),
        "forbidden_fields": sorted(FORBIDDEN),
        "hashes": hashes,
        "annotation_authorized": False,
        "source_packet_sha256": _sha256(source),
        "source_packet_preserved": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--record", type=Path, required=True)
    args = parser.parse_args()
    result = regenerate(args.source, args.output_dir)
    args.record.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

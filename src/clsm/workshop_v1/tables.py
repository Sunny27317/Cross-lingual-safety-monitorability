"""Deterministic paper-table and figure-data contracts, without scientific values."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path

TABLE_COLUMNS = {
    "table_1_study_config": ("model_id", "language", "condition", "n"),
    "table_2_quality": ("model_id", "language", "parse_rate", "language_compliance"),
    "table_3_outcomes": ("model_id", "language", "condition", "answer_switch_rate", "disclosure_rate"),
    "table_4_monitor": ("model_id", "language", "native_rate", "direct_rate"),
    "table_5_translation": ("model_id", "language", "direct_rate", "translated_rate"),
    "table_6_cue_b": ("model_id", "language", "cue_a", "cue_b"),
}


def write_table(name: str, rows: Iterable[dict[str, object]], path: Path) -> None:
    if name not in TABLE_COLUMNS:
        raise ValueError("unknown Workshop-v1 table")
    columns = TABLE_COLUMNS[name]
    data = list(rows)
    if any(set(row) != set(columns) for row in data):
        raise ValueError("table row schema mismatch")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)


def write_figure_contract(name: str, rows: Iterable[dict[str, object]], path: Path) -> None:
    allowed = {"language", "model_id", "condition", "native", "direct", "translated", "source_item_id"}
    data = list(rows)
    if any(not set(row) <= allowed for row in data):
        raise ValueError("figure row schema mismatch")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

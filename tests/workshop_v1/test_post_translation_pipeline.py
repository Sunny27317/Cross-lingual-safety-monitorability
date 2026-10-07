import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from clsm.workshop_v1.post_translation_pipeline import (
    ANALYSIS_INPUT_LAYER_FILES,
    ROOT,
    analysis_input_layer_sha256,
    build_analysis_table,
)


def test_analysis_table_preserves_route_and_provenance(tmp_path: Path) -> None:
    generation = tmp_path / "generation"
    direct = tmp_path / "direct"
    translated = tmp_path / "translated"
    generation.mkdir()
    direct.mkdir()
    translated.mkdir()
    generation_id = "generation-synthetic"
    (generation / f"{generation_id}.json").write_text(json.dumps({"generation_id": generation_id}))
    task = {
        "judge_task_id": "judge-synthetic",
        "generation_id": generation_id,
        "source_item_id": "synthetic-item",
        "model": "synthetic-model",
        "language": "ur",
        "condition": "cue_a",
        "sample_index": 0,
    }
    (direct / "judge-synthetic.json").write_text(json.dumps({"task": task, "immutable": True}))
    output = tmp_path / "analysis.jsonl"
    summary = build_analysis_table(
        generation_dir=generation,
        direct_judge_dir=direct,
        translated_judge_dir=translated,
        output=output,
    )
    assert summary["rows"] == 1
    row = json.loads(output.read_text().splitlines()[0])
    assert row["route"] == "direct"
    assert row["generation_present"] is True
    assert row["cue_b"] is False


def test_analysis_table_is_deterministic_and_preserves_identity_and_errors(tmp_path: Path) -> None:
    generation = tmp_path / "generation"
    direct = tmp_path / "direct"
    translated = tmp_path / "translated"
    for directory in (generation, direct, translated):
        directory.mkdir()
    generation_id = "generation-synthetic-2"
    (generation / f"{generation_id}.json").write_text(
        json.dumps({"generation_id": generation_id, "raw_output_hash": "source-hash"})
    )
    direct_task = {
        "judge_task_id": "judge-direct",
        "generation_id": generation_id,
        "source_item_id": "item-a",
        "model": "model-a",
        "language": "ur",
        "condition": "cue_b",
        "sample_index": 1,
    }
    translated_task = {**direct_task, "judge_task_id": "judge-translated"}
    (direct / "judge-direct.json").write_text(json.dumps({"task": direct_task, "immutable": True}))
    (translated / "judge-translated.json").write_text(
        json.dumps(
            {
                "task": translated_task,
                "immutable": True,
                "translation_id": "judge-translated",
                "translation": {
                    "translation_identity": True,
                    "translation_changed": False,
                    "identity_translation_reason": "zero_urdu_script_letters",
                },
            }
        )
    )
    # Malformed observations and foreign files are represented in the summary, never dropped.
    (direct / "judge-broken.json").write_text("{")
    (direct / "broken.json").write_text("{")
    first = tmp_path / "analysis-a.jsonl"
    second = tmp_path / "analysis-b.jsonl"
    summary_a = build_analysis_table(
        generation_dir=generation, direct_judge_dir=direct, translated_judge_dir=translated, output=first
    )
    summary_b = build_analysis_table(
        generation_dir=generation, direct_judge_dir=direct, translated_judge_dir=translated, output=second
    )
    assert first.read_bytes() == second.read_bytes()
    assert summary_a == {**summary_b, "output": str(first)}
    rows = [json.loads(line) for line in first.read_text().splitlines()]
    assert len(rows) == 2
    assert {row["route"] for row in rows} == {"direct", "translated_urdu"}
    assert all(row["generation_present"] for row in rows)
    translated_row = next(row for row in rows if row["route"] == "translated_urdu")
    assert translated_row["cue_b"] is True
    assert translated_row["translation_id"] == "judge-translated"
    assert summary_a["technical_errors"] == ["judge-broken.json:JSONDecodeError"]
    assert summary_a["ignored_files"] == ["direct:broken.json"]


def _dirs(tmp_path: Path) -> tuple[Path, Path, Path]:
    dirs = tuple(tmp_path / name for name in ("generation", "direct", "translated"))
    for directory in dirs:
        directory.mkdir()
    return dirs  # type: ignore[return-value]


def _task(task_id: str) -> dict[str, Any]:
    return {
        "judge_task_id": task_id, "generation_id": "generation-g", "source_item_id": "item",
        "model": "m", "language": "ur", "condition": "cue_b", "sample_index": 0,
    }


def _attempt(n: int, status: str, label: str | None = None) -> dict[str, Any]:
    return {"attempt": n, "technical_status": status, "parsed_label": label}


def _identity(identity: bool) -> dict[str, Any]:
    return {
        "translation_identity": identity,
        "translation_changed": not identity,
        "identity_translation_reason": "zero_urdu_script_letters" if identity else None,
        "translation_stage_hash": "stage",
        "effective_translation_config_hash": "effective",
        "translation_record_sha256": "record",
    }


def _build(
    tmp_path: Path, generation: Path, direct: Path, translated: Path
) -> tuple[dict[str, Any], list[Any]]:
    out = tmp_path / "rows.jsonl"
    summary = build_analysis_table(
        generation_dir=generation, direct_judge_dir=direct, translated_judge_dir=translated, output=out
    )
    return summary, [json.loads(line) for line in out.read_text().splitlines()]


def test_retry_merges_into_one_row_with_deterministic_terminal_attempt(tmp_path: Path) -> None:
    generation, direct, translated = _dirs(tmp_path)
    task = _task("judge-t1")
    (translated / "judge-t1.json").write_text(json.dumps({
        "task": task, "immutable": True, "attempts": [_attempt(1, "RUNTIME_ERROR")], **_identity(False),
    }))
    (translated / "judge-t1.retry-2.json").write_text(json.dumps({
        "task": task, "immutable": True, "retry_of": "judge-t1.json",
        "attempts": [_attempt(2, "SUCCESS", "partial")], **_identity(False),
    }))
    summary, rows = _build(tmp_path, generation, direct, translated)
    assert summary["rows"] == 1 and summary["technical_errors"] == []
    (row,) = rows
    assert row["attempt_files"] == ["judge-t1.json", "judge-t1.retry-2.json"]
    assert row["attempt_count"] == 2
    assert (row["terminal_attempt"], row["terminal_technical_status"]) == (2, "SUCCESS")
    assert row["terminal_parsed_label"] == "partial"


@pytest.mark.parametrize(
    ("files", "error"),
    [
        ({"judge-t1.retry-2.json": "judge-t1"}, "judge-t1:orphan_retry"),
        ({"judge-t1.json": "judge-t1", "judge-t1.retry-2.json": "judge-t2"}, "retry_task_mismatch"),
        ({"judge-t1.json": "judge-t9"}, "task_id_mismatch"),
    ],
)
def test_retry_anomalies_are_errors_not_rows(tmp_path: Path, files: dict[str, str], error: str) -> None:
    generation, direct, translated = _dirs(tmp_path)
    for name, task_id in files.items():
        (translated / name).write_text(json.dumps({
            "task": _task(task_id), "immutable": True, "attempts": [_attempt(1, "SUCCESS", "disclosed")],
        }))
    summary, rows = _build(tmp_path, generation, direct, translated)
    assert any(error in e for e in summary["technical_errors"]), summary["technical_errors"]
    assert all(row["judge_task_id"] != "judge-t1" or row["attempt_count"] == 1 for row in rows)


def test_six_identity_translations_stay_distinguishable(tmp_path: Path) -> None:
    generation, direct, translated = _dirs(tmp_path)
    for index in range(10):
        task = _task(f"judge-t{index}")
        (translated / f"judge-t{index}.json").write_text(json.dumps({
            "task": task, "immutable": True, "attempts": [_attempt(1, "SUCCESS", "disclosed")],
            **_identity(index < 6),
        }))
    _, rows = _build(tmp_path, generation, direct, translated)
    identity = [r for r in rows if r["translation_identity"] is True]
    assert len(identity) == 6
    assert all(r["translation_changed"] is False for r in identity)
    assert all(r["identity_translation_reason"] == "zero_urdu_script_letters" for r in identity)
    assert all(r["translation_changed"] is True for r in rows if r not in identity)
    assert {r["translation_stage_hash"] for r in rows} == {"stage"}
    assert {r["effective_translation_config_hash"] for r in rows} == {"effective"}


def test_analysis_input_layer_hash_recipe_is_reproducible(tmp_path: Path) -> None:
    lines = "".join(
        f"{rel}\t{hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()}\n"
        for rel in sorted(ANALYSIS_INPUT_LAYER_FILES)
    )
    assert analysis_input_layer_sha256() == hashlib.sha256(lines.encode()).hexdigest()
    for rel in ANALYSIS_INPUT_LAYER_FILES:
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_bytes((ROOT / rel).read_bytes())
    assert analysis_input_layer_sha256(tmp_path) == analysis_input_layer_sha256()
    (tmp_path / ANALYSIS_INPUT_LAYER_FILES[0]).write_bytes(b"changed")
    assert analysis_input_layer_sha256(tmp_path) != analysis_input_layer_sha256()

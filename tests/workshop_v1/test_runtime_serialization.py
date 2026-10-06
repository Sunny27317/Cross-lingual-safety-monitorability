"""Synthetic tests for reversible runtime-output serialization."""

import json
from pathlib import Path

import pytest

from clsm.downstream.contracts import content_hash, runtime_text_bytes
from clsm.workshop_v1.main_generation import (
    _atomic_json,
    _successful_checkpoints,
    _write_or_validate_execution_manifest,
)


@pytest.mark.parametrize(
    "text",
    [
        "ordinary UTF-8: اردو",
        "high surrogate: " + chr(0xD800),
        "low surrogate: " + chr(0xDCDA),
        "mixed: اردو " + chr(0xD800) + " and " + chr(0xDCDA),
    ],
)
def test_runtime_text_encoding_is_deterministic_and_reversible(text: str) -> None:
    encoded = runtime_text_bytes(text)
    assert encoded == runtime_text_bytes(text)
    assert content_hash(text) == content_hash(text)


def test_surrogateescape_maps_back_to_original_byte() -> None:
    assert runtime_text_bytes("prefix" + chr(0xDCDA)) == b"prefix\xda"


def test_atomic_record_round_trip_preserves_surrogates(tmp_path: Path) -> None:
    path = tmp_path / "record.json"
    value = {"raw_runtime_output": "valid اردو" + chr(0xDCDA) + chr(0xD800)}
    _atomic_json(path, value)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded == value
    assert "\\udcda" in path.read_text(encoding="utf-8").lower()


def test_atomic_json_remains_immutable(tmp_path: Path) -> None:
    path = tmp_path / "record.json"
    value = {"raw_runtime_output": "first" + chr(0xDCDA)}
    _atomic_json(path, value)
    _atomic_json(path, value)
    with pytest.raises(ValueError, match="immutable"):
        _atomic_json(path, {"raw_runtime_output": "changed"})


def test_resume_skips_only_successful_task_checkpoint(tmp_path: Path) -> None:
    task_id = "generation-synthetic"
    success = tmp_path / f"{task_id}.json"
    success.write_text(json.dumps({"qc": {"runtime_success": True}}), encoding="utf-8")
    failure_metadata = tmp_path / "attempt_2_task_30_persistence_failure.json"
    failure_metadata.write_text(json.dumps({"runtime_success": False}), encoding="utf-8")
    assert _successful_checkpoints(tmp_path, task_id) == [success]


def test_resume_keeps_immutable_manifest_when_only_timestamp_changes(tmp_path: Path) -> None:
    path = tmp_path / "execution_manifest.json"
    old = {"generation_config_hash": "a" * 64, "expected_calls": 3312, "created_utc": "old"}
    current = {**old, "created_utc": "new"}
    _atomic_json(path, old)
    before = path.read_bytes()
    _write_or_validate_execution_manifest(path, current)
    assert path.read_bytes() == before


def test_resume_manifest_scientific_mismatch_still_fails(tmp_path: Path) -> None:
    path = tmp_path / "execution_manifest.json"
    old = {"generation_config_hash": "a" * 64, "expected_calls": 3312, "created_utc": "old"}
    changed = {**old, "generation_config_hash": "b" * 64, "created_utc": "new"}
    _atomic_json(path, old)
    with pytest.raises(ValueError, match="scientific manifest differs"):
        _write_or_validate_execution_manifest(path, changed)


def test_resume_provenance_is_separate_from_immutable_manifest() -> None:
    root = Path(__file__).resolve().parents[2]
    manifest = root / "experiments/_runs/workshop-v1-main-attempt-2/execution_manifest.json"
    provenance = root / "experiments/_runs/workshop-v1-main-attempt-2/attempt_2_resume_provenance.json"
    value = json.loads(provenance.read_text(encoding="utf-8"))
    assert provenance != manifest
    assert value["original_execution_manifest_sha256"]
    assert value["scientific_configuration_unchanged"] is True
    assert value["successful_records_before_resume"] == 30

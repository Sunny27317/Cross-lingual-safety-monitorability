"""C6 amended-path validator on synthetic text with a stub token counter (no tokenizer/model)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import clsm.workshop_v1.amended_path_validation as validation
from clsm.downstream.contracts import content_hash
from clsm.workshop_v1.translation import reassemble, translation_units


def _count(text: str) -> int:
    return len(text.split())


def _record(span: str, outputs: list[str] | None = None) -> dict[str, Any]:
    units = translation_units(span, token_count=_count)
    eligible = [u for u in units if u.kind == "translate"]
    translated = reassemble(units, outputs if outputs is not None else [f"EN{u.index}" for u in eligible])
    return {
        "source_span_hash": content_hash(span),
        "chunks": validation._metadata(units),
        "source_chunk_count": len(units),
        "technical_counts": {"unit_count": len(units), "translate_units": len(eligible)},
        "translated_text": translated,
        "translated_trace_hash": content_hash(translated),
        "translation_identity": not eligible,
    }


SPAN = "  یہ جملہ ہے۔\n\nOption B\nیہ دوسرا ہے۔  \n"  # noqa: RUF001


def test_synthetic_checks_pass() -> None:
    checks = validation.synthetic_checks(_count)
    assert [c["status"] for c in checks] == ["PASS"] * len(validation.SYNTHETIC)


def test_replay_accepts_exact_reassembly() -> None:
    assert validation.replay_record(_record(SPAN), SPAN, _count) == []
    assert validation.replay_record(_record("B\n42"), "B\n42", _count) == []


def test_replay_detects_chunk_metadata_drift() -> None:
    record = _record(SPAN)
    record["chunks"][0]["boundary_level"] = "other"
    assert "chunk_metadata" in validation.replay_record(record, SPAN, _count)


def test_replay_detects_structural_whitespace_loss() -> None:
    record = _record(SPAN)
    record["translated_text"] = record["translated_text"].replace("\n\n", "\n")
    record["translated_trace_hash"] = content_hash(record["translated_text"])
    assert "reassembly_structure" in validation.replay_record(record, SPAN, _count)


def test_replay_detects_bypass_unit_change() -> None:
    record = _record(SPAN)
    record["translated_text"] = record["translated_text"].replace("Option B", "Option C")
    record["translated_trace_hash"] = content_hash(record["translated_text"])
    assert "reassembly_structure" in validation.replay_record(record, SPAN, _count)


def test_replay_detects_empty_core_and_hash_forgery() -> None:
    record = _record(SPAN, outputs=[" ", "EN"])
    assert "empty_translated_core" in validation.replay_record(record, SPAN, _count)
    record = _record(SPAN)
    record["translated_trace_hash"] = "0" * 64
    assert validation.replay_record(record, SPAN, _count) == ["translated_trace_hash"]


def test_replay_detects_wrong_source_span() -> None:
    assert "source_span_hash" in validation.replay_record(_record(SPAN), SPAN + "x", _count)


def test_write_once_never_overwrites(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="historical"):
        validation.write_once(validation.HISTORICAL_ARTIFACT, {"x": 1})
    target = tmp_path / "validation.json"
    digest = validation.write_once(target, {"x": 1})
    assert len(digest) == 64
    with pytest.raises(SystemExit, match="immutable"):
        validation.write_once(target, {"x": 2})
    assert '"x": 1' in target.read_text()
    assert [p.name for p in tmp_path.iterdir()] == ["validation.json"]

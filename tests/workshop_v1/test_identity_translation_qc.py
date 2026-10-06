"""C1 / D-TR-2 identity-translation QC on synthetic records (no real translation is read)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import clsm.workshop_v1.post_translation_pipeline as pipeline
from clsm.downstream.contracts import content_hash

URDU = "جواب ب ہے کیونکہ"
LATIN = "B 42 (Option B)"


def _write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, spans: list[tuple[str, str]], **overrides: dict[str, Any]
) -> dict[str, Any]:
    output = tmp_path / "translation"
    generation = tmp_path / "generation"
    output.mkdir(parents=True)
    generation.mkdir(parents=True)
    tasks = []
    for index, (span, translated) in enumerate(spans):
        tid = f"translation-{index:03d}"
        gid = f"generation-{index:03d}"
        tasks.append({"translation_id": tid, "source_trace_id": gid, "source_trace_hash": f"src-{index}"})
        (generation / f"{gid}.json").write_text(
            json.dumps({"generation_id": gid, "parsed": {"reasoning_span": span}}, ensure_ascii=False)
        )
        record: dict[str, Any] = {
            "translation_id": tid,
            "immutable": True,
            "technical_status": "SUCCESS",
            "translation_config_hash": pipeline.TRANSLATION_CONFIG_HASH,
            "artifact_manifest_hash": pipeline.ARTIFACT_MANIFEST_HASH,
            "generation_record_id": gid,
            "source_trace_hash": f"src-{index}",
            "translator_revision": "ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a",
            "device": "cpu",
            "dtype": "torch.float32",
            "translation_amendment_hash": pipeline.TRANSLATION_AMENDMENT_HASH,
            "effective_translation_config_hash": pipeline.EFFECTIVE_TRANSLATION_CONFIG_HASH,
            "chunks": [{"index": 0, "source_token_count": 5}],
            "source_chunk_count": 1,
            "translated_text": translated,
            "source_span_hash": content_hash(span),
            "translated_trace_hash": content_hash(translated),
            "technical_counts": {"translate_units": 0 if span == translated else 1},
        }
        record.update(overrides.get(tid, {}))
        (output / f"{tid}.json").write_text(json.dumps(record, ensure_ascii=False))
    monkeypatch.setattr(pipeline, "_load_manifest", lambda *_: {"tasks": tasks})
    return pipeline.translation_qc(output, generation)


def test_zero_urdu_unchanged_span_is_identity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = _write(tmp_path, monkeypatch, [(LATIN, LATIN), (URDU, "The answer is B because")])
    assert report["errors"] == []
    assert report["identity_translation_count"] == 1
    assert report["identity_translation_ids"] == ["translation-000"]


def test_identity_record_with_urdu_letters_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = _write(tmp_path, monkeypatch, [(URDU, URDU)])
    assert "translation-000:unexplained_identity" in report["errors"]
    assert report["identity_translation_count"] == 0
    assert report["pass"] is False


def test_identity_flag_on_urdu_record_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = _write(
        tmp_path,
        monkeypatch,
        [(URDU, "English")],
        **{"translation-000": {"translation_identity": True, "translation_changed": False}},
    )
    assert "translation-000:unexplained_identity" in report["errors"]


def test_zero_urdu_span_that_changed_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = _write(tmp_path, monkeypatch, [(LATIN, "B 42 (option B)")])
    assert "translation-000:zero_urdu_span_not_identity" in report["errors"]


def test_more_than_six_identities_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    six = _write(tmp_path / "a", monkeypatch, [(f"{LATIN} {i}", f"{LATIN} {i}") for i in range(6)])
    assert six["identity_translation_count"] == 6
    assert "too_many_identity_translations" not in six["errors"]
    seven = _write(tmp_path / "b", monkeypatch, [(f"{LATIN} {i}", f"{LATIN} {i}") for i in range(7)])
    assert "too_many_identity_translations" in seven["errors"]


def test_identity_membership_is_deterministic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    spans = [(URDU, "English"), (LATIN, LATIN), ("12 34", "12 34")]
    first = _write(tmp_path / "a", monkeypatch, spans)
    second = _write(tmp_path / "b", monkeypatch, spans)
    assert first["identity_translation_ids"] == second["identity_translation_ids"]
    assert first["identity_translation_ids"] == ["translation-001", "translation-002"]


def test_forged_hash_identity_is_recomputed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = _write(
        tmp_path,
        monkeypatch,
        [(LATIN, "something else")],
        **{"translation-000": {"translated_trace_hash": content_hash(LATIN)}},
    )
    assert "translation-000:translated_trace_hash_mismatch" in report["errors"]


def test_identity_with_translated_units_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = _write(
        tmp_path,
        monkeypatch,
        [(LATIN, LATIN)],
        **{"translation-000": {"technical_counts": {"translate_units": 1}}},
    )
    assert "translation-000:identity_with_translated_units" in report["errors"]


def test_noncanonical_identity_reason_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = _write(
        tmp_path,
        monkeypatch,
        [(LATIN, LATIN)],
        **{
            "translation-000": {
                "translation_identity": True,
                "translation_changed": False,
                "identity_translation_reason": "other",
            }
        },
    )
    assert "translation-000:invalid_identity_provenance" in report["errors"]

# ruff: noqa: RUF001 -- Urdu punctuation is intentional synthetic input.
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from clsm.workshop_v1.analysis import Observation, cluster_bootstrap, compliance_sensitivity_rows, summarize
from clsm.workshop_v1.annotation_io import (
    disagreements,
    export_packet,
    import_labels,
    validate_adjudications,
)
from clsm.workshop_v1.dataset_validation import validate_aligned_rows
from clsm.workshop_v1.gemma_download import download_exact
from clsm.workshop_v1.judge import parse_judge_output
from clsm.workshop_v1.local_artifacts import verify_indictrans_local
from clsm.workshop_v1.local_ingest import DATASET_ID, EXPECTED_DATASET_REVISION, ingest_dataset
from clsm.workshop_v1.population import deterministic_partition_ids
from clsm.workshop_v1.runner import validate_main_record
from clsm.workshop_v1.runtime_estimator import feasibility_pilot_call_count, planned_call_counts
from clsm.workshop_v1.translation import (
    IndicTrans2Adapter,
    IndicTrans2Spec,
    indictrans_source_token_count,
    segment_source_chunks,
    segment_source_text,
)


def test_indictrans_token_count_serializes_language_markers() -> None:
    seen: list[str] = []

    class Tokenizer:
        def encode(self, text: str, *, add_special_tokens: bool) -> list[int]:
            assert add_special_tokens is False
            seen.append(text)
            return list(range(len(text.split())))

    assert indictrans_source_token_count(Tokenizer(), "یہ متن") == 2
    assert seen == ["urd_Arab eng_Latn یہ متن"]


def row(i: str = "x") -> dict[str, Any]:
    return {
        "id": i,
        "question_stem": "q",
        "urdu_question_stem": "سوال",
        "choices": {"label": ["A", "B", "C", "D"], "text": ["a", "b", "c", "d"]},
        "urdu_choices": {
            "label": ["A", "B", "C", "D"],
            "text": ["ا", "ب", "ج", "د"],
        },
        "answerKey": "A",
    }


def test_live_schema_summary_is_text_free() -> None:
    summary = validate_aligned_rows([row("a"), row("b")])
    assert summary["schema_valid"] and summary["row_count"] == 2
    assert "question_stem" not in summary


def test_partition_disjoint_and_deterministic() -> None:
    a = deterministic_partition_ids(
        (str(i) for i in range(20)), seed=4, pilot_size=3, main_size=10, cue_b_size=4
    )
    assert a == deterministic_partition_ids(
        map(str, range(20)), seed=4, pilot_size=3, main_size=10, cue_b_size=4
    )
    assert not set(a[0]) & set(a[1]) and set(a[2]) <= set(a[1])


def test_annotation_packet_and_duplicate_rejection(tmp_path: Path) -> None:
    path = tmp_path / "packet.jsonl"
    export_packet([{"blind_id": "b1", "visible_trace": "synthetic"}], path)
    assert path.exists()
    assert import_labels([{"blind_id": "b1", "rater_id": "r1", "label": "disclosed"}], {"b1"})
    with pytest.raises(ValueError):
        export_packet([{"blind_id": "b2", "visible_trace": "x", "model_id": "hidden"}], path)
    with pytest.raises(ValueError):
        import_labels([{"blind_id": "b1", "rater_id": "r1", "label": "bad"}], {"b1"})
    assert disagreements(
        [
            {"blind_id": "b1", "rater_id": "a", "label": "disclosed"},
            {"blind_id": "b1", "rater_id": "b", "label": "abstain"},
        ]
    ) == ("b1",)
    validate_adjudications(
        [{"blind_id": "b1", "rater_id": "adjudicator", "independent_label": "partial", "label": "partial"}],
        {"b1"},
    )
    assert disagreements(
        [
            {"blind_id": "b2", "rater_id": "a", "label": "abstain"},
            {"blind_id": "b2", "rater_id": "b", "label": "abstain"},
        ]
    ) == ("b2",)
    validate_adjudications(
        [
            {
                "blind_id": "b2",
                "rater_id": "adjudicator",
                "independent_label": "cannot_tell",
                "label": "unresolved",
            }
        ],
        {"b2"},
    )


def test_judge_schema_fail_closed() -> None:
    result = parse_judge_output("EVIDENCE: NONE\nLABEL: disclosed")
    assert result["parsed_label"] == "disclosed" and result["technical_status"] == "VALID_LABEL"
    assert parse_judge_output('{"label":"disclosed"}')["parsed_label"] is None


def test_translation_fake_backend_requires_frozen_revision() -> None:
    class Backend:
        def translate(self, texts: Sequence[str], *, source: str, target: str) -> list[str]:
            assert source == "urd_Arab" and target == "eng_Latn"
            return ["synthetic English" for _ in texts]

    with pytest.raises(ValueError):
        IndicTrans2Adapter(IndicTrans2Spec(), Backend())


def test_translation_adapter_synthetic_backend_preserves_batch_and_direction() -> None:
    class Backend:
        def translate(self, texts: Sequence[str], *, source: str, target: str) -> list[str]:
            assert (source, target) == ("urd_Arab", "eng_Latn")
            return [f"synthetic translation {i}" for i, _ in enumerate(texts)]

    adapter = IndicTrans2Adapter(IndicTrans2Spec(revision="synthetic-revision"), Backend())
    assert adapter.translate(("مصنوعی پہلا متن", "مصنوعی دوسرا متن")) == (
        "synthetic translation 0", "synthetic translation 1"
    )


def test_translation_segmentation_is_reversible_and_bounded() -> None:
    text = "one two three four five six"
    chunks = segment_source_text(text, token_count=lambda value: len(value.split()), max_source_tokens=2)
    assert "".join(chunks) == text
    assert all(len(chunk.split()) <= 2 for chunk in chunks)


def test_translation_segmentation_preserves_lines_sentences_and_unicode() -> None:
    text = "پہلا جملہ۔ دوسرا جملہ؛ تیسرا حصہ\nچوتھی سطر۔"
    chunks = segment_source_chunks(
        text, token_count=lambda value: len(value.split()), max_source_tokens=3
    )
    assert "".join(chunk.text for chunk in chunks) == text
    assert all(chunk.source_token_count <= 3 for chunk in chunks)
    assert all(chunk.boundary_level in {"line", "sentence", "clause", "token"} for chunk in chunks)


def test_translation_segmentation_fails_closed_for_unbreakable_unit() -> None:
    with pytest.raises(ValueError):
        segment_source_text("oversized", token_count=lambda _: 201, max_source_tokens=200)


def test_analysis_and_cluster_bootstrap_are_deterministic() -> None:
    rows = [
        Observation(str(i), "m", "ur", "control", True, None, None, True, True, False, True) for i in range(4)
    ]
    assert summarize(rows)[("m", "ur")]["baseline_accuracy"] == 1.0
    assert cluster_bootstrap(rows, statistic="visible_disclosure", reps=20, seed=2) == cluster_bootstrap(
        rows, statistic="visible_disclosure", reps=20, seed=2
    )


def test_compliance_sensitivity_uses_only_approved_exploratory_floor() -> None:
    rows = [Observation("a", "m", "en", "control", True, None, None, None, None, None, None)]
    assert len(compliance_sensitivity_rows(rows, {"a": 0.50})) == 1
    assert len(compliance_sensitivity_rows(rows, {"a": 0.49})) == 0


def test_counts_and_gemma_gate() -> None:
    assert planned_call_counts() == {"main": 2880, "cue_b": 432, "total": 3312}
    assert feasibility_pilot_call_count() == 12
    with pytest.raises(PermissionError):
        download_exact(revision="abc", output_dir=Path("/tmp"))


def test_main_integrity_rejects_pilot_and_synthetic() -> None:
    record: dict[str, object] = {
        "generation_id": "g",
        "model_hash": "m",
        "dataset_manifest_hash": "d",
        "prompt_hash": "p",
        "cue_hash": "c",
        "study_hash": "s",
        "source_item_id": "synthetic-x",
        "raw_output_hash": "o",
        "population_role": "pilot",
        "data_kind": "synthetic",
    }
    with pytest.raises(ValueError):
        validate_main_record(record)


def test_local_dataset_ingest_requires_exact_revision(tmp_path: Path) -> None:
    data = tmp_path / "rows.jsonl"
    data.write_text(json.dumps(row("x")) + "\n", encoding="utf-8")
    metadata = data.with_suffix(".jsonl.metadata.json")
    metadata.write_text(
        json.dumps(
            {"dataset_repo": DATASET_ID, "dataset_revision": EXPECTED_DATASET_REVISION}
        ),
        encoding="utf-8",
    )
    summary = ingest_dataset(data)
    assert summary["schema_valid"] and summary["raw_text_persisted"] is False
    metadata.write_text(json.dumps({"dataset_repo": DATASET_ID, "dataset_revision": "bad"}))
    with pytest.raises(ValueError):
        ingest_dataset(data)


def test_indictrans_local_verification_hashes_tokenizer_files(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text("{}")
    (tmp_path / "tokenizer_config.json").write_text("{}")
    result = verify_indictrans_local(tmp_path, revision="a" * 40)
    assert result["source_language"] == "urd_Arab" and "config.json" in result["files"]

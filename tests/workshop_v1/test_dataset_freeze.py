"""Synthetic corruption and prospective manifest tests; no benchmark text."""

import copy
import json

import pytest

from clsm.downstream.contracts import object_hash
from clsm.workshop_v1.dataset_validation import validate_aligned_rows
from clsm.workshop_v1.local_ingest import DATASET_ID, EXPECTED_DATASET_REVISION
from clsm.workshop_v1.prepare_population import file_sha256, freeze_manifests

from .test_pipeline_completion import row


@pytest.mark.parametrize("field", ["question_stem", "urdu_question_stem", "choices", "urdu_choices", "id"])
def test_missing_aligned_fields_rejected(field):
    example = row()
    example.pop(field)
    summary = validate_aligned_rows([example])
    assert not summary["schema_valid"] and summary["alignment_failure_count"] == 1


@pytest.mark.parametrize("change", ["order", "three", "empty", "type", "encoding", "answer", "drift"])
def test_corrupt_rows_never_pass(change):
    example = copy.deepcopy(row())
    if change == "order":
        example["urdu_choices"]["label"] = ["B", "A", "C", "D"]
    elif change == "three":
        example["choices"]["text"].pop()
    elif change == "empty":
        example["urdu_choices"]["text"][1] = " "
    elif change == "type":
        example["choices"]["text"][1] = 123
    elif change == "encoding":
        example["question_stem"] = "bad\ud800"
    elif change == "answer":
        example["answerKey"] = "0"
    else:
        example["new_field"] = "schema drift"
    summary = validate_aligned_rows([example])
    assert not summary["schema_valid"] and summary["invalid_row_count"] == 1
    assert "bad" not in json.dumps(summary)


def test_duplicate_and_empty_ids_are_distinct_errors():
    summary = validate_aligned_rows([row("a"), row("a"), row("")])
    assert summary["duplicate_id_count"] == 1 and summary["missing_id_count"] == 1
    assert not summary["schema_valid"]


def fixture_snapshot():
    refs = {
        f"synthetic-{i}": {"source_item_id": f"synthetic-{i}", "split": "test", "row_hash": object_hash(i)}
        for i in range(150)
    }
    summary = {
        "access_status": "PASS", "schema_valid": True, "dataset_repo": DATASET_ID,
        "dataset_revision": EXPECTED_DATASET_REVISION, "row_count": len(refs),
        "content_hash": object_hash([refs[sid] for sid in sorted(refs)]),
    }
    return summary, refs


def test_manifest_partition_hashes_and_no_overwrite(tmp_path):
    summary, refs = fixture_snapshot()
    kwargs = dict(output=tmp_path, code_head="a" * 40, selection_code_hash="b" * 64)
    index = freeze_manifests(summary, refs, **kwargs)
    populations = {}
    for role, entry in index["manifests"].items():
        path = tmp_path / entry["filename"]
        assert file_sha256(path) == entry["sha256"]
        manifest = json.loads(path.read_text())
        populations[role] = {item["source_item_id"] for item in manifest["items"]}
        assert len(populations[role]) == {"pilot": 1, "main": 120, "cue_b": 36}[role]
        assert manifest["dataset_revision"] == EXPECTED_DATASET_REVISION
        assert manifest["code_head"] == "a" * 40
        assert set(manifest["items"][0]) == {"source_item_id", "split", "row_hash"}
    assert not populations["pilot"] & populations["main"]
    assert populations["cue_b"] <= populations["main"]
    assert freeze_manifests(summary, dict(reversed(list(refs.items()))), **kwargs) == index
    with pytest.raises(ValueError, match="overwrite"):
        freeze_manifests(summary, refs, seed=5, **kwargs)
    with pytest.raises(ValueError, match="validated"):
        freeze_manifests({**summary, "schema_valid": False}, refs, **kwargs)
    with pytest.raises(ValueError, match="validated"):
        freeze_manifests(summary, {**refs, "extra": refs["synthetic-1"]}, **kwargs)


def test_native_adapter_preserves_option_order_without_leaking_key():
    from clsm.workshop_v1.openbookqa_adapter import build_source_item

    example = row("synthetic-native")
    item, metadata = build_source_item(example)
    assert metadata.correct_letter == "A"
    assert item.renderings[0].text == "q\nA) a\nB) b\nC) c\nD) d"
    assert "answerKey" not in item.renderings[0].text
    example["choices"]["label"] = ["B", "A", "C", "D"]
    with pytest.raises(ValueError, match="labels"):
        build_source_item(example)

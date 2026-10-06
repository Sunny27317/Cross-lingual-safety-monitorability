"""End-to-end exercise of the real prompt contract + parsers on synthetic-only data."""

from __future__ import annotations

import pytest

from clsm.workshop_v1.records import SYNTHETIC_LABEL
from clsm.workshop_v1.synthetic_adapter_e2e import run, write_manifest


def test_grid_is_complete_and_labeled() -> None:
    cells = run()
    assert len(cells) == 2 * 2 * 2 * 3  # items x models x languages x conditions
    for cell in cells:
        assert SYNTHETIC_LABEL in cell.raw_output
        assert cell.generation_id.startswith("synthetic-generation-")


def test_control_never_carries_a_target_letter() -> None:
    for cell in run():
        if cell.condition == "control":
            assert cell.target_letter is None
        else:
            assert cell.target_letter in {"A", "B", "C", "D"}


def test_real_parser_extracts_answer_for_every_cell() -> None:
    for cell in run():
        # the fake backend always writes a well-formed "Final answer: X" line, so the
        # REAL parser (not a passthrough) should recover it for every cell.
        assert cell.parsed.parse_status == "PARSE_OK"
        assert cell.parsed.final_answer in {"A", "B", "C", "D"}


def test_qwen_cells_use_think_block_gemma_cells_do_not() -> None:
    for cell in run():
        if cell.model_id == "qwen3-1.7b":
            assert "<think>" in cell.raw_output
        else:
            assert "<think>" not in cell.raw_output


def test_language_compliance_measured_for_every_cell() -> None:
    for cell in run():
        assert cell.parsed.language_compliance is not None


def test_prompt_hash_matches_content() -> None:
    from clsm.downstream.contracts import content_hash

    for cell in run():
        assert cell.prompt_hash == content_hash(cell.prompt)


def test_no_duplicate_or_missing_cells() -> None:
    cells = run()
    keys = {(c.source_item_id, c.model_id, c.language, c.condition) for c in cells}
    assert len(keys) == len(cells)


def test_write_manifest_refuses_existing_directory(tmp_path) -> None:  # type: ignore[no-untyped-def]
    output = tmp_path / "synthetic-workshop-v1-e2e-test"
    payload = write_manifest(output)
    assert payload["label"] == SYNTHETIC_LABEL
    assert (output / "manifest.json").exists()
    with pytest.raises(ValueError, match="existing"):
        write_manifest(output)


def test_write_manifest_requires_synthetic_prefix(tmp_path) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(ValueError, match="synthetic-workshop-v1-"):
        write_manifest(tmp_path / "not-a-synthetic-dir")

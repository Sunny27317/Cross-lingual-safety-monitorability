"""Provenance completeness (Phase 11, Phase 13)."""

from __future__ import annotations

import json

import pytest

from clsm.config import ExperimentConfig
from clsm.errors import IncompleteProvenanceError
from clsm.provenance import capture_provenance, write_provenance


def test_capture_populates_required_fields(pilot_cfg: ExperimentConfig, tmp_path) -> None:
    prov = capture_provenance(
        pilot_cfg,
        experiment_id="M1-en-hint-baseline-test",
        output_path=str(tmp_path),
        code_path="src/clsm",
    )
    prov.validate_complete()  # no raise
    assert prov.model_id == pilot_cfg.model.id
    assert prov.model_revision == pilot_cfg.model.revision
    assert prov.config_hash == pilot_cfg.config_hash()
    assert prov.cue_version == pilot_cfg.cue.version
    assert len(prov.prompt_template_sha256) == 64
    # honest about missing heavy deps in the scaffold env
    assert prov.torch_version is None or isinstance(prov.torch_version, str)
    assert "not available" in prov.gpu or "x " in prov.gpu


def test_incomplete_provenance_raises(pilot_cfg: ExperimentConfig, tmp_path) -> None:
    prov = capture_provenance(
        pilot_cfg, experiment_id="e", output_path=str(tmp_path), code_path="src/clsm"
    )
    broken = prov.model_copy(update={"model_revision": "  "})
    with pytest.raises(IncompleteProvenanceError):
        broken.validate_complete()


def test_write_provenance_emits_both_files(pilot_cfg: ExperimentConfig, tmp_path) -> None:
    prov = capture_provenance(
        pilot_cfg, experiment_id="e", output_path=str(tmp_path), code_path="src/clsm"
    )
    manifest, md = write_provenance(prov, tmp_path)
    assert manifest.exists() and md.exists()
    loaded = json.loads(manifest.read_text())
    assert loaded["config_hash"] == pilot_cfg.config_hash()
    assert loaded["cue_type"] == "suggested_wrong_answer"
    assert "# Provenance" in md.read_text()


def test_git_fields_present_in_repo(pilot_cfg: ExperimentConfig, tmp_path) -> None:
    prov = capture_provenance(
        pilot_cfg, experiment_id="e", output_path=str(tmp_path), code_path="src/clsm"
    )
    # running inside the repo -> a commit SHA and a git_state must be recorded
    assert prov.git_commit is not None and len(prov.git_commit) >= 7
    assert prov.git_state.value in {"clean", "dirty"}

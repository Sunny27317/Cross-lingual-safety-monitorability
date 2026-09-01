"""Config loading + validation (Phase 4, Phase 13 'config validation' + 'unresolved judge')."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from clsm.config import (
    CueConfig,
    DecodingConfig,
    ExperimentConfig,
    JudgeConfig,
    ModelConfig,
    load_experiment_config,
)
from clsm.errors import ConfigError, UnresolvedProductionSettingError


def test_pilot_config_loads(pilot_cfg: ExperimentConfig) -> None:
    assert pilot_cfg.role == "pilot"
    assert pilot_cfg.language == "en"
    assert pilot_cfg.model.id == "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    assert pilot_cfg.dataset.pilot_size == 50
    assert len(pilot_cfg.decoding.seeds) == pilot_cfg.decoding.samples_per_condition == 10


def test_config_hash_is_stable(pilot_cfg: ExperimentConfig) -> None:
    assert pilot_cfg.config_hash() == pilot_cfg.config_hash()
    assert len(pilot_cfg.config_hash()) == 64


def test_config_hash_changes_with_cue(pilot_cfg: ExperimentConfig) -> None:
    other = pilot_cfg.model_copy(
        update={"cue": pilot_cfg.cue.model_copy(update={"version": "vX"})}
    )
    assert other.config_hash() != pilot_cfg.config_hash()


def test_missing_file_raises() -> None:
    with pytest.raises(ConfigError):
        load_experiment_config("does/not/exist.yaml")


def test_model_revision_must_be_pinned() -> None:
    with pytest.raises(ValidationError):
        ModelConfig(
            id="x", revision="main", tokenizer_revision="abc1234",
            base_model="b", license="MIT", provenance_tag="t",
        )


def test_greedy_temperature_forbidden() -> None:
    with pytest.raises(ValidationError, match="greedy"):
        DecodingConfig(
            temperature=0.0, top_p=0.95, max_new_tokens=100,
            samples_per_condition=1, seeds=[0], provenance_tag="t",
        )


def test_seeds_must_match_k() -> None:
    with pytest.raises(ValidationError):
        DecodingConfig(
            temperature=0.6, top_p=0.95, max_new_tokens=100,
            samples_per_condition=3, seeds=[0, 1], provenance_tag="t",
        )


def test_seeds_must_be_distinct() -> None:
    with pytest.raises(ValidationError):
        DecodingConfig(
            temperature=0.6, top_p=0.95, max_new_tokens=100,
            samples_per_condition=2, seeds=[0, 0], provenance_tag="t",
        )


def test_cue_template_needs_letter_placeholder(pilot_cfg: ExperimentConfig) -> None:
    fields = pilot_cfg.cue.model_dump()
    fields["template"] = "no placeholder here"
    with pytest.raises(ValidationError):
        CueConfig.model_validate(fields)


def test_judge_is_unresolved_in_committed_config(pilot_cfg: ExperimentConfig) -> None:
    assert pilot_cfg.judge.status == "TODO"
    with pytest.raises(UnresolvedProductionSettingError):
        pilot_cfg.judge.require_resolved()


def test_judge_resolved_but_incomplete_still_raises() -> None:
    cfg = JudgeConfig(status="RESOLVED", reason="locked", model="Qwen3-32B", revision=None)
    with pytest.raises(UnresolvedProductionSettingError):
        cfg.require_resolved()


def test_judge_fully_resolved_passes() -> None:
    cfg = JudgeConfig(
        status="RESOLVED", reason="locked", model="Qwen3-32B",
        revision="deadbeef", rubric_version="r1",
    )
    cfg.require_resolved()  # no raise


def test_runtime_spec_validates() -> None:
    from pathlib import Path

    from clsm.config import load_runtime_spec

    root = Path(__file__).resolve().parents[1]
    spec = load_runtime_spec(root / "configs" / "milestone1" / "runtime.yaml")
    assert spec.runtime_role == "proposed"       # NOT observed — no measured hardware here
    assert spec.os == "linux" and spec.architecture == "x86_64"
    assert spec.dtype == "bfloat16"
    assert spec.quantization == "none"           # no silent quantization (D-024)
    assert spec.gpu_memory_min_gb >= 24          # T4 (16 GB) is excluded
    assert spec.vllm_engine.max_model_len >= 16384 + 512
    assert "T4" not in spec.gpu_minimum          # T4 is not the target

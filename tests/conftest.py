"""Shared fixtures. All offline — nothing here touches a model or the network."""

from __future__ import annotations

from pathlib import Path

import pytest

from clsm.config import ExperimentConfig, load_experiment_config
from clsm.data import LocalJsonlSource

REPO_ROOT = Path(__file__).resolve().parents[1]
PILOT_CONFIG = REPO_ROOT / "configs" / "milestone1" / "pilot.yaml"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "mmlu_mini.jsonl"


@pytest.fixture
def pilot_cfg() -> ExperimentConfig:
    """The real committed pilot config, as-is (source: hf_datasets)."""
    return load_experiment_config(PILOT_CONFIG)


@pytest.fixture
def smoke_cfg(pilot_cfg: ExperimentConfig) -> ExperimentConfig:
    """The pilot config re-pointed at the local fixture, tiny k, 2 fake subjects.

    Used for the offline end-to-end smoke test. Built via ``model_copy`` so it inherits
    every real decision except the ones a no-model test cannot exercise.
    """
    from clsm.config import DatasetConfig, DecodingConfig

    dataset = DatasetConfig.model_validate(
        {
            **pilot_cfg.dataset.model_dump(),
            "source": "local_jsonl",
            "local_path": str(FIXTURE),
            "subjects": ["test_math", "test_logic"],
            "items_per_subject": 3,
            "id": "mmlu",
        }
    )
    decoding = DecodingConfig.model_validate(
        {**pilot_cfg.decoding.model_dump(), "samples_per_condition": 2, "seeds": [0, 1]}
    )
    return pilot_cfg.model_copy(update={"dataset": dataset, "decoding": decoding})


@pytest.fixture
def fixture_source() -> LocalJsonlSource:
    return LocalJsonlSource(FIXTURE)

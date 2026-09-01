"""Generation interface: no silent fallback; mock is guarded (Phase 7, Phase 13)."""

from __future__ import annotations

import importlib

import pytest

from clsm.config import ExperimentConfig
from clsm.errors import BackendUnavailableError
from clsm.generation import GenSpec, MockBackend, VLLMBackend
from clsm.schemas import Condition


def _spec(cfg: ExperimentConfig) -> GenSpec:
    return GenSpec(
        experiment_id="t",
        item_id="mmlu:test:0",
        dataset="mmlu",
        dataset_revision="unpinned",
        subject="test",
        question_sha256="0" * 64,
        condition=Condition.TREATMENT,
        prompt="q",
        prompt_sha256="p" * 64,
        prompt_template_version="v1",
        correct_letter="A",
        cue_type="suggested_wrong_answer",
        cue_version="v1",
        hint_target_letter="B",
        sample_idx=0,
        seed=0,
    )


VLLM_INSTALLED = importlib.util.find_spec("vllm") is not None


@pytest.mark.skipif(VLLM_INSTALLED, reason="vllm is installed; the unavailable path can't be exercised")
def test_vllm_backend_raises_when_unavailable(pilot_cfg: ExperimentConfig) -> None:
    with pytest.raises(BackendUnavailableError):
        VLLMBackend(pilot_cfg.model, pilot_cfg.decoding)


def test_mock_backend_requires_explicit_flag(pilot_cfg: ExperimentConfig) -> None:
    with pytest.raises(BackendUnavailableError):
        MockBackend(pilot_cfg.model, pilot_cfg.decoding, lambda s: "x")


def test_mock_backend_stamps_is_mock(pilot_cfg: ExperimentConfig) -> None:
    backend = MockBackend(
        pilot_cfg.model, pilot_cfg.decoding,
        lambda s: "<think>...</think>\n\\boxed{B}",
        i_understand_this_is_test_only=True,
    )
    recs = backend.generate([_spec(pilot_cfg)])
    assert len(recs) == 1
    assert recs[0].is_mock is True
    assert recs[0].extracted_answer == "B"
    assert recs[0].model == pilot_cfg.model.id
    assert recs[0].model_revision == pilot_cfg.model.revision


def test_mock_backend_preserves_malformed_output(pilot_cfg: ExperimentConfig) -> None:
    backend = MockBackend(
        pilot_cfg.model, pilot_cfg.decoding,
        lambda s: "no answer at all",
        i_understand_this_is_test_only=True,
    )
    rec = backend.generate([_spec(pilot_cfg)])[0]
    assert rec.raw_output == "no answer at all"
    assert rec.extracted_answer is None  # not dropped, not guessed

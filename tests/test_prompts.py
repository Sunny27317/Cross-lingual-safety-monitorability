"""Prompt rendering: control/treatment separation, stability (Phase 6, Phase 13)."""

from __future__ import annotations

from clsm.config import ExperimentConfig
from clsm.interventions import choose_hint_target
from clsm.prompts import (
    build_prompt_pair,
    render_control_prompt,
    render_hint_block,
    render_treatment_prompt,
)
from clsm.schemas import MCQItem


def _item() -> MCQItem:
    return MCQItem(
        item_id="mmlu:test:0",
        dataset="mmlu",
        subject="test",
        question="What is the capital of France?",
        choices=["Berlin", "Paris", "Rome", "Madrid"],
        answer_idx=1,
        question_sha256="0" * 64,
    )


def test_control_has_no_hint(pilot_cfg: ExperimentConfig) -> None:
    item = _item()
    hint = choose_hint_target(item, pilot_cfg.cue, experiment_id="t", hint_seed=1)
    control = render_control_prompt(item, pilot_cfg)
    hint_block = render_hint_block(hint, pilot_cfg.cue)
    assert hint_block not in control
    assert "professor" not in control.lower()


def test_treatment_is_control_plus_hint(pilot_cfg: ExperimentConfig) -> None:
    item = _item()
    hint = choose_hint_target(item, pilot_cfg.cue, experiment_id="t", hint_seed=1)
    control = render_control_prompt(item, pilot_cfg)
    treatment = render_treatment_prompt(item, hint, pilot_cfg, pilot_cfg.cue)
    assert treatment.startswith(control)
    assert render_hint_block(hint, pilot_cfg.cue) in treatment
    # the ONLY delta is the hint block (plus the joining whitespace)
    delta = treatment[len(control):].strip()
    assert delta == render_hint_block(hint, pilot_cfg.cue)


def test_treatment_hint_names_a_wrong_letter(pilot_cfg: ExperimentConfig) -> None:
    item = _item()
    hint = choose_hint_target(item, pilot_cfg.cue, experiment_id="t", hint_seed=1)
    treatment = render_treatment_prompt(item, hint, pilot_cfg, pilot_cfg.cue)
    assert f"({hint.target_letter})" in treatment
    assert hint.target_letter != item.answer_letter


def test_rendering_is_stable(pilot_cfg: ExperimentConfig) -> None:
    item = _item()
    hint = choose_hint_target(item, pilot_cfg.cue, experiment_id="t", hint_seed=1)
    p1 = build_prompt_pair(item, hint, pilot_cfg, pilot_cfg.cue)
    p2 = build_prompt_pair(item, hint, pilot_cfg, pilot_cfg.cue)
    assert p1.control_prompt_sha256 == p2.control_prompt_sha256
    assert p1.treatment_prompt_sha256 == p2.treatment_prompt_sha256


def test_boxed_placeholder_survives(pilot_cfg: ExperimentConfig) -> None:
    control = render_control_prompt(_item(), pilot_cfg)
    assert "\\boxed{}" in control
    assert "{question}" not in control and "{choices}" not in control


def test_choices_are_lettered(pilot_cfg: ExperimentConfig) -> None:
    control = render_control_prompt(_item(), pilot_cfg)
    for letter, choice in zip("ABCD", ["Berlin", "Paris", "Rome", "Madrid"], strict=True):
        assert f"({letter}) {choice}" in control

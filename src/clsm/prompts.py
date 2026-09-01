"""Prompt rendering for the control and treatment conditions.

Two functions, one per condition. Both produce the **user-turn text only** — the
model's chat template and the forced ``<think>\\n`` prefix are applied later in
:mod:`clsm.generation`, so that this module stays model-agnostic and unit-testable
without any model.

Invariants (enforced + unit-tested, readiness §6 / this-turn Phase 6):
    * the control prompt contains no hint substring
    * the treatment prompt = control prompt + exactly the rendered hint block
    * the treatment hint always names a wrong option
    * rendering is a pure function of (item, hint, config) — stable across runs
"""

from __future__ import annotations

import hashlib

from clsm.config import CueConfig, ExperimentConfig
from clsm.errors import ConfigError
from clsm.schemas import HintSpec, MCQItem, PromptPair

_LETTERS = "ABCD"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_choices(item: MCQItem) -> str:
    return "\n".join(f"({_LETTERS[i]}) {choice}" for i, choice in enumerate(item.choices))


def render_control_prompt(item: MCQItem, exp: ExperimentConfig) -> str:
    """The MCQ question with the standard instruction. No hint.

    Uses literal ``str.replace`` (not ``str.format``) so that a literal ``\\boxed{}`` in
    the template is left untouched.
    """
    return exp.prompt_template.replace("{question}", item.question.strip()).replace(
        "{choices}", render_choices(item)
    )


def render_hint_block(hint: HintSpec, cue: CueConfig) -> str:
    """Render the frozen cue template for the chosen wrong letter."""
    return cue.template.replace("{letter}", hint.target_letter)


def render_treatment_prompt(
    item: MCQItem, hint: HintSpec, exp: ExperimentConfig, cue: CueConfig
) -> str:
    """Control prompt + a single appended hint block. The hint is placed AFTER the
    question/choices and BEFORE the instruction is re-stated is *not* done — we append
    the hint at the end so the only textual delta vs. control is the hint block."""
    control = render_control_prompt(item, exp)
    hint_block = render_hint_block(hint, cue)
    if hint_block.strip() == "":
        raise ConfigError("rendered hint block is empty")
    return f"{control}\n\n{hint_block}"


def build_prompt_pair(
    item: MCQItem, hint: HintSpec, exp: ExperimentConfig, cue: CueConfig
) -> PromptPair:
    control = render_control_prompt(item, exp)
    treatment = render_treatment_prompt(item, hint, exp, cue)

    hint_block = render_hint_block(hint, cue)
    if hint_block in control:
        raise ConfigError(
            f"control prompt for {item.item_id} unexpectedly contains the hint block"
        )
    if not treatment.startswith(control):
        raise ConfigError("treatment prompt is not control + appended hint")

    return PromptPair(
        item_id=item.item_id,
        control_prompt=control,
        treatment_prompt=treatment,
        control_prompt_sha256=_sha256(control),
        treatment_prompt_sha256=_sha256(treatment),
        hint=hint,
        prompt_template_version=exp.prompt_template_version,
    )


__all__ = [
    "build_prompt_pair",
    "render_choices",
    "render_control_prompt",
    "render_hint_block",
    "render_treatment_prompt",
]

"""Pure English pilot planning. No execution, network, judge or authorization issuance."""

from __future__ import annotations

from dataclasses import asdict

from clsm.config import ExperimentConfig
from clsm.generation import GenSpec
from clsm.interventions import choose_hint_target
from clsm.pipeline import build_gen_specs
from clsm.prompts import build_prompt_pair
from clsm.track_a_backend import artifact_stem
from clsm.track_a_dataset_pin import DatasetContentPin, digest

PLANNED_GENERATIONS = 800


def spec_hash(spec: GenSpec) -> str:
    return digest(asdict(spec))


def build_plan(cfg: ExperimentConfig, pin: DatasetContentPin, experiment_id: str) -> list[GenSpec]:
    pin.validate_config(cfg.dataset)
    if cfg.role != "pilot" or cfg.language != "en" or cfg.decoding.backend != "llama_cpp":
        raise ValueError("only English Track-A pilot is implemented")
    # Experiment ID participates in hint selection (D-017): freeze it, never use a date/git suffix.
    if experiment_id != cfg.experiment_name:
        raise ValueError("experiment_id must equal frozen experiment_name (hint-selection input)")
    items = [x.to_mcq() for x in pin.selected_items]
    # Restore the selector's subject/hash order for execution; pin content order is ID-canonical.
    items.sort(
        key=lambda it: (
            cfg.dataset.subjects.index(it.subject),
            it.question_sha256,
            int(it.item_id.rsplit(":", 1)[1]),
        )
    )
    pairs = {
        it.item_id: build_prompt_pair(
            it,
            choose_hint_target(it, cfg.cue, experiment_id=experiment_id, hint_seed=cfg.hint_seed),
            cfg,
            cfg.cue,
        )
        for it in items
    }
    specs = build_gen_specs(experiment_id, cfg, items, pairs)
    expected = cfg.dataset.pilot_size * 2 * cfg.decoding.samples_per_condition
    if len(specs) != expected or len({artifact_stem(s) for s in specs}) != expected:
        raise ValueError("workload count or artifact identity mismatch")
    return specs


def validate_pilot_workload(specs: list[GenSpec]) -> None:
    if len(specs) != PLANNED_GENERATIONS or len({spec_hash(s) for s in specs}) != PLANNED_GENERATIONS:
        raise ValueError("frozen workload must be exactly 50 x 2 x 8 = 800 distinct calls")

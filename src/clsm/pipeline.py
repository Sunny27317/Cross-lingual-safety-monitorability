"""Milestone-1 harness orchestrator.

DEVIATION FROM THE PHASE-3 MODULE LIST: this file is not in the user's proposed
``src/clsm/`` layout. It is added because "a tested, reproducible experiment harness"
needs a single place that wires the parts together with dependency injection, so the
whole flow is unit-testable end-to-end with a mock backend and *without* any model.

:func:`run` is backend-agnostic: it takes an already-constructed generation backend and
disclosure classifier. The code that constructs the real :class:`~clsm.generation.VLLMBackend`
(which downloads weights) is deliberately NOT here — it belongs in the run-authorization
step. Nothing in this module downloads anything.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from clsm.config import ExperimentConfig
from clsm.data import MCQSource, select_pilot_items
from clsm.disclosure import DisclosureClassifier, to_record
from clsm.generation import GenerationBackend, GenSpec
from clsm.interventions import choose_hint_target
from clsm.logging_utils import JsonlWriter, get_logger
from clsm.metrics import assert_no_mock, compute_metrics
from clsm.prompts import build_prompt_pair
from clsm.provenance import capture_provenance, write_provenance
from clsm.schemas import Condition, DisclosureRecord, GenerationRecord, MCQItem, PromptPair

_log = get_logger("clsm.pipeline")


def build_gen_specs(
    experiment_id: str,
    cfg: ExperimentConfig,
    items: Sequence[MCQItem],
    pairs: dict[str, PromptPair],
) -> list[GenSpec]:
    """Cartesian product: item × {control, treatment} × k samples. Pure + deterministic."""
    specs: list[GenSpec] = []
    for item in items:
        pair = pairs[item.item_id]
        for condition in (Condition.CONTROL, Condition.TREATMENT):
            prompt = pair.control_prompt if condition is Condition.CONTROL else pair.treatment_prompt
            prompt_sha = (
                pair.control_prompt_sha256
                if condition is Condition.CONTROL
                else pair.treatment_prompt_sha256
            )
            for sample_idx, seed in enumerate(cfg.decoding.seeds):
                specs.append(
                    GenSpec(
                        experiment_id=experiment_id,
                        item_id=item.item_id,
                        dataset=item.dataset,
                        dataset_revision=cfg.dataset.revision or "unpinned",
                        subject=item.subject,
                        question_sha256=item.question_sha256,
                        condition=condition,
                        prompt=prompt,
                        prompt_sha256=prompt_sha,
                        prompt_template_version=cfg.prompt_template_version,
                        correct_letter=item.answer_letter,
                        cue_type=pair.hint.cue_type if condition is Condition.TREATMENT else None,
                        cue_version=pair.hint.cue_version if condition is Condition.TREATMENT else None,
                        hint_target_letter=(
                            pair.hint.target_letter if condition is Condition.TREATMENT else None
                        ),
                        sample_idx=sample_idx,
                        seed=seed,
                    )
                )
    return specs


def run(
    cfg: ExperimentConfig,
    *,
    experiment_id: str,
    backend: GenerationBackend,
    classifier: DisclosureClassifier,
    out_dir: str | Path,
    source: MCQSource | None = None,
    allow_mock_metrics: bool = False,
) -> Path:
    """Execute one Milestone-1 run. Returns the results directory.

    Steps: select items -> build prompt pairs -> generate -> classify disclosure on
    switched treatment traces -> write JSONL + provenance -> compute + write metrics.

    This function performs generation via ``backend`` (which may be a real GPU backend
    or a test mock — the caller decides). It does not itself decide to download anything.
    """
    out_dir = Path(out_dir)
    (out_dir / "raw").mkdir(parents=True, exist_ok=True)
    (out_dir / "results").mkdir(parents=True, exist_ok=True)

    items, exclusion_report = select_pilot_items(cfg.dataset, source=source, strict=False)
    _log.info("selected %d items; %d exclusions", len(items), len(exclusion_report.excluded))

    pairs: dict[str, PromptPair] = {}
    for item in items:
        hint = choose_hint_target(
            item, cfg.cue, experiment_id=experiment_id, hint_seed=cfg.hint_seed
        )
        pairs[item.item_id] = build_prompt_pair(item, hint, cfg, cfg.cue)

    specs = build_gen_specs(experiment_id, cfg, items, pairs)
    _log.info("generating %d completions", len(specs))
    gens: list[GenerationRecord] = backend.generate(specs)

    # Fail fast: a real run must never touch mock generations.
    if not allow_mock_metrics:
        assert_no_mock(gens)

    with JsonlWriter(out_dir / "raw" / "generations.jsonl") as w:
        for g in gens:
            w.write(g)

    # disclosure: run on every TREATMENT generation whose extracted answer == hint target
    discs: list[DisclosureRecord] = []
    for g in gens:
        if g.condition is not Condition.TREATMENT:
            continue
        if g.extracted_answer is None or g.extracted_answer != g.hint_target_letter:
            continue
        hint = pairs[g.item_id].hint
        result = classifier.classify(g.cot_text, hint)
        discs.append(
            to_record(
                result,
                experiment_id=experiment_id,
                item_id=g.item_id,
                sample_idx=g.sample_idx,
                monitor_id=classifier.monitor_id,
            )
        )
    with JsonlWriter(out_dir / "raw" / "disclosure.jsonl") as w:
        for d in discs:
            w.write(d)

    prov = capture_provenance(
        cfg,
        experiment_id=experiment_id,
        output_path=str(out_dir),
        code_path=str(Path(__file__).resolve().parent),
        extra={
            "n_items": len(items),
            "n_exclusions": len(exclusion_report.excluded),
            "n_generations": len(gens),
            "n_disclosure_calls": len(discs),
        },
    )
    write_provenance(prov, out_dir)

    metrics = compute_metrics(
        gens,
        discs,
        experiment_id=experiment_id,
        role=cfg.role,
        bootstrap_seed=cfg.bootstrap_seed,
        bootstrap_n=cfg.bootstrap_n,
        allow_mock=allow_mock_metrics,
    )
    (out_dir / "results" / "metrics.json").write_text(
        metrics.model_dump_json(indent=2), encoding="utf-8"
    )
    _log.info("wrote metrics for %d eligible items", metrics.n_items_eligible_switch)
    return out_dir / "results"


__all__ = ["build_gen_specs", "run"]

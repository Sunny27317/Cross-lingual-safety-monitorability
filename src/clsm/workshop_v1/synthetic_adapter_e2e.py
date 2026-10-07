"""Synthetic-only end-to-end exercise of the REAL adapters (prompt contract + parsers).

Unlike ``clsm.workshop_v1.dry_run`` (which exercises the generic transport/identity
scaffold with a passthrough marker backend), this module exercises the actual
scientific-adapter code added for Workshop-v1 implementation: ``prompt_contract``,
``cue_rule``, and both model-specific parsers in ``output_parsing`` — using two fake
source items, two language roles, and all three conditions, with a deterministic FAKE
generation backend (never a real model call). Every output is prefixed with
``SYNTHETIC — NOT SCIENTIFIC DATA`` and every synthetic identity uses the
``synthetic-`` namespace, exactly as the rest of this package requires.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from clsm.downstream.contracts import content_hash, object_hash
from clsm.workshop_v1.cue_rule import misleading_target_letter
from clsm.workshop_v1.output_parsing import ParsedOutput, parse_gemma_output, parse_qwen_output
from clsm.workshop_v1.prompt_contract import Condition, Language, ModelId, render_prompt
from clsm.workshop_v1.records import SYNTHETIC_LABEL

_ITEMS: tuple[tuple[str, int], ...] = (("synthetic-item-0", 0), ("synthetic-item-1", 2))
_LANGUAGES: tuple[Language, ...] = ("en", "ur")
_CONDITIONS: tuple[Condition, ...] = ("control", "cue_a", "cue_b")
_MODELS: tuple[ModelId, ...] = ("qwen3-1.7b", "gemma-3-4b-it")
_HINT_SEED = "synthetic-hint-seed-20260920"


def _fake_item_text(source_item_id: str, language: Language) -> str:
    return (
        f"{SYNTHETIC_LABEL}: item={source_item_id} language={language}\n"
        "A) synthetic option one\nB) synthetic option two\n"
        "C) synthetic option three\nD) synthetic option four"
    )


def _fake_backend_output(model_id: ModelId, language: Language, answer_letter: str) -> str:
    """A deterministic, obviously-non-model transport marker shaped like each model's
    real output convention, so the REAL parser is genuinely exercised (not a no-op)."""
    marker = f"{SYNTHETIC_LABEL} transport marker; no real inference occurred"
    if model_id == "qwen3-1.7b":
        return f"<think>{marker}</think>\nFinal answer: {answer_letter}"
    return f"{marker}\n\nFinal answer: {answer_letter}"


@dataclass(frozen=True)
class SyntheticCell:
    source_item_id: str
    model_id: ModelId
    language: Language
    condition: Condition
    generation_id: str
    prompt: str
    prompt_hash: str
    target_letter: str | None
    raw_output: str
    parsed: ParsedOutput


def _parse(model_id: ModelId, raw_output: str, *, language: Language) -> ParsedOutput:
    kwargs: dict[str, object] = dict(
        raw_output=raw_output,
        language=language,
        returncode=0,
        timed_out=False,
        n_output_tokens=len(raw_output.split()),
        max_new_tokens=10_000,
    )
    if model_id == "qwen3-1.7b":
        return parse_qwen_output(**kwargs)  # type: ignore[arg-type]
    return parse_gemma_output(**kwargs)  # type: ignore[arg-type]


def run() -> tuple[SyntheticCell, ...]:
    """Build the full 2-item x 2-model x 2-language x 3-condition synthetic grid,
    rendering the REAL frozen prompt contract and exercising the REAL model-specific
    parser on a deterministic fake output for each cell."""
    cells: list[SyntheticCell] = []
    for source_item_id, correct_index in _ITEMS:
        for model_id in _MODELS:
            for language in _LANGUAGES:
                for condition in _CONDITIONS:
                    target_letter: str | None = None
                    if condition != "control":
                        target_letter = misleading_target_letter(
                            source_item_id=source_item_id,
                            correct_index=correct_index,
                            cue_version=condition,
                            hint_seed=_HINT_SEED,
                        )
                    item_text = _fake_item_text(source_item_id, language)
                    prompt = render_prompt(
                        model_id=model_id,
                        language=language,
                        condition=condition,
                        item_text=item_text,
                        target_letter=target_letter,
                    )
                    answer_letter = target_letter or "ABCD"[correct_index]
                    raw_output = _fake_backend_output(model_id, language, answer_letter)
                    parsed = _parse(model_id, raw_output, language=language)
                    cell_key = (source_item_id, model_id, language, condition)
                    cells.append(
                        SyntheticCell(
                            source_item_id=source_item_id,
                            model_id=model_id,
                            language=language,
                            condition=condition,
                            generation_id="synthetic-generation-" + object_hash(list(cell_key)),
                            prompt=prompt,
                            prompt_hash=content_hash(prompt),
                            target_letter=target_letter,
                            raw_output=raw_output,
                            parsed=parsed,
                        )
                    )
    # Pairing check: exactly one cell per (item, model, language, condition) — no
    # duplicates, no missing combination in the intended Cartesian grid.
    expected = len(_ITEMS) * len(_MODELS) * len(_LANGUAGES) * len(_CONDITIONS)
    keys = {(c.source_item_id, c.model_id, c.language, c.condition) for c in cells}
    if len(keys) != expected or len(cells) != expected:
        raise ValueError("synthetic grid pairing is incomplete or has duplicates")
    if len({c.generation_id for c in cells}) != len(cells):
        raise ValueError("duplicate synthetic generation_id")
    return tuple(cells)


def write_manifest(output: Path) -> dict[str, object]:
    """Write a labeled manifest of the synthetic grid. Refuses to overwrite an
    existing directory (mirrors ``clsm.workshop_v1.preflight.safe_unused_output``'s
    intent for this smaller, adapter-focused exercise)."""
    if output.exists():
        raise ValueError(f"refusing to reuse an existing output directory: {output}")
    if not output.name.startswith("synthetic-workshop-v1-"):
        raise ValueError("synthetic output directory must start with synthetic-workshop-v1-")
    cells = run()
    output.mkdir(parents=True, exist_ok=False)
    payload = {
        "label": SYNTHETIC_LABEL,
        "scientific_outcomes": "NOT RUN",
        "cell_count": len(cells),
        "cells": [
            {
                **{k: v for k, v in asdict(c).items() if k != "parsed"},
                "parsed": asdict(c.parsed),
            }
            for c in cells
        ],
    }
    (output / "manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return payload


__all__ = ["SyntheticCell", "run", "write_manifest"]

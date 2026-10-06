"""Deterministic, outcome-blind human-reference pool planning."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clsm.downstream.contracts import object_hash

ROOT = Path(__file__).resolve().parents[3]
MODELS = ("Qwen/Qwen3-1.7B", "google/gemma-3-4b-it")


@dataclass(frozen=True)
class HumanCandidate:
    source_item_id: str
    source_row_hash: str
    model_id: str
    cue: str
    sample_index: int
    selection_key: str

    @property
    def blind_id(self) -> str:
        return "blind-" + object_hash([
            self.source_item_id, self.source_row_hash, self.model_id,
            self.cue, self.sample_index, "human-reference-v1",
        ])


def _items(root: Path, filename: str) -> dict[str, dict[str, str]]:
    value = json.loads((root / "engineering" / filename).read_text())
    return {row["source_item_id"]: row for row in value["items"]}


def candidate_pool(root: Path = ROOT) -> tuple[HumanCandidate, ...]:
    main = _items(root, "workshop_v1_main_manifest.json")
    cue_b = _items(root, "workshop_v1_cue_b_manifest.json")
    rows = []
    for model in MODELS:
        for cue, source in (("cue_a", main), ("cue_b", cue_b)):
            for item_id, row in source.items():
                token = f"{item_id}|{model}|{cue}|human_sample"
                value = int(hashlib.sha256(token.encode()).hexdigest()[:8], 16) % 3
                rows.append(HumanCandidate(item_id, row["row_hash"], model, cue, value, token))
    return tuple(rows)


def capacity_blocks(root: Path = ROOT) -> tuple[tuple[str, ...], ...]:
    main = _items(root, "workshop_v1_main_manifest.json")
    cue_b = _items(root, "workshop_v1_cue_b_manifest.json")
    def key(item_id: str) -> str:
        return hashlib.sha256(f"{item_id}|human_pool_order|v1".encode()).hexdigest()
    b = sorted(cue_b, key=key)
    other = sorted(set(main) - set(cue_b), key=key)
    return tuple(tuple(b[i:i + 3] + other[i * 7:(i + 1) * 7]) for i in range(12))


def validate_pool(root: Path = ROOT) -> dict[str, Any]:
    rows = candidate_pool(root)
    blocks = capacity_blocks(root)
    if len(rows) != 312 or len({(x.source_item_id, x.model_id, x.cue) for x in rows}) != 312:
        raise ValueError("human candidate pool must contain 312 unique item/model/cue cells")
    if len(blocks) != 12 or any(len(block) != 10 for block in blocks):
        raise ValueError("capacity block item order mismatch")
    return {
        "count": len(rows), "cue_a": sum(x.cue == "cue_a" for x in rows),
        "cue_b": sum(x.cue == "cue_b" for x in rows), "blocks": 12,
        "block_order_hash": object_hash(blocks), "language_compliance_filter": False,
        "annotation_executed": False,
        "packet_order": "lexicographic_blind_id",
        "packet_order_hash": object_hash(tuple(sorted(x.blind_id for x in rows))),
    }


def packet_order(candidates: tuple[HumanCandidate, ...]) -> tuple[HumanCandidate, ...]:
    """Return a reproducible presentation order independent of model/cue blocks."""
    return tuple(sorted(candidates, key=lambda candidate: candidate.blind_id))


def blinded_export_rows(
    candidates: tuple[HumanCandidate, ...], traces: dict[tuple[str, str, str, int], str]
) -> list[dict[str, str]]:
    """Build outcome-blinded annotation rows from already-produced trace text.

    The lookup key is explicit and model/condition fields never enter the exported
    packet. Missing traces fail closed; this function performs no annotation.
    """
    rows: list[dict[str, str]] = []
    for candidate in packet_order(candidates):
        key = (candidate.source_item_id, candidate.model_id, candidate.cue, candidate.sample_index)
        trace = traces.get(key)
        if not isinstance(trace, str) or not trace.strip():
            raise ValueError("missing trace for human candidate")
        rows.append({"blind_id": candidate.blind_id, "visible_trace": trace})
    if len({row["blind_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate blind IDs")
    return rows


def parity_export_rows(
    candidates: tuple[HumanCandidate, ...],
    contexts: dict[tuple[str, str, str, int], dict[str, object]],
) -> list[dict[str, object]]:
    """Build the approved judge-parity packet without exposing model metadata."""
    rows: list[dict[str, object]] = []
    for candidate in packet_order(candidates):
        key = (candidate.source_item_id, candidate.model_id, candidate.cue, candidate.sample_index)
        context = contexts.get(key)
        if not isinstance(context, dict):
            raise ValueError("missing parity context for human candidate")
        required = {"question", "options", "suggestion", "trace", "language"}
        if (
            not required <= set(context)
            or not isinstance(context["trace"], str)
            or not context["trace"].strip()
        ):
            raise ValueError("incomplete parity context")
        rows.append({
            "blind_id": candidate.blind_id,
            "language": context["language"],
            "question": context["question"],
            "options": context["options"],
            "suggestion": context["suggestion"],
            "trace": context["trace"],
        })
    if len({str(row["blind_id"]) for row in rows}) != len(rows):
        raise ValueError("duplicate blind IDs")
    return rows

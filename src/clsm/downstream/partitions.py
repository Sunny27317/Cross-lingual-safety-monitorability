"""Deterministic source-item partitions for calibration and confirmatory stages."""

from __future__ import annotations

import hashlib
from typing import Literal, cast

from pydantic import Field, model_validator

from clsm.downstream.contracts import Contract, Nonempty, object_hash

PartitionName = Literal["rubric_training", "calibration", "heldout", "confirmatory"]


class ItemPartitionPlan(Contract):
    """A hash-bound assignment; all variants of an item inherit one partition."""

    schema_version: Literal["item-partitions/1"] = "item-partitions/1"
    item_ids: tuple[Nonempty, ...]
    seed: int = Field(ge=0)
    assignments: dict[Nonempty, PartitionName]
    decision_record: Nonempty

    @model_validator(mode="after")
    def complete_and_disjoint(self) -> ItemPartitionPlan:
        if not self.item_ids or len(set(self.item_ids)) != len(self.item_ids):
            raise ValueError("item IDs must be nonempty and unique")
        if set(self.assignments) != set(self.item_ids):
            raise ValueError("partition assignment must cover each item exactly once")
        if not set(self.assignments.values()) == {
            "rubric_training",
            "calibration",
            "heldout",
            "confirmatory",
        }:
            raise ValueError("all four disjoint partitions must be represented")
        return self

    @property
    def partition_ids(self) -> dict[str, tuple[str, ...]]:
        return {
            name: tuple(sorted(item for item, part in self.assignments.items() if part == name))
            for name in ("rubric_training", "calibration", "heldout", "confirmatory")
        }


def assign_source_items(
    item_ids: tuple[str, ...] | list[str],
    *,
    seed: int,
    partition_sizes: tuple[int, int, int, int],
    decision_record: str,
) -> ItemPartitionPlan:
    """Assign IDs by a stable hash order, never by observed outcomes or row order."""
    ids = tuple(item_ids)
    if seed < 0 or len(partition_sizes) != 4 or any(n < 1 for n in partition_sizes):
        raise ValueError("four positive partition sizes and a nonnegative seed required")
    if sum(partition_sizes) != len(ids):
        raise ValueError("partition sizes must sum to the number of item IDs")
    if not decision_record.strip():
        raise ValueError("decision record required")
    if len(set(ids)) != len(ids) or any(not x.strip() for x in ids):
        raise ValueError("item IDs must be nonempty and unique")
    ranked = sorted(ids, key=lambda item: hashlib.sha256(f"{seed}:{item}".encode()).hexdigest())
    names = ("rubric_training", "calibration", "heldout", "confirmatory")
    assignments: dict[str, PartitionName] = {}
    offset = 0
    for name, size in zip(names, partition_sizes, strict=True):
        assignments.update({item: cast(PartitionName, name) for item in ranked[offset : offset + size]})
        offset += size
    return ItemPartitionPlan(
        item_ids=ids, seed=seed, assignments=assignments, decision_record=decision_record
    )


def partition_manifest_hash(plan: ItemPartitionPlan) -> str:
    return object_hash(plan.model_dump(mode="json"))

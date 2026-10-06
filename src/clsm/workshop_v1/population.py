"""Outcome-free deterministic population selection from an offline frozen snapshot."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal, Self

from pydantic import model_validator

from clsm.downstream.contracts import SHA, Contract, DataKind, Nonempty, content_hash, object_hash
from clsm.workshop_v1.config import DatasetSpec, Language, Resolved, Study


class ItemRendering(Contract):
    language: Language
    text: Nonempty  # adapter-owned serialized task, including choices if applicable
    text_hash: SHA

    @model_validator(mode="after")
    def verify(self) -> Self:
        if content_hash(self.text) != self.text_hash:
            raise ValueError("item text hash mismatch")
        return self


class SourceItem(Contract):
    source_item_id: Nonempty
    category: Nonempty
    difficulty_metadata: Nonempty | None  # source-supplied; never an invented measurement
    renderings: tuple[ItemRendering, ItemRendering]
    equivalence_status: Literal["pending", "accepted", "rejected", "synthetic_only"]
    equivalence_evidence: Resolved | None

    @model_validator(mode="after")
    def language_alignment(self) -> Self:
        if {r.language for r in self.renderings} != {"en", "ur"}:
            raise ValueError("each source item must preserve one en and one ur rendering")
        if self.equivalence_status == "accepted" and self.equivalence_evidence is None:
            raise ValueError("accepted equivalence requires evidence")
        return self


def snapshot_content_hash(items: tuple[SourceItem, ...]) -> str:
    return object_hash([i.model_dump(mode="json") for i in sorted(items, key=lambda i: i.source_item_id)])


class DatasetSnapshot(Contract):
    schema_version: Literal["workshop-v1-snapshot/1"] = "workshop-v1-snapshot/1"
    data_kind: DataKind
    dataset: DatasetSpec
    items: tuple[SourceItem, ...]

    @model_validator(mode="after")
    def integrity(self) -> Self:
        ids = [i.source_item_id for i in self.items]
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("snapshot requires unique source IDs")
        if snapshot_content_hash(self.items) != self.dataset.content_hash:
            raise ValueError("dataset content hash mismatch")
        if self.data_kind is DataKind.SCIENTIFIC and any(
            i.equivalence_status == "synthetic_only" for i in self.items
        ):
            raise ValueError("synthetic equivalence cannot enter a scientific snapshot")
        if self.data_kind is DataKind.SYNTHETIC and any(
            not i.startswith("synthetic-") for i in ids
        ):
            raise ValueError("synthetic source IDs require synthetic namespace")
        return self


class Population(Contract):
    schema_version: Literal["workshop-v1-population/1"] = "workshop-v1-population/1"
    data_kind: DataKind
    study_hash: SHA
    dataset_hash: SHA
    role: Literal["pilot", "confirmatory"]
    selection_rule: Literal["sha256_source_id_v1"]
    selection_seed: int
    selection_decision: Resolved
    items: tuple[SourceItem, ...]
    replacement_policy: Literal["prohibited"] = "prohibited"

    @model_validator(mode="after")
    def unique(self) -> Self:
        if not self.items or len({i.source_item_id for i in self.items}) != len(self.items):
            raise ValueError("population requires unique source IDs")
        return self


def select_population(study: Study, snapshot: DatasetSnapshot) -> Population:
    """Explicit rule choice required. Input row order/outcomes cannot select items.

    This is an engineering rule option, not a scientific decision to use random or
    stratified sampling. No replacement argument exists. An amendment must change
    the frozen study and invalidate every downstream binding.
    """
    study.require_generation_design()
    if study.data_kind != snapshot.data_kind or study.dataset != snapshot.dataset:
        raise ValueError("snapshot kind/dataset does not match study")
    sampling = study.sampling
    assert sampling.n_source_items is not None and sampling.selection_seed is not None
    assert sampling.population_role is not None and sampling.selection_decision is not None
    assert sampling.selection_rule is not None
    if sampling.n_source_items > len(snapshot.items):
        raise ValueError("requested population exceeds frozen snapshot; no replacement")
    ranked = sorted(
        snapshot.items,
        key=lambda i: (
            object_hash([sampling.selection_seed, snapshot.dataset.artifact_hash, i.source_item_id]),
            i.source_item_id,
        ),
    )
    selected = tuple(ranked[: sampling.n_source_items])
    # Never replace a failed-equivalence item with the next favorable/usable item.
    required = "synthetic_only" if study.data_kind is DataKind.SYNTHETIC else "accepted"
    if any(i.equivalence_status != required for i in selected):
        raise ValueError("selected item equivalence unresolved/rejected; do not replace items")
    return Population(
        data_kind=study.data_kind,
        study_hash=study.artifact_hash,
        dataset_hash=snapshot.dataset.artifact_hash,
        role=sampling.population_role,
        selection_rule=sampling.selection_rule,
        selection_seed=sampling.selection_seed,
        selection_decision=sampling.selection_decision,
        items=selected,
    )


def validate_population(study: Study, snapshot: DatasetSnapshot, population: Population) -> None:
    if select_population(study, snapshot) != population:
        raise ValueError("frozen population differs from prospective selection; replacement forbidden")


def require_disjoint_populations(pilot: Population, confirmatory: Population) -> None:
    """Use when the reviewed design requires disjoint populations; never silently pool."""
    if pilot.role != "pilot" or confirmatory.role != "confirmatory":
        raise ValueError("explicit pilot and confirmatory population roles required")
    if {i.source_item_id for i in pilot.items} & {i.source_item_id for i in confirmatory.items}:
        raise ValueError("pilot and confirmatory source populations overlap")


def deterministic_partition_ids(
    source_ids: Iterable[str], *, seed: int, pilot_size: int, main_size: int, cue_b_size: int
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Return disjoint pilot, main, and Cue-B IDs using IDs only.

    This helper deliberately accepts IDs rather than rows, so outcomes, answers, and
    monitor annotations cannot influence population membership.  It is a manifest
    primitive; callers must persist the dataset revision and resulting ID hashes.
    """
    ids = tuple(source_ids)
    if len(set(ids)) != len(ids):
        raise ValueError("source IDs must be unique")
    if min(pilot_size, main_size, cue_b_size) < 0 or cue_b_size > main_size:
        raise ValueError("invalid partition sizes")
    if pilot_size + main_size > len(ids):
        raise ValueError("partition exceeds available source IDs")
    ranked = sorted(ids, key=lambda item: (object_hash([seed, item]), item))
    pilot = tuple(ranked[:pilot_size])
    main = tuple(ranked[pilot_size : pilot_size + main_size])
    cue_b = tuple(sorted(main, key=lambda item: (object_hash([seed, "cue_b", item]), item))[:cue_b_size])
    if set(pilot) & set(main) or set(cue_b) - set(main):
        raise AssertionError("partition invariant violated")
    return pilot, main, cue_b

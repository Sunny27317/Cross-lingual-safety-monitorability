"""Generation identity, paired design, and full provenance without an executor."""

from __future__ import annotations

from datetime import datetime, timedelta
from itertools import product
from pathlib import PurePosixPath
from typing import Final, Literal, Self

from pydantic import Field, field_validator, model_validator

from clsm.downstream.contracts import SHA, Contract, DataKind, GitSHA, Nonempty, content_hash, object_hash
from clsm.downstream.matching import TraceIdentityKey
from clsm.workshop_v1.config import Condition, CueSpec, DatasetSpec, ModelSpec, Resolved, Study
from clsm.workshop_v1.population import Population

SYNTHETIC_LABEL: Final = "SYNTHETIC — NOT SCIENTIFIC DATA"


class Identity(TraceIdentityKey):
    """Extends historical H/D/T identity without dropping model or sample identity."""

    model_id: Resolved
    sample_index: int = Field(ge=0)
    condition: Condition
    seed: int = Field(ge=0)

    def cell(self) -> tuple[str, str, str, Condition, int, int]:
        return (
            self.source_item_id,
            self.model_id,
            self.language,
            self.condition,
            self.seed,
            self.sample_index,
        )


def generation_id(
    study: Study, population: Population, cell: tuple[str, str, str, Condition, int, int]
) -> str:
    prefix = "synthetic-generation-" if study.data_kind is DataKind.SYNTHETIC else "workshop-generation-"
    return prefix + object_hash([study.artifact_hash, population.artifact_hash, cell])


def validate_population_binding(study: Study, population: Population) -> None:
    study.require_generation_design()
    if (
        population.study_hash != study.artifact_hash
        or population.data_kind != study.data_kind
        or study.dataset is None
        or population.dataset_hash != study.dataset.artifact_hash
        or population.role != study.sampling.population_role
        or len(population.items) != study.sampling.n_source_items
        or population.selection_seed != study.sampling.selection_seed
        or population.selection_rule != study.sampling.selection_rule
        or population.selection_decision != study.sampling.selection_decision
    ):
        raise ValueError("population/study binding mismatch")


def full_design(study: Study, population: Population) -> tuple[Identity, ...]:
    """Cartesian design for an explicitly complete pairing claim only."""
    validate_population_binding(study, population)
    if study.sampling.pairing != "complete":
        raise ValueError(
            "partial designs require an explicit reviewed subset; no implicit Cartesian expansion"
        )
    specs = [slot.spec for slot in study.models]
    rows = []
    for item, model, language, cue, sample in product(
        population.items, specs, study.languages, study.conditions, enumerate(study.sampling.seeds)
    ):
        assert model is not None
        index, seed = sample
        cell = (item.source_item_id, model.model_id, language, cue.condition, seed, index)
        rows.append(
            Identity(
                source_item_id=item.source_item_id,
                model_id=model.model_id,
                language=language,
                condition=cue.condition,
                seed=seed,
                sample_index=index,
                generation_id=generation_id(study, population, cell),
            )
        )
    return tuple(rows)


def validate_identities(study: Study, population: Population, identities: tuple[Identity, ...]) -> None:
    """Reject duplicate, foreign or missing cells, including an entirely missing paired group."""
    validate_population_binding(study, population)
    if not identities or len({i.cell() for i in identities}) != len(identities):
        raise ValueError("empty design or duplicate generation cell")
    if len({i.generation_id for i in identities}) != len(identities):
        raise ValueError("duplicate generation ID")
    item_ids = {i.source_item_id for i in population.items}
    model_ids = {m.spec.model_id for m in study.models if m.spec is not None}
    for identity in identities:
        if (
            identity.source_item_id not in item_ids
            or identity.model_id not in model_ids
            or identity.language not in study.languages
            or identity.condition not in {c.condition for c in study.conditions}
            or identity.sample_index >= len(study.sampling.seeds)
            or study.sampling.seeds[identity.sample_index] != identity.seed
            or identity.generation_id != generation_id(study, population, identity.cell())
        ):
            raise ValueError("generation identity does not belong to frozen design")
    if study.sampling.pairing == "complete" and set(identities) != set(full_design(study, population)):
        raise ValueError("complete paired design missing requested source/model/language/cue/sample cells")


class Confounds(Contract):
    """Absent observations remain null. Evidence must accompany observed fields."""

    base_task_correctness: bool | None = None
    language_compliance: Literal["compliant", "noncompliant", "indeterminate"] | None = None
    observation_evidence_hash: SHA | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def observed_evidence(self) -> Self:
        if (
            any(
                v is not None
                for v in (
                    self.base_task_correctness,
                    self.language_compliance,
                    self.input_tokens,
                    self.output_tokens,
                )
            )
            and self.observation_evidence_hash is None
        ):
            raise ValueError("observations require evidence; do not invent confound measurements")
        return self


class GenerationRecord(Contract):
    schema_version: Literal["workshop-v1-generation/1"] = "workshop-v1-generation/1"
    data_kind: DataKind
    label: Literal["SYNTHETIC — NOT SCIENTIFIC DATA", "SCIENTIFIC"]
    study_id: Nonempty
    study_hash: SHA
    designation: Literal["confirmatory", "exploratory"]
    code_commit: GitSHA
    working_tree_hash: SHA  # includes uncommitted code for synthetic development runs
    environment_hash: SHA
    population_hash: SHA
    identity: Identity
    dataset: DatasetSpec
    source_item_hash: SHA
    category: Nonempty
    difficulty_metadata: Nonempty | None
    model: ModelSpec
    cue: CueSpec
    cue_text_hash: SHA
    prompt_template_hash: SHA
    prompt: Nonempty
    prompt_hash: SHA
    created_utc: str
    output_path: Nonempty
    output_text: Nonempty
    output_hash: SHA
    parser_version: Resolved
    confounds: Confounds

    @field_validator("created_utc")
    @classmethod
    def utc(cls, value: str) -> str:
        if datetime.fromisoformat(value).utcoffset() != timedelta(0):
            raise ValueError("timestamp must be UTC")
        return value

    @model_validator(mode="after")
    def integrity(self) -> Self:
        if self.model.model_id != self.identity.model_id or self.parser_version != self.model.parser_version:
            raise ValueError("model/parser identity mismatch")
        rendering = next(r for r in self.cue.renderings if r.language == self.identity.language)
        if rendering.text_hash != self.cue_text_hash:
            raise ValueError("language-specific cue hash mismatch")
        if (
            content_hash(self.prompt) != self.prompt_hash
            or content_hash(self.output_text) != self.output_hash
        ):
            raise ValueError("prompt/output hash mismatch")
        path = PurePosixPath(self.output_path)
        if (
            path.is_absolute()
            or ".." in path.parts
            or "results" in {p.casefold() for p in path.parts}
            or "\\" in self.output_path
            or not path.parts
            or str(path) != self.output_path
        ):
            raise ValueError("output_path must be relative and outside results/")
        if self.data_kind is DataKind.SYNTHETIC:
            if self.label != SYNTHETIC_LABEL or not self.identity.generation_id.startswith("synthetic-"):
                raise ValueError("synthetic label/identity required")
            if not self.output_text.startswith(SYNTHETIC_LABEL):
                raise ValueError("synthetic output must prominently identify itself")
        elif (
            self.label != "SCIENTIFIC"
            or self.code_commit == "0" * 40
            or self.identity.generation_id.startswith("synthetic-")
            or self.output_text.startswith(SYNTHETIC_LABEL)
        ):
            raise ValueError("scientific provenance cannot use synthetic labels/commit")
        return self


def validate_generation(record: GenerationRecord, study: Study, population: Population) -> None:
    validate_population_binding(study, population)
    item = next((i for i in population.items if i.source_item_id == record.identity.source_item_id), None)
    model = next(
        (m.spec for m in study.models if m.spec and m.spec.model_id == record.identity.model_id), None
    )
    cue = next((c.spec for c in study.conditions if c.condition == record.identity.condition), None)
    prompt = next((p for p in study.prompts if p.language == record.identity.language), None)
    if (
        record.study_id != study.study_id
        or record.study_hash != study.artifact_hash
        or record.population_hash != population.artifact_hash
        or record.dataset != study.dataset
        or record.designation != study.designation
        or record.data_kind != study.data_kind
        or item is None
        or record.source_item_hash != item.artifact_hash
        or record.category != item.category
        or record.difficulty_metadata != item.difficulty_metadata
        or record.model != model
        or record.cue != cue
        or prompt is None
        or record.prompt_template_hash != prompt.template_hash
        or record.identity.sample_index >= len(study.sampling.seeds)
        or record.identity.seed != study.sampling.seeds[record.identity.sample_index]
        or record.identity.generation_id != generation_id(study, population, record.identity.cell())
    ):
        raise ValueError("generation provenance differs from frozen study/population")


def validate_generations(records: tuple[GenerationRecord, ...], study: Study, population: Population) -> None:
    if len({r.output_path for r in records}) != len(records):
        raise ValueError("generation output paths must be unique within the run")
    for record in records:
        validate_generation(record, study, population)
    validate_identities(study, population, tuple(r.identity for r in records))

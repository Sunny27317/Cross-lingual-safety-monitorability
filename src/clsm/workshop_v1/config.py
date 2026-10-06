"""Strict, immutable Workshop-v1 design contracts and composed YAML drafts.

This layer intentionally does not inherit Track-A's scientific defaults.
Nulls in a draft mean unresolved, never permission to substitute a default.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Literal, Self

import yaml
from pydantic import AfterValidator, Field, model_validator

from clsm.downstream.contracts import SHA, Contract, DataKind, Nonempty, canonical, content_hash


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate keys rather than silently replacing a scientific selection."""

    def construct_mapping(self, node: yaml.Node, deep: bool = False) -> dict[Any, Any]:
        pairs = self.construct_pairs(node, deep=deep)
        result: dict[Any, Any] = {}
        for key, value in pairs:
            if not isinstance(key, str):
                raise ValueError("configuration keys must be strings")
            if key in result:
                raise ValueError(f"duplicate YAML key: {key}")
            result[key] = value
        return result


def resolved(value: str) -> str:
    if (
        value != value.strip()
        or any(
            marker in value.upper()
            for marker in ("TODO", "BLOCKED", "UNRESOLVED", "PENDING", "DECISION REQUIRED")
        )
        or value.lower() in {"main", "master", "head", "latest", "unknown", "unsigned"}
    ):
        raise ValueError("explicit resolved value required; mutable aliases/placeholders are forbidden")
    return value


Resolved = Annotated[Nonempty, AfterValidator(resolved)]
Language = Literal["en", "ur"]
Designation = Literal["confirmatory", "exploratory"]


class Condition(StrEnum):
    CONTROL = "control"
    MISLEADING_CUE_A = "misleading_cue_a"
    MISLEADING_CUE_B = "misleading_cue_b"


class Decoding(Contract):
    temperature: float = Field(ge=0)
    top_p: float = Field(gt=0, le=1)
    top_k: int | None = Field(ge=0)
    repetition_penalty: float = Field(gt=0)
    max_new_tokens: int = Field(gt=0)
    stop_sequences: tuple[Nonempty, ...]
    sampling_mode: Resolved
    determinism_note: Resolved
    additional_settings_hash: SHA  # content-addressed backend-specific options, including empty options


class ModelSpec(Contract):
    model_id: Resolved
    model_family: Resolved
    revision: Resolved
    checkpoint_hash: SHA
    open_weight_evidence: Resolved
    tokenizer_id: Resolved
    tokenizer_revision: Resolved
    tokenizer_hash: SHA
    runtime: Resolved
    runtime_version: Resolved
    backend: Resolved
    backend_version: Resolved
    quantization: Resolved  # explicit "none" if not applicable
    decoding: Decoding | None
    parser_version: Resolved
    decision_record: Resolved

    artifact_repo: Resolved | None = None
    local_path: Resolved | None = None
    size_bytes: int | None = Field(default=None, gt=0)
    runtime_commit: Resolved | None = None
    runtime_binary: Resolved | None = None
    runtime_binary_hash: SHA | None = None
    reasoning_trace_policy: Resolved | None = None
    prompt_mode: Resolved | None = None
    final_answer_policy: Resolved | None = None
    completion_boundary_policy: Resolved | None = None
    tokenizer_hash_policy: Resolved | None = None
    additional_settings: dict[str, Any] | None = None
    unresolved_fields: tuple[Nonempty, ...] = ()

    def blockers(self) -> list[str]:
        blockers = list(self.unresolved_fields)
        if self.decoding is None:
            blockers.append("BLOCKED/TODO: decoding not frozen")
        if not self.model_id.startswith("synthetic-"):
            for field in (
                "artifact_repo", "local_path", "size_bytes", "runtime_commit", "runtime_binary",
                "runtime_binary_hash", "reasoning_trace_policy", "prompt_mode", "final_answer_policy",
                "completion_boundary_policy", "tokenizer_hash_policy", "additional_settings",
            ):
                if getattr(self, field) is None:
                    blockers.append(f"BLOCKED/TODO: {field}")
            if (
                self.decoding is not None and self.additional_settings is not None
                and self.decoding.additional_settings_hash
                != content_hash(canonical(self.additional_settings))
            ):
                blockers.append("runtime settings hash mismatch")
        return blockers


class ModelSlot(Contract):
    slot_id: Nonempty
    status: Literal["TODO", "frozen"]
    spec: ModelSpec | None

    @model_validator(mode="after")
    def consistent(self) -> Self:
        if self.status == "frozen" and (self.spec is None or self.spec.blockers()):
            raise ValueError("frozen model slots require complete specifications")
        return self


class CueRendering(Contract):
    language: Language
    text: str  # control is explicitly empty
    text_hash: SHA

    @model_validator(mode="after")
    def verify(self) -> Self:
        if content_hash(self.text) != self.text_hash:
            raise ValueError("cue text hash mismatch")
        return self


class CueSpec(Contract):
    cue_id: Resolved
    version: Resolved
    renderings: tuple[CueRendering, CueRendering]
    target_rule: Resolved
    equivalence_evidence: Resolved
    decision_record: Resolved

    @model_validator(mode="after")
    def both_languages(self) -> Self:
        if {x.language for x in self.renderings} != {"en", "ur"}:
            raise ValueError("cue must define exactly one rendering for en and ur")
        return self


class CueSlot(Contract):
    condition: Condition
    status: Literal["TODO", "frozen"]
    spec: CueSpec | None

    @model_validator(mode="after")
    def consistent(self) -> Self:
        if (self.status == "frozen") != (self.spec is not None):
            raise ValueError("only frozen cue slots may contain specifications")
        if self.spec is not None:
            texts = [x.text for x in self.spec.renderings]
            if self.condition is Condition.CONTROL and any(texts):
                raise ValueError("control must contain no cue text")
            if self.condition is not Condition.CONTROL and any(not t.strip() for t in texts):
                raise ValueError("misleading cue text cannot be empty")
        return self


class DatasetSpec(Contract):
    dataset_id: Resolved
    revision: Resolved
    split: Resolved
    content_hash: SHA
    license_evidence: Resolved
    provenance_evidence: Resolved


class PromptSpec(Contract):
    language: Language
    version: Resolved
    template: Nonempty
    template_hash: SHA
    renderer_version: Resolved
    decision_record: Resolved

    @model_validator(mode="after")
    def verify(self) -> Self:
        if content_hash(self.template) != self.template_hash:
            raise ValueError("prompt template hash mismatch")
        return self


class ServiceSpec(Contract):
    """Identity of an automated monitor or translator; no callable client."""

    service_id: Resolved
    revision: Resolved
    specification_hash: SHA  # exact full prompt/decoding/runtime/rubric package
    selection_record: Resolved


class HumanReferenceSpec(Contract):
    protocol_version: Resolved
    protocol_hash: SHA
    rubric_hash: SHA
    population_role: Literal["workshop_v1_native_urdu"]
    decision_record: Resolved


class Monitoring(Contract):
    automated_monitor: ServiceSpec | None
    translator: ServiceSpec | None
    human_reference: HumanReferenceSpec | None
    # One monitor spec for English baseline, direct Urdu, and translated English.
    # Different judge-input languages are represented on each downstream request.


class Sampling(Contract):
    planning_target_only: int = Field(gt=0)
    n_source_items: int | None = Field(gt=0)
    population_role: Literal["pilot", "confirmatory"] | None
    selection_rule: Literal["sha256_source_id_v1"] | None
    selection_seed: int | None = Field(ge=0)
    selection_decision: Resolved | None
    seeds: tuple[Annotated[int, Field(ge=0)], ...]
    pairing: Literal["complete", "partial"] | None
    pairing_decision: Resolved | None
    sample_size_rationale: Resolved | None
    replacement_policy: Literal["prohibited"] = "prohibited"

    @model_validator(mode="after")
    def no_duplicate_seeds(self) -> Self:
        if len(set(self.seeds)) != len(self.seeds):
            raise ValueError("seeds must be unique")
        return self


class Study(Contract):
    schema_version: Literal["workshop-v1/1"] = "workshop-v1/1"
    study_id: Nonempty
    data_kind: DataKind
    status: Literal["TODO", "frozen"]
    designation: Designation | None
    scope: Literal["tested_models_and_settings_only"]
    languages: tuple[Language, Language]
    models: tuple[ModelSlot, ...] = Field(min_length=2)
    conditions: tuple[CueSlot, CueSlot, CueSlot]
    sampling: Sampling
    dataset: DatasetSpec | None
    prompts: tuple[PromptSpec, ...]
    monitoring: Monitoring
    protocol_hash: SHA | None
    decision_record: Resolved | None

    @model_validator(mode="after")
    def design_shape(self) -> Self:
        if set(self.languages) != {"en", "ur"}:
            raise ValueError("Workshop-v1 requires exactly en and ur")
        if len({m.slot_id for m in self.models}) != len(self.models):
            raise ValueError("duplicate model slot")
        specs = [m.spec for m in self.models if m.spec is not None]
        if len({m.model_id for m in specs}) != len(specs):
            raise ValueError("model IDs must be unique; use explicit distinct specifications")
        if {c.condition for c in self.conditions} != set(Condition):
            raise ValueError("all three distinct condition levels are required")
        cues = [c.spec for c in self.conditions if c.spec is not None]
        if len({c.cue_id for c in cues}) != len(cues):
            raise ValueError("cue IDs must be distinct")
        misleading = [c.spec for c in self.conditions if c.condition is not Condition.CONTROL]
        if all(misleading):
            a, b = misleading
            assert a is not None and b is not None
            for language in self.languages:
                at = next(r.text for r in a.renderings if r.language == language)
                bt = next(r.text for r in b.renderings if r.language == language)
                if at == bt:
                    raise ValueError("cue A/B must have distinct wording in each language")
        if len({p.language for p in self.prompts}) != len(self.prompts):
            raise ValueError("duplicate language prompt")
        if self.data_kind is DataKind.SCIENTIFIC:
            identities = [self.study_id, *(m.model_id for m in specs), *(c.cue_id for c in cues)]
            if self.dataset is not None:
                identities.append(self.dataset.dataset_id)
            if any(identity.startswith("synthetic-") for identity in identities):
                raise ValueError("synthetic identities cannot be relabeled as scientific")
        if self.status == "frozen" and self.generation_blockers():
            raise ValueError("frozen design is incomplete: " + "; ".join(self.generation_blockers()))
        return self

    def generation_blockers(self) -> list[str]:
        blockers = []
        for field in ("designation", "dataset", "protocol_hash", "decision_record"):
            if getattr(self, field) is None:
                blockers.append(f"unresolved {field}")
        for field in (
            "n_source_items",
            "population_role",
            "selection_rule",
            "selection_seed",
            "selection_decision",
            "pairing",
            "pairing_decision",
            "sample_size_rationale",
        ):
            if getattr(self.sampling, field) is None:
                blockers.append(f"unresolved sampling.{field}")
        if not self.sampling.seeds:
            blockers.append("unresolved generation seeds/sample count")
        specs = [m.spec for m in self.models if m.spec is not None]
        if len(specs) != len(self.models) or any(m.blockers() for m in specs):
            blockers.append("unresolved model identities/decoding")
        if len({m.model_family for m in specs}) != 2:
            blockers.append("Workshop-v1 requires exactly two active model families")
        if any(c.spec is None for c in self.conditions):
            blockers.append("unresolved cue identities/wording/equivalence")
        if {p.language for p in self.prompts} != {"en", "ur"}:
            blockers.append("unresolved language prompt templates")
        return blockers

    def require_generation_design(self) -> None:
        errors = self.generation_blockers()
        if self.status != "frozen":
            errors.append("study is not frozen")
        if errors:
            raise ValueError("; ".join(errors))


def load_study(path: Path) -> Study:
    """Compose siblings like the historical YAML loader, without inheriting its defaults.

    JSON-mode validation allows YAML lists to populate immutable tuple fields; no
    integer/string coercion or unknown keys are accepted. Includes cannot escape
    their directory or mask top-level settings.
    """
    root = path.resolve().parent

    def read(file: Path) -> Any:
        with file.open(encoding="utf-8") as stream:
            return yaml.load(stream, Loader=UniqueKeyLoader)

    top = read(path)
    if not isinstance(top, dict):
        raise ValueError("study YAML must be a mapping")
    includes = top.pop("includes", None)
    expected = {"models", "conditions", "languages", "monitoring"}
    if not isinstance(includes, dict) or set(includes) != expected:
        raise ValueError(f"includes must contain exactly {sorted(expected)}")
    for key, name in includes.items():
        if key in top or not isinstance(name, str) or Path(name).name != name:
            raise ValueError("include must be a unique sibling filename")
        file = (root / name).resolve()
        if file.parent != root:
            raise ValueError("include escapes config directory")
        top[key] = read(file)
    try:
        payload = canonical(top)
    except (TypeError, ValueError) as exc:
        raise ValueError("configuration must contain finite JSON-compatible values") from exc
    return Study.model_validate_json(payload)

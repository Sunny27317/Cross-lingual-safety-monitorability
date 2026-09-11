"""Strict, versioned downstream data contracts. No runtime authorization is issued here."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SHA = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
GitSHA = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
Nonempty = Annotated[str, Field(min_length=1, pattern=r"\S")]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def object_hash(value: Any) -> str:
    return content_hash(canonical(value))


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, allow_inf_nan=False)

    @property
    def artifact_hash(self) -> str:
        return object_hash(self.model_dump(mode="json"))


class DataKind(StrEnum):
    SYNTHETIC = "synthetic"
    SCIENTIFIC = "scientific"


class SoftwareVersion(Contract):
    package: Nonempty
    version: Nonempty

    @field_validator("version")
    @classmethod
    def exact_version(cls, value: str) -> str:
        if any(marker in value for marker in ("<", ">", "*", "~", "^")) or value.lower() in {
            "main",
            "latest",
            "head",
        }:
            raise ValueError("exact installed software version required")
        return value


class Provenance(Contract):
    schema_version: Literal["downstream-provenance/1"] = "downstream-provenance/1"
    git_sha: GitSHA
    config_hash: SHA
    dataset_hash: SHA
    analysis_version: Literal["downstream/1"] = "downstream/1"
    random_seed: int = Field(ge=0)
    data_kind: DataKind
    created_utc: str
    source_artifact_hashes: tuple[SHA, ...]
    software_versions: tuple[SoftwareVersion, ...]

    @model_validator(mode="after")
    def installed_versions(self) -> Self:
        packages = {v.package for v in self.software_versions}
        if len(packages) != len(self.software_versions) or not {"python", "numpy", "pydantic"} <= packages:
            raise ValueError("unique exact python/numpy/pydantic versions required")
        if self.data_kind is DataKind.SCIENTIFIC and self.git_sha == "0" * 40:
            raise ValueError("scientific provenance cannot use synthetic git placeholder")
        return self

    @field_validator("created_utc")
    @classmethod
    def timezone_required(cls, value: str) -> str:
        if datetime.fromisoformat(value).utcoffset() != timedelta(0):
            raise ValueError("timestamp must be UTC")
        return value


class Trace(Contract):
    trace_id: Nonempty
    item_id: Nonempty  # resampling cluster, private to steward/analyst
    language: Literal["en", "ur"]
    text: Nonempty
    text_hash: SHA
    generator_identity: Nonempty  # never sent to annotators/judges/translators
    condition: Nonempty
    provenance: Provenance

    @model_validator(mode="after")
    def check_hash(self) -> Self:
        if content_hash(self.text) != self.text_hash:
            raise ValueError("trace hash mismatch")
        if self.provenance.data_kind is DataKind.SYNTHETIC and not self.trace_id.startswith("synthetic-"):
            raise ValueError("synthetic traces require explicit synthetic namespace")
        return self


class TraceSet(Contract):
    traces: tuple[Trace, ...]
    prospective_population_definition: Nonempty
    selection_record_hash: SHA

    @model_validator(mode="after")
    def unique(self) -> Self:
        if not self.traces or len({t.trace_id for t in self.traces}) != len(self.traces):
            raise ValueError("empty set or duplicated trace")
        if len({t.provenance.data_kind for t in self.traces}) != 1:
            raise ValueError("cannot mix synthetic and scientific traces")
        return self


class DisclosureLabel(StrEnum):
    DISCLOSED = "disclosed"
    NOT_DISCLOSED = "not_disclosed"
    PARTIAL = "partial"
    CANNOT_TELL = "cannot_tell"
    ABSTAIN = "abstain"


def normalize_label(value: object) -> DisclosureLabel:
    """Exact category vocabulary only; no substring, truthiness, yes/no or numeric guessing."""
    if isinstance(value, DisclosureLabel):
        return value
    if type(value) is not str:
        raise ValueError("judge/annotation label must be a category string")
    normalized = value.strip().lower().replace("-", "_")
    try:
        return DisclosureLabel(normalized)
    except ValueError as exc:
        raise ValueError(f"unknown disclosure label: {value!r}") from exc


class LabelPolicy(Contract):
    """Investigator-supplied partial-label rule; cannot-tell and abstain are always missing."""

    partial: Literal["exclude", "disclosed", "not_disclosed"]
    decision_record: Nonempty
    rubric_version: Nonempty

    def binary(self, label: DisclosureLabel) -> int | None:
        if not isinstance(label, DisclosureLabel):
            raise ValueError("binary mapping requires a normalized disclosure category")
        if label is DisclosureLabel.DISCLOSED:
            return 1
        if label is DisclosureLabel.NOT_DISCLOSED:
            return 0
        if label is DisclosureLabel.PARTIAL:
            return {"exclude": None, "disclosed": 1, "not_disclosed": 0}[self.partial]
        return None


class Decoding(Contract):
    temperature: float = Field(ge=0)
    top_p: float = Field(gt=0, le=1)
    max_output_tokens: int = Field(gt=0)
    seed: int | None
    determinism_note: Nonempty


class JudgeSpec(Contract):
    candidate_id: Nonempty
    provider: Nonempty
    model: Nonempty
    version: Nonempty
    prompt: Nonempty
    rubric_version: Nonempty
    decoding: Decoding
    identity_evidence: Nonempty
    provenance: Provenance

    @field_validator("version")
    @classmethod
    def immutable_version(cls, value: str) -> str:
        if value != value.strip() or value.lower() in {
            "main",
            "master",
            "latest",
            "head",
            "unresolved",
            "todo",
        }:
            raise ValueError("mutable or unresolved judge version")
        return value


class JudgeInput(Contract):
    """Allowlist prevents metadata leakage; trace text itself cannot be perfectly blinded."""

    blind_id: SHA
    language: Literal["en", "ur"]
    text: Nonempty
    text_hash: SHA
    rubric_version: Nonempty

    @model_validator(mode="after")
    def check_hash(self) -> Self:
        if content_hash(self.text) != self.text_hash:
            raise ValueError("judge input hash mismatch")
        return self


class JudgeOutput(Contract):
    blind_id: SHA
    input_hash: SHA
    judge_spec_hash: SHA
    rubric_version: Nonempty
    label: DisclosureLabel
    confidence: float | None = Field(ge=0, le=1)
    rationale: str
    raw_response_hash: SHA
    error: str | None
    provenance: Provenance

    @field_validator("label", mode="before")
    @classmethod
    def normalize(cls, value: object) -> DisclosureLabel:
        return normalize_label(value)

    @model_validator(mode="after")
    def error_is_not_label(self) -> Self:
        if self.error is not None and self.label is not DisclosureLabel.ABSTAIN:
            raise ValueError("judge error must remain an abstention")
        return self


def validate_judge_output(output: JudgeOutput, request: JudgeInput, spec: JudgeSpec) -> None:
    if (
        output.blind_id != request.blind_id
        or output.input_hash != request.text_hash
        or output.judge_spec_hash != spec.artifact_hash
        or output.rubric_version != spec.rubric_version
        or request.rubric_version != spec.rubric_version
    ):
        raise ValueError("judge identity/version/input/rubric mismatch")


class ProspectiveCandidatePlan(Contract):
    """No score/outcome fields accepted. Comparing scores never selects a winner automatically."""

    candidate_spec_hashes: tuple[SHA, ...]
    reference_set_hash: SHA
    heldout_reference_set_hash: SHA
    calibration_trace_set_hash: SHA
    heldout_trace_set_hash: SHA
    label_policy_hash: SHA
    acceptance_decision_record: Nonempty
    investigator: Nonempty
    provenance: Provenance

    @model_validator(mode="after")
    def independent_sets(self) -> Self:
        if not self.candidate_spec_hashes or len(set(self.candidate_spec_hashes)) != len(
            self.candidate_spec_hashes
        ):
            raise ValueError("candidate list empty or duplicated")
        if self.calibration_trace_set_hash == self.heldout_trace_set_hash:
            raise ValueError("calibration and heldout sets must differ")
        return self

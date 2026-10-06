"""Read-only stage checks. Passing structural checks never authorizes execution."""

from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Literal, Self

from pydantic import field_validator, model_validator

from clsm.downstream.contracts import SHA, Contract, DataKind, GitSHA
from clsm.track_a_preflight import check_output_directory, git_integrity
from clsm.workshop_v1.config import Resolved, Study
from clsm.workshop_v1.population import DatasetSnapshot, Population, validate_population
from clsm.workshop_v1.records import GenerationRecord, validate_generations


class Stage(StrEnum):
    GENERATION = "generation"
    DIRECT_MONITOR = "direct_monitor"
    HUMAN_REFERENCE = "human_reference"
    TRANSLATED_MONITOR = "translated_monitor"
    CONFIRMATORY = "confirmatory"


# Conservative engineering minima, subject to prospective scientific protocol review.
# No legacy English Track-A approval or G0..G12 ledger is accepted implicitly.
BASE_GATES = frozenset({"design_review", "item_equivalence", "generation_authorization"})
MONITOR_GATES = frozenset({"judge_criteria", "judge_validation", "monitor_authorization"})
HUMAN_GATES = frozenset({"ethics", "human_protocol", "rater_qualification", "human_authorization"})
TRANSLATION_GATES = frozenset({"translator_selection", "translation_audit_plan", "translation_authorization"})
REQUIRED_GATES = {
    Stage.GENERATION: BASE_GATES,
    Stage.DIRECT_MONITOR: BASE_GATES | MONITOR_GATES,
    Stage.HUMAN_REFERENCE: BASE_GATES | HUMAN_GATES,
    Stage.TRANSLATED_MONITOR: BASE_GATES | MONITOR_GATES | TRANSLATION_GATES,
    Stage.CONFIRMATORY: BASE_GATES
    | MONITOR_GATES
    | HUMAN_GATES
    | TRANSLATION_GATES
    | {
        "native_reference_locked",
        "confirmatory_parameters",
        "preregistration",
        "confirmatory_authorization",
    },
}


class Evidence(Contract):
    gate: Resolved
    relative_path: Resolved
    sha256: SHA
    approver: Resolved
    attestation: Resolved  # textual attestation only, NOT authenticated by this scaffold
    approved_utc: str

    @field_validator("approved_utc")
    @classmethod
    def utc(cls, value: str) -> str:
        parsed = datetime.fromisoformat(value)
        if parsed.utcoffset() != timedelta(0):
            raise ValueError("approval timestamp must be UTC")
        if parsed > datetime.now().astimezone():
            raise ValueError("approval cannot be future-dated")
        return value


class ReviewBundle(Contract):
    """External review inputs; this package cannot issue or authenticate an approval."""

    schema_version: Literal["workshop-v1-review/1"] = "workshop-v1-review/1"
    data_kind: Literal["scientific"]
    stage: Stage
    study_hash: SHA
    population_hash: SHA
    source_manifest_hash: SHA | None
    reviewed_commit: GitSHA
    output_directory: Resolved
    evidence: tuple[Evidence, ...]

    @model_validator(mode="after")
    def gates(self) -> Self:
        if len({e.gate for e in self.evidence}) != len(self.evidence):
            raise ValueError("duplicate gate evidence")
        return self


class PreflightReport(Contract):
    stage: Stage
    study_hash: SHA
    blockers: tuple[str, ...]
    structural_checks_passed: bool
    execution_ready: Literal[False] = False
    limitation: Literal["No scientific executor or authenticated authorization verifier is implemented."] = (
        "No scientific executor or authenticated authorization verifier is implemented."
    )


def safe_unused_output(path: Path, *, synthetic: bool = False) -> Path:
    """Check both lexical and resolved paths, including symlink aliases into results/."""
    if "results" in {p.casefold() for p in path.parts}:
        raise ValueError("Workshop-v1 scaffold cannot write into results/")
    resolved = path.expanduser().resolve()
    if "results" in {p.casefold() for p in resolved.parts}:
        raise ValueError("output resolves into results/")
    check_output_directory(path)
    if synthetic and not resolved.name.startswith("synthetic-workshop-v1-"):
        raise ValueError("synthetic output directory must start with synthetic-workshop-v1-")
    return resolved


def check_review(
    review: ReviewBundle,
    *,
    study: Study,
    population: Population,
    stage: Stage,
    output: Path,
    root: Path,
    commit: str | None,
    source_manifest_hash: str | None,
) -> None:
    if (
        review.stage != stage
        or review.study_hash != study.artifact_hash
        or review.population_hash != population.artifact_hash
        or review.reviewed_commit != commit
        or review.source_manifest_hash != source_manifest_hash
        or Path(review.output_directory) != output
    ):
        raise ValueError("review is stale or bound to another stage/study/population/commit/output/input")
    missing = REQUIRED_GATES[stage] - {e.gate for e in review.evidence}
    if missing:
        raise ValueError("missing review gates: " + ", ".join(sorted(missing)))
    for evidence in review.evidence:
        relative = Path(evidence.relative_path)
        file = (root / relative).resolve()
        if relative.is_absolute() or ".." in relative.parts or not file.is_relative_to(root.resolve()):
            raise ValueError("review evidence must be repository-relative without traversal")
        if hashlib.sha256(file.read_bytes()).hexdigest() != evidence.sha256:
            raise ValueError(f"review evidence content drift: {evidence.gate}")


def preflight(
    study: Study,
    *,
    root: Path,
    output: Path,
    stage: Stage = Stage.GENERATION,
    expected_commit: str | None = None,
    expected_study_hash: str | None = None,
    snapshot: DatasetSnapshot | None = None,
    population: Population | None = None,
    review: ReviewBundle | None = None,
    generations: tuple[GenerationRecord, ...] | None = None,
) -> PreflightReport:
    blockers = study.generation_blockers()
    if study.status != "frozen":
        blockers.append("study is not frozen")
    if study.sampling.pairing == "partial":
        blockers.append("partial scheduling requires a reviewed cell manifest; adapter not implemented")
    if study.data_kind is not DataKind.SCIENTIFIC:
        blockers.append("synthetic fixtures cannot pass scientific preflight")
    if expected_study_hash != study.artifact_hash:
        blockers.append("reviewed study hash absent or mismatched")
    commit = None
    try:
        commit, _ = git_integrity(root, expected_commit)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        blockers.append(f"git integrity: {exc}")
    resolved_output = (root / output).resolve()
    try:
        resolved_output = safe_unused_output(root / output)
    except (ValueError, OSError) as exc:
        blockers.append(f"output: {exc}")
    if snapshot is None or population is None:
        blockers.append("frozen dataset snapshot and selected population are required")
    else:
        try:
            validate_population(study, snapshot, population)
        except ValueError as exc:
            blockers.append(f"population: {exc}")
    if (
        stage in {Stage.DIRECT_MONITOR, Stage.TRANSLATED_MONITOR, Stage.CONFIRMATORY}
        and study.monitoring.automated_monitor is None
    ):
        blockers.append("automated monitor unresolved")
    if stage in {Stage.HUMAN_REFERENCE, Stage.CONFIRMATORY} and study.monitoring.human_reference is None:
        blockers.append("native human-reference protocol unresolved")
    if stage in {Stage.TRANSLATED_MONITOR, Stage.CONFIRMATORY} and study.monitoring.translator is None:
        blockers.append("translator unresolved")
    if stage is Stage.CONFIRMATORY and (
        study.designation != "confirmatory" or study.sampling.population_role != "confirmatory"
    ):
        blockers.append("confirmatory stage requires an explicit confirmatory design and population")
    source_hash = None
    if stage is not Stage.GENERATION:
        if not generations or population is None:
            blockers.append("exact validated source-generation manifest required for this stage")
        else:
            from clsm.downstream.contracts import object_hash

            try:
                validate_generations(generations, study, population)
                source_hash = object_hash([r.model_dump(mode="json") for r in generations])
            except ValueError as exc:
                blockers.append(f"source generations: {exc}")
    elif generations is not None:
        blockers.append("pre-generation review cannot bind existing outcomes")
    if review is None or population is None:
        blockers.append("external stage-specific review/authorization evidence required")
    else:
        try:
            check_review(
                review,
                study=study,
                population=population,
                stage=stage,
                output=resolved_output,
                root=root,
                commit=commit,
                source_manifest_hash=source_hash,
            )
        except (ValueError, OSError) as exc:
            blockers.append(f"review: {exc}")
    return PreflightReport(
        stage=stage,
        study_hash=study.artifact_hash,
        blockers=tuple(blockers),
        structural_checks_passed=not blockers,
    )

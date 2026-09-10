"""Track-A artifact integrity and completion accounting, without model execution."""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from clsm.generation import GenSpec
from clsm.schemas import GenerationRecord, ParseStatus, StopReason
from clsm.track_a_dataset_pin import digest


def write_new(path: Path, text: str) -> None:
    """Atomic publication without overwrite, including concurrent writers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp, path)  # fails if target already exists; never os.replace
    finally:
        os.unlink(temp)


def record_key(record: GenerationRecord | GenSpec) -> tuple[str, str, int]:
    return record.item_id, record.condition.value, record.sample_idx


def validate_records(specs: list[GenSpec], records: list[GenerationRecord]) -> list[GenSpec]:
    planned = {record_key(s): s for s in specs}
    if len(planned) != len(specs):
        raise ValueError("duplicate planned specifications")
    seen = set()
    for rec in records:
        key = record_key(rec)
        if key in seen or key not in planned:
            raise ValueError("duplicate or unplanned output record")
        seen.add(key)
        spec = planned[key]
        for field in (
            "experiment_id",
            "seed",
            "prompt_sha256",
            "question_sha256",
            "correct_letter",
            "hint_target_letter",
            "dataset_revision",
            "subject",
            "cue_version",
            "prompt_template_version",
            "dataset",
            "cue_type",
        ):
            if getattr(rec, field) != getattr(spec, field):
                raise ValueError(f"output/spec mismatch: {field}")
    return [s for key, s in planned.items() if key not in seen]


def artifact_hashes(directory: Path) -> dict[str, str]:
    return {
        str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(directory.rglob("*"))
        if p.is_file()
    }


class TrackARunCompletionManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal["track-a-completion/1"] = "track-a-completion/1"
    experiment_id: str
    scientific_config_hash: str
    git_commit: str
    dataset_content_hash: str
    planned_generations: int = Field(gt=0)
    completed_generations: int = Field(ge=0)
    missing_generations: int = Field(ge=0)
    parse_valid: int = Field(ge=0)
    parse_invalid: int = Field(ge=0)
    stop_reason_counts: dict[str, int]
    raw_artifact_count: int = Field(ge=0)
    raw_artifact_manifest_hash: str
    raw_artifacts: dict[str, str]
    output_artifacts: dict[str, str] = Field(default_factory=dict)
    started_utc: str
    finished_utc: str

    @model_validator(mode="after")
    def check_counts(self) -> TrackARunCompletionManifest:
        if self.completed_generations + self.missing_generations != self.planned_generations:
            raise ValueError("completion accounting mismatch")
        if self.missing_generations:
            raise ValueError("incomplete run cannot publish a completion manifest")
        if self.parse_valid + self.parse_invalid != self.completed_generations:
            raise ValueError("parse accounting mismatch")
        if (
            set(self.stop_reason_counts) != {s.value for s in StopReason}
            or any(v < 0 for v in self.stop_reason_counts.values())
            or sum(self.stop_reason_counts.values()) != self.completed_generations
        ):
            raise ValueError("stop reason accounting mismatch")
        if self.raw_artifact_count != 4 * self.completed_generations:
            raise ValueError("missing raw artifacts")
        if len(self.raw_artifacts) != self.raw_artifact_count or digest(self.raw_artifacts) != (
            self.raw_artifact_manifest_hash
        ):
            raise ValueError("raw artifact manifest hash/count mismatch")
        for value in (
            self.scientific_config_hash,
            self.dataset_content_hash,
            self.raw_artifact_manifest_hash,
            *self.raw_artifacts.values(),
            *self.output_artifacts.values(),
        ):
            if not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("invalid artifact/scientific SHA-256")
        if not re.fullmatch(r"[0-9a-f]{40}", self.git_commit):
            raise ValueError("invalid git commit")
        start, end = dt.datetime.fromisoformat(self.started_utc), dt.datetime.fromisoformat(self.finished_utc)
        if start.utcoffset() is None or end.utcoffset() is None or end < start:
            raise ValueError("invalid completion timestamps")
        return self


def completion_from_records(
    specs: list[GenSpec],
    records: list[GenerationRecord],
    *,
    scientific_hash: str,
    git_commit: str,
    dataset_content_hash: str,
    raw_hashes: dict[str, str],
    started_utc: str,
    finished_utc: str,
) -> TrackARunCompletionManifest:
    missing = validate_records(specs, records)
    from clsm.track_a_backend import artifact_stem

    if not missing:
        expected_files = {
            f"{artifact_stem(s)}.{suffix}"
            for s in specs
            for suffix in ("stdout.txt", "stderr.txt", "cleaned.txt", "meta.json")
        }
        if set(raw_hashes) != expected_files:
            raise ValueError("missing raw artifacts or unexpected artifact names")
    stops = Counter(r.stop_reason.value for r in records)
    valid = sum(r.parse_status is ParseStatus.VALID for r in records)
    return TrackARunCompletionManifest(
        experiment_id=specs[0].experiment_id,
        scientific_config_hash=scientific_hash,
        git_commit=git_commit,
        dataset_content_hash=dataset_content_hash,
        planned_generations=len(specs),
        completed_generations=len(records),
        missing_generations=len(missing),
        parse_valid=valid,
        parse_invalid=len(records) - valid,
        stop_reason_counts={s.value: stops[s.value] for s in StopReason},
        raw_artifact_count=len(raw_hashes),
        raw_artifact_manifest_hash=digest(raw_hashes),
        raw_artifacts=raw_hashes,
        started_utc=started_utc,
        finished_utc=finished_utc,
    )

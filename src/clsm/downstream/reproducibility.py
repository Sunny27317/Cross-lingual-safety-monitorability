"""Generic provenance manifest for any future downstream execution stage."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal

from pydantic import Field, field_validator, model_validator

from clsm.downstream.contracts import SHA, Contract, DataKind, Nonempty, Provenance


class DownstreamExecutionManifest(Contract):
    schema_version: Literal["downstream-execution/1"] = "downstream-execution/1"
    stage: Nonempty
    protocol_hash: SHA
    config_hash: SHA
    dataset_hash: SHA
    source_trace_hashes: tuple[SHA, ...] = ()
    source_item_ids: tuple[Nonempty, ...] = ()
    model_identity: Nonempty | None = None
    judge_identity: Nonempty | None = None
    translator_identity: Nonempty | None = None
    prompt_hash: SHA | None = None
    rubric_version: Nonempty | None = None
    planned_calls: int = Field(ge=0)
    completed_calls: int = Field(ge=0)
    retries: int = Field(ge=0)
    failures: tuple[Nonempty, ...] = ()
    exclusions: tuple[Nonempty, ...] = ()
    started_utc: str
    finished_utc: str | None = None
    authorization_artifact_hash: SHA | None = None
    output_hashes: tuple[SHA, ...] = ()
    provenance: Provenance

    @field_validator("started_utc", "finished_utc")
    @classmethod
    def utc_timestamp(cls, value: str | None) -> str | None:
        if value is not None and datetime.fromisoformat(value).utcoffset() != timedelta(0):
            raise ValueError("manifest timestamp must be UTC")
        return value

    @model_validator(mode="after")
    def coherent(self) -> DownstreamExecutionManifest:
        if self.completed_calls > self.planned_calls:
            raise ValueError("completed calls exceed planned calls")
        if len(set(self.source_trace_hashes)) != len(self.source_trace_hashes):
            raise ValueError("duplicate source trace hash")
        if len(set(self.output_hashes)) != len(self.output_hashes):
            raise ValueError("duplicate output hash")
        if self.provenance.data_kind is DataKind.SCIENTIFIC and self.authorization_artifact_hash is None:
            raise ValueError("scientific execution requires an authorization artifact")
        return self


def manifest_hash(manifest: DownstreamExecutionManifest) -> str:
    return manifest.artifact_hash

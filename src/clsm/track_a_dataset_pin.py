"""Auditable dataset selection and content pins. Only create-real-pin may use network.

Fixture checks never download. Pin validation never runs a generator or a judge.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib
import json
import re
from collections import Counter
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from clsm.config import DatasetConfig, load_experiment_config
from clsm.data import MCQSource, RawItem, coerce_answer_idx, question_sha256, select_pilot_items
from clsm.errors import ClsmError
from clsm.schemas import MCQItem

DEFAULT_PIN = Path("experiments/M1-Mac-Feasibility/DATASET_CONTENT_PIN.json")
TOOL_VERSION: Literal["track-a-dataset-pin/1"] = "track-a-dataset-pin/1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def utcnow() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def content_digest(
    *,
    dataset_repo: str,
    dataset_config: str,
    dataset_split: str,
    requested_revision: str,
    resolved_revision: str,
    datasets_library_version: str,
    selection_rule: str,
    subjects: Sequence[str],
    items_per_subject: int,
    number_of_items: int,
    exact_item_ids: Sequence[str],
    selected_items: Sequence[PinnedItem],
) -> str:
    """D-067: the content SHA binds BOTH the ordered selected item content AND the
    identifying dataset metadata (repo/config/split, requested + resolved revision,
    datasets library version, selection rule, subject list, per-subject and total
    counts, exact IDs). The pin file is git-ignored, so this hash — bound into the
    human authorization and the RunToken — is the sole cryptographic anchor for the
    whole reviewed selection."""
    return digest(
        {
            "dataset_repo": dataset_repo,
            "dataset_config": dataset_config,
            "dataset_split": dataset_split,
            "requested_revision": requested_revision,
            "resolved_revision": resolved_revision,
            "datasets_library_version": datasets_library_version,
            "selection_rule": selection_rule,
            "subjects": list(subjects),
            "items_per_subject": items_per_subject,
            "number_of_items": number_of_items,
            "exact_item_ids": list(exact_item_ids),
            "items": [it.model_dump() for it in selected_items],
        }
    )


class PinnedItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    item_id: str
    subject: str
    question: str
    choices: list[str] = Field(min_length=4, max_length=4)
    answer_idx: int = Field(ge=0, le=3)

    @model_validator(mode="after")
    def check_content(self) -> PinnedItem:
        if not self.question.strip() or any(not c.strip() for c in self.choices):
            raise ValueError("empty question or choice")
        if not re.fullmatch(rf"mmlu:{re.escape(self.subject)}:[0-9]+", self.item_id):
            raise ValueError("invalid stable item identity")
        return self

    def to_mcq(self) -> MCQItem:
        return MCQItem(
            **self.model_dump(), dataset="mmlu", question_sha256=question_sha256(self.question, self.choices)
        )


class DatasetContentPin(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    schema_version: Literal["track-a-dataset-pin/1"] = TOOL_VERSION
    dataset_repo: str
    dataset_config: str
    dataset_split: str
    requested_revision: str
    resolved_revision: str
    datasets_library_version: str = Field(min_length=1)
    source_kind: Literal["fixture", "huggingface"]
    source_files_sha256: dict[str, str]
    selection_rule: Literal["sha256_sorted_first_n"]
    subjects: list[str]
    items_per_subject: int = Field(gt=0)
    max_chars: int = Field(gt=0)
    exact_item_ids: list[str]
    number_of_items: int = Field(gt=0)
    content_sha256: str
    schema_verified: Literal[True]
    choice_order_verified: Literal[True]
    label_mapping_verified: Literal[True]
    created_utc: str
    tool_version: Literal["track-a-dataset-pin/1"] = TOOL_VERSION
    selected_items: list[PinnedItem]
    exclusions: list[dict[str, Any]]

    @model_validator(mode="after")
    def validate_contents(self) -> DatasetContentPin:
        if not re.fullmatch(r"[0-9a-f]{40}", self.requested_revision):
            raise ValueError("requested revision must be an exact commit")
        if self.resolved_revision != self.requested_revision:
            raise ValueError("resolved revision mismatch")
        if len(set(self.subjects)) != len(self.subjects) or not self.subjects:
            raise ValueError("duplicate or missing subjects")
        ids = [it.item_id for it in self.selected_items]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate item IDs")
        if ids != sorted(ids) or ids != self.exact_item_ids:
            raise ValueError("item IDs must match canonical sorted content")
        if len(ids) != self.number_of_items or len(ids) != len(self.subjects) * self.items_per_subject:
            raise ValueError("wrong expected number of items")
        if Counter(it.subject for it in self.selected_items) != Counter(
            {s: self.items_per_subject for s in self.subjects}
        ):
            raise ValueError("wrong subject or per-subject count")
        if any(len(it.question) + sum(map(len, it.choices)) > self.max_chars for it in self.selected_items):
            raise ValueError("item exceeds frozen length cap")
        if content_digest(
            dataset_repo=self.dataset_repo,
            dataset_config=self.dataset_config,
            dataset_split=self.dataset_split,
            requested_revision=self.requested_revision,
            resolved_revision=self.resolved_revision,
            datasets_library_version=self.datasets_library_version,
            selection_rule=self.selection_rule,
            subjects=self.subjects,
            items_per_subject=self.items_per_subject,
            number_of_items=self.number_of_items,
            exact_item_ids=self.exact_item_ids,
            selected_items=self.selected_items,
        ) != self.content_sha256:
            raise ValueError("content hash mismatch")
        if not self.source_files_sha256 or any(
            not re.fullmatch(r"[0-9a-f]{64}", h) for h in self.source_files_sha256.values()
        ):
            raise ValueError("missing source file hashes")
        if dt.datetime.fromisoformat(self.created_utc).utcoffset() is None:
            raise ValueError("created_utc must include timezone")
        return self

    def validate_config(self, cfg: DatasetConfig, *, require_real: bool = False) -> None:
        for key, value in {
            "dataset_repo": cfg.id,
            "dataset_config": cfg.config_name,
            "dataset_split": cfg.split,
            "requested_revision": cfg.revision,
            "subjects": list(cfg.subjects),
            "items_per_subject": cfg.items_per_subject,
            "max_chars": cfg.max_chars,
            "selection_rule": cfg.selection_rule,
        }.items():
            if getattr(self, key) != value:
                raise ValueError(f"dataset pin/config mismatch: {key}")
        if require_real and self.source_kind != "huggingface":
            raise ValueError("fixture pin cannot be used for scientific generation")


def create_pin(
    cfg: DatasetConfig,
    source: MCQSource,
    *,
    resolved_revision: str,
    datasets_library_version: str,
    source_kind: Literal["fixture", "huggingface"],
    source_files_sha256: dict[str, str],
) -> DatasetContentPin:
    # Reuse the frozen selector: invalid items are logged, never silently dropped.
    items, exclusions = select_pilot_items(cfg, source=source, strict=False)
    selected = [
        PinnedItem(
            item_id=x.item_id,
            subject=x.subject,
            question=x.question,
            choices=x.choices,
            answer_idx=x.answer_idx,
        )
        for x in sorted(items, key=lambda x: x.item_id)
    ]
    exact_item_ids = [x.item_id for x in selected]
    return DatasetContentPin(
        dataset_repo=cfg.id,
        dataset_config=cfg.config_name,
        dataset_split=cfg.split,
        requested_revision=cfg.revision or "",
        resolved_revision=resolved_revision,
        datasets_library_version=datasets_library_version,
        source_kind=source_kind,
        source_files_sha256=source_files_sha256,
        selection_rule=cfg.selection_rule,
        subjects=cfg.subjects,
        items_per_subject=cfg.items_per_subject,
        max_chars=cfg.max_chars,
        exact_item_ids=exact_item_ids,
        number_of_items=len(selected),
        content_sha256=content_digest(
            dataset_repo=cfg.id,
            dataset_config=cfg.config_name,
            dataset_split=cfg.split,
            requested_revision=cfg.revision or "",
            resolved_revision=resolved_revision,
            datasets_library_version=datasets_library_version,
            selection_rule=cfg.selection_rule,
            subjects=cfg.subjects,
            items_per_subject=cfg.items_per_subject,
            number_of_items=len(selected),
            exact_item_ids=exact_item_ids,
            selected_items=selected,
        ),
        schema_verified=True,
        choice_order_verified=True,
        label_mapping_verified=True,
        created_utc=utcnow(),
        selected_items=selected,
        exclusions=[{"subject": s, "row_index": r, "reason": why} for s, r, why in exclusions.excluded],
    )


def load_pin(path: str | Path, cfg: DatasetConfig, *, require_real: bool = False) -> DatasetContentPin:
    pin = DatasetContentPin.model_validate_json(Path(path).read_text(encoding="utf-8"))
    pin.validate_config(cfg, require_real=require_real)
    return pin


def write_pin(pin: DatasetContentPin, path: Path) -> None:
    # Exclusive creation: reruns must never overwrite reviewed content.
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(pin.model_dump_json(indent=2) + "\n")


class FixtureSource:
    """Clearly synthetic, deterministic test questions; no scientific dataset content."""

    def iter_subject(self, subject: str) -> Iterator[RawItem]:
        for i in range(7):
            yield RawItem(
                subject,
                i,
                f"SYNTHETIC FIXTURE {subject} {i}",
                ["fixture A", "fixture B", "fixture C", "fixture D"],
                i % 4,
            )


def fixture_pin(cfg: DatasetConfig) -> DatasetContentPin:
    return create_pin(
        cfg,
        FixtureSource(),
        resolved_revision=cfg.revision or "",
        datasets_library_version="fixture-no-datasets-library",
        source_kind="fixture",
        source_files_sha256={"synthetic": digest("fixture-v1")},
    )


class _RowsSource:
    def __init__(self, rows: Sequence[dict[str, Any]]) -> None:
        self.rows = rows

    def iter_subject(self, subject: str) -> Iterator[RawItem]:
        for i, row in enumerate(self.rows):
            if row["subject"] == subject:
                yield RawItem(subject, i, row["question"], row["choices"], coerce_answer_idx(row["answer"]))


def create_real_pin(cfg: DatasetConfig, *, allow_dataset_download: bool) -> DatasetContentPin:
    """Explicit dataset-only opt-in; pinned native parquet files, never scripts or model code.

    Refuse if the pinned revision lacks the expected native parquet layout. Never fall
    back to a converted branch or a different revision. That needs separate review.
    """
    if not allow_dataset_download:
        raise ValueError("real dataset pin requires --allow-dataset-download")
    hub = importlib.import_module("huggingface_hub")
    datasets = importlib.import_module("datasets")
    info = hub.HfApi().dataset_info(cfg.id, revision=cfg.revision, files_metadata=True)
    if info.sha != cfg.revision:
        raise ValueError("resolved revision mismatch")
    names = sorted(
        s.rfilename
        for s in info.siblings
        if re.fullmatch(
            rf"{re.escape(cfg.config_name)}/{re.escape(cfg.split)}-[0-9]+-of-[0-9]+\.parquet", s.rfilename
        )
    )
    if not names:
        raise ValueError("pinned revision has no expected native parquet files; STOP for source review")
    paths = [hub.hf_hub_download(cfg.id, name, repo_type="dataset", revision=info.sha) for name in names]
    hashes = {
        name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
        for name, path in zip(names, paths, strict=True)
    }
    ds = datasets.load_dataset("parquet", data_files={cfg.split: paths}, split=cfg.split)
    if not {"question", "choices", "answer", "subject"} <= set(ds.column_names):
        raise ValueError("dataset schema missing required columns")
    feature = ds.features["answer"]
    if getattr(feature, "names", None) != ["A", "B", "C", "D"]:
        raise ValueError("label mapping not verified as A/B/C/D in exact order")
    rows = list(ds)
    for row in rows:
        # Preserve original question/choice order; no string/int coercion of malformed rows.
        if not isinstance(row["question"], str) or not isinstance(row["subject"], str):
            raise ValueError("invalid question/subject schema")
        if not isinstance(row["choices"], list) or any(not isinstance(c, str) for c in row["choices"]):
            raise ValueError("invalid choice schema")
        coerce_answer_idx(row["answer"])
    return create_pin(
        cfg,
        _RowsSource(rows),
        resolved_revision=info.sha,
        datasets_library_version=datasets.__version__,
        source_kind="huggingface",
        source_files_sha256=hashes,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["fixture-check", "create-real-pin"])
    parser.add_argument("--config", default="configs/track_a_pilot/pilot.yaml")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-dataset-download", action="store_true")
    args = parser.parse_args(argv)
    try:
        cfg = load_experiment_config(args.config).dataset
        pin = (
            fixture_pin(cfg)
            if args.mode == "fixture-check"
            else create_real_pin(cfg, allow_dataset_download=args.allow_dataset_download)
        )
        DatasetContentPin.model_validate_json(pin.model_dump_json()).validate_config(cfg)
        if args.mode == "create-real-pin":
            write_pin(pin, args.output or DEFAULT_PIN)
        elif args.output is not None:
            raise ValueError("fixture-check never writes a production content pin")
        print(
            canonical_json(
                {
                    "mode": args.mode,
                    "valid": True,
                    "items": pin.number_of_items,
                    "content_sha256": pin.content_sha256,
                }
            )
        )
        return 0
    except (ValueError, OSError, ImportError, ClsmError) as exc:
        print(f"REFUSED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

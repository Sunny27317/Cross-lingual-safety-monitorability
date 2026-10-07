"""Read stage directories into ``final_analysis.build_observations`` inputs.

Pre-result implementation, validated on synthetic miniature directories only
(2026-10-06). Loading the real run directories is the unseal step: the loader refuses any
path inside an ``experiments/_runs`` tree unless the caller passes
``allow_scientific_runs=True`` together with an existing analysis-authorization file
(pre-unseal checklist U-17/U-18).

Guarantees:

- Every file is either read, explicitly ignored (listed), or reported as an error.
  Nothing is skipped silently.
- File names must agree with the identifiers inside them (generation_id, judge_task_id,
  retry suffix).
- A translated-judge record must match the SHA-256 of its translation record when a
  translation directory is given.
- No filtering depends on any label or outcome. Labels are passed through untouched.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from clsm.workshop_v1 import final_analysis as fa
from clsm.workshop_v1.output_parsing import _ARABIC_SCRIPT_RE, _LATIN_RE

RETRY_SUFFIX = ".retry-2.json"


@dataclass
class LoadedStage:
    generations: list[dict[str, Any]] = field(default_factory=list)
    direct_judge: list[dict[str, Any]] = field(default_factory=list)
    translated_judge: list[dict[str, Any]] = field(default_factory=list)
    rater_rows: list[dict[str, Any]] | None = None
    adjudications: list[dict[str, Any]] | None = None
    errors: list[str] = field(default_factory=list)
    ignored: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)


def script_fraction(text: str | None, language: str) -> float | None:
    """D-PG-1 continuous covariate: share of script characters in the requested script,
    recomputed with the frozen parser's own expressions. None when undefined."""
    if text is None or not text.strip():
        return None
    arabic = len(_ARABIC_SCRIPT_RE.findall(text))
    latin = len(_LATIN_RE.findall(text))
    total = arabic + latin
    if total == 0:
        return None
    return (arabic if language == "ur" else latin) / total


def _guard(paths: Sequence[Path | None], allow: bool, authorization: Path | None) -> None:
    for path in paths:
        if path is None:
            continue
        parts = path.resolve().parts
        if any(parts[i] == "experiments" and parts[i + 1] == "_runs" for i in range(len(parts) - 1)):
            if not allow:
                raise PermissionError(
                    f"refusing to read scientific run outputs ({path}); loading them is the unseal step"
                )
            if authorization is None or not authorization.is_file():
                raise PermissionError(
                    "an existing analysis-authorization file is required to read run outputs"
                )


def _read_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}:unreadable:{type(exc).__name__}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path.name}:not_an_object")
        return None
    return value


def _generations(directory: Path, stage: LoadedStage) -> None:
    for path in sorted(directory.iterdir()):
        if not (path.name.startswith("generation-") and path.suffix == ".json"):
            stage.ignored.append(f"generation_dir:{path.name}")
            continue
        rec = _read_json(path, stage.errors)
        if rec is None:
            continue
        gid = rec.get("generation_id")
        if path.stem != gid:
            stage.errors.append(f"{path.name}:filename_generation_id_mismatch")
            continue
        parsed = rec.get("parsed") or {}
        span = parsed.get("reasoning_span")
        stage.generations.append(
            {
                "generation_id": gid,
                "source_item_id": rec.get("source_item_id"),
                "model": rec.get("model"),
                "language": rec.get("language"),
                "condition": rec.get("condition"),
                "sample_index": rec.get("sample_index"),
                "runtime_success": bool((rec.get("qc") or {}).get("runtime_success")),
                "final_answer": parsed.get("final_answer"),
                "compliance_flag": parsed.get("language_compliance"),
                "compliance_fraction": script_fraction(span, str(rec.get("language"))),
                "visible_trace": isinstance(span, str) and bool(span.strip()),
            }
        )


def _judges(directory: Path, arm: str, stage: LoadedStage) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for path in sorted(directory.iterdir()):
        if not (path.name.startswith("judge-") and path.name.endswith(".json")):
            stage.ignored.append(f"{arm}_dir:{path.name}")
            continue
        rec = _read_json(path, stage.errors)
        if rec is None:
            continue
        task = rec.get("task") or {}
        tid = task.get("judge_task_id")
        is_retry = path.name.endswith(RETRY_SUFFIX)
        expected = f"{tid}{RETRY_SUFFIX}" if is_retry else f"{tid}.json"
        if path.name != expected:
            stage.errors.append(f"{arm}:{path.name}:filename_task_id_mismatch")
            continue
        if is_retry and not rec.get("retry_of"):
            stage.errors.append(f"{arm}:{path.name}:retry_without_retry_of")
            continue
        if rec.get("immutable") is not True:
            stage.errors.append(f"{arm}:{path.name}:not_immutable")
            continue
        out.append(rec)
    return out


def _jsonl(path: Path, stage: LoadedStage, kind: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        stage.errors.append(f"{kind}:{path.name}:unreadable:{type(exc).__name__}")
        return rows
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            stage.errors.append(f"{kind}:{path.name}:line_{n}:invalid_json")
    return rows


def load_stage(
    *,
    generation_dir: Path,
    direct_judge_dir: Path,
    translated_judge_dir: Path,
    translation_dir: Path | None = None,
    rater_files: Sequence[Path] = (),
    adjudication_file: Path | None = None,
    allow_scientific_runs: bool = False,
    authorization: Path | None = None,
) -> LoadedStage:
    _guard(
        [
            generation_dir,
            direct_judge_dir,
            translated_judge_dir,
            translation_dir,
            *rater_files,
            adjudication_file,
        ],
        allow_scientific_runs,
        authorization,
    )
    stage = LoadedStage()
    _generations(generation_dir, stage)
    stage.direct_judge = _judges(direct_judge_dir, "direct", stage)
    stage.translated_judge = _judges(translated_judge_dir, "translated", stage)
    if translation_dir is not None:
        failures = sorted(translation_dir.glob("translation-failure-*.json"))
        stage.counts["historical_translation_failure_records"] = len(failures)
        for rec in stage.translated_judge:
            if rec.get("retry_of"):
                continue
            tid = rec.get("translation_id") or (rec.get("task") or {}).get("translation_id")
            path = translation_dir / f"{tid}.json"
            if not path.is_file():
                stage.errors.append(f"translated:{tid}:translation_record_missing")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != rec.get("translation_record_sha256"):
                stage.errors.append(f"translated:{tid}:translation_record_sha256_mismatch")
    if rater_files:
        rows = [r for p in sorted(rater_files) for r in _jsonl(p, stage, "rater")]
        seen: set[tuple[str, str]] = set()
        for r in rows:
            key = (str(r.get("blind_id")), str(r.get("rater_id")))
            if key in seen:
                stage.errors.append(f"rater:{key[0]}:{key[1]}:duplicate_label")
            seen.add(key)
        stage.rater_rows = rows
        stage.adjudications = _jsonl(adjudication_file, stage, "adjudication") if adjudication_file else []
    stage.counts.update(
        {
            "generation_records": len(stage.generations),
            "direct_judge_records": len(stage.direct_judge),
            "translated_judge_records": len(stage.translated_judge),
            "rater_rows": len(stage.rater_rows or []),
            "adjudication_rows": len(stage.adjudications or []),
            "ignored_files": len(stage.ignored),
            "errors": len(stage.errors),
        }
    )
    stage.errors.sort()
    stage.ignored.sort()
    return stage


def load_observations(
    *, items: Mapping[str, Mapping[str, Any]], human_pool: Mapping[str, Mapping[str, Any]], **paths: Any
) -> tuple[fa.JoinReport, LoadedStage]:
    """Load the stage, then join. Any loader error is carried into the join report, so a
    non-empty ``errors`` list blocks analysis."""
    stage = load_stage(**paths)
    report = fa.build_observations(
        generations=stage.generations,
        items=items,
        direct_judge=stage.direct_judge,
        translated_judge=stage.translated_judge,
        human_pool=human_pool,
        rater_rows=stage.rater_rows,
        adjudications=stage.adjudications,
    )
    report.errors = sorted([*report.errors, *(f"loader:{e}" for e in stage.errors)])
    report.rows = fa.annotate_missingness(report.rows)
    report.accounting["loader_ignored_files"] = len(stage.ignored)
    return report, stage


__all__ = ["LoadedStage", "load_observations", "load_stage", "script_fraction"]

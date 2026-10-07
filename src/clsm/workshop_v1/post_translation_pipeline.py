"""Post-translation technical QC and analysis-input-table scaffolding.
# mypy: ignore-errors

The canonical translation stage seal is written ONLY by
``clsm.workshop_v1.translator_launcher.seal()``; this module never writes a seal.

All functions are fail-closed and outcome-agnostic. They inspect schemas, IDs,
hashes, and technical states; they do not summarize scientific labels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TRANSLATION_MANIFEST = ROOT / "engineering/workshop_v1_translation_task_manifest.json"
TRANSLATION_OUTPUT = ROOT / "experiments/_runs/workshop-v1-translation"
TRANSLATION_CONFIG_HASH = "74b81473f4c714e8146c352c6c351772ea995b3dff6f37c8a4af06ca311f99bc"
ARTIFACT_MANIFEST_HASH = "84cad691de2a13f19b4609f924e24aa5aceb582be7278d406359bdd861f7a2bd"
TASK_MANIFEST_HASH = "635d5f8b58b972dcaa40bc4c2933b0529fb2a5b35fc3b76f1dd2f8b1e1f7fb8d"
JUDGE_PROMPT_HASH = "050ed49289b435ed84ab565dcca000cafd4554de3c11230edc2fe56d29844984"
TRANSLATION_AMENDMENT_HASH = "3a054e8bac831a1cbbfd25b545c15562bbc76b82824266ba707798e104720dc5"
EFFECTIVE_TRANSLATION_CONFIG_HASH = "106f366c7a0010dab11849150e48b2fb88cb3a4d23260a9abdd750760e6b4171"
IDENTITY_REASON = "zero_urdu_script_letters"
MAX_AUTHORIZED_IDENTITY_TRANSLATIONS = 6
GENERATION_DIR = ROOT / "experiments/_runs/workshop-v1-main-attempt-2"
ANALYSIS_INPUT_LAYER_FILES = (
    "engineering/workshop_v1_analysis_contract.json",
    "src/clsm/workshop_v1/post_translation_pipeline.py",
)
ANALYSIS_INPUT_LAYER_RECIPE = (
    "sha256 over UTF-8 concatenation of '<repo-relative path>\\t<sha256(file bytes)>\\n' for each "
    "path in ANALYSIS_INPUT_LAYER_FILES, sorted by path; file bytes are hashed as stored (no "
    "normalization)"
)


def analysis_input_layer_sha256(root: Path = ROOT) -> str:
    """Reproducible hash of the analysis-input layer (recipe: ANALYSIS_INPUT_LAYER_RECIPE)."""
    lines = "".join(
        f"{rel}\t{hashlib.sha256((root / rel).read_bytes()).hexdigest()}\n"
        for rel in sorted(ANALYSIS_INPUT_LAYER_FILES)
    )
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def _load_manifest(path: Path = TRANSLATION_MANIFEST) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    tasks = value.get("tasks", [])
    computed = hashlib.sha256(
        json.dumps(tasks, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    if value.get("manifest_hash") != computed or computed != TASK_MANIFEST_HASH:
        raise ValueError("translation manifest hash mismatch")
    if value.get("eligible_tasks") != 935 or len(tasks) != 935:
        raise ValueError("translation manifest must contain 935 tasks")
    return value


def _success_files(output: Path) -> list[Path]:
    return sorted(
        p for p in output.glob("translation-*.json") if not p.name.startswith("translation-failure-")
    )


def translation_qc(
    output: Path = TRANSLATION_OUTPUT, generation_dir: Path = GENERATION_DIR
) -> dict[str, Any]:
    """Validate translation records without reading translated text semantically."""
    manifest = _load_manifest()
    expected = {task["translation_id"]: task for task in manifest["tasks"]}
    files = _success_files(output) if output.exists() else []
    failures = sorted(output.glob("translation-failure-*.json")) if output.exists() else []
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in files:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append(f"corrupt:{path.name}")
            continue
        task_id = value.get("translation_id")
        task = expected.get(task_id)
        if task is None:
            errors.append(f"unexpected:{task_id}")
            continue
        required = {
            "immutable": True,
            "technical_status": "SUCCESS",
            "translation_config_hash": TRANSLATION_CONFIG_HASH,
            "artifact_manifest_hash": ARTIFACT_MANIFEST_HASH,
            "generation_record_id": task["source_trace_id"],
            "source_trace_hash": task["source_trace_hash"],
            "translator_revision": "ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a",
            "device": "cpu",
            "dtype": "torch.float32",
            "translation_amendment_hash": TRANSLATION_AMENDMENT_HASH,
            "effective_translation_config_hash": EFFECTIVE_TRANSLATION_CONFIG_HASH,
        }
        for field, wanted in required.items():
            if value.get(field) != wanted:
                errors.append(f"{task_id}:{field}")
        chunks = value.get("chunks")
        if not isinstance(chunks, list) or len(chunks) != value.get("source_chunk_count"):
            errors.append(f"{task_id}:chunk_count")
        elif [c.get("index") for c in chunks] != list(range(len(chunks))):
            errors.append(f"{task_id}:chunk_order")
        elif any(
            not isinstance(c.get("source_token_count"), int) or c["source_token_count"] > 200 for c in chunks
        ):
            errors.append(f"{task_id}:chunk_limit")
        if not isinstance(value.get("translated_text"), str) or not value["translated_text"].strip():
            errors.append(f"{task_id}:empty_output")
        records.append(value)
    ids = [r.get("translation_id") for r in records]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    missing_ids = sorted(set(expected) - set(ids))
    success_ids = set(ids)
    unresolved_failures = []
    for failure in failures:
        try:
            failure_value = json.loads(failure.read_text(encoding="utf-8"))
            failure_id = failure_value.get("translation_id")
        except (OSError, json.JSONDecodeError):
            failure_id = None
        if failure_id not in success_ids:
            unresolved_failures.append(failure.name)
    # D-TR-2 identity rule, checked here (before any judging): a record is an identity
    # translation iff its source span has zero Urdu-script letters.  Then its translated
    # trace must equal the source span, no unit may have been translated, and any explicit
    # identity fields must carry the canonical values.  Equal text with Urdu letters fails.
    from clsm.downstream.contracts import content_hash
    from clsm.workshop_v1.translation import has_urdu_script_letter

    identity_records = []
    for value in records:
        task_id = value.get("translation_id")
        hash_identity = (
            isinstance(value.get("source_span_hash"), str)
            and value.get("source_span_hash") == value.get("translated_trace_hash")
        )
        try:
            span = json.loads(
                (generation_dir / f"{value.get('generation_record_id')}.json").read_text(encoding="utf-8")
            )["parsed"]["reasoning_span"]
            zero_urdu = isinstance(span, str) and not has_urdu_script_letter(span)
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            errors.append(f"{task_id}:source_span_unavailable")
            continue
        if value.get("source_span_hash") != content_hash(span):
            errors.append(f"{task_id}:source_span_hash_mismatch")
        translated = value.get("translated_text")
        if not isinstance(translated, str) or content_hash(translated) != value.get("translated_trace_hash"):
            errors.append(f"{task_id}:translated_trace_hash_mismatch")
        flagged = value.get("translation_identity") is True
        if zero_urdu:
            translate_units = (value.get("technical_counts") or {}).get("translate_units")
            if not hash_identity:
                errors.append(f"{task_id}:zero_urdu_span_not_identity")
            if translate_units not in (0, None):
                errors.append(f"{task_id}:identity_with_translated_units")
            if "translation_identity" in value and (
                not flagged
                or value.get("translation_changed") is not False
                or value.get("identity_translation_reason") != IDENTITY_REASON
            ):
                errors.append(f"{task_id}:invalid_identity_provenance")
            identity_records.append(task_id)
        elif hash_identity or flagged or value.get("translation_changed") is False:
            errors.append(f"{task_id}:unexplained_identity")
    if len(identity_records) > MAX_AUTHORIZED_IDENTITY_TRANSLATIONS:
        errors.append("too_many_identity_translations")
    report = {
        "schema_version": "workshop-v1-translation-qc/1",
        "scientific_outcomes_inspected": False,
        "expected_tasks": 935,
        "successful_records": len(records),
        "technical_failure_records": len(failures),
        "unresolved_technical_failures": len(unresolved_failures),
        "identity_translation_count": len(identity_records),
        "identity_translation_ids": sorted(x for x in identity_records if isinstance(x, str)),
        "missing_ids": len(missing_ids),
        "duplicate_ids": duplicate_ids,
        "unexpected_ids": sorted(set(ids) - set(expected)),
        "errors": sorted(set(errors)),
        "task_manifest_hash": TASK_MANIFEST_HASH,
        "translation_config_hash": TRANSLATION_CONFIG_HASH,
        "translation_amendment_hash": TRANSLATION_AMENDMENT_HASH,
        "effective_translation_config_hash": EFFECTIVE_TRANSLATION_CONFIG_HASH,
        "artifact_manifest_hash": ARTIFACT_MANIFEST_HASH,
        "pass": (
            len(records) == 935
            and not unresolved_failures
            and not errors
            and not duplicate_ids
            and not missing_ids
        ),
    }
    return report


def _terminal(attempts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Deterministic terminal attempt: the highest attempt number (ties: last listed)."""
    if not attempts:
        return None
    return sorted(enumerate(attempts), key=lambda pair: (pair[1].get("attempt") or 0, pair[0]))[-1][1]


def _row(route: str, task: dict[str, Any], records: list[dict[str, Any]], files: list[str],
         generation: dict[str, Any]) -> dict[str, Any]:
    attempts = [a for record in records for a in record.get("attempts", [])]
    terminal = _terminal(attempts)
    primary = records[0]
    row = {
        "route": route,
        "judge_task_id": task.get("judge_task_id"),
        "generation_id": task.get("generation_id"),
        "translation_id": primary.get("translation_id", task.get("translation_id")),
        "item_id": task.get("source_item_id"),
        "model": task.get("model"),
        "language": task.get("language"),
        "condition": task.get("condition"),
        "sample_index": task.get("sample_index"),
        "cue_b": task.get("condition") == "cue_b",
        "attempt_files": files,
        "attempt_count": len(attempts),
        "terminal_attempt": None if terminal is None else terminal.get("attempt"),
        "terminal_technical_status": None if terminal is None else terminal.get("technical_status"),
        "terminal_parsed_label": None if terminal is None else terminal.get("parsed_label"),
        "judge_records": records,
        "generation_present": task.get("generation_id") in generation,
    }
    if route == "translated_urdu":
        for field in (
            "translation_identity", "translation_changed", "identity_translation_reason",
            "translation_stage_hash", "effective_translation_config_hash", "translation_record_sha256",
        ):
            row[field] = primary.get(field, (primary.get("translation") or {}).get(field))
    return row


def build_analysis_table(
    *,
    generation_dir: Path,
    direct_judge_dir: Path,
    translated_judge_dir: Path,
    output: Path,
) -> dict[str, Any]:
    """One row per scientific judge task; retry artifacts are provenance, never extra rows.

    Files named ``judge-*.json`` are observations (``*.retry-2.json`` merges into its task);
    other JSON files are listed in ``ignored_files``; unreadable observations are listed in
    ``technical_errors``.  Nothing is dropped silently.
    """
    generation = {}
    for p in generation_dir.glob("generation-*.json"):
        value = json.loads(p.read_text(encoding="utf-8"))
        generation[value["generation_id"]] = value
    rows: list[dict[str, Any]] = []
    technical_errors: list[str] = []
    ignored: list[str] = []
    for route, directory in (("direct", direct_judge_dir), ("translated_urdu", translated_judge_dir)):
        groups: dict[str, dict[str, Any]] = {}
        for path in sorted(directory.glob("*.json")):
            if not path.name.startswith("judge-"):
                ignored.append(f"{route}:{path.name}")
                continue
            is_retry = path.name.endswith(".retry-2.json")
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
                task = value["task"]
                task_id = task["judge_task_id"]
            except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
                technical_errors.append(f"{path.name}:{type(exc).__name__}")
                continue
            if is_retry and path.name != f"{task_id}.retry-2.json":
                technical_errors.append(f"{path.name}:retry_task_mismatch")
                continue
            if not is_retry and path.name != f"{task_id}.json":
                technical_errors.append(f"{path.name}:task_id_mismatch")
                continue
            slot = groups.setdefault(task_id, {"task": task, "primary": None, "retry": None})
            if slot["task"] != task:
                technical_errors.append(f"{path.name}:task_lineage_mismatch")
                continue
            key = "retry" if is_retry else "primary"
            if slot[key] is not None:
                technical_errors.append(f"{path.name}:duplicate_{key}")
                continue
            slot[key] = (path.name, value)
        for task_id in sorted(groups):
            slot = groups[task_id]
            if slot["primary"] is None:
                technical_errors.append(f"{task_id}:orphan_retry")
                continue
            parts = [slot["primary"]] + ([slot["retry"]] if slot["retry"] else [])
            rows.append(_row(route, slot["task"], [v for _, v in parts], [n for n, _ in parts], generation))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    summary = {
        "schema_version": "workshop-v1-analysis-table/2",
        "rows": len(rows),
        "technical_errors": sorted(technical_errors),
        "ignored_files": sorted(ignored),
        "scientific_analysis_performed": False,
        "cue_a_b_separate": True,
        "one_row_per_judge_task": True,
        "analysis_input_layer_sha256": analysis_input_layer_sha256(),
        "output": str(output),
    }
    output.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--translation-qc", action="store_true")
    parser.add_argument("--translation-output", type=Path, default=TRANSLATION_OUTPUT)
    args = parser.parse_args()
    if args.translation_qc:
        report = translation_qc(args.translation_output)
        print(json.dumps(report, indent=2, sort_keys=True))
        if report["pass"] is not True:
            raise SystemExit(1)
    else:
        parser.error("select --translation-qc (sealing: translator_launcher --seal)")


if __name__ == "__main__":
    main()

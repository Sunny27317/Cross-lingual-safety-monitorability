"""C6: non-model validation of the amended (D-TR-1..6) translation_units/reassemble path.

Loads only the pinned IndicTrans2 *tokenizer* (never the model) and performs:

1. synthetic round-trip checks of ``translation_units`` and ``reassemble`` with a stub
   translator (D-TR-1 structural whitespace, D-TR-2 non-Urdu bypass, D-TR-3 exact
   reassembly, 200-token bound, fail-closed count mismatch);
2. a read-only structural replay over every completed success record: units are
   recomputed from the D-TR-4 source span and compared field-by-field with the record's
   ``chunks`` metadata, hashes are recomputed, and the persisted translated trace must be
   exactly the verbatim non-translated units in order with a non-empty translated core
   in each translate slot (no semantic reading of the translation).

The result is written once to a NEW immutable JSON file; the historical
``engineering/indictrans2_segmentation_validation.json`` is never touched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clsm.downstream.contracts import content_hash
from clsm.workshop_v1 import translator_launcher as launcher
from clsm.workshop_v1.translation import (
    MAX_SOURCE_TOKENS,
    TranslationUnit,
    has_urdu_script_letter,
    reassemble,
    translation_units,
)

ROOT = launcher.ROOT
DEFAULT_OUTPUT = ROOT / "engineering/indictrans2_amended_path_validation_2026-10-06.json"
HISTORICAL_ARTIFACT = ROOT / "engineering/indictrans2_segmentation_validation.json"
SCHEMA = "workshop-v1-amended-path-validation/1"
COMMAND = "PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.amended_path_validation"

# Synthetic text only (D-TR edge cases); no study trace appears here.
SYNTHETIC: tuple[tuple[str, str], ...] = (
    ("urdu_two_lines", "یہ ایک مصنوعی جملہ ہے۔\nیہ دوسرا مصنوعی جملہ ہے۔"),  # noqa: RUF001
    ("structural_whitespace", "  \n\nیہ جملہ ہے۔  \n\t\n"),  # noqa: RUF001
    ("bypass_latin_digits", "Option B 42\nیہ جملہ ہے۔\n(A) 3.5"),  # noqa: RUF001
    ("urdu_punctuation_only", "۔ ، ؟\nیہ جملہ ہے"),  # noqa: RUF001
    ("zero_urdu_identity", "B\n\n42 (B)"),
    ("long_resplit", " ".join(["یہ ایک بہت لمبا مصنوعی جملہ ہے"] * 60)),
)


def _stub(units: tuple[TranslationUnit, ...]) -> list[str]:
    return [f"<T{u.index}>" for u in units if u.kind == "translate"]


def synthetic_checks(token_count: Callable[[str], int]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for name, text in SYNTHETIC:
        failures: list[str] = []
        units = translation_units(text, token_count=token_count, max_source_tokens=MAX_SOURCE_TOKENS)
        if "".join(u.text for u in units) != text:
            failures.append("units do not concatenate to source")
        for u in units:
            if u.kind == "translate":
                if "\n" in u.core or u.core != u.core.strip() or u.lead + u.core + u.trail != u.text:
                    failures.append(f"unit {u.index}: translate core not exact")
                if not has_urdu_script_letter(u.core) or u.source_token_count > MAX_SOURCE_TOKENS:
                    failures.append(f"unit {u.index}: translate unit invalid")
            elif u.kind == "structural" and u.text.strip():
                failures.append(f"unit {u.index}: structural unit has content")
            elif u.kind == "bypass" and has_urdu_script_letter(u.text):
                failures.append(f"unit {u.index}: bypass unit has Urdu letters")
        stub = _stub(units)
        joined = reassemble(units, stub)
        if _pattern(units).fullmatch(joined) is None:
            failures.append("reassembly does not preserve non-translated units")
        if not stub and joined != text:
            failures.append("zero-Urdu text is not an identity")
        try:
            reassemble(units, [*stub, "extra"])
            failures.append("count mismatch did not fail closed")
        except ValueError:
            pass
        checks.append({
            "check": f"synthetic:{name}",
            "units": len(units),
            "translate_units": len(stub),
            "status": "FAIL" if failures else "PASS",
            "failures": failures,
        })
    return checks


def _pattern(units: tuple[TranslationUnit, ...]) -> re.Pattern[str]:
    parts = [
        re.escape(u.lead) + r"(.+?)" + re.escape(u.trail) if u.kind == "translate" else re.escape(u.text)
        for u in units
    ]
    return re.compile("".join(parts), re.DOTALL)


def _metadata(units: tuple[TranslationUnit, ...]) -> list[dict[str, Any]]:
    return [
        {
            "index": u.index,
            "kind": u.kind,
            "source_token_count": u.source_token_count,
            "boundary_level": u.boundary_level,
            "text_hash": content_hash(u.text),
        }
        for u in units
    ]


def replay_record(record: dict[str, Any], span: str, token_count: Callable[[str], int]) -> list[str]:
    """Structural replay of one success record; returns failure codes (empty = PASS)."""
    failures: list[str] = []
    units = translation_units(span, token_count=token_count, max_source_tokens=MAX_SOURCE_TOKENS)
    if record.get("source_span_hash") != content_hash(span):
        failures.append("source_span_hash")
    if record.get("chunks") != _metadata(units):
        failures.append("chunk_metadata")
    if record.get("source_chunk_count") != len(units):
        failures.append("source_chunk_count")
    counts = record.get("technical_counts") or {}
    translate = sum(u.kind == "translate" for u in units)
    if counts.get("unit_count") != len(units) or counts.get("translate_units") != translate:
        failures.append("technical_counts")
    translated = record.get("translated_text")
    if not isinstance(translated, str) or content_hash(translated) != record.get("translated_trace_hash"):
        failures.append("translated_trace_hash")
        return failures
    match = _pattern(units).fullmatch(translated)
    if match is None:
        failures.append("reassembly_structure")
    elif any(not group.strip() for group in match.groups()):
        failures.append("empty_translated_core")
    identity = translate == 0
    if identity != (translated == span):
        failures.append("identity_rule")
    if record.get("translation_identity") is not None and record.get("translation_identity") is not identity:
        failures.append("identity_flag")
    return failures


def replay_population(
    output: Path, generation_dir: Path, token_count: Callable[[str], int]
) -> dict[str, Any]:
    failures: dict[str, list[str]] = {}
    records = 0
    identity = 0
    units_total = {"translate": 0, "structural": 0, "bypass": 0}
    for path in sorted(output.glob("translation-*.json")):
        if path.name.startswith("translation-failure-"):
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        records += 1
        source = json.loads(
            (generation_dir / f"{record['generation_record_id']}.json").read_text(encoding="utf-8")
        )
        span = source["parsed"]["reasoning_span"]
        found = replay_record(record, span, token_count)
        if found:
            failures[path.name] = found
        for chunk in record.get("chunks") or []:
            units_total[chunk.get("kind")] = units_total.get(chunk.get("kind"), 0) + 1
        identity += record.get("translation_identity") is True
    return {
        "check": "replay:completed_success_records",
        "records": records,
        "identity_records": identity,
        "unit_kinds": units_total,
        "failing_records": len(failures),
        "failures": failures,
        "status": "PASS" if records == 935 and not failures else "FAIL",
    }


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bindings() -> dict[str, Any]:
    _, manifest = launcher._load()  # type: ignore[no-untyped-call]
    return {
        "translation_population_hash": launcher.translation_population_hash(),  # type: ignore[no-untyped-call]
        "translation_population_hash_recipe": launcher.POPULATION_HASH_RECIPE,
        "task_manifest_hash": launcher._manifest_hash(manifest),  # type: ignore[no-untyped-call]
        "artifact_manifest_hash": launcher.EXPECTED_ARTIFACTS,
        "translation_config_hash": launcher.EXPECTED_CONFIG,
        "translation_amendment_hash": launcher.EXPECTED_AMENDMENT,
        "effective_translation_config_hash": launcher.EXPECTED_EFFECTIVE,
        "executed_launcher_sha256": launcher.EXECUTED_LAUNCHER_SHA256,
        "current_launcher_sha256": _sha(Path(launcher.__file__)),
        "translation_py_sha256": _sha(launcher.TRANSLATION_IMPL),
        "validator_sha256": _sha(Path(__file__)),
        "generation_stage_hash": launcher.EXPECTED_GENERATION,
        "tokenizer_files_sha256": {
            name: _sha(launcher.ARTIFACT_DIR / name)
            for name in (
                "dict.SRC.json", "model.SRC", "tokenization_indictrans.py",
                "tokenizer_config.json", "special_tokens_map.json",
            )
            if (launcher.ARTIFACT_DIR / name).is_file()
        },
    }


def write_once(path: Path, value: dict[str, Any]) -> str:
    if path.resolve() == HISTORICAL_ARTIFACT.resolve():
        raise SystemExit("FAIL_CLOSED: the historical segmentation artifact is never overwritten")
    if path.exists():
        raise SystemExit(f"FAIL_CLOSED: validation artifact already exists and is immutable: {path}")
    payload = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink()
    return hashlib.sha256(payload).hexdigest()


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    from transformers import AutoTokenizer  # type: ignore[attr-defined]

    from clsm.workshop_v1.translation import indictrans_source_token_count

    if output.exists():
        raise SystemExit(f"FAIL_CLOSED: validation artifact already exists and is immutable: {output}")
    tokenizer = AutoTokenizer.from_pretrained(
        launcher.ARTIFACT_DIR, trust_remote_code=True, local_files_only=True
    )

    def token_count(text: str) -> int:
        return indictrans_source_token_count(tokenizer, text)

    checks = synthetic_checks(token_count)
    checks.append(replay_population(launcher.OUTPUT, launcher.SOURCE_DIR, token_count))
    value = {
        "schema_version": SCHEMA,
        "immutable": True,
        "created_utc": datetime.now(UTC).isoformat(),
        "command": COMMAND,
        "model_loaded": False,
        "tokenizer_loaded": True,
        "scientific_outcomes_inspected": False,
        "translation_outputs_modified": False,
        "supersedes_for_manuscript": {
            "path": str(HISTORICAL_ARTIFACT.relative_to(ROOT)),
            "sha256": _sha(HISTORICAL_ARTIFACT) if HISTORICAL_ARTIFACT.is_file() else None,
            "note": "historical artifact (not valid JSON; validated the pre-amendment "
                    "segment_source_chunks path) is retained unchanged",
        },
        "bindings": bindings(),
        "checks": checks,
        "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
    }
    value["artifact_sha256"] = write_once(output, value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    value = run(args.output)
    print(json.dumps({k: value[k] for k in ("status", "artifact_sha256")}, indent=2))
    if value["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

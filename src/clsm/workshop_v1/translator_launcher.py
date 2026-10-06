"""Fail-closed Workshop-v1 IndicTrans2 executor."""
# mypy: ignore-errors

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.metadata
import json
import os
import platform
import tempfile
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "engineering/indictrans2_final_contract.json"
MANIFEST = ROOT / "engineering/workshop_v1_translation_task_manifest.json"
OUTPUT = ROOT / "experiments/_runs/workshop-v1-translation"
LOCK_PATH = OUTPUT / ".translation_stage.lock"
SOURCE_DIR = ROOT / "experiments/_runs/workshop-v1-main-attempt-2"
ARTIFACT_DIR = ROOT / "experiments/_artifacts/indictrans2/ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a"
EXPECTED_CONFIG = "74b81473f4c714e8146c352c6c351772ea995b3dff6f37c8a4af06ca311f99bc"
EXPECTED_ARTIFACTS = "84cad691de2a13f19b4609f924e24aa5aceb582be7278d406359bdd861f7a2bd"
EXPECTED_GENERATION = "7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec"
EXPECTED_MANIFEST = "635d5f8b58b972dcaa40bc4c2933b0529fb2a5b35fc3b76f1dd2f8b1e1f7fb8d"
EXPECTED_MODEL = "ai4bharat/indictrans2-indic-en-1B"
EXPECTED_REVISION = "ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a"
AMENDMENT = ROOT / "engineering/indictrans2_contract_amendment_DTR_2026-10-05.json"
EXPECTED_AMENDMENT = "3a054e8bac831a1cbbfd25b545c15562bbc76b82824266ba707798e104720dc5"
EXPECTED_EFFECTIVE = "106f366c7a0010dab11849150e48b2fb88cb3a4d23260a9abdd750760e6b4171"
TRANSLATION_IMPL = ROOT / "src/clsm/workshop_v1/translation.py"
OPERATIVE_AUTHORIZATION = ROOT / "engineering/INVESTIGATOR_TRANSLATION_AUTHORIZATION_AMENDED_2026-10-05.json"
HISTORICAL_AUTHORIZATION = ROOT / "engineering/INVESTIGATOR_TRANSLATION_AUTHORIZATION.json"
SEAL_NAME = "translation_stage_seal.json"
SEAL_SCHEMA = "workshop-v1-translation-seal/2"
# The 935 translations were produced by the process started 2026-10-05T14:30:46Z, which
# loaded this launcher file as verified at 2026-10-05T14:29Z (sha256 below).  The file was
# edited on disk later (2026-10-06); that later code did not produce any translation.
EXECUTED_LAUNCHER_SHA256 = "8f7c241ad048a5982bbf7656ab4627d4588cfb6f5636caee06d0118b5488f9a6"
EXECUTED_LAUNCHER_EVIDENCE = (
    "launcher sha256 verified 2026-10-05T14:29Z after the seal-authorization fix; resume process "
    "pid 95917 started 2026-10-05T14:30:46Z (stage lock) and ran until the last record "
    "2026-10-06T12:01Z; on-disk edits at 2026-10-06T10:43Z were not loaded by that process"
)
POPULATION_HASH_RECIPE = (
    "sha256 over UTF-8 concatenation of '<filename>\\t<sha256(file bytes)>\\n' for every "
    "translation-*.json success record (excluding translation-failure-*), sorted by filename"
)


def _load():
    return json.loads(CONTRACT.read_text()), json.loads(MANIFEST.read_text())


def _manifest_hash(m):
    recorded = m.get("manifest_hash")
    computed = hashlib.sha256(
        json.dumps(m["tasks"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    if recorded != computed:
        raise ValueError("translation task manifest hash mismatch")
    return computed


def _amendment_blockers():
    """D-TR-1..6 amendment must be intact and bind the current segmentation code."""
    try:
        value = json.loads(AMENDMENT.read_text())
    except (OSError, json.JSONDecodeError):
        return ["translation contract amendment is missing"]
    derived = ("amendment_hash", "effective_translation_config_hash")
    body = {k: v for k, v in value.items() if k not in derived}
    b = []
    computed = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if computed != value.get("amendment_hash") or computed != EXPECTED_AMENDMENT:
        b.append("translation contract amendment hash mismatch")
    effective = hashlib.sha256(
        json.dumps(
            {"amendment_hash": EXPECTED_AMENDMENT, "base_translation_config_hash": EXPECTED_CONFIG},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    if effective != value.get("effective_translation_config_hash") or effective != EXPECTED_EFFECTIVE:
        b.append("effective translation config hash mismatch")
    impl = hashlib.sha256(TRANSLATION_IMPL.read_bytes()).hexdigest()
    if impl != value.get("implementation", {}).get("translation_py_sha256"):
        b.append("segmentation implementation differs from amendment")
    return b


def preflight(*, allow_resume=False):
    c, m = _load()
    b = _amendment_blockers()
    v = dict(c)
    rec = v.pop("translation_config_hash", None)
    comp = hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if rec != comp or rec != EXPECTED_CONFIG:
        b.append("translator config hash mismatch")
    if c.get("status") != "FROZEN":
        b.append("translator contract is not frozen")
    try:
        inv = json.loads((ROOT / c["artifact_inventory"]).read_text())
        if inv.get("inventory_sha256") != EXPECTED_ARTIFACTS:
            b.append("translator artifact inventory hash mismatch")
    except (OSError, KeyError, json.JSONDecodeError):
        b.append("translator artifact inventory is missing")
    try:
        runtime = json.loads((ROOT / "engineering/indictrans2_runtime_inventory.json").read_text())
        expected = {
            "transformers": "4.51.3",
            "torch": "2.6.0",
            "tokenizers": "0.21.1",
            "sentencepiece": "0.2.2",
            "sacremoses": "0.2.0",
            "huggingface-hub": "0.36.2",
            "IndicTransToolkit": "1.1.1",
        }
        for n, x in expected.items():
            if runtime.get("packages", {}).get(n) != x:
                b.append(f"translator runtime mismatch: {n}")
        if runtime.get("torch_runtime", {}).get("selected_device") != "cpu":
            b.append("translator selected device is not frozen CPU")
        package_names = {
            "transformers": "transformers",
            "torch": "torch",
            "tokenizers": "tokenizers",
            "sentencepiece": "sentencepiece",
            "sacremoses": "sacremoses",
            "huggingface-hub": "huggingface-hub",
            "IndicTransToolkit": "indictranstoolkit",
        }
        for recorded_name, package_name in package_names.items():
            try:
                installed = importlib.metadata.version(package_name)
            except importlib.metadata.PackageNotFoundError:
                installed = None
            if installed != expected[recorded_name]:
                b.append(f"installed translator runtime mismatch: {recorded_name}")
    except (OSError, json.JSONDecodeError):
        b.append("translator runtime inventory is missing")
    try:
        if _manifest_hash(m) != EXPECTED_MANIFEST:
            b.append("translation task manifest hash mismatch")
    except ValueError as e:
        b.append(str(e))
    if m.get("expected_tasks") != 935 or m.get("eligible_tasks") != 935:
        b.append("translation manifest must contain exactly 935 eligible tasks")
    if OUTPUT.exists() and any(OUTPUT.iterdir()) and not allow_resume:
        b.append("translation output directory is not empty")
    return {"ready": not b, "blockers": b, "tasks": m.get("eligible_tasks", 0), "scientific_execution": False}


def validate_authorization(path):
    value = json.loads(path.read_text())
    c, m = _load()
    b = []
    if value.get("authorized") is not True or value.get("status") != "APPROVED":
        b.append("translation authorization is not approved")
    checks = {
        "task_count": 935,
        "translation_config_hash": EXPECTED_CONFIG,
        "generation_stage_hash": EXPECTED_GENERATION,
        "translation_manifest_sha256": EXPECTED_MANIFEST,
        "artifact_inventory_sha256": EXPECTED_ARTIFACTS,
        "primary_model": EXPECTED_MODEL,
        "primary_revision": EXPECTED_REVISION,
        "output_directory": "experiments/_runs/workshop-v1-translation",
        "translation_amendment_hash": EXPECTED_AMENDMENT,
        "effective_translation_config_hash": EXPECTED_EFFECTIVE,
    }
    for k, x in checks.items():
        if value.get(k) != x:
            b.append(f"authorization {k} mismatch")
    if m.get("eligible_tasks") != 935 or c.get("translation_config_hash") != EXPECTED_CONFIG:
        b.append("frozen population or contract mismatch")
    return {"valid": not b, "blockers": b, "scientific_execution": False}


def resume_preflight(authorization):
    """Validate a non-empty directory as a same-stage governed resume."""
    auth = validate_authorization(authorization)
    plan = preflight(allow_resume=True)
    blockers = list(auth["blockers"]) + list(plan["blockers"])
    _, manifest = _load()
    expected = {task["translation_id"] for task in manifest["tasks"]}
    if not OUTPUT.exists():
        blockers.append("resume output directory is missing")
        return {"ready": False, "blockers": blockers, "scientific_execution": False}
    success_paths = _success_paths()
    failure_paths = sorted(OUTPUT.glob("translation-failure-*.json"))
    allowed = set(success_paths) | set(failure_paths) | {OUTPUT / ".translation_stage.lock"}
    for path in OUTPUT.iterdir():
        if path not in allowed:
            blockers.append(f"foreign or partial output: {path.name}")
    by_task: dict[str, dict[str, object]] = {}
    for path in allowed:
        if path.name == ".translation_stage.lock":
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            blockers.append(f"corrupt output: {path.name}")
            continue
        task_id = value.get("translation_id")
        if task_id not in expected:
            blockers.append(f"unexpected task ID: {task_id}")
            continue
        if value.get("immutable") is not True:
            blockers.append(f"mutable output: {path.name}")
        if value.get("translation_config_hash") != EXPECTED_CONFIG:
            blockers.append(f"contract mismatch: {path.name}")
        if value.get("artifact_manifest_hash") != EXPECTED_ARTIFACTS:
            blockers.append(f"artifact mismatch: {path.name}")
        amended = value.get("translation_amendment_hash")
        effective = value.get("effective_translation_config_hash")
        if amended is not None and (amended != EXPECTED_AMENDMENT or effective != EXPECTED_EFFECTIVE):
            blockers.append(f"amendment mismatch: {path.name}")
        entry = by_task.setdefault(task_id, {"failures": {}, "success": None})
        if path in success_paths:
            if value.get("technical_status") != "SUCCESS":
                blockers.append(f"non-success canonical output: {path.name}")
            if amended is None:
                blockers.append(f"success record without amendment binding: {path.name}")
            entry["success"] = value.get("attempt")
        else:
            if value.get("technical_status") != "FAILED":
                blockers.append(f"invalid failure record: {path.name}")
            suffix = path.name.rsplit("-attempt-", 1)[-1].removesuffix(".json")
            if not suffix.isdigit() or value.get("attempt") != int(suffix):
                blockers.append(f"attempt number mismatch: {path.name}")
                continue
            failures = entry["failures"]
            if int(suffix) in failures:
                blockers.append(f"duplicate task attempt: {path.name}")
            failures[int(suffix)] = amended is not None
    for task_id, entry in by_task.items():
        numbers = sorted(entry["failures"])
        if numbers != list(range(1, len(numbers) + 1)):
            blockers.append(f"unexplained attempt numbering: {task_id}")
        flags = [entry["failures"][n] for n in numbers]
        if flags != sorted(flags):
            blockers.append(f"pre-amendment attempt after amended attempt: {task_id}")
        if entry["success"] is not None and entry["success"] != len(numbers) + 1:
            blockers.append(f"conflicting success attempt number: {task_id}")
    unresolved = sum(1 for e in by_task.values() if e["success"] is None)
    return {
        "ready": not blockers,
        "blockers": sorted(set(blockers)),
        "scientific_execution": False,
        "successful_records": len(success_paths),
        "technical_failure_records": len(failure_paths),
        "unattempted": 935 - len(by_task),
        "attempted_unresolved": unresolved,
        "tasks": 935,
    }


def _atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"immutable output differs: {path}")
        return
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as h:
        h.write(payload)
        h.flush()
        os.fsync(h.fileno())
        tmp = Path(h.name)
    os.replace(tmp, path)


class StageLock:
    """Exclusive Unix stage lock shared by execute and resume."""

    def __init__(self, mode):
        self.mode = mode
        self.handle = None
        self.previous = {}

    def __enter__(self):
        OUTPUT.mkdir(parents=True, exist_ok=True)
        self.handle = LOCK_PATH.open("a+")
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self.handle.close()
            raise RuntimeError("translation stage is already locked by another process") from exc
        metadata = {
            "pid": os.getpid(),
            "started_utc": datetime.now(UTC).isoformat(),
            "mode": self.mode,
        }
        self.handle.seek(0)
        self.handle.truncate()
        self.handle.write(json.dumps(metadata, sort_keys=True) + "\n")
        self.handle.flush()
        os.fsync(self.handle.fileno())
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.handle is not None:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close()
        return False


def _source_index():
    out = {}
    for p in SOURCE_DIR.glob("generation-*.json"):
        v = json.loads(p.read_text())
        out[v["generation_id"]] = v
    return out


def _runtime_versions():
    return {"python": platform.python_version(), "platform": platform.platform()}


class TranslationStageError(ValueError):
    """Technical failure carrying text-free counts for the immutable failure record."""

    def __init__(self, message, stage, counts):
        super().__init__(message)
        self.technical = {"stage": stage, **counts}


def _translate_task(task, source, tokenizer, processor, model):
    import torch

    from clsm.downstream.contracts import content_hash
    from clsm.workshop_v1.translation import (
        indictrans_source_token_count,
        reassemble,
        translation_units,
    )

    if source.get("raw_output_hash") != task["source_trace_hash"]:
        raise ValueError("source runtime output hash mismatch")
    if source.get("qc", {}).get("runtime_success") is not True:
        raise ValueError("source generation is not a runtime success")
    # D-TR-4: the exact reasoning span scored by the direct judge.
    text = (source.get("parsed") or {}).get("reasoning_span")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("source reasoning span is missing")
    counts = {"unit_count": None, "translate_units": None}
    try:
        units = translation_units(
            text, token_count=lambda s: indictrans_source_token_count(tokenizer, s), max_source_tokens=200
        )
    except ValueError as exc:
        raise TranslationStageError(str(exc), "segmentation", counts) from exc
    eligible = [u for u in units if u.kind == "translate"]
    counts = {
        "unit_count": len(units),
        "translate_units": len(eligible),
        "structural_units": sum(u.kind == "structural" for u in units),
        "bypass_units": sum(u.kind == "bypass" for u in units),
        "max_source_tokens": max((u.source_token_count for u in units), default=0),
    }
    translated = []
    if eligible:
        prepared = processor.preprocess_batch(
            [u.core for u in eligible], src_lang="urd_Arab", tgt_lang="eng_Latn", visualize=False
        )
        if len(prepared) != len(eligible):
            raise TranslationStageError("preprocessed chunk count mismatch", "preprocess", counts)
        # Frozen contract: batch_size=1.  Padded multi-chunk batches let short rows run
        # to max_length and decode empty, so each unit is generated on its own.
        eos = getattr(getattr(model, "generation_config", None), "eos_token_id", None)
        decoded = []
        longest = 0
        for item in prepared:
            batch = tokenizer([item], padding="longest", truncation=False, return_tensors="pt").to("cpu")
            with torch.inference_mode():
                generated = model.generate(
                    **batch, num_beams=5, max_length=256, num_return_sequences=1, use_cache=True
                )
            longest = max(longest, int(generated.shape[1]))
            if generated.shape[0] != 1:
                raise TranslationStageError("generated sequence count mismatch", "generate", counts)
            if generated.shape[1] >= 256 and (eos is None or not bool((generated[0] == eos).any())):
                raise TranslationStageError(
                    "translation reached max_length without EOS; no silent truncation",
                    "generate",
                    {**counts, "max_generated_length": longest},
                )
            decoded.extend(
                tokenizer.batch_decode(generated, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            )
        translated = processor.postprocess_batch(decoded, lang="eng_Latn")
        counts["max_generated_length"] = longest
        empty = sum(not isinstance(x, str) or not x.strip() for x in translated)
        if len(translated) != len(eligible) or empty:
            raise TranslationStageError(
                "incomplete translated chunks",
                "postprocess",
                {**counts, "postprocessed": len(translated), "empty_outputs": empty},
            )
    joined = reassemble(units, translated)
    identity = joined == text
    if identity and any(u.kind == "translate" for u in units):
        raise TranslationStageError(
            "identity output despite translatable source units", "reassembly", counts
        )
    return {
        "source_span": "parsed.reasoning_span",
        "source_span_hash": content_hash(text),
        "source_chunk_count": len(units),
        "technical_counts": counts,
        "chunks": [
            {
                "index": u.index,
                "kind": u.kind,
                "source_token_count": u.source_token_count,
                "boundary_level": u.boundary_level,
                "text_hash": content_hash(u.text),
            }
            for u in units
        ],
        "translated_text": joined,
        "translated_trace_hash": content_hash(joined),
        "translation_identity": identity,
        "translation_changed": not identity,
        "identity_translation_reason": "zero_urdu_script_letters" if identity else None,
    }


def _execute_unlocked(authorization, resume=False):
    validation = validate_authorization(authorization)
    if not validation["valid"]:
        raise SystemExit(f"FAIL_CLOSED: {validation['blockers']}")
    if resume:
        resumed = resume_preflight(authorization)
        if not resumed["ready"]:
            raise SystemExit(f"FAIL_CLOSED: {resumed['blockers']}")
    plan = preflight(allow_resume=resume)
    if not plan["ready"]:
        raise SystemExit(f"FAIL_CLOSED: {plan['blockers']}")
    _, manifest = _load()
    import torch
    from IndicTransToolkit import IndicProcessor
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(ARTIFACT_DIR, trust_remote_code=True, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        ARTIFACT_DIR, trust_remote_code=True, local_files_only=True, torch_dtype=torch.float32
    ).to("cpu")
    processor = IndicProcessor(inference=True)
    sources = _source_index()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for task in manifest["tasks"]:
        path = OUTPUT / f"{task['translation_id']}.json"
        failure_paths = sorted(OUTPUT.glob(f"translation-failure-{task['translation_id']}-attempt-*.json"))
        if path.exists():
            existing = json.loads(path.read_text())
            if existing.get("immutable") is not True:
                raise SystemExit(f"FAIL_CLOSED: mutable output {path.name}")
            if existing.get("technical_status") == "SUCCESS":
                continue
            raise SystemExit(
                f"FAIL_CLOSED: non-success canonical record requires governed retry: {path.name}"
            )
        attempt = len(failure_paths) + 1
        base = {
            "schema_version": "workshop-v1-translation-record/1",
            "immutable": True,
            "translation_id": task["translation_id"],
            "task_id": task["translation_id"],
            "generation_record_id": task["source_trace_id"],
            "item_id": task["source_item_id"],
            "model": task["model"],
            "language": task["source_language"],
            "condition": task["condition"],
            "sample_index": task["sample_index"],
            "source_trace_hash": task["source_trace_hash"],
            "translator_model": EXPECTED_MODEL,
            "translator_revision": EXPECTED_REVISION,
            "artifact_manifest_hash": EXPECTED_ARTIFACTS,
            "translation_config_hash": EXPECTED_CONFIG,
            "translation_amendment_hash": EXPECTED_AMENDMENT,
            "effective_translation_config_hash": EXPECTED_EFFECTIVE,
            "device": "cpu",
            "dtype": "torch.float32",
            "runtime": _runtime_versions(),
            "attempt": attempt,
            "created_utc": datetime.now(UTC).isoformat(),
        }
        try:
            base.update(
                _translate_task(task, sources[task["source_trace_id"]], tokenizer, processor, model),
                technical_status="SUCCESS",
                error=None,
            )
        except Exception as exc:
            base.update(technical_status="FAILED", error=f"{type(exc).__name__}: {exc}")
            if isinstance(exc, TranslationStageError):
                base["technical_counts"] = exc.technical
        target = (
            path
            if base.get("technical_status") == "SUCCESS"
            else OUTPUT / f"translation-failure-{task['translation_id']}-attempt-{attempt}.json"
        )
        _atomic(target, base)


def execute(authorization, resume=False):
    """Run one governed stage under the exclusive process lock."""
    with StageLock("resume" if resume else "execute"):
        return _execute_unlocked(authorization, resume=resume)


def _success_paths():
    return (
        sorted(p for p in OUTPUT.glob("translation-*.json") if not p.name.startswith("translation-failure-"))
        if OUTPUT.exists()
        else []
    )


def post_qc():
    _, manifest = _load()
    expected = {t["translation_id"] for t in manifest["tasks"]}
    paths = _success_paths()
    failure_paths = sorted(OUTPUT.glob("translation-failure-*.json")) if OUTPUT.exists() else []
    records = []
    failures = []
    for p in paths:
        try:
            records.append(json.loads(p.read_text()))
        except (OSError, json.JSONDecodeError):
            failures.append(p.name)
    ids = [v.get("translation_id") for v in records]
    by_id = {t["translation_id"]: t for t in manifest["tasks"]}
    source_records = _source_index()
    for v in records:
        task = by_id.get(v.get("translation_id"))
        source = source_records.get(v.get("generation_record_id")) if task else None
        if (
            task is None
            or source is None
            or v.get("generation_record_id") != task["source_trace_id"]
            or (
                source.get("raw_output_hash") != v.get("source_trace_hash")
                or v.get("source_trace_hash") != task["source_trace_hash"]
            )
        ):
            failures.append(str(v.get("translation_id", "invalid")))
        chunks = v.get("chunks", [])
        if v.get("technical_status") == "SUCCESS" and (
            len(chunks) != v.get("source_chunk_count")
            or [c.get("index") for c in chunks] != list(range(len(chunks)))
            or any(c.get("source_token_count", 201) > 200 for c in chunks)
        ):
            failures.append(str(v.get("translation_id", "invalid")))
    for v in records:
        if (
            v.get("immutable") is not True
            or v.get("translation_config_hash") != EXPECTED_CONFIG
            or v.get("artifact_manifest_hash") != EXPECTED_ARTIFACTS
        ):
            failures.append(str(v.get("translation_id", "invalid")))
        if v.get("technical_status") == "SUCCESS" and (
            not v.get("translated_text") or v.get("source_chunk_count", 0) < 1
        ):
            failures.append(str(v.get("translation_id", "invalid")))
    success = sum(v.get("technical_status") == "SUCCESS" for v in records)
    technical = len(failure_paths) + sum(v.get("technical_status") != "SUCCESS" for v in records)
    failure_ids = []
    for path in failure_paths:
        with suppress(OSError, json.JSONDecodeError):
            failure_ids.append(json.loads(path.read_text()).get("translation_id"))
    success_ids = {v.get("translation_id") for v in records if v.get("technical_status") == "SUCCESS"}
    unresolved = len({x for x in failure_ids if x} - success_ids)
    unattempted = max(0, 935 - success - unresolved)
    return {
        "scientific_execution": False,
        "expected_tasks": 935,
        "persisted_records": len(records),
        "successful_records": success,
        "technical_failures": technical,
        "current_technical_failures": technical,
        "retried_success": 0,
        "unresolved_failures": unresolved,
        "unattempted": unattempted,
        "remaining": 935 - success,
        "failure_ids": sorted(x for x in failure_ids if x),
        "unique_ids": len(ids) == len(set(ids)),
        "unexpected_ids": sorted(set(ids) - expected),
        "missing_ids": len(expected - set(ids)),
        "technical_qc_failures": sorted(set(failures)),
        "ready_for_seal": len(records) == 935
        and set(ids) == expected
        and len(ids) == len(set(ids))
        and not failures,
    }


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _canonical_json_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def translation_population_hash(output=None):
    """Canonical artifact-population hash (recipe in POPULATION_HASH_RECIPE)."""
    root = OUTPUT if output is None else output
    lines = "".join(
        f"{p.name}\t{_sha(p)}\n"
        for p in sorted(root.glob("translation-*.json"))
        if not p.name.startswith("translation-failure-")
    )
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def _failure_population(output=None):
    root = OUTPUT if output is None else output
    return [{"name": p.name, "sha256": _sha(p)} for p in sorted(root.glob("translation-failure-*.json"))]


def canonical_qc():
    """Both technical QCs over the current terminal state; seal and gate use exactly this."""
    from clsm.workshop_v1.post_translation_pipeline import translation_qc

    launcher_qc = post_qc()
    stage_qc = translation_qc(OUTPUT)
    ok = (
        launcher_qc["ready_for_seal"] is True
        and stage_qc["pass"] is True
        and launcher_qc["successful_records"] == 935
        and launcher_qc["unresolved_failures"] == 0
        and stage_qc["unresolved_technical_failures"] == 0
    )
    return {"launcher_post_qc": launcher_qc, "translation_qc": stage_qc, "pass": ok}


def _base_config_hash():
    contract, _ = _load()
    body = dict(contract)
    body.pop("translation_config_hash", None)
    return _canonical_json_hash(body)


def _seal_body(qc):
    _, manifest = _load()
    return {
        "schema_version": SEAL_SCHEMA,
        "immutable": True,
        "expected_tasks": 935,
        "successful_records": qc["launcher_post_qc"]["successful_records"],
        "unresolved_failures": qc["launcher_post_qc"]["unresolved_failures"],
        "task_manifest_hash": _manifest_hash(manifest),
        "artifact_manifest_hash": EXPECTED_ARTIFACTS,
        "translation_config_hash": _base_config_hash(),
        "translation_amendment_hash": EXPECTED_AMENDMENT,
        "effective_translation_config_hash": EXPECTED_EFFECTIVE,
        "amendment_record": {"path": str(AMENDMENT.relative_to(ROOT)), "sha256": _sha(AMENDMENT)},
        "translation_population_hash": translation_population_hash(),
        "translation_population_hash_recipe": POPULATION_HASH_RECIPE,
        "historical_failure_records": _failure_population(),
        "identity_translation_count": qc["translation_qc"]["identity_translation_count"],
        "identity_translation_ids": qc["translation_qc"]["identity_translation_ids"],
        "technical_qc": qc,
        "technical_qc_hash": _canonical_json_hash(qc),
        "source_lineage_hash": hashlib.sha256(
            "".join(sorted(t["source_trace_hash"] for t in manifest["tasks"])).encode()
        ).hexdigest(),
        "operative_authorization": {
            "path": str(OPERATIVE_AUTHORIZATION.relative_to(ROOT)),
            "sha256": _sha(OPERATIVE_AUTHORIZATION),
        },
        "historical_authorization": {
            "path": str(HISTORICAL_AUTHORIZATION.relative_to(ROOT)),
            "sha256": _sha(HISTORICAL_AUTHORIZATION),
            "status": "SUPERSEDED_HISTORICAL",
        },
        "translation_py_sha256": _sha(TRANSLATION_IMPL),
        "executed_launcher_sha256": EXECUTED_LAUNCHER_SHA256,
        "executed_launcher_evidence": EXECUTED_LAUNCHER_EVIDENCE,
    }


def seal():
    """The only writer of the canonical translation stage seal (immutable, fail-closed)."""
    path = OUTPUT / SEAL_NAME
    if path.exists():
        raise SystemExit("FAIL_CLOSED: canonical translation seal already exists and is immutable")
    qc = canonical_qc()
    if not qc["pass"]:
        raise SystemExit("FAIL_CLOSED: translation post-QC has not passed")
    blockers = _amendment_blockers()
    if blockers:
        raise SystemExit(f"FAIL_CLOSED: amendment provenance invalid: {blockers}")
    operative = validate_authorization(OPERATIVE_AUTHORIZATION)
    if not operative["valid"]:
        raise SystemExit(f"FAIL_CLOSED: operative authorization invalid: {operative['blockers']}")
    value = _seal_body(qc)
    value.update({
        "authorization_hash": value["operative_authorization"]["sha256"],
        "current_launcher_sha256_at_seal": _sha(Path(__file__)),
        "runtime": _runtime_versions(),
        "created_utc": datetime.now(UTC).isoformat(),
    })
    value["translation_stage_hash"] = _canonical_json_hash(value)
    _atomic(path, value)
    return value


def _seal_failure(reason):
    return {"valid": False, "blockers": [reason], "translation_stage_hash": None}


def verify_translation_seal():
    """Independently recompute everything the seal binds. Never trusts stored values alone."""
    path = OUTPUT / SEAL_NAME
    blockers = []
    if not path.is_file():
        return _seal_failure("canonical translation seal is missing")
    try:
        seal_value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _seal_failure("canonical translation seal is corrupt")
    if not isinstance(seal_value, dict):
        return _seal_failure("canonical translation seal is malformed")
    stored = seal_value.get("translation_stage_hash")
    body = {k: v for k, v in seal_value.items() if k != "translation_stage_hash"}
    if seal_value.get("schema_version") != SEAL_SCHEMA or seal_value.get("immutable") is not True:
        blockers.append("seal schema invalid")
    if not isinstance(stored, str) or _canonical_json_hash(body) != stored:
        blockers.append("seal stage hash does not recompute")
    try:
        qc = canonical_qc()
        expected = _seal_body(qc)
    except (OSError, ValueError, KeyError) as exc:
        return {
            "valid": False,
            "blockers": sorted({*blockers, f"seal inputs cannot be recomputed: {type(exc).__name__}"}),
            "translation_stage_hash": stored,
        }
    if not qc["pass"]:
        blockers.append("translation QC does not pass on current state")
    for key, wanted in expected.items():
        if seal_value.get(key) != wanted:
            blockers.append(f"seal field mismatch: {key}")
    if seal_value.get("authorization_hash") != expected["operative_authorization"]["sha256"]:
        blockers.append("seal field mismatch: authorization_hash")
    for check, ok in (
        ("base translation config", expected["translation_config_hash"] == EXPECTED_CONFIG),
        ("task manifest", expected["task_manifest_hash"] == EXPECTED_MANIFEST),
        ("successful population", expected["successful_records"] == 935),
        ("unresolved failures", expected["unresolved_failures"] == 0),
        ("executed launcher hash", seal_value.get("executed_launcher_sha256") == EXECUTED_LAUNCHER_SHA256),
    ):
        if not ok:
            blockers.append(f"{check} invalid")
    blockers.extend(_amendment_blockers())
    try:
        if not validate_authorization(OPERATIVE_AUTHORIZATION)["valid"]:
            blockers.append("operative translation authorization invalid")
    except (OSError, json.JSONDecodeError):
        blockers.append("operative translation authorization missing")
    return {"valid": not blockers, "blockers": sorted(set(blockers)), "translation_stage_hash": stored}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--preflight", action="store_true")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--progress", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--post-qc", action="store_true")
    p.add_argument("--seal", action="store_true")
    p.add_argument("--verify-seal", action="store_true")
    p.add_argument("--authorization", type=Path)
    a = p.parse_args()
    if a.preflight:
        if a.resume:
            if a.authorization is None or not a.authorization.exists():
                raise SystemExit("FAIL_CLOSED: resume preflight requires authorization")
            print(json.dumps(resume_preflight(a.authorization), indent=2, sort_keys=True))
        else:
            print(json.dumps(preflight(), indent=2, sort_keys=True))
        return
    if a.execute or a.resume:
        if a.authorization is None or not a.authorization.exists():
            raise SystemExit("FAIL_CLOSED: explicit translation authorization file is required")
        execute(a.authorization, resume=a.resume)
        return
    if a.post_qc:
        print(json.dumps(post_qc(), indent=2, sort_keys=True))
        return
    if a.seal:
        print(json.dumps(seal(), indent=2, sort_keys=True))
        return
    if a.verify_seal:
        verdict = verify_translation_seal()
        print(json.dumps(verdict, indent=2, sort_keys=True))
        if not verdict["valid"]:
            raise SystemExit(1)
        return
    if a.progress:
        q = post_qc()
        print(
            json.dumps(
                {
                    k: q[k]
                    for k in (
                        "expected_tasks",
                        "successful_records",
                        "current_technical_failures",
                        "retried_success",
                        "unresolved_failures",
                        "unattempted",
                        "remaining",
                    )
                },
                indent=2,
            )
        )
        return
    p.error("select --preflight, --execute, --resume, --progress, --post-qc, --seal, or --verify-seal")


if __name__ == "__main__":
    main()

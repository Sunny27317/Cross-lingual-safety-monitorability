"""Fail-closed planner for translated-Urdu Judge V2 evaluation.

This module performs only static preflight/progress checks unless a future,
separately reviewed executor is supplied. It cannot silently run translated
judging while translation or authorization is incomplete.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, cast

import yaml

from clsm.workshop_v1.config import ModelSpec
from clsm.workshop_v1.direct_judge_launcher import _generation_record, _judge_inputs
from clsm.workshop_v1.judge import render_judge_prompt, run_judge
from clsm.workshop_v1.local_runtime import run_local
from clsm.workshop_v1.translated_context import validate_translated_context
from clsm.workshop_v1.translation import has_urdu_script_letter

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "engineering/workshop_v1_translated_urdu_judge_manifest.json"
TRANSLATION_CONTRACT = ROOT / "engineering/indictrans2_final_contract.json"
OUTPUT = ROOT / "experiments/_runs/workshop-v1-translated-urdu-judge"
TRANSLATIONS = ROOT / "experiments/_runs/workshop-v1-translation"
PROMPT_HASH = "050ed49289b435ed84ab565dcca000cafd4554de3c11230edc2fe56d29844984"
EFFECTIVE_TRANSLATION_CONFIG_HASH = "106f366c7a0010dab11849150e48b2fb88cb3a4d23260a9abdd750760e6b4171"
MAX_JUDGE_ATTEMPTS = 2


def retry_decision(attempts: list[dict[str, Any]]) -> str:
    """Return the immutable, two-attempt translated-judge state."""
    if any(a.get("technical_status") != "RUNTIME_ERROR" for a in attempts):
        return "SUCCESS"
    if len(attempts) >= MAX_JUDGE_ATTEMPTS:
        return "RETRY_EXHAUSTED"
    return "RETRY_ONCE"


def validate_task_context(direct_context: dict[str, Any], translated_context: dict[str, Any]) -> None:
    """Enforce D_ur/T parity before any translated judge request is built."""
    validate_translated_context(direct_context, translated_context)


def _seal_verification() -> dict[str, Any]:
    from clsm.workshop_v1 import translator_launcher

    return cast(dict[str, Any], translator_launcher.verify_translation_seal())  # type: ignore[no-untyped-call]


def preflight() -> dict[str, object]:
    """Fail-closed gate: canonical seal independently re-verified from disk."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = json.loads(TRANSLATION_CONTRACT.read_text(encoding="utf-8"))
    blockers: list[str] = []
    if manifest.get("count") != 935 or len(manifest.get("tasks", [])) != 935:
        blockers.append("translated-Urdu judge workload must contain 935 tasks")
    if contract.get("status") != "FROZEN":
        blockers.append("translation contract is not frozen")
    seal = _seal_verification()
    if not seal["valid"]:
        blockers.extend(f"translation seal: {b}" for b in seal["blockers"])
    return {
        "ready": not blockers,
        "blockers": blockers,
        "tasks": manifest.get("count", 0),
        "prompt_hash": PROMPT_HASH,
        "scientific_execution": False,
        "translation_stage_hash": seal.get("translation_stage_hash"),
    }


def _translation(task: dict[str, Any]) -> dict[str, Any]:
    path = TRANSLATIONS / f"{task['translation_id']}.json"
    if not path.is_file():
        raise ValueError(f"missing translation artifact: {task['translation_id']}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("immutable") is not True or value.get("technical_status") != "SUCCESS":
        raise ValueError(f"translation is not an immutable success: {path.name}")
    if value.get("translation_id") != task["translation_id"]:
        raise ValueError("translation ID lineage mismatch")
    if value.get("effective_translation_config_hash") != EFFECTIVE_TRANSLATION_CONFIG_HASH:
        raise ValueError(f"translation record lacks amended config provenance: {path.name}")
    value["_record_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return cast(dict[str, Any], value)


def identity_translation(translation: dict[str, Any], urdu_trace: str) -> bool:
    """C1 / D-TR-2: identity iff the source has zero Urdu-script letters AND the bytes are
    unchanged. Any disagreement with the record's own flags fails closed."""
    unchanged = (
        translation.get("source_span_hash") == translation.get("translated_trace_hash")
        and translation.get("translated_text") == urdu_trace
    )
    zero_urdu = not has_urdu_script_letter(urdu_trace)
    if unchanged and not zero_urdu:
        raise ValueError(f"unexplained identity translation: {translation.get('translation_id')}")
    identity = unchanged and zero_urdu
    flagged = translation.get("translation_identity")
    if flagged is not None and flagged is not identity:
        raise ValueError(f"identity flag disagrees with C1 rules: {translation.get('translation_id')}")
    return identity


def validate_authorization(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    if value.get("authorized") is not True or value.get("status") != "APPROVED":
        blockers.append("translated-judge authorization is not approved")
    if value.get("translated_urdu_tasks") != 935:
        blockers.append("translated-Urdu task count must be 935")
    if value.get("prompt_hash") != PROMPT_HASH:
        blockers.append("Judge V2 prompt hash mismatch")
    if value.get("output_directory") != "experiments/_runs/workshop-v1-translated-urdu-judge":
        blockers.append("output directory mismatch")
    requested_stage_hash = value.get("translation_stage_hash")
    if not isinstance(requested_stage_hash, str):
        blockers.append("authorization must bind the final translation stage hash")
    plan = preflight()
    verified_stage_hash = plan.get("translation_stage_hash")
    if isinstance(requested_stage_hash, str) and requested_stage_hash != verified_stage_hash:
        blockers.append("translation stage hash mismatch")
    blockers.extend(cast(list[str], plan["blockers"]) if not plan["ready"] else [])
    return {"valid": not blockers, "blockers": blockers, "scientific_execution": False}


def _atomic(path: Path, value: dict[str, Any]) -> None:
    payload = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"immutable judge output differs: {path.name}")
        return
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


def post_qc() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = {task["judge_task_id"] for task in manifest["tasks"]}
    files = sorted(OUTPUT.glob("judge-*.json")) if OUTPUT.exists() else []
    by_id: dict[str, list[dict[str, Any]]] = {}
    errors: list[str] = []
    for path in files:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            task_id = value.get("task", {}).get("judge_task_id")
            if value.get("immutable") is not True or not isinstance(value.get("attempts"), list):
                errors.append(path.name)
            else:
                by_id.setdefault(task_id, []).append(value)
        except (OSError, json.JSONDecodeError):
            errors.append(path.name)
    states: dict[str, str] = {}
    for task_id, values in by_id.items():
        attempts: list[dict[str, Any]] = []
        for value in sorted(values, key=lambda item: item.get("retry_of") is not None):
            attempts.extend(value.get("attempts", []))
        states[task_id] = retry_decision(attempts)
    ids = set(by_id)
    return {
        "scientific_execution": False,
        "expected_tasks": 935,
        "persisted_records": len(ids),
        "successful_records": sum(state == "SUCCESS" for state in states.values()),
        "retry_exhausted": sum(state == "RETRY_EXHAUSTED" for state in states.values()),
        "unique_ids": True,
        "missing_ids": len(expected - ids),
        "unexpected_ids": sorted(ids - expected),
        "technical_errors": sorted(set(errors)),
        "ready_for_seal": (
            len(ids) == 935 and ids == expected and not errors
            and all(state == "SUCCESS" for state in states.values())
        ),
    }


def execute(authorization: Path, *, resume: bool = False) -> None:
    validation = validate_authorization(authorization)
    if not validation["valid"]:
        raise SystemExit(f"FAIL_CLOSED: {validation['blockers']}")
    stage_hash = json.loads(authorization.read_text(encoding="utf-8"))["translation_stage_hash"]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    spec_data = yaml.safe_load((ROOT / "configs/workshop_v1/judge_model.yaml").read_text())["spec"]
    spec = ModelSpec.model_validate_json(json.dumps(spec_data))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for task in manifest["tasks"]:
        out = OUTPUT / f"{task['judge_task_id']}.json"
        retry_path = OUTPUT / f"{task['judge_task_id']}.retry-2.json"
        retrying = out.exists()
        if retry_path.exists() and not out.exists():
            raise SystemExit(f"FAIL_CLOSED: orphan retry artifact: {retry_path.name}")
        if out.exists():
            existing = json.loads(out.read_text(encoding="utf-8"))
            if existing.get("immutable") is not True:
                raise SystemExit(f"FAIL_CLOSED: mutable output {out}")
            attempts = existing.get("attempts", [])
            decision = retry_decision(attempts)
            if decision == "SUCCESS":
                continue
            if decision == "RETRY_EXHAUSTED":
                continue
            if not resume:
                raise SystemExit(f"FAIL_CLOSED: existing non-success output requires --resume: {out.name}")
            if retry_path.exists():
                retry_value = json.loads(retry_path.read_text(encoding="utf-8"))
                if retry_value.get("immutable") is not True:
                    raise SystemExit(f"FAIL_CLOSED: mutable retry output {retry_path.name}")
                continue
        translation = _translation(task)
        direct = _generation_record(task["generation_id"])
        question, options, suggestion, urdu_trace = _judge_inputs(direct)
        derived_identity = identity_translation(translation, urdu_trace)
        translated_context = {
            "question": question,
            "options": options,
            "suggestion": suggestion,
            "trace": translation["translated_text"],
            "translation_identity": derived_identity,
            "translation_changed": not derived_identity,
            "identity_translation_reason": (
                "zero_urdu_script_letters"
                if derived_identity
                else translation.get("identity_translation_reason")
            ),
        }
        validate_task_context(
            {"question": question, "options": options, "suggestion": suggestion, "trace": urdu_trace},
            translated_context,
        )
        prompt = render_judge_prompt(
            question=question,
            options=options,
            suggestion_sentence=suggestion,
            trace=translated_context["trace"],
        )
        attempts = run_judge(
            lambda text: run_local(spec, text, seed=0),
            spec=spec,
            prompt=prompt,
            generation_id=task["generation_id"],
            arm="translated",
            trace_language="en",
            attempt_start=2 if retrying else 1,
            max_attempts=2,
        )
        _atomic(
            retry_path if out.exists() else out,
            {
                "immutable": True,
                "task": task,
                "translation_id": task["translation_id"],
                "attempts": attempts,
                "terminal_state": retry_decision(attempts),
                "retry_of": out.name if out.exists() else None,
                "translation_identity": translated_context["translation_identity"],
                "translation_changed": translated_context["translation_changed"],
                "identity_translation_reason": translated_context["identity_translation_reason"],
                "translation_stage_hash": stage_hash,
                "effective_translation_config_hash": translation["effective_translation_config_hash"],
                "translation_record_sha256": translation["_record_sha256"],
                "translated_trace_hash": translation.get("translated_trace_hash"),
                "source_span_hash": translation.get("source_span_hash"),
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--post-qc", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--authorization", type=Path)
    args = parser.parse_args()
    if args.preflight:
        plan = preflight()
        print(json.dumps(plan, indent=2, sort_keys=True))
        if plan["ready"] is not True:
            raise SystemExit(1)
    elif args.execute or args.resume:
        if args.authorization is None or not args.authorization.exists():
            raise SystemExit("FAIL_CLOSED: translated-judge authorization is required")
        execute(args.authorization, resume=args.resume)
    elif args.progress or args.post_qc:
        print(json.dumps(post_qc(), indent=2, sort_keys=True))
    else:
        parser.error("select --preflight, --progress, or --post-qc")


if __name__ == "__main__":
    main()

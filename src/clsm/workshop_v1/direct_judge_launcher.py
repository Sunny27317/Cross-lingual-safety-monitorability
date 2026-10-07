"""Fail-closed direct Judge V2 planner/launcher."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

import yaml

from clsm.workshop_v1.config import ModelSpec
from clsm.workshop_v1.judge import render_judge_prompt, run_judge
from clsm.workshop_v1.local_runtime import run_local
from clsm.workshop_v1.prompt_contract import CUE_TEXT, LANGUAGE_CONTROL_INSTRUCTION

ROOT = Path(__file__).resolve().parents[3]
PROMPT_HASH = "050ed49289b435ed84ab565dcca000cafd4554de3c11230edc2fe56d29844984"
JUDGE_SPEC_HASH = "a8cb84c12821a2352442a25589bf88834b8c87744350ea45c0af0db8f7dfb419"
GENERATION_STAGE_HASH = "7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec"
MANIFESTS = (
    ROOT / "engineering/workshop_v1_english_direct_judge_manifest.json",
    ROOT / "engineering/workshop_v1_urdu_direct_judge_manifest.json",
)
OUTPUT = ROOT / "experiments/_runs/workshop-v1-direct-judge"


def preflight() -> dict[str, object]:
    counts = [json.loads(path.read_text())["count"] for path in MANIFESTS]
    blockers = []
    if counts != [936, 935]:
        blockers.append("direct judge workload must be 936 English + 935 Urdu")
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        blockers.append("direct judge output directory is not empty")
    return {
        "ready": not blockers,
        "blockers": blockers,
        "english_direct": counts[0],
        "urdu_direct": counts[1],
        "total": sum(counts),
        "prompt_hash": PROMPT_HASH,
        "scientific_execution": False,
    }


def validate_authorization(authorization: Path) -> dict[str, object]:
    """Validate approval metadata without executing any judge call."""
    try:
        auth = cast(dict[str, Any], json.loads(authorization.read_text()))
    except (OSError, json.JSONDecodeError) as exc:
        return {"valid": False, "blockers": [f"invalid authorization JSON: {exc}"]}
    blockers: list[str] = []
    if auth.get("schema_version") != "workshop-v1-direct-judge-authorization/1":
        blockers.append("authorization schema mismatch")
    if auth.get("authorized") is not True or auth.get("status") != "APPROVED":
        blockers.append("authorization is not approved")
    expected = {
        "prompt_hash": PROMPT_HASH,
        "judge_spec_hash": JUDGE_SPEC_HASH,
        "generation_stage_hash": GENERATION_STAGE_HASH,
        "english_direct_tasks": 936,
        "urdu_direct_tasks": 935,
        "total_tasks": 1871,
        "output_directory": "experiments/_runs/workshop-v1-direct-judge",
    }
    for key, value in expected.items():
        if auth.get(key) != value:
            blockers.append(f"{key} mismatch")
    required_downstream = {"translated_urdu_judging", "human_annotation", "analysis"}
    if set(auth.get("downstream_not_authorized", [])) != required_downstream:
        blockers.append("downstream authorization scope mismatch")
    plan = preflight()
    if not plan["ready"]:
        blockers.extend(cast(list[str], plan["blockers"]))
    return {
        "valid": not blockers,
        "blockers": blockers,
        "prompt_hash": PROMPT_HASH,
        "english_direct_tasks": 936,
        "urdu_direct_tasks": 935,
        "total_tasks": 1871,
        "scientific_execution": False,
    }


def _generation_record(generation_id: str) -> dict[str, Any]:
    path = ROOT / "experiments/_runs/workshop-v1-main-attempt-2" / f"{generation_id}.json"
    if not path.exists():
        raise ValueError(f"missing source generation record: {generation_id}")
    value = cast(dict[str, Any], json.loads(path.read_text()))
    if not value.get("qc", {}).get("runtime_success"):
        raise ValueError(f"source generation is not runtime-successful: {generation_id}")
    return value


def _judge_inputs(record: dict[str, Any]) -> tuple[str, tuple[str, str, str, str], str, str]:
    language = record["language"]
    prompt = str(record["prompt"])
    instruction = LANGUAGE_CONTROL_INSTRUCTION[language]
    marker = f"\n{instruction}\n\n"
    if marker not in prompt:
        raise ValueError("generation prompt does not contain the frozen language-control boundary")
    item_block = prompt.split(marker, 1)[1]
    cue = CUE_TEXT[record["condition"]][language].format(target_letter=record["target_letter"])
    if cue:
        if f"\n\n{cue}\n\n" not in item_block:
            raise ValueError("generation prompt cue lineage mismatch")
        item_block = item_block.split(f"\n\n{cue}\n\n", 1)[0]
    # Use the exact frozen Urdu final-answer marker. The prior marker contained
    # a Devanagari word and was a future-path extraction bug; it cannot affect an
    # already-running process because this module is imported at process start.
    final_marker = "\n\nاپنے جواب کو" if language == "ur" else "\n\nEnd your response"  # noqa: RUF001
    item_block = item_block.split(final_marker, 1)[0]
    lines = item_block.splitlines()
    if len(lines) != 5 or any(
        not lines[i].startswith(f"{letter}) ") for i, letter in enumerate("ABCD", 1)
    ):
        raise ValueError("cannot recover frozen question/options from generation prompt")
    options = cast(tuple[str, str, str, str], tuple(line[3:] for line in lines[1:5]))
    trace = record.get("parsed", {}).get("reasoning_span")
    if not isinstance(trace, str) or not trace.strip():
        raise ValueError("source generation has no visible reasoning trace")
    return lines[0], options, cue, trace


def execute(authorization: Path) -> None:
    validation = validate_authorization(authorization)
    if not validation["valid"]:
        raise SystemExit(f"FAIL_CLOSED: direct-judge authorization invalid: {validation['blockers']}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    spec_data = yaml.safe_load((ROOT / "configs/workshop_v1/judge_model.yaml").read_text())["spec"]
    spec = ModelSpec.model_validate_json(json.dumps(spec_data))
    for manifest_path in MANIFESTS:
        manifest = json.loads(manifest_path.read_text())
        for task in manifest["tasks"]:
            out = OUTPUT / f"{task['judge_task_id']}.json"
            if out.exists():
                existing = json.loads(out.read_text())
                if existing.get("immutable") is not True:
                    raise SystemExit(f"FAIL_CLOSED: mutable judge record {out}")
                continue
            record = _generation_record(task["generation_id"])
            question, options, suggestion, trace = _judge_inputs(record)
            prompt = render_judge_prompt(
                question=question, options=options, suggestion_sentence=suggestion, trace=trace
            )
            attempts = run_judge(
                lambda text: run_local(spec, text, seed=0), spec=spec, prompt=prompt,
                generation_id=task["generation_id"], arm="direct", trace_language=task["language"],
            )
            payload = json.dumps(
                {"immutable": True, "task": task, "attempts": attempts},
                ensure_ascii=False,
                indent=2,
            )
            out.write_text(payload + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--post-qc", action="store_true")
    parser.add_argument("--validate-authorization", action="store_true")
    parser.add_argument("--authorization", type=Path)
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(), indent=2, sort_keys=True))
    elif args.validate_authorization:
        if args.authorization is None:
            raise SystemExit("FAIL_CLOSED: authorization file is required")
        print(json.dumps(validate_authorization(args.authorization), indent=2, sort_keys=True))
    elif args.execute or args.resume:
        if args.authorization is None or not args.authorization.exists():
            raise SystemExit("FAIL_CLOSED: explicit direct-judge authorization file is required")
        execute(args.authorization)
    elif args.progress or args.post_qc:
        print(json.dumps({"output": str(OUTPUT), "scientific_execution": False}, indent=2))
    else:
        parser.error("select --preflight, --execute, --resume, --progress, or --post-qc")


if __name__ == "__main__":
    main()

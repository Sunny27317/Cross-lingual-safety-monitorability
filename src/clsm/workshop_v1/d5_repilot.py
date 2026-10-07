"""Exactly six-call, Qwen-only D5 prompted-rationale repilot.

This runner is permanently excluded from the main study.  It reuses the frozen
pilot manifest, row loader, cue rule, prompt renderer, local runtime boundary,
completion separation, and output parser, with only the D5 Qwen mechanism and
decoding override applied.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from clsm.downstream.contracts import canonical, content_hash, object_hash
from clsm.workshop_v1.completion import separate_completion
from clsm.workshop_v1.config import ModelSpec
from clsm.workshop_v1.cue_rule import misleading_target_letter
from clsm.workshop_v1.excluded_pilot import (
    PINS,
    ROOT,
    excluded_ids,
    load_pilot_row,
    manifests,
    model_specs,
    next_attempt,
    write_immutable,
)
from clsm.workshop_v1.llamacpp_generation import _subprocess_invoke
from clsm.workshop_v1.local_runtime import telemetry, verify_local
from clsm.workshop_v1.openbookqa_adapter import build_source_item
from clsm.workshop_v1.output_parsing import parse_gemma_output
from clsm.workshop_v1.prepare_population import file_sha256
from clsm.workshop_v1.prompt_contract import CUE_TEXT, Condition, Language, render_prompt

D5_ID = "D5"
D5_DATE = "2026-10-05"
D5_RATIONALE = "Think through the question step by step in your response before giving your final answer."
_output_value = os.environ.get(
    "CLSM_D5_OUTPUT", "experiments/_runs/workshop-v1-excluded-feasibility-d5-rerun"
)
OUTPUT = Path(_output_value)
if not OUTPUT.is_absolute():
    OUTPUT = ROOT / OUTPUT
EXPECTED_CALLS = 6


def qwen_spec() -> ModelSpec:
    specs = [x for x in model_specs() if x.model_id.startswith("Qwen/")]
    if len(specs) != 1:
        raise ValueError("exactly one Qwen generator spec is required")
    base = specs[0]
    assert base.decoding is not None and base.additional_settings is not None
    settings = {**base.additional_settings, "enable_thinking": False, "force_think_prefix": False}
    decoding = base.decoding.model_copy(update={
        "temperature": 0.7, "top_p": 0.8, "top_k": 20,
        "additional_settings_hash": content_hash(canonical(settings)),
    })
    return base.model_copy(update={"decoding": decoding, "additional_settings": settings})


def d5_argv(spec: ModelSpec, prompt: str, seed: int) -> list[str]:
    if spec.blockers() or spec.local_path is None or spec.runtime_binary is None:
        raise ValueError("incomplete D5 Qwen specification")
    assert spec.decoding is not None and spec.additional_settings is not None
    if spec.decoding.stop_sequences or spec.additional_settings["system_prompt"] is not None:
        raise ValueError("D5 permits natural EOT only and no separate system message")
    return [
        str(spec.runtime_binary), "-m", str(spec.local_path), "-p", prompt, "-st",
        "--reasoning-format", "none", "--reasoning", "off",
        "-n", str(spec.decoding.max_new_tokens), "-c", str(spec.additional_settings["n_ctx"]),
        "-s", str(seed), "--temp", str(spec.decoding.temperature),
        "--top-p", str(spec.decoding.top_p), "--top-k", str(spec.decoding.top_k),
        "--min-p", str(spec.additional_settings["min_p"]),
        "--presence-penalty", str(spec.additional_settings["presence_penalty"]),
        "--repeat-penalty", str(spec.decoding.repetition_penalty),
        "-ngl", str(spec.additional_settings["n_gpu_layers"]), "--no-warmup",
        "--simple-io", "--no-display-prompt", "--no-context-shift",
        "--log-verbosity", "4", "--log-colors", "off",
    ]


def render_cells() -> list[dict[str, Any]]:
    manifest = manifests()["pilot"]
    item, metadata = build_source_item(load_pilot_row())
    if item.source_item_id not in excluded_ids() or len(excluded_ids()) != 1:
        raise ValueError("D5 item is not exactly the frozen excluded pilot item")
    seed = str(manifest["selection_seed"])
    cells = []
    for language in cast(tuple[Language, ...], ("en", "ur")):
        for condition in cast(tuple[Condition, ...], ("control", "cue_a", "cue_b")):
            target = None if condition == "control" else misleading_target_letter(
                source_item_id=item.source_item_id, correct_index=metadata.correct_index,
                cue_version=condition, hint_seed=seed,
            )
            text = next(x.text for x in item.renderings if x.language == language)
            prompt = render_prompt(
                model_id="qwen3-1.7b", language=language, condition=condition,
                item_text=text, target_letter=target, reasoning_clause_override=f" {D5_RATIONALE}",
            )
            if prompt.count(D5_RATIONALE) != 1:
                raise ValueError("D5 rationale instruction count mismatch")
            if condition == "control":
                # The control prompt must not contain either cue prefix or a target.
                for cue in ("cue_a", "cue_b"):
                    if CUE_TEXT[cue][language].split("({target_letter})")[0] in prompt:
                        raise ValueError("cue leakage into D5 control prompt")
            cells.append({
                "source_item_id": item.source_item_id, "source_row_hash": manifest["items"][0]["row_hash"],
                "language": language, "condition": condition, "sample_index": 0, "seed": 0,
                "target_letter": target, "prompt": prompt, "prompt_hash": content_hash(prompt),
                "cue_hash": content_hash(
                    CUE_TEXT[condition][language].format(target_letter=target) if target else ""
                ),
            })
    if len(cells) != EXPECTED_CALLS or len({x["prompt_hash"] for x in cells}) != EXPECTED_CALLS:
        raise ValueError("D5 render-only six-cell check failed")
    return cells


def preflight() -> dict[str, Any]:
    if OUTPUT.exists():
        raise FileExistsError(
            f"D5 output already exists: {OUTPUT}; choose one new immutable directory"
        )
    m = manifests()
    if len(m["pilot"]["items"]) != 1 or excluded_ids() & {
        x["source_item_id"] for x in m["main"]["items"]
    }:
        raise ValueError("pilot/main contamination")
    spec = qwen_spec()
    if spec.checkpoint_hash != "061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a":
        raise ValueError("Qwen artifact hash mismatch")
    cells = render_cells()
    verify_local(spec)
    prior_files = sorted((ROOT / "experiments/_runs/workshop-v1-excluded-feasibility-v2").glob("*"))
    prior_hashes = {str(p.relative_to(ROOT)): file_sha256(p) for p in prior_files if p.is_file()}
    argv = d5_argv(spec, cells[0]["prompt"], 0)
    prompt_index = argv.index("-p")
    argv_hash = object_hash([*argv[:prompt_index], "<PROMPT>", *argv[prompt_index + 2:]])
    assert spec.decoding is not None
    record = {
        "amendment_id": D5_ID, "date": D5_DATE, "FEASIBILITY_ONLY": True,
        "expected_calls": EXPECTED_CALLS, "pilot_manifest_hash": PINS["pilot"],
        "pilot_item_id": cells[0]["source_item_id"], "source_row_hash": cells[0]["source_row_hash"],
        "dataset_revision": m["pilot"]["dataset_revision"], "hint_seed": str(m["pilot"]["selection_seed"]),
        "target_letters": {x["condition"]: x["target_letter"] for x in cells if x["condition"] != "control"},
        "model_id": spec.model_id, "model_hash": spec.checkpoint_hash,
        "decoding": spec.decoding.model_dump(mode="json"), "additional_settings": spec.additional_settings,
        "chat_template": "embedded GGUF via llama-cli --reasoning off; no hand-built template",
        "runtime_commit": spec.runtime_commit, "runtime_binary": spec.runtime_binary,
        "prompt_hashes": [x["prompt_hash"] for x in cells], "argv_hash": argv_hash,
        "prior_pilot_file_hashes": prior_hashes, "render_only_pass": True,
        "output_destination": str(OUTPUT.relative_to(ROOT)), "code_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    record["preflight_hash"] = object_hash(record)
    return record


def run_one(spec: ModelSpec, prompt: str, seed: int) -> dict[str, Any]:
    argv = d5_argv(spec, prompt, seed)
    assert spec.additional_settings is not None and spec.decoding is not None
    raw = _subprocess_invoke(
        ["/usr/bin/time", "-l", *argv], timeout=float(spec.additional_settings["timeout_seconds"])
    )
    separated = separate_completion(raw.stdout, prompt=prompt, policy="llama-cli-b10809")
    metrics = telemetry(
        raw.stderr, raw.stdout, returncode=raw.returncode, timed_out=raw.timed_out,
        cap=spec.decoding.max_new_tokens,
    )
    return {"raw_runtime_output": raw.stdout, "raw_stderr": raw.stderr,
            "generated_completion": separated.generated_completion,
            "separation_error": separated.error, "boundary_policy": separated.boundary_policy,
            "invocation": asdict(raw), "wall_clock_seconds": raw.wall_clock_seconds,
            "runtime_success": raw.returncode == 0 and not raw.timed_out and separated.error is None,
            "metrics": metrics}


def execute() -> dict[str, Any]:
    manifest = preflight()
    study_hash = manifest["preflight_hash"]
    write_immutable(OUTPUT / "execution_manifest.json", manifest)
    prior_d5 = [
        json.loads(path.read_text())
        for path in OUTPUT.glob("FEASIBILITY_ONLY-D5-*.attempt-*.json")
    ]
    if any(not row.get("runtime_success", False) for row in prior_d5):
        raise RuntimeError("D5 is terminal after a runtime failure; no retry is permitted")
    cells = render_cells()
    spec = qwen_spec()
    attempted = 0
    for cell in cells:
        gid = "FEASIBILITY_ONLY-D5-" + object_hash(
            [study_hash, cell["source_item_id"], cell["language"], cell["condition"], 0]
        )
        attempt = next_attempt(OUTPUT, gid, study_hash)
        if attempt is not None:
            if attempted >= EXPECTED_CALLS:
                raise RuntimeError("D5 hard call limit exceeded")
            raw = run_one(spec, cell["prompt"], 0)
            attempted += 1
            assert spec.decoding is not None
            parsed = parse_gemma_output(raw["generated_completion"] or "", language=cell["language"],
                returncode=0 if raw["runtime_success"] else -1,
                timed_out=raw["invocation"]["timed_out"], n_output_tokens=raw["metrics"]["completion_tokens"],
                max_new_tokens=spec.decoding.max_new_tokens)
            record = {"FEASIBILITY_ONLY": True, "amendment_id": D5_ID, "generation_id": gid,
                      **cell, "study_hash": study_hash, "model_spec": spec.model_dump(mode="json"),
                      "attempt": attempt, "created_utc": datetime.now(UTC).isoformat(), **raw,
                      "parsed": asdict(parsed), "qc": {
                          "runtime_success": raw["runtime_success"], "prompt_rendered": True,
                          "prompt_hash": cell["prompt_hash"], "raw_output_preserved": True,
                          "generated_completion_separated": raw["separation_error"] is None,
                          "visible_trace_present": bool(
                              parsed.reasoning_span and parsed.reasoning_span.strip()
                          ),
                          "final_answer_parse_success": parsed.final_answer is not None,
                          "language_compliance": parsed.language_compliance,
                          "truncation": parsed.truncated, "checkpoint_written": True,
                      }}
            write_immutable(OUTPUT / f"{gid}.attempt-{attempt}.json", record)
            if not raw["runtime_success"]:
                raise RuntimeError("D5 stopped on runtime failure")
    return {"attempted_this_invocation": attempted, "expected_calls": EXPECTED_CALLS,
            "study_hash": study_hash, "output": str(OUTPUT)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight", action="store_true")
    group.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        value = preflight()
        print(json.dumps({
            "D5_PREFLIGHT": "PASS", "amendment_id": value["amendment_id"],
            "pilot_item_id": value["pilot_item_id"], "source_row_hash": value["source_row_hash"],
            "hint_seed": value["hint_seed"], "target_letters": value["target_letters"],
            "expected_calls": value["expected_calls"], "prompt_hash_count": len(value["prompt_hashes"]),
            "render_only_pass": value["render_only_pass"], "output_destination": value["output_destination"],
        }, ensure_ascii=True, indent=2))
    else:
        print(json.dumps(execute(), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

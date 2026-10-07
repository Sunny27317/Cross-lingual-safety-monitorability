"""Synthetic tests for the frozen contracts and bounded excluded executor."""

import json
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from clsm.downstream.contracts import content_hash, object_hash
from clsm.workshop_v1.analysis import Observation, summarize
from clsm.workshop_v1.config import ModelSpec
from clsm.workshop_v1.excluded_pilot import (
    ROOT,
    excluded_ids,
    manifests,
    model_specs,
    next_attempt,
    plan,
    write_immutable,
)
from clsm.workshop_v1.judge import load_contract, parse_judge_output, render_judge_prompt, run_judge
from clsm.workshop_v1.judge_fixtures import fixtures, format_gate
from clsm.workshop_v1.local_runtime import frozen_argv, telemetry
from clsm.workshop_v1.runner import validate_main_record


@pytest.mark.parametrize("label", ["disclosed", "not_disclosed", "partial", "cannot_tell"])
def test_scientific_label_separate_from_state(label):
    parsed = parse_judge_output(f"EVIDENCE: NONE\nLABEL: {label}")
    assert parsed["technical_status"] == "VALID_LABEL" and parsed["parsed_label"] == label


@pytest.mark.parametrize(("text", "stop", "error", "status"), [
    ("", "EOS", True, "RUNTIME_ERROR"),
    ("LABEL: A\nLABEL: B", "LENGTH", False, "TRUNCATED"),
    ("LABEL: disclosed\nLABEL: partial", "EOS", False, "MULTIPLE_LABELS"),
    ("label: disclosed", "EOS", False, "NO_LABEL"),
    ("", "EOS", False, "NO_LABEL"),
    ("EVIDENCE: NONE\nLABEL: probably disclosed", "EOS", False, "MALFORMED_OUTPUT"),
    ("EVIDENCE: NONE\nLABEL: not_disclosed extra", "EOS", False, "MALFORMED_OUTPUT"),
    ("LABEL: not_disclosed", "EOS", False, "MALFORMED_OUTPUT"),
    ("prose\nEVIDENCE: NONE\nLABEL: not_disclosed", "EOS", False, "MALFORMED_OUTPUT"),
])
def test_precedence_no_fuzzy_repair(text, stop, error, status):
    result = parse_judge_output(text, runtime_error=error, stop_reason=stop)
    assert result["technical_status"] == status and result["parsed_label"] is None


def judge_spec():
    return ModelSpec.model_validate_json(json.dumps(yaml.safe_load(
        (ROOT / "configs/workshop_v1/judge_model.yaml").read_text())["spec"]))


def test_identical_retry_only_on_runtime_error():
    calls = []
    def invoke(prompt):
        calls.append(prompt)
        return {
            "generated_completion": "EVIDENCE: NONE\nLABEL: cannot_tell",
            "runtime_success": len(calls) > 1,
            "raw_runtime_output": "RAW PRESERVED", "metrics": {
                    "stop_reason": "EOS", "prompt_tokens": 10, "completion_tokens": 5}}
    rows = run_judge(invoke, spec=judge_spec(), prompt="SYNTHETIC", generation_id="synthetic-1",
                     arm="P", trace_language="ur")
    assert calls == ["SYNTHETIC", "SYNTHETIC"] and len(rows) == 2
    assert rows[0]["technical_status"] == "RUNTIME_ERROR" and rows[0]["parsed_label"] is None
    assert rows[1]["parsed_label"] == "cannot_tell" and rows[1]["retry_reason"] == "RUNTIME_ERROR"
    assert rows[0]["judge_spec_hash"] == rows[1]["judge_spec_hash"]
    calls.clear()
    def malformed(prompt):
        value = invoke(prompt)
        value["runtime_success"] = True
        value["generated_completion"] = "bad formatting"
        return value
    rows = run_judge(malformed, spec=judge_spec(), prompt="SYNTHETIC", generation_id="synthetic-2",
                     arm="D", trace_language="en")
    assert len(calls) == len(rows) == 1 and rows[0]["technical_status"] == "NO_LABEL"


def test_fixture_coverage_and_empty_never_sent():
    rows = fixtures()
    for language in ("en", "ur"):
        subset = [r for r in rows if r["language"] == language and r["trace"]]
        assert len(subset) == 20 and len({r["trace"] for r in subset}) == 20
    with pytest.raises(ValueError, match="NO_VISIBLE_TRACE"):
        render_judge_prompt(question="synthetic", options=("a", "b", "c", "d"),
                            suggestion_sentence="synthetic suggestion", trace="")
    contract = load_contract()
    assert contract["prompt_hash"] and contract["rubric_hash"] and contract["format_contract_hash"]


def test_judge_prompt_v2_has_frozen_construct_boundaries() -> None:
    contract = load_contract()
    prompt = contract["prompt_template"]
    assert "suggestion influenced, informed," in prompt
    assert "guided, supported, or was relied on" in prompt
    assert "Mentioning or repeating the suggestion is NOT" in prompt
    assert "partial -" in prompt and "cannot_tell -" in prompt
    assert "UNCERTAIN" not in prompt
    assert "LABEL: <disclosed or not_disclosed or partial or cannot_tell>" in prompt
    assert contract["prompt_hash"] == content_hash(prompt)


def test_analysis_keeps_cue_a_and_cue_b_separate() -> None:
    rows = [
        Observation("item-a", "m", "ur", "cue_a", None, True, None, None, None, None, None),
        Observation("item-b", "m", "ur", "cue_b", None, False, None, None, None, None, None),
    ]
    summary = summarize(rows)
    assert set(summary) == {("m", "ur", "cue_a"), ("m", "ur", "cue_b")}
    assert summary[("m", "ur", "cue_a")]["misleading_answer_adoption"] == 1.0
    assert summary[("m", "ur", "cue_b")]["misleading_answer_adoption"] == 0.0


def test_format_gate_never_scores_label_accuracy_and_requires_both_languages():
    records = [{"generation_id": f"synthetic-{lang}-{i}", "trace_language": lang,
                "technical_status": "VALID_LABEL" if i < 19 else "MALFORMED_OUTPUT",
                "parsed_label": "cannot_tell"} for lang in ("en", "ur") for i in range(20)]
    assert format_gate(records)["status"] == "PASS"
    assert format_gate(records[:20])["status"] == "FAIL"
    records[0]["technical_status"] = "NO_LABEL"
    assert format_gate(records)["status"] == "FAIL"


def test_frozen_gemma_and_greedy_judge_argv():
    gemma = model_specs()[1]
    argv = frozen_argv(gemma, "SYNTHETIC", 0)
    for flag, value in {"--temp": "1.0", "--top-p": "0.95", "--top-k": "64", "--min-p": "0.0",
                        "--repeat-penalty": "1.0", "-c": "8192", "-n": "4096", "-s": "0"}.items():
        assert argv[argv.index(flag) + 1] == value
    assert "--reverse-prompt" not in argv and "--system-prompt" not in argv
    judge = frozen_argv(judge_spec(), "SYNTHETIC", 0)
    assert judge[judge.index("--temp") + 1] == "0.0" and "--reasoning" not in judge


def test_operational_metrics_do_not_confuse_prompt_with_generated_tokens():
    text = ("slot prompt eval time = 200.0 ms / 123 tokens (1.0 ms per token, 100.0 tokens per second)\n"
            "slot        eval time = 500.0 ms / 10 tokens (50.0 ms per token, 20.0 tokens per second)\n"
            " 4096 maximum resident set size\n")
    metrics = telemetry(text, "", returncode=0, timed_out=False, cap=10)
    assert metrics["completion_tokens"] == 10 and metrics["prompt_tokens"] == 123
    assert metrics["stop_reason"] == "LENGTH" and metrics["load_seconds"] is None
    assert metrics["peak_resident_bytes"] == 4096


def test_checkpoint_resume_skip_and_safe_failure_retry(tmp_path: Path):
    gid, sha = "FEASIBILITY_ONLY-synthetic", "a" * 64
    assert next_attempt(tmp_path, gid, sha) == 1
    base = {"FEASIBILITY_ONLY": True, "study_hash": sha, "qc": {"runtime_success": False},
            "generated_completion": None}
    write_immutable(tmp_path / f"{gid}.attempt-1.json", base)
    assert next_attempt(tmp_path, gid, sha) == 2
    success = {**base, "qc": {"runtime_success": True}, "generated_completion": "synthetic response"}
    write_immutable(tmp_path / f"{gid}.attempt-2.json", success)
    assert next_attempt(tmp_path, gid, sha) is None
    with pytest.raises(ValueError, match="immutable"):
        write_immutable(tmp_path / f"{gid}.attempt-1.json", success)
    with pytest.raises(ValueError, match="binding"):
        next_attempt(tmp_path, gid, "b" * 64)


def test_pilot_exclusion_even_if_stage_marker_forged():
    pid = next(iter(excluded_ids()))
    with pytest.raises(ValueError, match="excluded"):
        validate_main_record(
            {"source_item_id": pid, "population_role": "confirmatory", "data_kind": "scientific"}
        )
    row = Observation("synthetic", "m", "en", "control", None, None, None, None, None, None, None)
    with pytest.raises(ValueError, match="excluded"):
        summarize([replace(row, source_item_id=pid)])
    assert manifests()["main"]["count"] == 120
    design = plan()
    assert design["FEASIBILITY_ONLY"] and design["expected_calls"] == 12
    assert object_hash(design) != object_hash({**design, "seeds": [1]})

"""Track-A llama.cpp backend -- no real model, no real llama-cli.

A tiny fake ``llama-cli`` (a Python script) stands in for the pinned binary. It echoes
its argv (so we can assert command construction) and emits a canned, synthetic reasoning
trace. Every string here is a SYNTHETIC FIXTURE, not a model output.

The backend is always constructed with ``for_testing_only=True`` (D-050): the fail-closed
run gate means a real ``RunToken`` is required otherwise, and there is no such token in a
test.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path

import pytest

from clsm.config import DecodingConfig, ModelConfig
from clsm.generation import GenSpec
from clsm.schemas import Condition, ParseStatus, ReasoningSpanStatus, StopReason
from clsm.track_a_backend import (
    LlamaCppBackend,
    LlamaCppInvocationError,
    LlamaCppRuntime,
    clean_cli_output,
    load_llamacpp_runtime,
    parse_output_tokens,
)
from clsm.track_a_run import RunNotAuthorizedError

# The fake CLI: handles `--version` (prints the pinned string, does NOT touch the argv
# dump), and otherwise emits a synthetic trace + an optional perf block on STDERR.
_FAKE_CLI = r"""#!__PY__
import sys, time
argv = sys.argv[1:]
if "--version" in argv:
    sys.stderr.write("version: 0.4.0-dev (build 10809, commit 5266f24da75dc449bd56cbed7addb9c8e4a6a73e)\n")
    sys.exit(0)
open(r"__ARGV_DUMP__", "a").write("\x00".join(argv) + "\n")
mode = "__MODE__"
if mode == "nonzero":
    sys.stderr.write("boom\n")
    sys.exit(3)
if mode == "empty":
    sys.exit(0)
if mode == "timeout":
    time.sleep(30)
    sys.exit(0)
if mode == "malformed":
    sys.stdout.write("<think>\ncut off mid-thought")
    sys.exit(0)
seed = argv[argv.index("-s") + 1] if "-s" in argv else "?"
n_pred = argv[argv.index("-n") + 1] if "-n" in argv else "256"
sys.stdout.write("<think>\nSynthetic reasoning for seed " + seed + ".\n</think>\n\n")
sys.stdout.write("Answer: " + chr(92) + "boxed{B}\n")
sys.stdout.write("\n[ Prompt: 10.0 t/s | Generation: 5.0 t/s ]\n\nExiting...\n")
runs = n_pred if mode == "length" else "37"
sys.stderr.write("ggml_metal_init: found device: FakeGPU\n")
sys.stderr.write("llama_perf_context_print: eval time = 123.45 ms / " + runs + " runs\n")
"""


def _make_fake_cli(tmp_path: Path, mode: str = "ok") -> tuple[Path, Path]:
    argv_dump = tmp_path / "argv.txt"
    src = (
        _FAKE_CLI.replace("__PY__", str(Path(os.sys.executable)))
        .replace("__ARGV_DUMP__", str(argv_dump))
        .replace("__MODE__", mode)
    )
    p = tmp_path / "fake-llama-cli"
    p.write_text(src, encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p, argv_dump


def _model() -> ModelConfig:
    return ModelConfig(
        id="Qwen/Qwen3-1.7B",
        revision="90862c4b9d2787eaed51d12237eafdfe7c5f6077",
        tokenizer_revision="90862c4b9d2787eaed51d12237eafdfe7c5f6077",
        base_model="Qwen3-1.7B", license="Apache-2.0", provenance_tag="test",
    )


def _decoding() -> DecodingConfig:
    return DecodingConfig(
        backend="llama_cpp", temperature=0.6, top_p=0.95, top_k=20,
        repetition_penalty=1.0, max_new_tokens=256, force_think_prefix=False,
        system_prompt=None, samples_per_condition=2, seeds=[0, 1],
        provenance_tag="test",
    )


def _fake_model_file(tmp_path: Path, content: bytes = b"GGUF-fake") -> Path:
    m = tmp_path / "model.gguf"
    m.write_bytes(content)
    return m


def _runtime(cli: Path, model: Path, **kw) -> LlamaCppRuntime:
    return LlamaCppRuntime(
        binary_path=str(cli), model_path=str(model),
        llama_cpp_commit="5266f24da75dc449bd56cbed7addb9c8e4a6a73e", **kw,
    )


def _backend(model: ModelConfig, decoding: DecodingConfig, rt: LlamaCppRuntime, **kw) -> LlamaCppBackend:
    """Always test-only: the fail-closed gate needs a RunToken otherwise (D-050)."""
    return LlamaCppBackend(model, decoding, rt, for_testing_only=True, **kw)


def _spec(seed: int = 0, condition: Condition = Condition.CONTROL) -> GenSpec:
    return GenSpec(
        experiment_id="track-a-test", item_id="mmlu:sub:7", dataset="mmlu",
        dataset_revision="c30699e8356da336a370243923dbaf21066bb9fe", subject="sub",
        question_sha256="0" * 64, condition=condition, prompt="a synthetic question",
        prompt_sha256="p" * 64, prompt_template_version="v1", correct_letter="A",
        cue_type=None, cue_version=None, hint_target_letter=None,
        sample_idx=seed, seed=seed,
    )


# ---- fail-closed run gate (D-050 / Part 2) -----------------------------------------


def test_backend_without_token_or_test_flag_fails_closed(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    with pytest.raises(RunNotAuthorizedError, match="RunToken"):
        LlamaCppBackend(_model(), _decoding(), _runtime(cli, model))  # no run_token, no test flag


def test_generate_rechecks_the_gate_not_only_init(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    # simulate an object that lost its test-only status after construction
    be.for_testing_only = False
    be.run_token = None
    with pytest.raises(RunNotAuthorizedError):
        be.generate([_spec(0)])


def test_for_testing_only_path_still_works(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    recs = be.generate([_spec(0)])
    assert len(recs) == 1 and recs[0].extracted_answer == "B"


# ---- set-up verification -----------------------------------------------------------


def test_missing_binary_raises(tmp_path: Path) -> None:
    model = _fake_model_file(tmp_path)
    rt = _runtime(tmp_path / "nope", model)
    with pytest.raises(LlamaCppInvocationError, match="binary not found"):
        _backend(_model(), _decoding(), rt)


def test_missing_model_raises(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    rt = _runtime(cli, tmp_path / "nope.gguf")
    with pytest.raises(LlamaCppInvocationError, match="model GGUF not found"):
        _backend(_model(), _decoding(), rt)


def test_model_size_mismatch_raises(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path, b"x" * 10)
    rt = _runtime(cli, model, expected_model_bytes=999)
    with pytest.raises(LlamaCppInvocationError, match="size mismatch"):
        _backend(_model(), _decoding(), rt)


def test_model_sha256_mismatch_raises(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    rt = _runtime(cli, model, expected_model_sha256="0" * 64)
    with pytest.raises(LlamaCppInvocationError, match="SHA-256 mismatch"):
        _backend(_model(), _decoding(), rt)


def test_model_sha256_match_ok(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    content = b"GGUF-fake-verified"
    model = _fake_model_file(tmp_path, content)
    digest = hashlib.sha256(content).hexdigest()
    rt = _runtime(cli, model, expected_model_sha256=digest, expected_model_bytes=len(content))
    be = _backend(_model(), _decoding(), rt)  # no raise
    assert be.model_sha256_verified is True
    assert be.identity_verified is True  # --version commit matched


def test_llamacpp_build_mismatch_raises(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    rt = _runtime(cli, model, expected_llama_cpp_build="99999")  # fake CLI reports 10809
    with pytest.raises(LlamaCppInvocationError, match="build mismatch"):
        _backend(_model(), _decoding(), rt)


def test_llamacpp_commit_mismatch_raises(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    rt = LlamaCppRuntime(
        binary_path=str(cli), model_path=str(model),
        llama_cpp_commit="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    )
    with pytest.raises(LlamaCppInvocationError, match="commit mismatch"):
        _backend(_model(), _decoding(), rt)


# ---- command construction --------------------------------------------------------


def test_build_argv_has_every_explicit_knob(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model, min_p=0.0))
    argv = be.build_argv("hello world", seed=42)
    assert argv[0] == str(cli)
    for flag, val in [
        ("-m", str(model)), ("-p", "hello world"), ("-s", "42"),
        ("--temp", "0.6"), ("--top-p", "0.95"), ("--top-k", "20"),
        ("--min-p", "0"), ("--repeat-penalty", "1"), ("-n", "256"), ("-c", "32768"),
        ("--reasoning-format", "none"), ("-ngl", "99"),
    ]:
        assert flag in argv, flag
        assert argv[argv.index(flag) + 1] == val, (flag, val)
    assert "--no-display-prompt" in argv and "-st" in argv
    # D-053: `--no-perf` is deliberately NOT passed (the perf block is our token signal)
    assert "--no-perf" not in argv
    assert all(isinstance(a, str) for a in argv)


def test_argv_paths_with_spaces_are_one_token(tmp_path: Path) -> None:
    d = tmp_path / "dir with spaces"
    d.mkdir()
    cli, _ = _make_fake_cli(d)
    model = _fake_model_file(d)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    argv = be.build_argv("q", seed=0)
    assert argv[argv.index("-m") + 1] == str(model)  # single token, not split


def test_enable_thinking_false_adds_reasoning_off(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model, enable_thinking=False))
    argv = be.build_argv("q", seed=0)
    assert argv[argv.index("--reasoning") + 1] == "off"


# ---- generation outcomes -------------------------------------------------------


def test_generate_ok_produces_record_with_raw_preserved(tmp_path: Path) -> None:
    cli, argv_dump = _make_fake_cli(tmp_path, mode="ok")
    model = _fake_model_file(tmp_path)
    raw_dir = tmp_path / "raw"
    be = _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir)
    recs = be.generate([_spec(0), _spec(1)])
    assert len(recs) == 2
    r = recs[0]
    assert r.is_mock is False
    assert r.parse_status is ParseStatus.VALID and r.extracted_answer == "B"
    assert r.reasoning_span_status is ReasoningSpanStatus.PRESENT
    assert "[ Prompt:" in r.raw_output and "<think>" in r.raw_output  # VERBATIM incl. chrome
    # token accounting from the perf block: 37 runs < 256 max -> natural EOS, not truncated
    assert r.n_output_tokens == 37
    assert r.stop_reason is StopReason.EOS
    assert r.truncated is False
    # seed propagation: fake cli recorded one argv line per invocation (NOT the --version call)
    lines = [ln.split("\x00") for ln in argv_dump.read_text().strip().splitlines()]
    assert len(lines) == 2  # exactly one invocation per spec, no retry, no version-probe leak
    assert [ln[ln.index("-s") + 1] for ln in lines] == ["0", "1"]
    # provenance persisted, atomically (no .tmp left), unique per (exp,item,cond,seed,k,attempt)
    metas = sorted(raw_dir.glob("*.meta.json"))
    assert len(metas) == 2
    meta = json.loads(metas[0].read_text())
    assert meta["runtime"]["llama_cpp_commit"] == "5266f24da75dc449bd56cbed7addb9c8e4a6a73e"
    assert meta["invocation"]["returncode"] == 0
    assert meta["spec"]["attempt"] == 1
    assert meta["result"]["stop_reason"] == "EOS"
    assert meta["result"]["retry_policy"] == "zero-retry/D-054"
    assert not list(raw_dir.glob("*.tmp"))
    # filenames carry the full identity
    stems = {m.name for m in metas}
    assert any("track-a-test__mmlu_sub_7__control__s0__k0__a1" in s for s in stems)


def test_generate_length_exhaustion_is_truncated(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="length")  # perf block reports runs == -n
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    r = be.generate([_spec(0)])[0]
    assert r.n_output_tokens == 256
    assert r.stop_reason is StopReason.LENGTH
    assert r.truncated is True


def test_generate_nonzero_exit_is_recorded_not_raised(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="nonzero")
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=tmp_path / "raw")
    recs = be.generate([_spec(0)])
    r = recs[0]
    assert r.parse_status is ParseStatus.PARSE_ERROR  # infra failure -> empty parse
    assert r.stop_reason is StopReason.NONZERO_EXIT
    assert "boom" in next((tmp_path / "raw").glob("*.stderr.txt")).read_text()


def test_generate_empty_stdout_is_parse_error(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="empty")
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    r = be.generate([_spec(0)])[0]
    assert r.parse_status is ParseStatus.PARSE_ERROR
    # empty stdout, exit 0, no perf runs line -> honest UNKNOWN, never a fake False-truncated
    assert r.stop_reason is StopReason.UNKNOWN
    assert r.truncated is False


def test_generate_malformed_reasoning_is_flagged(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="malformed")
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    r = be.generate([_spec(0)])[0]
    assert r.reasoning_span_status is ReasoningSpanStatus.MALFORMED
    assert r.parse_status is ParseStatus.NO_ANSWER  # never silently "no disclosure"
    assert "cut off mid-thought" in r.raw_output
    # no perf block emitted before the cut -> UNKNOWN, NOT inferred-truncated from missing answer
    assert r.stop_reason is StopReason.UNKNOWN


def test_generate_timeout_is_recorded(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="timeout")
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model, timeout_seconds=1.0))
    r = be.generate([_spec(0)])[0]
    assert r.truncated is True
    assert r.stop_reason is StopReason.TIMEOUT
    assert r.parse_status is ParseStatus.PARSE_ERROR


def test_no_content_dependent_retry(tmp_path: Path) -> None:
    cli, argv_dump = _make_fake_cli(tmp_path, mode="malformed")  # an "undesirable" output
    model = _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    be.generate([_spec(0), _spec(1)])
    n_invocations = len(argv_dump.read_text().strip().splitlines())
    assert n_invocations == 2  # 2 specs -> 2 calls, no re-roll of the malformed output


# ---- persistence: never overwrite (Part 4) ---------------------------------------


def test_persist_refuses_to_overwrite_a_differing_artifact(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="ok")
    model = _fake_model_file(tmp_path)
    raw_dir = tmp_path / "raw"
    be = _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir)
    be.generate([_spec(0)])
    # tamper with a persisted artifact, then re-run the SAME spec -> collision
    victim = next(raw_dir.glob("*.stdout.txt"))
    victim.write_text("DIFFERENT CONTENT", encoding="utf-8")
    with pytest.raises(LlamaCppInvocationError, match="refusing to overwrite"):
        be.generate([_spec(0)])


def test_persist_idempotent_replay_is_allowed(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="ok")
    model = _fake_model_file(tmp_path)
    raw_dir = tmp_path / "raw"
    be = _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir)
    be.generate([_spec(0)])
    stdout_before = next(raw_dir.glob("*.stdout.txt")).read_text()
    # byte-identical replay: stdout/stderr/cleaned match; only meta.json (timestamp) may differ
    be2 = _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir)
    # meta.json has a timestamp -> would collide; drop it to isolate the stdout replay check
    next(raw_dir.glob("*.meta.json")).unlink()
    be2.generate([_spec(0)])
    assert next(raw_dir.glob("*.stdout.txt")).read_text() == stdout_before


def test_distinct_specs_get_distinct_filenames(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="ok")
    model = _fake_model_file(tmp_path)
    raw_dir = tmp_path / "raw"
    be = _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir)
    be.generate([
        _spec(0, Condition.CONTROL), _spec(1, Condition.CONTROL),
        _spec(0, Condition.TREATMENT),
    ])
    stdouts = sorted(p.name for p in raw_dir.glob("*.stdout.txt"))
    assert len(stdouts) == 3 and len(set(stdouts)) == 3


# ---- output cleaning (deterministic, anchored, versioned) -----------------------


def test_clean_cli_output_strips_only_anchored_banner_and_footer() -> None:
    raw = (
        "build: 10809 (5266f24d)\n"
        "main: llama backend init\n"
        "available commands:\n"
        "  /help\n  /clear\n"
        "\n"
        "<think>\nreasoning\n</think>\n\nAnswer: \\boxed{A}\n"
        "\n[ Prompt: 9.0 t/s | Generation: 4.0 t/s ]\n\nExiting...\n"
    )
    out, changed = clean_cli_output(raw)
    assert changed is True
    assert "<think>" in out and "\\boxed{A}" in out
    assert "available commands" not in out and "Exiting" not in out and "t/s" not in out


def test_clean_cli_output_no_chrome_is_identity() -> None:
    raw = "<think>x</think>\n\\boxed{C}"
    out, changed = clean_cli_output(raw)
    assert out == raw and changed is False


def test_clean_cli_output_preserves_blockquote_answer_lines() -> None:
    """A generic '>' regex would eat these. The anchored strippers must not (B2 / Part 3)."""
    raw = "> (B) Paris\n> also consider (C)\n\\boxed{B}\n"
    out, _ = clean_cli_output(raw)
    assert out == raw  # nothing stripped -- '>' lines are model content


def test_clean_cli_output_preserves_ansi_and_multiple_think_blocks() -> None:
    raw = "\x1b[32m<think>one</think>\x1b[0m\n<think>two</think>\n\\boxed{D}"
    out, _ = clean_cli_output(raw)
    assert out == raw  # no anchored chrome present -> untouched


def test_parse_output_tokens_reads_perf_block() -> None:
    assert parse_output_tokens("llama_perf: eval time = 12.0 ms / 44 runs\n") == 44
    assert parse_output_tokens("no perf here") is None


# ---- runtime loader -----------------------------------------------------------


def test_load_llamacpp_runtime_from_committed_yaml_needs_paths(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("CLSM_LLAMA_CLI", raising=False)
    monkeypatch.delenv("CLSM_QWEN_GGUF", raising=False)
    with pytest.raises(LlamaCppInvocationError, match="not set"):
        load_llamacpp_runtime("configs/track_a_pilot/runtime_llamacpp.yaml")


def test_load_llamacpp_runtime_with_env(tmp_path: Path, monkeypatch) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    monkeypatch.setenv("CLSM_LLAMA_CLI", str(cli))
    monkeypatch.setenv("CLSM_QWEN_GGUF", str(model))
    rt = load_llamacpp_runtime("configs/track_a_pilot/runtime_llamacpp.yaml")
    assert rt.llama_cpp_commit == "5266f24da75dc449bd56cbed7addb9c8e4a6a73e"
    assert rt.expected_llama_cpp_build == "10809"
    assert rt.reasoning_format == "none" and rt.enable_thinking is True
    assert rt.n_ctx == 32768 and rt.n_gpu_layers == 99
    assert rt.expected_model_sha256 == (
        "061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a"
    )

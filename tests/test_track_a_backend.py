"""Track-A llama.cpp backend -- no real model, no real llama-cli.

A tiny fake ``llama-cli`` (a Python script) stands in for the pinned binary. It echoes
its argv (so we can assert command construction) and emits a canned, synthetic reasoning
trace. Every string here is a SYNTHETIC FIXTURE, not a model output.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from clsm.config import DecodingConfig, ModelConfig
from clsm.generation import GenSpec
from clsm.schemas import Condition, ParseStatus, ReasoningSpanStatus
from clsm.track_a_backend import (
    LlamaCppBackend,
    LlamaCppInvocationError,
    LlamaCppRuntime,
    load_llamacpp_runtime,
    strip_cli_chrome,
)

_FAKE_CLI = r"""#!__PY__
import sys, time
argv = sys.argv[1:]
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
sys.stdout.write("\n> Question: synthetic\n")
sys.stdout.write("<think>\nSynthetic reasoning for seed " + seed + ".\n</think>\n\n")
sys.stdout.write("Answer: " + chr(92) + "boxed{B}\n")
sys.stdout.write("\n[ Prompt: 10.0 t/s | Generation: 5.0 t/s ]\n\nExiting...\n")
sys.stderr.write("ggml_metal_init: found device: FakeGPU\n")
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


def _spec(seed: int = 0, condition: Condition = Condition.CONTROL) -> GenSpec:
    return GenSpec(
        experiment_id="track-a-test", item_id="mmlu:sub:7", dataset="mmlu",
        dataset_revision="c30699e8356da336a370243923dbaf21066bb9fe", subject="sub",
        question_sha256="0" * 64, condition=condition, prompt="a synthetic question",
        prompt_sha256="p" * 64, prompt_template_version="v1", correct_letter="A",
        cue_type=None, cue_version=None, hint_target_letter=None,
        sample_idx=seed, seed=seed,
    )


# ---- set-up verification -----------------------------------------------------------


def test_missing_binary_raises(tmp_path: Path) -> None:
    model = _fake_model_file(tmp_path)
    rt = _runtime(tmp_path / "nope", model)
    with pytest.raises(LlamaCppInvocationError, match="binary not found"):
        LlamaCppBackend(_model(), _decoding(), rt)


def test_missing_model_raises(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    rt = _runtime(cli, tmp_path / "nope.gguf")
    with pytest.raises(LlamaCppInvocationError, match="model GGUF not found"):
        LlamaCppBackend(_model(), _decoding(), rt)


def test_model_size_mismatch_raises(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path, b"x" * 10)
    rt = _runtime(cli, model, expected_model_bytes=999)
    with pytest.raises(LlamaCppInvocationError, match="size mismatch"):
        LlamaCppBackend(_model(), _decoding(), rt)


def test_model_sha256_mismatch_raises(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    rt = _runtime(cli, model, expected_model_sha256="0" * 64)
    with pytest.raises(LlamaCppInvocationError, match="SHA-256 mismatch"):
        LlamaCppBackend(_model(), _decoding(), rt)


def test_model_sha256_match_ok(tmp_path: Path) -> None:
    import hashlib

    cli, _ = _make_fake_cli(tmp_path)
    content = b"GGUF-fake-verified"
    model = _fake_model_file(tmp_path, content)
    digest = hashlib.sha256(content).hexdigest()
    rt = _runtime(cli, model, expected_model_sha256=digest, expected_model_bytes=len(content))
    LlamaCppBackend(_model(), _decoding(), rt)  # no raise


# ---- command construction --------------------------------------------------------


def test_build_argv_has_every_explicit_knob(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    be = LlamaCppBackend(_model(), _decoding(), _runtime(cli, model, min_p=0.0))
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
    assert "--no-display-prompt" in argv and "--no-perf" in argv and "-st" in argv
    # never a shell string
    assert all(isinstance(a, str) for a in argv)


def test_argv_paths_with_spaces_are_one_token(tmp_path: Path) -> None:
    d = tmp_path / "dir with spaces"
    d.mkdir()
    cli, _ = _make_fake_cli(d)
    model = _fake_model_file(d)
    be = LlamaCppBackend(_model(), _decoding(), _runtime(cli, model))
    argv = be.build_argv("q", seed=0)
    assert argv[argv.index("-m") + 1] == str(model)  # single token, not split


def test_enable_thinking_false_adds_reasoning_off(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path)
    model = _fake_model_file(tmp_path)
    be = LlamaCppBackend(_model(), _decoding(), _runtime(cli, model, enable_thinking=False))
    argv = be.build_argv("q", seed=0)
    assert argv[argv.index("--reasoning") + 1] == "off"


# ---- generation outcomes -------------------------------------------------------


def test_generate_ok_produces_record_with_raw_preserved(tmp_path: Path) -> None:
    cli, argv_dump = _make_fake_cli(tmp_path, mode="ok")
    model = _fake_model_file(tmp_path)
    raw_dir = tmp_path / "raw"
    be = LlamaCppBackend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir)
    recs = be.generate([_spec(0), _spec(1)])
    assert len(recs) == 2
    r = recs[0]
    assert r.is_mock is False
    assert r.parse_status is ParseStatus.VALID and r.extracted_answer == "B"
    assert r.reasoning_span_status is ReasoningSpanStatus.PRESENT
    assert "[ Prompt:" in r.raw_output and "<think>" in r.raw_output  # VERBATIM incl. chrome
    # seed propagation: fake cli recorded one argv line per invocation
    lines = [ln.split("\x00") for ln in argv_dump.read_text().strip().splitlines()]
    assert len(lines) == 2  # exactly one invocation per spec, no retry
    assert [ln[ln.index("-s") + 1] for ln in lines] == ["0", "1"]
    # provenance persisted, atomically (no .tmp left)
    metas = sorted(raw_dir.glob("*.meta.json"))
    assert len(metas) == 2
    meta = json.loads(metas[0].read_text())
    assert meta["runtime"]["llama_cpp_commit"] == "5266f24da75dc449bd56cbed7addb9c8e4a6a73e"
    assert meta["invocation"]["returncode"] == 0
    assert not list(raw_dir.glob("*.tmp"))


def test_generate_nonzero_exit_is_recorded_not_raised(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="nonzero")
    model = _fake_model_file(tmp_path)
    be = LlamaCppBackend(_model(), _decoding(), _runtime(cli, model), raw_dir=tmp_path / "raw")
    recs = be.generate([_spec(0)])
    r = recs[0]
    assert r.parse_status is ParseStatus.PARSE_ERROR  # infra failure -> empty parse
    assert "boom" in (tmp_path / "raw").glob("*.stderr.txt").__iter__().__next__().read_text()


def test_generate_empty_stdout_is_parse_error(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="empty")
    model = _fake_model_file(tmp_path)
    be = LlamaCppBackend(_model(), _decoding(), _runtime(cli, model))
    r = be.generate([_spec(0)])[0]
    assert r.parse_status is ParseStatus.PARSE_ERROR


def test_generate_malformed_reasoning_is_flagged(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="malformed")
    model = _fake_model_file(tmp_path)
    be = LlamaCppBackend(_model(), _decoding(), _runtime(cli, model))
    r = be.generate([_spec(0)])[0]
    assert r.reasoning_span_status is ReasoningSpanStatus.MALFORMED
    assert r.parse_status is ParseStatus.NO_ANSWER  # never silently "no disclosure"
    assert "cut off mid-thought" in r.raw_output


def test_generate_timeout_is_recorded(tmp_path: Path) -> None:
    cli, _ = _make_fake_cli(tmp_path, mode="timeout")
    model = _fake_model_file(tmp_path)
    be = LlamaCppBackend(_model(), _decoding(), _runtime(cli, model, timeout_seconds=1.0))
    r = be.generate([_spec(0)])[0]
    assert r.truncated is True
    assert r.parse_status is ParseStatus.PARSE_ERROR


def test_no_content_dependent_retry(tmp_path: Path) -> None:
    # the backend invokes the CLI exactly once per spec, whatever the output.
    cli, argv_dump = _make_fake_cli(tmp_path, mode="malformed")  # an "undesirable" output
    model = _fake_model_file(tmp_path)
    be = LlamaCppBackend(_model(), _decoding(), _runtime(cli, model))
    be.generate([_spec(0), _spec(1)])
    n_invocations = len(argv_dump.read_text().strip().splitlines())
    assert n_invocations == 2  # 2 specs -> 2 calls, no re-roll of the malformed output


# ---- output cleaning (deterministic, versioned) ---------------------------------


def test_strip_cli_chrome_removes_banner_and_footer_keeps_think() -> None:
    raw = (
        "llama.cpp banner...\n"
        "> Question: capital of France?\n"
        "<think>\nreasoning\n</think>\n\nAnswer: \\boxed{A}\n"
        "\n[ Prompt: 9.0 t/s | Generation: 4.0 t/s ]\n\nExiting...\n"
    )
    out = strip_cli_chrome(raw, prompt="Question: capital of France?")
    assert "<think>" in out and "\\boxed{A}" in out
    assert "banner" not in out and "Exiting" not in out and "t/s" not in out


def test_strip_cli_chrome_no_chrome_is_identity() -> None:
    raw = "<think>x</think>\n\\boxed{C}"
    assert strip_cli_chrome(raw, prompt="q") == raw


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
    assert rt.reasoning_format == "none" and rt.enable_thinking is True
    assert rt.n_ctx == 32768 and rt.n_gpu_layers == 99
    assert rt.expected_model_sha256 == (
        "061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a"
    )

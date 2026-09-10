"""Track-A llama.cpp backend -- NO real model, NO real llama-cli.

Tests exercise helpers directly, never an authorized production backend.

Every string here is a SYNTHETIC FIXTURE, not a model output.
"""

from __future__ import annotations

import dataclasses
import hashlib
import inspect
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
    RawInvocation,
    _atomic_write,
    _binary_version,
    _subprocess_invoke,
    artifact_stem,
    build_argv,
    clean_cli_output,
    load_llamacpp_runtime,
    parse_output_tokens,
    parse_version_output,
    record_from_invocation,
    verify_runtime_identity,
)
from clsm.track_a_run import RunNotAuthorizedError, RunToken

_PINNED_COMMIT = "5266f24da75dc449bd56cbed7addb9c8e4a6a73e"
_PINNED_BUILD = "10809"
_GGUF_SHA = "061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a"


# ---- synthetic fixtures ----------------------------------------------------------


def _fake_binary(tmp_path: Path, name: str = "fake-llama-cli") -> Path:
    p = tmp_path / name
    p.write_text("#!/bin/sh\necho fake\n", encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p


def _fake_model_file(tmp_path: Path, content: bytes = b"GGUF-fake") -> Path:
    m = tmp_path / "model.gguf"
    m.write_bytes(content)
    return m


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


def _runtime(binary: Path, model: Path, **kw) -> LlamaCppRuntime:
    """A runtime whose SHA/build are pinned to match the fake model + fake probe, unless
    a test overrides them to exercise a mismatch."""
    if "expected_model_sha256" not in kw:
        kw["expected_model_sha256"] = (
            hashlib.sha256(model.read_bytes()).hexdigest() if model.exists() else "0" * 64
        )
    kw.setdefault("expected_llama_cpp_build", _PINNED_BUILD)
    return LlamaCppRuntime(
        binary_path=str(binary), model_path=str(model), llama_cpp_commit=_PINNED_COMMIT, **kw
    )


class _FakeInvoker:
    """Records argv; returns a canned RawInvocation. NEVER runs a subprocess."""

    def __init__(self, mode: str = "ok") -> None:
        self.mode = mode
        self.calls: list[list[str]] = []

    def __call__(self, argv: list[str], *, timeout: float) -> RawInvocation:
        self.calls.append(list(argv))
        seed = argv[argv.index("-s") + 1] if "-s" in argv else "?"
        n_pred = argv[argv.index("-n") + 1] if "-n" in argv else "256"
        if self.mode == "nonzero":
            return RawInvocation(argv, 3, "", "boom\n", 0.01, False)
        if self.mode == "empty":
            return RawInvocation(argv, 0, "", "", 0.01, False)
        if self.mode == "timeout":
            return RawInvocation(argv, -1, "", "\n[TIMEOUT]", timeout, True)
        if self.mode == "malformed":
            return RawInvocation(argv, 0, "<think>\ncut off mid-thought", "", 0.01, False)
        runs = n_pred if self.mode == "length" else "37"
        stdout = (
            f"<think>\nSynthetic reasoning for seed {seed}.\n</think>\n\n"
            "Answer: " + chr(92) + "boxed{B}\n"
            "\n[ Prompt: 10.0 t/s | Generation: 5.0 t/s ]\n\nExiting...\n"
        )
        stderr = (
            "ggml_metal_init: found device: FakeGPU\n"
            f"llama_perf_context_print: eval time = 123.45 ms / {runs} runs\n"
        )
        return RawInvocation(argv, 0, stdout, stderr, 0.05, False)


def _spec(seed: int = 0, condition: Condition = Condition.CONTROL) -> GenSpec:
    return GenSpec(
        experiment_id="track-a-test", item_id="mmlu:sub:7", dataset="mmlu",
        dataset_revision="c30699e8356da336a370243923dbaf21066bb9fe", subject="sub",
        question_sha256="0" * 64, condition=condition, prompt="a synthetic question",
        prompt_sha256="p" * 64, prompt_template_version="v1", correct_letter="A",
        cue_type=None, cue_version=None, hint_target_letter=None,
        sample_idx=seed, seed=seed,
    )


# ---- FIX 1: fail-closed run gate, NO public boolean bypass (D-065) --------------


def test_no_public_boolean_bypass_flag_exists() -> None:
    params = inspect.signature(LlamaCppBackend.__init__).parameters
    assert "for_testing_only" not in params
    assert not any("test" in p.lower() and params[p].annotation is bool for p in params)


@pytest.mark.parametrize("token", [None, True, False, 1, object(), "authorized"])
def test_invalid_token_fails_before_io(tmp_path: Path, token) -> None:
    rt = _runtime(tmp_path / "missing", tmp_path / "missing.gguf")
    with pytest.raises(RunNotAuthorizedError):
        LlamaCppBackend(_model(), _decoding(), rt, token)


def test_no_test_authorization_route() -> None:
    assert not hasattr(RunToken, "for_synthetic_test")
    assert "for_synthetic_test_only" not in RunToken.__dataclass_fields__
    params = inspect.signature(LlamaCppBackend).parameters
    for name in ("invoker", "version_probe", "test_mode", "skip_auth", "unsafe"):
        assert name not in params


@pytest.mark.parametrize("method", ["generate", "invoke_once"])
@pytest.mark.parametrize("token", [None, True, False, 1, object(), "authorized"])
def test_execution_rechecks_gate(method, token) -> None:
    # Deliberately uninitialized object: rejection must precede all runtime access.
    be = object.__new__(LlamaCppBackend)
    be.run_token = token
    with pytest.raises(RunNotAuthorizedError):
        if method == "generate":
            be.generate([_spec()])
        else:
            be.invoke_once("synthetic", seed=0)


def test_no_extra_args_escape_hatch() -> None:
    fields = {f.name for f in dataclasses.fields(LlamaCppRuntime)}
    assert "extra_args" not in fields
    with pytest.raises(TypeError):
        LlamaCppRuntime(
            binary_path="x", model_path="y", llama_cpp_commit=_PINNED_COMMIT,
            extra_args=("--rope-freq-base", "1e6"),
        )


# ---- FIX 2: llama.cpp identity verification FAILS CLOSED (D-065) ----------------


def _version_script(tmp_path: Path, body: str) -> Path:
    src = f"#!{Path(os.sys.executable)}\nimport sys\n{body}\n"
    p = tmp_path / "verscript"
    p.write_text(src, encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p


def test_binary_version_parses_a_valid_string(tmp_path: Path) -> None:
    p = _version_script(
        tmp_path,
        'sys.stderr.write("version: 0.4.0-dev (build 10809, commit 5266f24da75dc4)\\n")',
    )
    vs, build, commit = _binary_version(p)
    assert build == "10809" and commit == "5266f24da75dc4" and "0.4.0" in vs


def test_binary_version_subprocess_failure_raises(tmp_path: Path) -> None:
    with pytest.raises(LlamaCppInvocationError, match="could not run"):
        _binary_version(tmp_path / "does-not-exist")


def test_binary_version_nonzero_exit_raises(tmp_path: Path) -> None:
    p = _version_script(tmp_path, 'sys.stderr.write("nope\\n"); sys.exit(2)')
    with pytest.raises(LlamaCppInvocationError, match="exited 2"):
        _binary_version(p)


def test_binary_version_empty_output_raises(tmp_path: Path) -> None:
    p = _version_script(tmp_path, "sys.exit(0)")
    with pytest.raises(LlamaCppInvocationError, match="no output"):
        _binary_version(p)


def test_binary_version_unparsable_raises(tmp_path: Path) -> None:
    p = _version_script(tmp_path, 'sys.stdout.write("hello world, not a version\\n")')
    with pytest.raises(LlamaCppInvocationError, match="does not match"):
        _binary_version(p)


def test_binary_version_missing_build_raises(tmp_path: Path) -> None:
    p = _version_script(tmp_path, 'sys.stdout.write("version: 0.4.0 (commit 5266f24da)\\n")')
    with pytest.raises(LlamaCppInvocationError, match="does not match"):
        _binary_version(p)


def test_binary_version_missing_commit_raises(tmp_path: Path) -> None:
    p = _version_script(tmp_path, 'sys.stdout.write("version: 0.4.0 (build 10809)\\n")')
    with pytest.raises(LlamaCppInvocationError, match="does not match"):
        _binary_version(p)


@pytest.mark.parametrize("body, update, error", [
    ('print("malformed")', {}, "does not match"),
    ('pass', {}, "no output"),
    ('sys.exit(2)', {}, "exited 2"),
    ('print("version: 0.4.0 (build 10809, commit deadbeef)")', {}, "commit mismatch"),
    ('print("version: 0.4.0 (build 999, commit 5266f24da)")', {}, "build mismatch"),
    (None, {"expected_model_sha256": None}, "not pinned"),
    (None, {"expected_model_sha256": "0" * 64}, "SHA-256 mismatch"),
    (None, {"expected_llama_cpp_build": None}, "not pinned"),
    (None, {"expected_model_bytes": 999}, "size mismatch"),
])
def test_verify_runtime_fails_closed(tmp_path, body, update, error) -> None:
    cli = _version_script(tmp_path, body or
        'print("version: 0.4.0 (build 10809, commit 5266f24da)")')
    model = _fake_model_file(tmp_path)
    with pytest.raises(LlamaCppInvocationError, match=error):
        verify_runtime_identity(_runtime(cli, model, **update))


def test_verify_runtime_valid_identity_passes(tmp_path) -> None:
    cli = _version_script(tmp_path,
        'print("version: 0.4.0 (build 10809, commit 5266f24da)")')
    assert verify_runtime_identity(_runtime(cli, _fake_model_file(tmp_path)))[1] == "10809"


@pytest.mark.parametrize("missing", ["binary", "model"])
def test_verify_missing_file(tmp_path, missing) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    (cli if missing == "binary" else model).unlink()
    with pytest.raises(LlamaCppInvocationError, match="not found"):
        verify_runtime_identity(_runtime(cli, model))


# ---- command construction --------------------------------------------------------


def test_build_argv_has_every_explicit_knob(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    argv = build_argv(_decoding(), _runtime(cli, model), "hello world", seed=42)
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
    assert "--no-perf" not in argv  # D-053
    assert all(isinstance(a, str) for a in argv)


def test_argv_paths_with_spaces_are_one_token(tmp_path: Path) -> None:
    d = tmp_path / "dir with spaces"
    d.mkdir()
    cli, model = _fake_binary(d), _fake_model_file(d)
    argv = build_argv(_decoding(), _runtime(cli, model), "q", seed=0)
    assert argv[argv.index("-m") + 1] == str(model)


def test_enable_thinking_false_adds_reasoning_off(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    argv = build_argv(_decoding(), _runtime(cli, model, enable_thinking=False), "q", seed=0)
    assert argv[argv.index("--reasoning") + 1] == "off"


# ---- generation outcomes -------------------------------------------------------


@pytest.mark.parametrize("mode, reason, status", [
    ("ok", StopReason.EOS, ParseStatus.VALID),
    ("length", StopReason.LENGTH, ParseStatus.VALID),
    ("nonzero", StopReason.NONZERO_EXIT, ParseStatus.PARSE_ERROR),
    ("empty", StopReason.UNKNOWN, ParseStatus.PARSE_ERROR),
    ("malformed", StopReason.UNKNOWN, ParseStatus.NO_ANSWER),
    ("timeout", StopReason.TIMEOUT, ParseStatus.PARSE_ERROR),
])
def test_record_from_synthetic_invocation(mode, reason, status) -> None:
    raw = _FakeInvoker(mode)(["fixture", "-s", "0", "-n", "256"], timeout=1)
    rec = record_from_invocation(_spec(), raw, _model(), _decoding())
    assert rec.raw_output == raw.stdout
    assert rec.stop_reason is reason and rec.parse_status is status
    assert rec.truncated == (reason in (StopReason.LENGTH, StopReason.TIMEOUT))
    if mode == "ok":
        assert rec.extracted_answer == "B" and rec.n_output_tokens == 37
        assert rec.reasoning_span_status is ReasoningSpanStatus.PRESENT
    if mode == "malformed":
        assert rec.reasoning_span_status is ReasoningSpanStatus.MALFORMED


@pytest.mark.parametrize("body, code, timed_out", [
    ('print("synthetic output"); sys.stderr.write("fixture error")', 0, False),
    ('sys.exit(3)', 3, False),
    ('import time; time.sleep(2)', -1, True),
])
def test_subprocess_directly_with_temporary_script(tmp_path, body, code, timed_out) -> None:
    script = _version_script(tmp_path, body)
    raw = _subprocess_invoke([str(script)], timeout=0.2 if timed_out else 10)
    assert raw.returncode == code and raw.timed_out is timed_out
    if code == 0:
        assert raw.stdout == "synthetic output\n" and raw.stderr == "fixture error"


def test_atomic_persistence_collision_and_replay(tmp_path) -> None:
    path = tmp_path / "fixture.stdout.txt"
    _atomic_write(path, "synthetic")
    _atomic_write(path, "synthetic")
    with pytest.raises(LlamaCppInvocationError, match="refusing to overwrite"):
        _atomic_write(path, "different")
    assert path.read_text() == "synthetic"
    assert not list(tmp_path.glob("*.tmp"))


# ---- output cleaning (deterministic, anchored, versioned) -----------------------


def test_clean_cli_output_strips_only_anchored_banner_and_footer() -> None:
    raw = (
        "build: 10809 (5266f24d)\nmain: llama backend init\n"
        "available commands:\n  /help\n  /clear\n\n"
        "<think>\nreasoning\n</think>\n\nAnswer: \\boxed{A}\n"
        "\n[ Prompt: 9.0 t/s | Generation: 4.0 t/s ]\n\nExiting...\n"
    )
    out, changed = clean_cli_output(raw)
    assert changed is True
    assert "<think>" in out and "\\boxed{A}" in out
    assert "available commands" not in out and "Exiting" not in out and "t/s" not in out


def test_clean_cli_output_no_chrome_is_identity() -> None:
    raw = "<think>x</think>\n\\boxed{C}"
    assert clean_cli_output(raw) == (raw, False)


def test_clean_cli_output_preserves_blockquote_answer_lines() -> None:
    raw = "> (B) Paris\n> also consider (C)\n\\boxed{B}\n"
    assert clean_cli_output(raw)[0] == raw


def test_clean_cli_output_preserves_ansi_and_multiple_think_blocks() -> None:
    raw = "\x1b[32m<think>one</think>\x1b[0m\n<think>two</think>\n\\boxed{D}"
    assert clean_cli_output(raw)[0] == raw


def test_parse_output_tokens_reads_perf_block() -> None:
    assert parse_output_tokens("llama_perf: eval time = 12.0 ms / 44 runs\n") == 44
    assert parse_output_tokens("no perf here") is None


# ---- runtime loader -----------------------------------------------------------


def test_load_llamacpp_runtime_from_committed_yaml_needs_paths(monkeypatch) -> None:
    monkeypatch.delenv("CLSM_LLAMA_CLI", raising=False)
    monkeypatch.delenv("CLSM_QWEN_GGUF", raising=False)
    with pytest.raises(LlamaCppInvocationError, match="not set"):
        load_llamacpp_runtime("configs/track_a_pilot/runtime_llamacpp.yaml")


def test_load_llamacpp_runtime_with_env(tmp_path: Path, monkeypatch) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    monkeypatch.setenv("CLSM_LLAMA_CLI", str(cli))
    monkeypatch.setenv("CLSM_QWEN_GGUF", str(model))
    rt = load_llamacpp_runtime("configs/track_a_pilot/runtime_llamacpp.yaml")
    assert rt.llama_cpp_commit == _PINNED_COMMIT
    assert rt.expected_llama_cpp_build == _PINNED_BUILD
    assert rt.reasoning_format == "none" and rt.enable_thinking is True
    assert rt.n_ctx == 32768 and rt.n_gpu_layers == 99
    assert rt.expected_model_sha256 == _GGUF_SHA


def test_artifact_names_distinguish_specs() -> None:
    specs = [_spec(0), _spec(1), _spec(0, Condition.TREATMENT)]
    assert len({artifact_stem(spec) for spec in specs}) == 3
    assert artifact_stem(specs[0]) == "track-a-test__mmlu_sub_7__control__s0__k0__a1"
    assert artifact_stem(specs[0], attempt=2).endswith("__a2")


@pytest.mark.parametrize("text", ["", "malformed", "version: 0.4.0 (build 10809)",
    "version: 0.4.0 (commit 5266f24da)"])
def test_version_parser_rejects_incomplete_identity(text) -> None:
    with pytest.raises(LlamaCppInvocationError):
        parse_version_output(text)


def test_version_parser_accepts_pinned_identity() -> None:
    text = f"version: 0.4.0 (build {_PINNED_BUILD}, commit {_PINNED_COMMIT})"
    assert parse_version_output(text) == (text, _PINNED_BUILD, _PINNED_COMMIT)


def test_uninitialized_token_and_subclass_cannot_authorize(tmp_path) -> None:
    class PretendToken(RunToken):
        pass

    for token in (object.__new__(RunToken), object.__new__(PretendToken)):
        with pytest.raises(RunNotAuthorizedError):
            LlamaCppBackend(_model(), _decoding(),
                _runtime(tmp_path / "missing", tmp_path / "missing.gguf"), token)


def test_missing_token_argument_fails(tmp_path) -> None:
    with pytest.raises(TypeError, match="run_token"):
        LlamaCppBackend(_model(), _decoding(),
            _runtime(tmp_path / "missing", tmp_path / "missing.gguf"))


def test_runtime_verification_option_cannot_bypass_authorization(tmp_path) -> None:
    with pytest.raises(RunNotAuthorizedError):
        LlamaCppBackend(_model(), _decoding(),
            _runtime(tmp_path / "missing", tmp_path / "missing.gguf"), None,
            verify_runtime=False)

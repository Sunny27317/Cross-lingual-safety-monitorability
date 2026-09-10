"""Track-A llama.cpp backend -- NO real model, NO real llama-cli.

Architecture (DECISION_LOG D-065): the production ``LlamaCppBackend`` always requires a
:class:`~clsm.track_a_run.RunToken` and has **no public boolean bypass**. Synthetic unit
tests pass ``RunToken.for_synthetic_test()`` together with an injected fake ``invoker``
and fake ``version_probe`` -- such a backend is structurally incapable of driving the
real ``llama-cli`` or the real GGUF. The ``_binary_version`` parser (the REAL version
probe) is unit-tested directly against a tiny synthetic ``--version``-only script.

Every string here is a SYNTHETIC FIXTURE, not a model output.
"""

from __future__ import annotations

import dataclasses
import hashlib
import inspect
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
    RawInvocation,
    _binary_version,
    clean_cli_output,
    load_llamacpp_runtime,
    parse_output_tokens,
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


def _ok_probe(_binary: Path) -> tuple[str, str, str]:
    return (
        f"version: 0.4.0-dev (build {_PINNED_BUILD}, commit {_PINNED_COMMIT})",
        _PINNED_BUILD,
        _PINNED_COMMIT,
    )


def _probe_returning(vs: str, build: str, commit: str):
    def p(_b: Path) -> tuple[str, str, str]:
        return vs, build, commit
    return p


def _probe_raising(msg: str):
    def p(_b: Path) -> tuple[str, str, str]:
        raise LlamaCppInvocationError(msg)
    return p


def _backend(
    model: ModelConfig, decoding: DecodingConfig, rt: LlamaCppRuntime, *,
    invoker: _FakeInvoker | None = None, version_probe=None, **kw
) -> LlamaCppBackend:
    """A synthetic-test backend: RunToken.for_synthetic_test() + injected fakes."""
    return LlamaCppBackend(
        model, decoding, rt, RunToken.for_synthetic_test(),
        invoker=invoker if invoker is not None else _FakeInvoker(),
        version_probe=version_probe if version_probe is not None else _ok_probe,
        **kw,
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


# ---- FIX 1: fail-closed run gate, NO public boolean bypass (D-065) --------------


def test_no_public_boolean_bypass_flag_exists() -> None:
    params = inspect.signature(LlamaCppBackend.__init__).parameters
    assert "for_testing_only" not in params
    assert not any("test" in p.lower() and params[p].annotation is bool for p in params)


def test_construction_without_a_runtoken_fails(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    rt = _runtime(cli, model)
    with pytest.raises(RunNotAuthorizedError, match="RunToken"):
        LlamaCppBackend(_model(), _decoding(), rt, True)  # a bool is not a RunToken
    with pytest.raises(RunNotAuthorizedError, match="RunToken"):
        LlamaCppBackend(_model(), _decoding(), rt, object())  # arbitrary object


def test_runtoken_cannot_be_constructed_directly() -> None:
    with pytest.raises(RunNotAuthorizedError, match="only be created"):
        RunToken(scientific_hash="x", reviewer="x", reviewed_utc="x", manifest_status={})


def test_synthetic_token_requires_injected_fakes(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    rt = _runtime(cli, model)
    with pytest.raises(RunNotAuthorizedError, match="injected"):
        LlamaCppBackend(_model(), _decoding(), rt, RunToken.for_synthetic_test())
    with pytest.raises(RunNotAuthorizedError, match="injected"):
        LlamaCppBackend(
            _model(), _decoding(), rt, RunToken.for_synthetic_test(), invoker=_FakeInvoker()
        )  # probe still missing


def test_generate_rechecks_the_gate_not_only_init(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    be.run_token = "not a token"  # tamper after construction
    with pytest.raises(RunNotAuthorizedError):
        be.generate([_spec(0)])


def test_behavior_only_specs_cannot_bypass_the_gate(tmp_path: Path) -> None:
    """A backend cannot be pointed at the real runtime with behaviour-only specs: a
    synthetic token forces injected fakes, and a real token cannot be forged."""
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    rt = _runtime(cli, model)
    # cannot combine a (forged) plain object token with real execution
    with pytest.raises(RunNotAuthorizedError):
        LlamaCppBackend(_model(), _decoding(), rt, object(), invoker=_FakeInvoker())


def test_synthetic_backend_generate_works_without_real_auth(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    recs = be.generate([_spec(0)])
    assert len(recs) == 1 and recs[0].extracted_answer == "B" and recs[0].is_mock is False


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


def test_verify_runtime_fails_closed_when_probe_raises(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    with pytest.raises(LlamaCppInvocationError, match="boom-probe"):
        _backend(_model(), _decoding(), _runtime(cli, model),
                 version_probe=_probe_raising("boom-probe"))


def test_verify_runtime_wrong_commit_raises(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    with pytest.raises(LlamaCppInvocationError, match="commit mismatch"):
        _backend(_model(), _decoding(), _runtime(cli, model),
                 version_probe=_probe_returning("v", _PINNED_BUILD, "deadbeefdeadbeef"))


def test_verify_runtime_wrong_build_raises(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    with pytest.raises(LlamaCppInvocationError, match="build mismatch"):
        _backend(_model(), _decoding(), _runtime(cli, model),
                 version_probe=_probe_returning("v", "99999", _PINNED_COMMIT))


def test_verify_runtime_requires_pinned_sha(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    rt = _runtime(cli, model, expected_model_sha256=None)
    with pytest.raises(LlamaCppInvocationError, match="expected_model_sha256 is not pinned"):
        _backend(_model(), _decoding(), rt)


def test_verify_runtime_requires_pinned_build(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    rt = _runtime(cli, model, expected_llama_cpp_build=None)
    with pytest.raises(LlamaCppInvocationError, match="expected_llama_cpp_build is not pinned"):
        _backend(_model(), _decoding(), rt)


def test_verify_runtime_valid_identity_passes(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    assert be.identity_verified is True and be.model_sha256_verified is True


def test_missing_binary_raises(tmp_path: Path) -> None:
    model = _fake_model_file(tmp_path)
    with pytest.raises(LlamaCppInvocationError, match="binary not found"):
        _backend(_model(), _decoding(), _runtime(tmp_path / "nope", model))


def test_missing_model_raises(tmp_path: Path) -> None:
    cli = _fake_binary(tmp_path)
    with pytest.raises(LlamaCppInvocationError, match="model GGUF not found"):
        _backend(_model(), _decoding(), _runtime(cli, tmp_path / "nope.gguf"))


def test_model_size_mismatch_raises(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path, b"x" * 10)
    with pytest.raises(LlamaCppInvocationError, match="size mismatch"):
        _backend(_model(), _decoding(), _runtime(cli, model, expected_model_bytes=999))


def test_model_sha256_mismatch_raises(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    with pytest.raises(LlamaCppInvocationError, match="SHA-256 mismatch"):
        _backend(_model(), _decoding(), _runtime(cli, model, expected_model_sha256="0" * 64))


# ---- command construction --------------------------------------------------------


def test_build_argv_has_every_explicit_knob(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
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
    assert "--no-perf" not in argv  # D-053
    assert all(isinstance(a, str) for a in argv)


def test_argv_paths_with_spaces_are_one_token(tmp_path: Path) -> None:
    d = tmp_path / "dir with spaces"
    d.mkdir()
    cli, model = _fake_binary(d), _fake_model_file(d)
    be = _backend(_model(), _decoding(), _runtime(cli, model))
    argv = be.build_argv("q", seed=0)
    assert argv[argv.index("-m") + 1] == str(model)


def test_enable_thinking_false_adds_reasoning_off(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model, enable_thinking=False))
    argv = be.build_argv("q", seed=0)
    assert argv[argv.index("--reasoning") + 1] == "off"


# ---- generation outcomes -------------------------------------------------------


def test_generate_ok_produces_record_with_raw_preserved(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    raw_dir = tmp_path / "raw"
    inv = _FakeInvoker("ok")
    be = _backend(_model(), _decoding(), _runtime(cli, model), invoker=inv, raw_dir=raw_dir)
    recs = be.generate([_spec(0), _spec(1)])
    assert len(recs) == 2
    r = recs[0]
    assert r.is_mock is False
    assert r.parse_status is ParseStatus.VALID and r.extracted_answer == "B"
    assert r.reasoning_span_status is ReasoningSpanStatus.PRESENT
    assert "[ Prompt:" in r.raw_output and "<think>" in r.raw_output
    assert r.n_output_tokens == 37 and r.stop_reason is StopReason.EOS and r.truncated is False
    # exactly one invocation per spec, no retry, no version-probe leak into the invoker
    assert len(inv.calls) == 2
    assert [c[c.index("-s") + 1] for c in inv.calls] == ["0", "1"]
    metas = sorted(raw_dir.glob("*.meta.json"))
    assert len(metas) == 2
    meta = json.loads(metas[0].read_text())
    assert meta["runtime"]["llama_cpp_commit"] == _PINNED_COMMIT
    assert meta["invocation"]["returncode"] == 0
    assert meta["spec"]["attempt"] == 1
    assert meta["result"]["stop_reason"] == "EOS"
    assert meta["result"]["retry_policy"] == "zero-retry/D-054"
    assert meta["authorization"]["synthetic_test_token"] is True
    assert not list(raw_dir.glob("*.tmp"))
    assert any("track-a-test__mmlu_sub_7__control__s0__k0__a1" in m.name for m in metas)


def test_generate_length_exhaustion_is_truncated(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model), invoker=_FakeInvoker("length"))
    r = be.generate([_spec(0)])[0]
    assert r.n_output_tokens == 256 and r.stop_reason is StopReason.LENGTH and r.truncated is True


def test_generate_nonzero_exit_is_recorded_not_raised(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model),
                  invoker=_FakeInvoker("nonzero"), raw_dir=tmp_path / "raw")
    r = be.generate([_spec(0)])[0]
    assert r.parse_status is ParseStatus.PARSE_ERROR
    assert r.stop_reason is StopReason.NONZERO_EXIT
    assert "boom" in next((tmp_path / "raw").glob("*.stderr.txt")).read_text()


def test_generate_empty_stdout_is_parse_error_and_unknown(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model), invoker=_FakeInvoker("empty"))
    r = be.generate([_spec(0)])[0]
    assert r.parse_status is ParseStatus.PARSE_ERROR
    assert r.stop_reason is StopReason.UNKNOWN and r.truncated is False


def test_generate_malformed_reasoning_is_flagged(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model), invoker=_FakeInvoker("malformed"))
    r = be.generate([_spec(0)])[0]
    assert r.reasoning_span_status is ReasoningSpanStatus.MALFORMED
    assert r.parse_status is ParseStatus.NO_ANSWER
    assert "cut off mid-thought" in r.raw_output
    assert r.stop_reason is StopReason.UNKNOWN  # never inferred from a missing answer


def test_generate_timeout_is_recorded(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    be = _backend(_model(), _decoding(), _runtime(cli, model, timeout_seconds=1.0),
                  invoker=_FakeInvoker("timeout"))
    r = be.generate([_spec(0)])[0]
    assert r.truncated is True and r.stop_reason is StopReason.TIMEOUT
    assert r.parse_status is ParseStatus.PARSE_ERROR


def test_no_content_dependent_retry(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    inv = _FakeInvoker("malformed")
    be = _backend(_model(), _decoding(), _runtime(cli, model), invoker=inv)
    be.generate([_spec(0), _spec(1)])
    assert len(inv.calls) == 2  # 2 specs -> 2 calls, no re-roll of the malformed output


# ---- persistence: never overwrite ----------------------------------------------


def test_persist_refuses_to_overwrite_a_differing_artifact(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    raw_dir = tmp_path / "raw"
    be = _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir)
    be.generate([_spec(0)])
    next(raw_dir.glob("*.stdout.txt")).write_text("DIFFERENT", encoding="utf-8")
    with pytest.raises(LlamaCppInvocationError, match="refusing to overwrite"):
        _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir).generate([_spec(0)])


def test_persist_idempotent_replay_is_allowed(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    raw_dir = tmp_path / "raw"
    _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir).generate([_spec(0)])
    stdout_before = next(raw_dir.glob("*.stdout.txt")).read_text()
    next(raw_dir.glob("*.meta.json")).unlink()  # timestamp would collide; isolate the check
    _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir).generate([_spec(0)])
    assert next(raw_dir.glob("*.stdout.txt")).read_text() == stdout_before


def test_distinct_specs_get_distinct_filenames(tmp_path: Path) -> None:
    cli, model = _fake_binary(tmp_path), _fake_model_file(tmp_path)
    raw_dir = tmp_path / "raw"
    be = _backend(_model(), _decoding(), _runtime(cli, model), raw_dir=raw_dir)
    be.generate([
        _spec(0, Condition.CONTROL), _spec(1, Condition.CONTROL), _spec(0, Condition.TREATMENT),
    ])
    stdouts = sorted(p.name for p in raw_dir.glob("*.stdout.txt"))
    assert len(stdouts) == 3 and len(set(stdouts)) == 3


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

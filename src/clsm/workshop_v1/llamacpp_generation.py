"""Workshop-v1 generation over the pinned local ``llama-cli`` runtime.

Deliberately reuses Track-A's already-verified, fail-closed low-level primitives
(``clsm.track_a_backend``: runtime identity verification, argv construction, the
subprocess invocation wrapper) rather than reimplementing them. It does **not** reuse
Track-A's ``RunToken``/manifest authorization apparatus — that machinery is scoped to
Track-A's own English-pilot scientific config; Workshop-v1 has its own authorization
layer (``clsm.workshop_v1.preflight`` / ``Study.require_generation_design``), and a
non-scientific smoke test needs neither gate.

**This module issues no scientific authorization of its own.** Calling
``generate_and_parse`` with real weights and a real prompt performs a real local
inference call — callers (the Workshop-v1 executor, once it exists) are responsible for
only ever doing so under an authorized ``Study``/``Population``/review, exactly as
``preflight.py`` already requires. Direct use for a synthetic/engineering smoke test
(this session's Phases 3/4/11) is expected and does not touch that gate at all.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import Literal

from clsm.config import DecodingConfig, ModelConfig
from clsm.track_a_backend import (
    LlamaCppInvocationError,
    LlamaCppRuntime,
    RawInvocation,
    build_argv,
    parse_output_tokens,
    verify_runtime_identity,
)
from clsm.workshop_v1.completion import PINNED_COMMIT, separate_completion
from clsm.workshop_v1.output_parsing import ParsedOutput, parse_gemma_output, parse_qwen_output
from clsm.workshop_v1.prompt_contract import Condition, Language, ModelId, render_prompt

ParserKind = Literal["qwen_think", "prompted_final_answer", "gemma_final_answer"]


@dataclass(frozen=True)
class WorkshopInvocation(RawInvocation):
    """RAW_RUNTIME_OUTPUT (stdout) and GENERATED_COMPLETION are distinct evidence."""

    generated_completion: str | None
    boundary_policy: str
    separation_error: str | None


@dataclass(frozen=True)
class WorkshopGeneratorSpec:
    """Everything needed to invoke one of the two frozen generators once."""

    model_id: ModelId
    parser: ParserKind
    model: ModelConfig
    decoding: DecodingConfig
    runtime: LlamaCppRuntime


def verify_generator_runtime(spec: WorkshopGeneratorSpec) -> tuple[str, str]:
    """Fail-closed identity check (binary/model exist, size+SHA-256 pinned and
    matching, ``llama-cli --version`` build/commit matching) — no generation without
    this passing. Reused verbatim from Track-A (D-043/D-052/D-065)."""
    if spec.model_id == "qwen3-1.7b" and spec.parser != "prompted_final_answer":
        raise LlamaCppInvocationError(
            "authoritative Workshop-v1 Qwen path requires D5 prompted_final_answer parser"
        )
    return verify_runtime_identity(spec.runtime)


def _decode_or_empty(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="surrogateescape")
    return value or ""


def _subprocess_invoke(argv: list[str], *, timeout: float) -> RawInvocation:
    """Same shape as ``clsm.track_a_backend``'s internal invoker (kept as a local,
    public-surface copy rather than importing a leading-underscore symbol across
    modules); behavior is identical: one attempt, wall-clock timing, no retry."""
    t0 = time.perf_counter()
    timed_out = False
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=timeout, check=False)
        stdout, stderr, rc = _decode_or_empty(proc.stdout), _decode_or_empty(proc.stderr), proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = _decode_or_empty(exc.stdout)
        stderr = _decode_or_empty(exc.stderr)
        stderr += "\n[TIMEOUT]"
        rc = -1
    return RawInvocation(
        argv=argv, returncode=rc, stdout=stdout, stderr=stderr,
        wall_clock_seconds=time.perf_counter() - t0, timed_out=timed_out,
    )


def invoke_once(spec: WorkshopGeneratorSpec, prompt: str, *, seed: int) -> WorkshopInvocation:
    """One raw llama-cli invocation. No retries (matches the existing zero-retry
    policy, D-054) — a caller wanting a k-sample cell issues k separate calls with
    k distinct seeds, each recorded independently, failures included."""
    if (
        spec.runtime.llama_cpp_commit != PINNED_COMMIT
        or spec.runtime.expected_llama_cpp_build != "10809"
    ):
        raise LlamaCppInvocationError("completion protocol requires pinned b10809 runtime")
    argv = build_argv(spec.decoding, spec.runtime, prompt, seed=seed)
    raw = _subprocess_invoke(argv, timeout=spec.runtime.timeout_seconds)
    completion = separate_completion(raw.stdout, prompt=prompt, policy="llama-cli-b10809")
    return WorkshopInvocation(
        argv=raw.argv, returncode=raw.returncode, stdout=raw.stdout, stderr=raw.stderr,
        wall_clock_seconds=raw.wall_clock_seconds, timed_out=raw.timed_out,
        generated_completion=completion.generated_completion,
        boundary_policy=completion.boundary_policy, separation_error=completion.error,
    )


def parse_raw_invocation(
    spec: WorkshopGeneratorSpec, raw: WorkshopInvocation, *, language: Language
) -> ParsedOutput:
    n_tokens = parse_output_tokens(raw.stderr)
    kwargs = dict(
        raw_output=raw.generated_completion or "",
        language=language,
        returncode=raw.returncode if raw.separation_error is None else -1,
        timed_out=raw.timed_out,
        n_output_tokens=n_tokens,
        max_new_tokens=spec.decoding.max_new_tokens,
    )
    if spec.parser == "qwen_think":
        return parse_qwen_output(**kwargs)  # type: ignore[arg-type]
    return parse_gemma_output(**kwargs)  # type: ignore[arg-type]


def generate_and_parse(
    spec: WorkshopGeneratorSpec,
    *,
    language: Language,
    condition: Condition,
    item_text: str,
    target_letter: str | None,
    seed: int,
) -> tuple[str, WorkshopInvocation, ParsedOutput]:
    """Render the frozen prompt, invoke the model once, parse the result.

    Returns ``(prompt, raw_invocation, parsed)`` so the caller can persist every piece
    of provenance the frozen output contract requires (Phase 7/9) — this function does
    not write anything to disk itself.
    """
    prompt = render_prompt(
        model_id=spec.model_id,
        language=language,
        condition=condition,
        item_text=item_text,
        target_letter=target_letter,
    )
    raw = invoke_once(spec, prompt, seed=seed)
    parsed = parse_raw_invocation(spec, raw, language=language)
    return prompt, raw, parsed


def smoke_test(
    spec: WorkshopGeneratorSpec, *, prompt: str, seed: int = 0
) -> tuple[WorkshopInvocation, ParsedOutput]:
    """Non-scientific engineering check: does the runtime load this model and produce
    *any* parseable output for a trivial prompt? Verifies identity first (fail-closed);
    raises ``LlamaCppInvocationError`` on any identity mismatch rather than attempting
    generation against an unverified binary/model."""
    verify_generator_runtime(spec)
    raw = invoke_once(spec, prompt, seed=seed)
    parsed = parse_raw_invocation(spec, raw, language="en")
    return raw, parsed


__all__ = [
    "LlamaCppInvocationError",
    "ParserKind",
    "WorkshopGeneratorSpec",
    "WorkshopInvocation",
    "generate_and_parse",
    "invoke_once",
    "parse_raw_invocation",
    "smoke_test",
    "verify_generator_runtime",
]

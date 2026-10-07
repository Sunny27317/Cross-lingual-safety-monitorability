"""Frozen local runtime calls and operational telemetry; no study scheduler."""

from __future__ import annotations

import os
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from clsm.track_a_backend import LlamaCppRuntime, verify_runtime_identity
from clsm.workshop_v1.completion import PINNED_COMMIT, separate_completion
from clsm.workshop_v1.config import ModelSpec
from clsm.workshop_v1.llamacpp_generation import _subprocess_invoke


def portable_path(value: str) -> str:
    """Resolve legacy laptop paths through optional portable environment roots.

    The frozen YAML remains byte-identical. This only changes where an already
    frozen artifact is found on a different machine.
    """
    replacements = {
        "/Users/sullah1/models/clsm": os.environ.get("CLSM_MODEL_ROOT"),
        "/Users/sullah1/tools/llama.cpp": os.environ.get("CLSM_LLAMA_CPP_ROOT"),
    }
    for old, new in replacements.items():
        if new and value.startswith(old):
            return str(Path(new) / value[len(old):].lstrip("/"))
    return os.path.expanduser(os.path.expandvars(value))


def runtime_for(spec: ModelSpec) -> LlamaCppRuntime:
    if spec.blockers() or spec.local_path is None or spec.runtime_binary is None:
        raise ValueError("incomplete local model specification")
    settings = spec.additional_settings
    assert settings is not None
    return LlamaCppRuntime(
        binary_path=portable_path(spec.runtime_binary), model_path=portable_path(spec.local_path),
        llama_cpp_commit=PINNED_COMMIT, expected_llama_cpp_build="10809",
        expected_model_sha256=spec.checkpoint_hash, expected_model_bytes=spec.size_bytes,
        n_ctx=int(settings["n_ctx"]), n_gpu_layers=int(settings["n_gpu_layers"]),
        timeout_seconds=float(settings["timeout_seconds"]),
    )


def frozen_argv(spec: ModelSpec, prompt: str, seed: int) -> list[str]:
    r = runtime_for(spec)
    d, settings = spec.decoding, spec.additional_settings
    assert d is not None and settings is not None
    if d.stop_sequences or settings["system_prompt"] is not None:
        raise ValueError("frozen runtime permits only natural EOT and no system message")
    if settings.get("force_think_prefix"):
        raise ValueError("a generated reasoning prefix cannot be fabricated")
    # Workshop-specific schema permits the frozen greedy Falcon judge. Track-A's
    # generator DecodingConfig prohibition of greedy is intentionally unchanged.
    return [
        str(r.resolved_binary), "-m", str(r.resolved_model), "-p", prompt, "-st",
        "--reasoning-format", str(settings["reasoning_format"]),
        "-n", str(d.max_new_tokens), "-c", str(r.n_ctx), "-s", str(seed),
        "--temp", str(d.temperature), "--top-p", str(d.top_p), "--top-k", str(d.top_k),
        "--min-p", str(settings["min_p"]), "--presence-penalty", str(settings["presence_penalty"]),
        "--repeat-penalty", str(d.repetition_penalty), "-ngl", str(r.n_gpu_layers),
        "--no-warmup", "--simple-io", "--no-display-prompt", "--no-context-shift",
        "--log-verbosity", "4", "--log-colors", "off",
    ]


def telemetry(stderr: str, stdout: str, *, returncode: int, timed_out: bool, cap: int) -> dict[str, Any]:
    # Match generation evaluation, never the 'prompt eval time' substring. The
    # historical Track-A best-effort regex conflated those, so do not reuse it.
    evals = re.findall(
        r"(?<!prompt )eval time\s*=\s*([0-9.]+) ms\s*/\s*(\d+) (?:tokens|runs)"
        r"\s*\([0-9.]+ ms per token,\s*([0-9.]+) tokens per second\)", stderr
    )
    prompt = re.findall(r"prompt eval time\s*=\s*([0-9.]+) ms\s*/\s*(\d+) tokens", stderr)
    load = re.findall(r"load time\s*=\s*([0-9.]+) ms", stderr)
    rss = re.findall(r"(\d+)\s+maximum resident set size", stderr)
    tokens = int(evals[-1][1]) if evals else None
    reason = "UNKNOWN"
    if timed_out:
        reason = "TIMEOUT"
    elif returncode:
        reason = "NONZERO_EXIT"
    elif tokens is not None:
        reason = "LENGTH" if tokens >= cap else "EOS"
    return {
        "load_seconds": float(load[-1]) / 1000 if load else None,
        "generation_eval_seconds": float(evals[-1][0]) / 1000 if evals else None,
        "completion_tokens": tokens,
        "tokens_per_second": float(evals[-1][2]) if evals else None,
        "prompt_eval_seconds": float(prompt[-1][0]) / 1000 if prompt else None,
        "prompt_tokens": int(prompt[-1][1]) if prompt else None,
        "peak_resident_bytes": int(rss[-1]) if rss else None,
        "stop_reason": reason,
        "metric_source": "pinned llama.cpp eval logs; macOS /usr/bin/time -l RSS; null if absent",
    }


def run_local(spec: ModelSpec, prompt: str, *, seed: int) -> dict[str, Any]:
    """One attempt. Callers verify the pinned identity before their bounded run."""
    argv = frozen_argv(spec, prompt, seed)
    settings = spec.additional_settings
    assert settings is not None and spec.decoding is not None
    raw = _subprocess_invoke(["/usr/bin/time", "-l", *argv], timeout=float(settings["timeout_seconds"]))
    separated = separate_completion(raw.stdout, prompt=prompt, policy="llama-cli-b10809")
    metrics = telemetry(
        raw.stderr, raw.stdout, returncode=raw.returncode, timed_out=raw.timed_out,
        cap=spec.decoding.max_new_tokens,
    )
    return {
        "raw_runtime_output": raw.stdout, "raw_stderr": raw.stderr,
        "generated_completion": separated.generated_completion,
        "separation_error": separated.error, "boundary_policy": separated.boundary_policy,
        "invocation": asdict(raw), "wall_clock_seconds": raw.wall_clock_seconds,
        "runtime_success": raw.returncode == 0 and not raw.timed_out and separated.error is None,
        "metrics": metrics,
    }


def verify_local(spec: ModelSpec) -> None:
    verify_runtime_identity(runtime_for(spec))

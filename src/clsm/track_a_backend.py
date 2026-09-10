"""Track-A (Mac / Apple-Silicon) real generation backend: the pinned ``llama-cli``.

Implements :class:`~clsm.generation.GenerationBackend` so it drops straight into
``clsm.pipeline.run`` in place of the (GPU / vLLM) ``VLLMBackend`` and the ``MockBackend``.

Design constraints (PILOT_PROTOCOL.md §6, DECISION_LOG D-043/D-050/D-052/D-053/D-054/D-065):

* **Fail-closed run gate (D-050, hardened D-065).** Construction and ``generate()`` both
  require a :class:`~clsm.track_a_run.RunToken`. There is **no public boolean bypass**.
  Synthetic unit tests pass ``RunToken.for_synthetic_test()`` *together with* an injected
  ``invoker`` + ``version_probe``; such a backend is structurally incapable of driving
  the real ``llama-cli`` or the real GGUF. Without a token, ``RunNotAuthorizedError``.
* **Subprocess argument LIST, never a shell string.** No ``shell=True``, no string
  interpolation into a command line. The argv is fully determined by the frozen,
  hashed scientific config — there is **no ``extra_args`` escape hatch** (D-065).
* **No hard-coded user paths.** Binary / model paths come from :class:`LlamaCppRuntime`
  (loaded from a YAML / env), never a literal ``/Users/...`` in committed code.
* **Runtime + model identity is verified FAIL-CLOSED (D-043/D-052/D-065)** before the
  first generation: the GGUF size + SHA-256 (both must be pinned), AND
  ``llama-cli --version`` is parsed and its build + commit compared to the pinned
  values. ANY problem — subprocess failure, nonzero exit, empty/unparsable output,
  missing or mismatched build/commit, missing pin — raises. It never proceeds with
  ``identity_verified=False``.
* **Every knob is explicit** on the command line.
* **Full provenance is captured** per generation: exact argv, exit code, wall-clock,
  stdout, stderr, stop reason, token count.
* **ZERO retries (D-054).** One invocation per spec, whatever the output. An
  infrastructure fault is a recorded failure, counted, never silently retried.
* **Raw output is preserved verbatim** (``GenerationRecord.raw_output``); a separate
  ``cleaned`` form removes ONLY two anchored, runtime-generated strings — the leading
  ``llama-cli`` startup banner and the exact trailing perf-summary line — via
  :func:`strip_cli_banner` / :func:`strip_cli_footer` (``cli_chrome_v2``, D-052). **No
  generic regex ever interprets model content structurally.**
* **Persistence never overwrites (D-052).** Every artifact filename includes the
  experiment id, item id, condition, seed, sample index, and attempt number;
  :func:`_atomic_write` refuses to overwrite an existing file.

**This module never chooses a model, never downloads anything, and cannot be run on
scientific data without an authorized, frozen protocol.**
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import yaml

from clsm.config import DecodingConfig, ModelConfig
from clsm.extraction import extract_answer
from clsm.generation import GenSpec
from clsm.logging_utils import get_logger
from clsm.schemas import GenerationRecord, StopReason
from clsm.track_a_run import RunNotAuthorizedError, RunToken

_log = get_logger("clsm.track_a_backend")


def _utcnow() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat()


# --------------------------------------------------------------------------------------
# Runtime configuration (llama.cpp-specific knobs not covered by clsm.config.DecodingConfig)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LlamaCppRuntime:
    """Everything needed to invoke the pinned ``llama-cli`` reproducibly.

    Paths are provided by the caller (from a local YAML / env), never hard-coded.
    """

    binary_path: str  # e.g. "~/tools/llama.cpp/build/bin/llama-cli"
    model_path: str  # e.g. "~/models/clsm/Qwen3-1.7B/Qwen3-1.7B-Q8_0.gguf"
    llama_cpp_commit: str  # pinned; VERIFIED against `--version` (D-052), fail-closed
    expected_llama_cpp_build: str | None = None  # e.g. "10809"; REQUIRED for a real run (D-065)
    expected_model_sha256: str | None = None  # REQUIRED for a real run (D-065)
    expected_model_bytes: int | None = None  # verified before the first generation

    # decoding knobs llama-cli needs that DecodingConfig does not carry
    min_p: float = 0.0
    presence_penalty: float = 0.0
    reasoning_format: str = "none"  # keep literal <think>...</think> (D-038)
    enable_thinking: bool = True
    n_ctx: int = 32768
    n_gpu_layers: int = 99  # offload all; Metal on M5 (D-036/D-040)

    # process controls
    timeout_seconds: float = 900.0  # D-065: part of the scientific config hash
    # NOTE (D-065): there is NO `extra_args` field. The llama-cli command surface is
    # fully frozen -- an authorized run's argv is entirely determined by the hashed
    # scientific config. Synthetic tests use dependency injection, not scientific args.

    @property
    def resolved_binary(self) -> Path:
        return Path(self.binary_path).expanduser()

    @property
    def resolved_model(self) -> Path:
        return Path(self.model_path).expanduser()


# --------------------------------------------------------------------------------------
# Deterministic output cleaning (PILOT_PROTOCOL.md §14, DECISION_LOG D-052)
#
# cli_chrome_v2: RAW stdout is always persisted verbatim. `cleaned` removes ONLY two
# strings that are proven runtime-generated (never model tokens):
#   1. the leading `llama-cli` startup banner block (ASCII logo + `build : ...` lines +
#      `available commands:` list), matched ANCHORED to the start of the stream and only
#      up to the first blank line after `available commands:`;
#   2. the exact trailing perf-summary line, matched ANCHORED to the end of the stream
#      with an exact numeric format, single-line, NO `re.DOTALL`.
# There is NO generic `>` / `[Prompt:` regex that could interpret model content.
# With `--no-display-prompt` the prompt is not echoed, and with the model's own
# `<think>` output these strippers are usually no-ops.
# --------------------------------------------------------------------------------------

CLI_CHROME_VERSION = "cli_chrome_v2"  # D-052; pinned to llama.cpp v0.4.0 build b10809

# Anchored: from \A, the banner ends at the blank line(s) after the `available commands:`
# bullet list. `available commands:` must appear within the first 40 lines or nothing is
# stripped. `[\s\S]` (not `.` + DOTALL) keeps intent explicit.
_BANNER = re.compile(
    r"\A(?:[^\n]*\n){0,40}?[ \t]*available commands:\n"
    r"(?:[ \t]*/[^\n]*\n)+"
    r"\n+"
)
# Anchored to \Z, single line, exact llama-cli end-of-turn summary format.
_FOOTER = re.compile(
    r"\n?\[ Prompt:\s*[0-9.]+\s*t/s\s*\|\s*Generation:\s*[0-9.]+\s*t/s\s*\]\s*"
    r"(?:\n\s*Exiting\.\.\.\s*)?\Z"
)


def strip_cli_banner(stdout: str) -> str:
    """Remove ONLY the anchored leading ``llama-cli`` startup banner. No-op if absent."""
    return _BANNER.sub("", stdout, count=1)


def strip_cli_footer(text: str) -> str:
    """Remove ONLY the anchored trailing perf-summary line. No-op if absent."""
    return _FOOTER.sub("", text)


def clean_cli_output(stdout: str) -> tuple[str, bool]:
    """Return (cleaned, changed). ``cleaned`` = banner-stripped + footer-stripped, then
    a single leading-newline trim. RAW is preserved by the caller regardless."""
    body = strip_cli_footer(strip_cli_banner(stdout))
    body = body.lstrip("\n")
    return body, body != stdout


# best-effort token accounting from the llama.cpp perf block on STDERR (D-053).
_PERF_EVAL = re.compile(r"eval time\s*=\s*[0-9.]+\s*ms\s*/\s*(\d+)\s*(?:runs|tokens)", re.IGNORECASE)
_PERF_LLAMA = re.compile(r"llama_perf.*?(\d+)\s*runs", re.IGNORECASE | re.DOTALL)


def parse_output_tokens(stderr: str) -> int | None:
    """Best-effort output-token count from the llama.cpp perf block (STDERR). None if
    the perf block is absent (e.g. built with `--no-perf`)."""
    m = _PERF_EVAL.search(stderr) or _PERF_LLAMA.search(stderr)
    return int(m.group(1)) if m else None


# --------------------------------------------------------------------------------------
# One raw invocation
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class RawInvocation:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str
    wall_clock_seconds: float
    timed_out: bool


class LlamaCppInvocationError(RuntimeError):
    """Raised for a set-up fault (missing binary/model, hash mismatch) -- never for
    an undesirable *generation*."""


# Dependency-injection seams (D-065). The DEFAULTS are the real subprocess code paths;
# a synthetic-test RunToken REQUIRES both to be injected, so it can never reach them.
Invoker = Callable[..., "RawInvocation"]          # (argv: list[str], *, timeout: float) -> RawInvocation
VersionProbe = Callable[[Path], "tuple[str, str, str]"]  # path -> (version_string, build, commit)


class LlamaCppBackend:
    """A pinned-``llama-cli`` :class:`~clsm.generation.GenerationBackend`.

    Construct with the shared :class:`~clsm.config.ModelConfig` +
    :class:`~clsm.config.DecodingConfig` (so it is interchangeable with the other
    backends in ``clsm.pipeline.run``) plus a :class:`LlamaCppRuntime`.
    """

    IS_TEST_ONLY = False

    def __init__(
        self,
        model: ModelConfig,
        decoding: DecodingConfig,
        runtime: LlamaCppRuntime,
        run_token: RunToken,
        *,
        raw_dir: str | Path | None = None,
        verify_runtime: bool = True,
        invoker: Invoker | None = None,
        version_probe: VersionProbe | None = None,
    ) -> None:
        # FAIL-CLOSED run gate (D-050, hardened D-065). A RunToken is ALWAYS required and
        # there is NO public boolean bypass. `True`/`1`/an object/None are not RunTokens.
        if not isinstance(run_token, RunToken):
            raise RunNotAuthorizedError(
                "LlamaCppBackend requires an authorized RunToken from "
                "clsm.track_a_run.authorize_track_a_run(). There is no boolean bypass. "
                "For synthetic unit tests pass RunToken.for_synthetic_test() together "
                "with an injected `invoker` and `version_probe`."
            )
        self._synthetic = run_token.for_synthetic_test_only
        if self._synthetic:
            # A synthetic token is structurally forbidden from reaching the real runtime.
            if invoker is None or version_probe is None:
                raise RunNotAuthorizedError(
                    "A synthetic-test RunToken REQUIRES an injected `invoker` and "
                    "`version_probe`; it must never drive the real llama-cli or GGUF."
                )
        else:
            # An authorized run uses the real, frozen invoker + probe -- no injection.
            if invoker is not None or version_probe is not None:
                raise RunNotAuthorizedError(
                    "An authorized RunToken must use the real (frozen) invoker + version "
                    "probe; injection is only for RunToken.for_synthetic_test()."
                )
        self.model = model
        self.decoding = decoding
        self.runtime = runtime
        self.run_token = run_token
        self._invoke: Invoker = invoker if invoker is not None else _subprocess_invoke
        self._probe_version: VersionProbe = (
            version_probe if version_probe is not None else _binary_version
        )
        self.raw_dir = Path(raw_dir).expanduser() if raw_dir is not None else None
        self._verified = False
        self._version_string: str = ""
        self._version_build: str = ""
        self.model_sha256_verified = False
        self.identity_verified = False
        if verify_runtime:
            self._verify_runtime()

    # -- set-up verification (no generation) -----------------------------------------

    def _verify_runtime(self) -> None:
        """FAIL-CLOSED identity verification (D-052/D-065). Every branch either positively
        verifies a pinned value or raises -- generation never proceeds unverified."""
        b = self.runtime.resolved_binary
        m = self.runtime.resolved_model
        if not b.exists():
            raise LlamaCppInvocationError(f"llama-cli binary not found: {b}")
        if not b.is_file():
            raise LlamaCppInvocationError(f"llama-cli binary path is not a file: {b}")
        if not m.exists():
            raise LlamaCppInvocationError(f"model GGUF not found: {m}")
        size = m.stat().st_size
        if self.runtime.expected_model_bytes is not None and size != self.runtime.expected_model_bytes:
            raise LlamaCppInvocationError(
                f"model size mismatch: {size} != expected {self.runtime.expected_model_bytes}"
            )
        # GGUF SHA-256 MUST be pinned and MUST match (D-065).
        if not self.runtime.expected_model_sha256:
            raise LlamaCppInvocationError(
                "expected_model_sha256 is not pinned -- cannot verify the GGUF identity"
            )
        got = _sha256_file(m)
        if got != self.runtime.expected_model_sha256.lower():
            raise LlamaCppInvocationError(
                f"model SHA-256 mismatch: {got} != expected {self.runtime.expected_model_sha256}"
            )
        self.model_sha256_verified = True

        # Runtime identity (D-052/D-065). `self._probe_version` RAISES on any failure
        # mode (subprocess error, nonzero exit, empty/unparsable output, missing groups).
        self._version_string, version_build, version_commit = self._probe_version(b)
        exp_commit = self.runtime.llama_cpp_commit
        if not exp_commit:
            raise LlamaCppInvocationError("llama_cpp_commit is not pinned")
        # Accept a short<->long prefix match either way (e.g. "5266f24da" vs the full 40).
        if not (
            exp_commit == version_commit
            or exp_commit.startswith(version_commit)
            or version_commit.startswith(exp_commit)
        ):
            raise LlamaCppInvocationError(
                f"llama.cpp commit mismatch: --version reports {version_commit!r}, "
                f"pinned {exp_commit!r}"
            )
        exp_build = self.runtime.expected_llama_cpp_build
        if not exp_build:
            raise LlamaCppInvocationError(
                "expected_llama_cpp_build is not pinned -- cannot verify the build"
            )
        if version_build != exp_build:
            raise LlamaCppInvocationError(
                f"llama.cpp build mismatch: --version reports build {version_build!r}, "
                f"pinned build {exp_build!r}"
            )
        self._version_build = version_build
        self.identity_verified = True
        self._verified = True
        _log.info("llama.cpp runtime verified: %s (%s)", b, self._version_string)

    # -- command construction --------------------------------------------------------

    def build_argv(self, prompt: str, *, seed: int) -> list[str]:
        """Deterministic argv for ONE generation. No shell, no interpolation."""
        d = self.decoding
        r = self.runtime
        argv = [
            str(r.resolved_binary),
            "-m", str(r.resolved_model),
            "-p", prompt,
            "-st",  # single turn; non-interactive because -p is predefined
            "--reasoning-format", r.reasoning_format,
            "-n", str(d.max_new_tokens),
            "-c", str(r.n_ctx),
            "-s", str(seed),
            "--temp", _fmt(d.temperature),
            "--top-p", _fmt(d.top_p),
            "--min-p", _fmt(r.min_p),
            "--presence-penalty", _fmt(r.presence_penalty),
            "--repeat-penalty", _fmt(d.repetition_penalty),
            "-ngl", str(r.n_gpu_layers),
            "--no-warmup",
            "--simple-io",
            "--no-display-prompt",  # do not echo the user turn (v0.4.0 flag)
            # NOTE: `--no-perf` is deliberately NOT passed (D-053) -- the llama.cpp perf
            # block on STDERR is the token-count / stop-reason signal. STDOUT chrome is
            # removed by the anchored strip_cli_footer, never a generic regex.
        ]
        if d.top_k is not None:
            argv += ["--top-k", str(d.top_k)]
        if not r.enable_thinking:
            argv += ["--reasoning", "off"]
        # D-065: NO extra_args. The command surface is fully frozen.
        return argv

    # -- one invocation ------------------------------------------------------------

    def invoke_once(self, prompt: str, *, seed: int) -> RawInvocation:
        argv = self.build_argv(prompt, seed=seed)
        return self._invoke(argv, timeout=self.runtime.timeout_seconds)

    # -- GenerationBackend protocol ------------------------------------------------

    # ZERO retries (D-054): exactly one attempt per spec, always attempt 1.
    ATTEMPT = 1

    def generate(self, specs: list[GenSpec]) -> list[GenerationRecord]:
        # FAIL-CLOSED (D-050/D-065): re-checked here, not only in __init__, so a backend
        # whose run_token was tampered with after construction cannot run.
        if not isinstance(self.run_token, RunToken):
            raise RunNotAuthorizedError(
                "LlamaCppBackend.generate() called without an authorized RunToken."
            )
        if self._synthetic:
            _log.warning(
                "LlamaCppBackend: SYNTHETIC-TEST RunToken + injected fakes -- NOT a scientific run."
            )
        if not self._verified:
            self._verify_runtime()
        records: list[GenerationRecord] = []
        for spec in specs:
            raw = self.invoke_once(spec.prompt, seed=spec.seed)
            cleaned, chrome_stripped = clean_cli_output(raw.stdout)
            infra_ok = raw.returncode == 0 and not raw.timed_out and bool(cleaned.strip())
            # An infrastructure failure (nonzero exit / timeout / empty output) is a
            # PARSE_ERROR -- NOT a genuine "model gave no answer" (which would pollute the
            # non-differential-parse-failure check). The infra reason is in the .meta.json.
            ext = extract_answer(cleaned) if infra_ok else extract_answer(None)
            n_tokens = parse_output_tokens(raw.stderr)
            stop_reason = _derive_stop_reason(
                raw, n_tokens=n_tokens, max_new_tokens=self.decoding.max_new_tokens
            )
            truncated = stop_reason in (StopReason.LENGTH, StopReason.TIMEOUT)
            rec = GenerationRecord(
                experiment_id=spec.experiment_id,
                item_id=spec.item_id,
                dataset=spec.dataset,
                dataset_revision=spec.dataset_revision,
                subject=spec.subject,
                question_sha256=spec.question_sha256,
                condition=spec.condition,
                cue_type=spec.cue_type,
                cue_version=spec.cue_version,
                hint_target_letter=spec.hint_target_letter,
                correct_letter=spec.correct_letter,
                sample_idx=spec.sample_idx,
                seed=spec.seed,
                model=self.model.id,
                model_revision=self.model.revision,
                tokenizer_revision=self.model.tokenizer_revision,
                temperature=self.decoding.temperature,
                top_p=self.decoding.top_p,
                max_new_tokens=self.decoding.max_new_tokens,
                prompt_sha256=spec.prompt_sha256,
                prompt_template_version=spec.prompt_template_version,
                timestamp_utc=_utcnow(),
                raw_output=raw.stdout,  # VERBATIM, including chrome
                cot_text=ext.cot_text,
                answer_text=ext.answer_text,
                extracted_answer=ext.answer,
                parse_status=ext.status,
                reasoning_span_status=ext.reasoning_status,
                reasoning_marker_style=ext.reasoning_marker_style,
                n_output_tokens=n_tokens,
                truncated=truncated,
                stop_reason=stop_reason,
                is_mock=False,
            )
            records.append(rec)
            if self.raw_dir is not None:
                self._persist_raw(
                    spec, raw, cleaned, chrome_stripped, infra_ok,
                    n_tokens=n_tokens, stop_reason=stop_reason,
                )
        return records

    # -- provenance persistence (atomic) -----------------------------------------

    def _persist_raw(
        self, spec: GenSpec, raw: RawInvocation, cleaned: str, chrome_stripped: bool, infra_ok: bool,
        *, n_tokens: int | None, stop_reason: StopReason,
    ) -> None:
        assert self.raw_dir is not None
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        # Unique deterministic identity (D-052 / Part 4): experiment id + item + condition
        # + seed + sample index + attempt number. `_atomic_write` refuses to overwrite.
        safe_exp = re.sub(r"[^A-Za-z0-9._-]", "_", spec.experiment_id)
        safe_item = re.sub(r"[^A-Za-z0-9._-]", "_", spec.item_id)
        stem = (
            f"{safe_exp}__{safe_item}__{spec.condition.value}"
            f"__s{spec.seed}__k{spec.sample_idx}__a{self.ATTEMPT}"
        )
        payload = {
            "spec": {
                "experiment_id": spec.experiment_id, "item_id": spec.item_id,
                "condition": spec.condition.value, "seed": spec.seed,
                "sample_idx": spec.sample_idx, "prompt_sha256": spec.prompt_sha256,
                "attempt": self.ATTEMPT,
            },
            "result": {
                "stop_reason": stop_reason.value, "n_output_tokens": n_tokens,
                "retry_policy": "zero-retry/D-054",
            },
            "runtime": {
                "llama_cpp_commit": self.runtime.llama_cpp_commit,
                "binary": str(self.runtime.resolved_binary),
                "model": str(self.runtime.resolved_model),
                "expected_model_sha256": self.runtime.expected_model_sha256,
                "reasoning_format": self.runtime.reasoning_format,
                "enable_thinking": self.runtime.enable_thinking,
                "n_ctx": self.runtime.n_ctx, "n_gpu_layers": self.runtime.n_gpu_layers,
                "min_p": self.runtime.min_p, "presence_penalty": self.runtime.presence_penalty,
            },
            "decoding": {
                "temperature": self.decoding.temperature, "top_p": self.decoding.top_p,
                "top_k": self.decoding.top_k, "repetition_penalty": self.decoding.repetition_penalty,
                "max_new_tokens": self.decoding.max_new_tokens,
            },
            "invocation": {
                "argv": raw.argv, "returncode": raw.returncode, "timed_out": raw.timed_out,
                "wall_clock_seconds": raw.wall_clock_seconds,
                "chrome_stripped": chrome_stripped, "infra_ok": infra_ok,
                "cli_chrome_version": CLI_CHROME_VERSION,
            },
            "authorization": {
                "synthetic_test_token": self._synthetic,
                "run_token_scientific_hash": self.run_token.scientific_hash,
                "run_token_reviewer": self.run_token.reviewer,
            },
            "runtime_identity": {
                "llama_cpp_version_string": self._version_string,
                "llama_cpp_build": self._version_build,
                "model_sha256_verified": self.model_sha256_verified,
                "identity_verified": self.identity_verified,
            },
            "timestamp_utc": _utcnow(),
        }
        _atomic_write(self.raw_dir / f"{stem}.stdout.txt", raw.stdout)
        _atomic_write(self.raw_dir / f"{stem}.stderr.txt", raw.stderr)
        _atomic_write(self.raw_dir / f"{stem}.cleaned.txt", cleaned)
        _atomic_write(self.raw_dir / f"{stem}.meta.json", json.dumps(payload, indent=2, sort_keys=True))


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------


def _fmt(x: float) -> str:
    """Stable float formatting for argv (no locale, no sci notation for our ranges)."""
    return f"{x:g}"


def _sha256_file(path: Path, *, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _derive_stop_reason(
    raw: RawInvocation, *, n_tokens: int | None, max_new_tokens: int
) -> StopReason:
    """Honest tri-state stop reason (D-053). NEVER inferred from a missing final answer.

    * TIMEOUT      -- the subprocess wall-clock timeout fired.
    * NONZERO_EXIT -- llama-cli exited non-zero (and did not time out).
    * LENGTH       -- perf block reports >= the requested ``-n`` (length exhaustion).
    * EOS          -- perf block reports a token count strictly below ``-n`` (natural stop).
    * UNKNOWN      -- no reliable perf signal on STDERR; we do not guess.
    """
    if raw.timed_out:
        return StopReason.TIMEOUT
    if raw.returncode != 0:
        return StopReason.NONZERO_EXIT
    if n_tokens is None:
        return StopReason.UNKNOWN
    if n_tokens >= max_new_tokens:
        return StopReason.LENGTH
    return StopReason.EOS


_VERSION_RE = re.compile(
    r"version:\s*([0-9][^\s(]*)\s*\(build\s*(\d+)\s*,\s*commit\s*([0-9a-f]+)", re.IGNORECASE
)


def _binary_version(path: Path) -> tuple[str, str, str]:
    """Run ``<binary> --version`` and return ``(version_string, build, commit)``.

    FAIL-CLOSED (DECISION_LOG D-065). Raises :class:`LlamaCppInvocationError` on ANY of:
    a subprocess failure, a nonzero exit, empty output, output that does not match the
    expected ``version: X (build N, commit H)`` shape, or a missing build / commit
    group. It NEVER returns a partial or unverified result -- the caller can trust that
    a successful return means the identity was positively parsed.
    """
    try:
        proc = subprocess.run(
            [str(path), "--version"], capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise LlamaCppInvocationError(f"could not run `{path} --version`: {exc}") from exc
    if proc.returncode != 0:
        raise LlamaCppInvocationError(
            f"`{path} --version` exited {proc.returncode} "
            f"(stderr: {proc.stderr.strip()[:200]!r})"
        )
    blob = f"{proc.stdout}\n{proc.stderr}".strip()
    if not blob:
        raise LlamaCppInvocationError(f"`{path} --version` produced no output")
    m = _VERSION_RE.search(blob)
    if m is None:
        raise LlamaCppInvocationError(
            f"`{path} --version` output does not match the expected "
            f"`version: X (build N, commit H)` shape: {blob[:200]!r}"
        )
    line = next((ln.strip() for ln in blob.splitlines() if "version:" in ln.lower()), blob[:120])
    return line, m.group(2), m.group(3)


def _subprocess_invoke(argv: list[str], *, timeout: float) -> RawInvocation:
    """The REAL invocation adapter: run ``argv`` as a subprocess. Only reached for an
    authorized (non-synthetic) :class:`~clsm.track_a_run.RunToken`."""
    t0 = time.perf_counter()
    timed_out = False
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
        stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr if isinstance(exc.stderr, str) else "") + "\n[TIMEOUT]"
        rc = -1
    return RawInvocation(
        argv=argv, returncode=rc, stdout=stdout, stderr=stderr,
        wall_clock_seconds=time.perf_counter() - t0, timed_out=timed_out,
    )


def _atomic_write(path: Path, text: str) -> None:
    """Atomic write that REFUSES to overwrite (Part 4). If the target exists, it is only
    accepted when the on-disk bytes are already identical (idempotent replay); otherwise
    a collision is a hard error -- a silent overwrite would destroy a prior generation."""
    if path.exists():
        if path.read_text(encoding="utf-8") == text:
            return  # idempotent replay -- byte-identical, safe no-op
        raise LlamaCppInvocationError(
            f"refusing to overwrite an existing generation artifact: {path} "
            f"(on-disk content differs from the new write)"
        )
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def load_llamacpp_runtime(
    yaml_path: str | Path,
    *,
    binary_path: str | None = None,
    model_path: str | None = None,
) -> LlamaCppRuntime:
    """Build a :class:`LlamaCppRuntime` from ``configs/track_a_pilot/runtime_llamacpp.yaml``.

    Local paths precedence: explicit arg > env (``CLSM_LLAMA_CLI`` / ``CLSM_QWEN_GGUF``)
    > the YAML's ``binary`` / ``path`` (usually ``null`` in the committed file). The
    committed YAML never carries a machine path.
    """
    data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    rt, mdl, dx, pr = data["runtime"], data["model"], data["decoding_extras"], data["process"]
    b = binary_path or os.environ.get("CLSM_LLAMA_CLI") or rt.get("binary")
    m = model_path or os.environ.get("CLSM_QWEN_GGUF") or mdl.get("path")
    if not b or not m:
        raise LlamaCppInvocationError(
            "llama-cli binary / model GGUF path not set. Pass binary_path/model_path, or "
            "export CLSM_LLAMA_CLI and CLSM_QWEN_GGUF, or set them in a local override."
        )
    return LlamaCppRuntime(
        binary_path=str(b),
        model_path=str(m),
        llama_cpp_commit=rt["commit"],
        expected_llama_cpp_build=(str(rt["build_number"]) if rt.get("build_number") else None),
        expected_model_sha256=mdl.get("sha256"),
        expected_model_bytes=mdl.get("size_bytes"),
        min_p=float(dx["min_p"]),
        presence_penalty=float(dx["presence_penalty"]),
        reasoning_format=str(dx["reasoning_format"]),
        enable_thinking=bool(dx["enable_thinking"]),
        n_ctx=int(pr["n_ctx"]),
        n_gpu_layers=int(pr["n_gpu_layers"]),
        timeout_seconds=float(pr["timeout_seconds"]),
    )


def llamacpp_runtime_available(binary_path: str, model_path: str) -> bool:
    """Cheap check used by tests / dry-runs -- does NOT invoke the model."""
    return (
        Path(binary_path).expanduser().is_file()
        and Path(model_path).expanduser().is_file()
        and shutil.which("true") is not None  # sanity: a working subprocess env
    )


__all__ = [
    "CLI_CHROME_VERSION",
    "LlamaCppBackend",
    "LlamaCppInvocationError",
    "LlamaCppRuntime",
    "RawInvocation",
    "clean_cli_output",
    "llamacpp_runtime_available",
    "load_llamacpp_runtime",
    "parse_output_tokens",
    "strip_cli_banner",
    "strip_cli_footer",
]

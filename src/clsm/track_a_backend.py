"""Track-A (Mac / Apple-Silicon) real generation backend: the pinned ``llama-cli``.

Implements :class:`~clsm.generation.GenerationBackend` so it drops straight into
``clsm.pipeline.run`` in place of the (GPU / vLLM) ``VLLMBackend`` and the ``MockBackend``.

Design constraints (PILOT_PROTOCOL.md §6, DECISION_LOG D-043):

* **Subprocess argument LIST, never a shell string.** No ``shell=True``, no string
  interpolation into a command line.
* **No hard-coded user paths.** Binary / model paths come from :class:`LlamaCppRuntime`
  (loaded from a YAML / env), never a literal ``/Users/...`` in committed code.
* **Model identity is verified** (size + optional SHA-256) before the first generation,
  once per backend instance -- a mismatch raises, it never silently proceeds.
* **Every knob is explicit** on the command line: seed, temperature, top-p, top-k,
  min-p, repeat-penalty, n-predict, ctx-size, ``--reasoning-format``, ``-ngl``.
* **Full provenance is captured** per generation: exact argv, exit code, wall-clock,
  stdout, stderr, timeout flag.
* **No retry of any kind here.** A failure is recorded (``error`` field / a
  ``PARSE_ERROR`` record) and returned; the *pipeline's* frozen retry policy
  (PILOT_PROTOCOL.md §15) is applied one layer up, and only for infrastructure faults.
* **Raw output is preserved verbatim** on the record; parsing is a separate step
  (``clsm.extraction``), and the llama-cli banner / ``[ Prompt: ... t/s ]`` footer are
  stripped only by the documented deterministic rule in :func:`strip_cli_chrome`.

**This module never chooses a model, never downloads anything, and must not be run on
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
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from clsm.config import DecodingConfig, ModelConfig
from clsm.extraction import extract_answer
from clsm.generation import GenSpec
from clsm.logging_utils import get_logger
from clsm.schemas import GenerationRecord

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
    llama_cpp_commit: str  # pinned; recorded in provenance, not enforced here
    expected_model_sha256: str | None = None  # verified once if given
    expected_model_bytes: int | None = None  # verified once if given

    # decoding knobs llama-cli needs that DecodingConfig does not carry
    min_p: float = 0.0
    presence_penalty: float = 0.0
    reasoning_format: str = "none"  # keep literal <think>...</think> (D-038)
    enable_thinking: bool = True
    n_ctx: int = 32768
    n_gpu_layers: int = 99  # offload all; Metal on M5 (D-036/D-040)

    # process controls
    timeout_seconds: float = 900.0
    extra_args: tuple[str, ...] = field(default_factory=tuple)

    @property
    def resolved_binary(self) -> Path:
        return Path(self.binary_path).expanduser()

    @property
    def resolved_model(self) -> Path:
        return Path(self.model_path).expanduser()


# --------------------------------------------------------------------------------------
# Deterministic output cleaning (PILOT_PROTOCOL.md §14)
# --------------------------------------------------------------------------------------

# The pinned llama-cli prints a fixed banner block and a trailing perf/exit footer to
# stdout around the model's own tokens. These patterns are matched to the pinned
# v0.4.0 build ONLY and are versioned with the parser.
_BANNER_END = re.compile(r"^\s*>\s.*?$", re.MULTILINE)  # the "> <prompt>" echo line
_FOOTER = re.compile(
    r"\n\s*\[\s*Prompt:.*?t/s\s*\|\s*Generation:.*?t/s\s*\]\s*\n.*?Exiting\.\.\.\s*$",
    re.DOTALL,
)


def strip_cli_chrome(stdout: str, *, prompt: str) -> str:
    """Return the model's own text from a ``llama-cli`` stdout.

    Deterministic, versioned (`cli_chrome_v1`, pinned to llama.cpp v0.4.0). Rule:

    1. drop everything up to and including the echoed ``> <prompt-first-line>`` line
       (llama-cli echoes the user turn once);
    2. drop the trailing ``[ Prompt: ... t/s | Generation: ... t/s ] ... Exiting...``
       footer.

    Nothing else is altered -- no grammar repair, no reasoning edits, no letter
    inference. If the banner/footer are not found, the input is returned unchanged
    (the caller records ``chrome_stripped=False``).
    """
    body = stdout
    m = list(_BANNER_END.finditer(body))
    if m:
        body = body[m[-1].end():]
    body = _FOOTER.sub("", body)
    return body.lstrip("\n")


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
        *,
        raw_dir: str | Path | None = None,
        verify_model: bool = True,
    ) -> None:
        self.model = model
        self.decoding = decoding
        self.runtime = runtime
        self.raw_dir = Path(raw_dir).expanduser() if raw_dir is not None else None
        self._verified = False
        if verify_model:
            self._verify_runtime()

    # -- set-up verification (no generation) -----------------------------------------

    def _verify_runtime(self) -> None:
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
        if self.runtime.expected_model_sha256 is not None:
            got = _sha256_file(m)
            if got != self.runtime.expected_model_sha256.lower():
                raise LlamaCppInvocationError(
                    f"model SHA-256 mismatch: {got} != expected {self.runtime.expected_model_sha256}"
                )
        self._verified = True
        _log.info("llama.cpp runtime verified: %s (commit %s)", b, self.runtime.llama_cpp_commit)

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
            "--no-perf",            # suppress the internal perf-timing footer
        ]
        if d.top_k is not None:
            argv += ["--top-k", str(d.top_k)]
        if not r.enable_thinking:
            argv += ["--reasoning", "off"]
        argv += list(r.extra_args)
        return argv

    # -- one invocation ------------------------------------------------------------

    def invoke_once(self, prompt: str, *, seed: int) -> RawInvocation:
        argv = self.build_argv(prompt, seed=seed)
        t0 = time.perf_counter()
        timed_out = False
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self.runtime.timeout_seconds,
                check=False,
            )
            stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = exc.stdout or "" if isinstance(exc.stdout, str) else ""
            stderr = (exc.stderr or "" if isinstance(exc.stderr, str) else "") + "\n[TIMEOUT]"
            rc = -1
        wall = time.perf_counter() - t0
        return RawInvocation(
            argv=argv, returncode=rc, stdout=stdout, stderr=stderr,
            wall_clock_seconds=wall, timed_out=timed_out,
        )

    # -- GenerationBackend protocol ------------------------------------------------

    def generate(self, specs: list[GenSpec]) -> list[GenerationRecord]:
        if not self._verified:
            self._verify_runtime()
        records: list[GenerationRecord] = []
        for spec in specs:
            raw = self.invoke_once(spec.prompt, seed=spec.seed)
            cleaned = strip_cli_chrome(raw.stdout, prompt=spec.prompt)
            chrome_stripped = cleaned != raw.stdout
            infra_ok = raw.returncode == 0 and not raw.timed_out and bool(cleaned.strip())
            # An infrastructure failure (nonzero exit / timeout / empty output) is a
            # PARSE_ERROR -- NOT a genuine "model gave no answer" (which would pollute the
            # non-differential-parse-failure check). The infra reason is in the .meta.json.
            ext = extract_answer(cleaned) if infra_ok else extract_answer(None)
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
                n_output_tokens=None,
                truncated=raw.timed_out,
                is_mock=False,
            )
            records.append(rec)
            if self.raw_dir is not None:
                self._persist_raw(spec, raw, cleaned, chrome_stripped, infra_ok)
        return records

    # -- provenance persistence (atomic) -----------------------------------------

    def _persist_raw(
        self, spec: GenSpec, raw: RawInvocation, cleaned: str, chrome_stripped: bool, infra_ok: bool
    ) -> None:
        assert self.raw_dir is not None
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{spec.item_id.replace(':', '_')}__{spec.condition.value}__s{spec.seed}__k{spec.sample_idx}"
        payload = {
            "spec": {
                "experiment_id": spec.experiment_id, "item_id": spec.item_id,
                "condition": spec.condition.value, "seed": spec.seed,
                "sample_idx": spec.sample_idx, "prompt_sha256": spec.prompt_sha256,
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


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
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


CLI_CHROME_VERSION = "cli_chrome_v1"  # pinned to llama.cpp v0.4.0 build b10809

__all__ = [
    "CLI_CHROME_VERSION",
    "LlamaCppBackend",
    "LlamaCppInvocationError",
    "LlamaCppRuntime",
    "RawInvocation",
    "llamacpp_runtime_available",
    "load_llamacpp_runtime",
    "strip_cli_chrome",
]

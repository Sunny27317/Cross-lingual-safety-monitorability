"""Track-A run-authorization gate + scientific-config hash + run provenance.

**Technically enforced (DECISION_LOG D-050, hardened D-065).** A real Track-A generation
cannot occur unless :func:`authorize_track_a_run` succeeds and hands back a
:class:`RunToken`; the real backend (:class:`clsm.track_a_backend.LlamaCppBackend`)
**always** requires a :class:`RunToken` and fails **closed** otherwise. There is no
public boolean bypass. Synthetic unit tests use :meth:`RunToken.for_synthetic_test`,
which is structurally incapable of authorizing a real run: a backend holding one MUST
be given an injected fake invoker + fake version probe, so it can never drive the real
``llama-cli`` or the real GGUF.

Three separable readiness layers (all must pass):

1. **methodology readiness** — every run-blocking METHODOLOGY field in the manifest is
   LOCKED (``TrackAPilotManifest.methodology_frozen()``).
2. **external-resource readiness** — every run-blocking EXTERNAL_RESOURCE field is
   resolved (disclosure judge, human audit, ethics, dataset content pin, …).
3. **explicit human run authorization** — a *structured* token in the environment
   variable ``CLSM_TRACK_A_RUN_AUTHORIZED`` whose payload names the exact scientific
   hash it authorizes and the reviewer's assertion. It is **not** a boolean toggle:
   ``true`` / ``1`` / ``yes`` are rejected. Default (unset) → refuse.

Nothing here downloads data, runs a model, or authorizes anything by itself.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import platform
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

from clsm.config import ExperimentConfig, load_experiment_config
from clsm.errors import UnresolvedProductionSettingError
from clsm.logging_utils import get_logger
from clsm.track_a_manifest import TrackAPilotManifest, build_pilot_manifest

_log = get_logger("clsm.track_a_run")

ENV_AUTH = "CLSM_TRACK_A_RUN_AUTHORIZED"
# The authorization payload must be JSON with these keys, and `scientific_hash` must
# equal the hash of the exact config+runtime being run. This makes "authorized" specific
# to one frozen protocol, not a global switch.
_AUTH_REQUIRED_KEYS = {"scientific_hash", "reviewer", "reviewed_utc", "assertion"}
_AUTH_ASSERTION = (
    "I have reviewed the Track-A pilot manifest and preregistration and authorize this "
    "exact scientific configuration to run."
)

PARSER_VERSION = "clsm.extraction/D-038"
CLI_CHROME_VERSION = "cli_chrome_v2"       # D-052 (banner-only, anchored)
METRICS_VERSION = "clsm.metrics/D-031"     # last metric-definition change
RETRY_POLICY_VERSION = "zero-retry/D-054"  # D-054: zero retries


# --------------------------------------------------------------------------------------
# Scientific-config hash (D-051) — covers EVERYTHING that can change model output or the
# scientific analysis; deliberately EXCLUDES prose (`provenance_tag`) and local paths.
# --------------------------------------------------------------------------------------


def scientific_config_dict(cfg: ExperimentConfig, runtime: dict[str, Any]) -> dict[str, Any]:
    """The curated, canonical dict the Track-A scientific hash is computed over.

    ``runtime`` is the parsed ``runtime_llamacpp.yaml`` (or an equivalent dict).
    """
    d = cfg.decoding
    rt, mdl, dx, pr = runtime["runtime"], runtime["model"], runtime["decoding_extras"], runtime["process"]
    return {
        "protocol": "track-a-en-hint-pilot",
        "generator_model": cfg.model.id,
        "model_revision": cfg.model.revision,
        "tokenizer_revision": cfg.model.tokenizer_revision,
        "gguf_sha256": mdl["sha256"],
        "gguf_size_bytes": mdl["size_bytes"],
        "runtime": rt["name"],
        "llama_cpp_commit": rt["commit"],
        "llama_cpp_tag": rt.get("tag"),
        "backend": d.backend,
        "temperature": d.temperature,
        "top_p": d.top_p,
        "top_k": d.top_k,
        "min_p": dx["min_p"],
        "presence_penalty": dx["presence_penalty"],
        "repetition_penalty": d.repetition_penalty,
        "max_new_tokens": d.max_new_tokens,
        "n_ctx": pr["n_ctx"],
        "n_gpu_layers": pr["n_gpu_layers"],
        # D-065: timeout_seconds can flip a trace to TIMEOUT and thus change missingness
        # and downstream estimates -> it is a scientific setting, hashed here.
        "timeout_seconds": pr["timeout_seconds"],
        "llama_cpp_build": rt.get("build_number"),
        # D-065: the llama-cli command surface is FROZEN. LlamaCppRuntime has no
        # `extra_args` escape hatch; an authorized run's argv is fully determined by the
        # hashed fields above. (Marker kept so a future re-introduction moves the hash.)
        "llama_cli_extra_args": [],
        "reasoning_format": dx["reasoning_format"],
        "enable_thinking": dx["enable_thinking"],
        "force_think_prefix": d.force_think_prefix,
        "system_prompt": d.system_prompt,
        "samples_per_condition": d.samples_per_condition,
        "seeds": list(d.seeds),
        "prompt_template_version": cfg.prompt_template_version,
        "prompt_template_sha256": hashlib.sha256(cfg.prompt_template.encode()).hexdigest(),
        "cue_type": cfg.cue.cue_type,
        "cue_version": cfg.cue.version,
        "cue_template_sha256": hashlib.sha256(cfg.cue.template.encode()).hexdigest(),
        "cue_target_rule": cfg.cue.target_rule,
        "hint_seed": cfg.hint_seed,
        "dataset_id": cfg.dataset.id,
        "dataset_config": cfg.dataset.config_name,
        "dataset_split": cfg.dataset.split,
        "dataset_revision": cfg.dataset.revision,
        "dataset_subjects": list(cfg.dataset.subjects),
        "dataset_items_per_subject": cfg.dataset.items_per_subject,
        "dataset_selection_rule": cfg.dataset.selection_rule,
        "dataset_max_chars": cfg.dataset.max_chars,
        "bootstrap_seed": cfg.bootstrap_seed,
        "bootstrap_n": cfg.bootstrap_n,
        "parser_version": PARSER_VERSION,
        "cli_chrome_version": CLI_CHROME_VERSION,
        "metrics_version": METRICS_VERSION,
        "retry_policy_version": RETRY_POLICY_VERSION,
        "judge_status": cfg.judge.status,
        "judge_model": cfg.judge.model,
        "judge_rubric_version": cfg.judge.rubric_version,
    }


def scientific_config_hash(cfg: ExperimentConfig, runtime: dict[str, Any]) -> str:
    payload = json.dumps(scientific_config_dict(cfg, runtime), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------------------
# Authorization
# --------------------------------------------------------------------------------------


class RunNotAuthorizedError(UnresolvedProductionSettingError):
    """Raised (fail-closed) when a real Track-A generation is attempted without a valid
    :class:`RunToken`."""


# Module-private construction guard: a RunToken can ONLY come from
# authorize_track_a_run() or RunToken.for_synthetic_test(). A bare RunToken(...) raises.
_RUNTOKEN_GUARD = object()


@dataclass(frozen=True)
class RunToken:
    """Proof that all three readiness layers passed for one exact scientific hash.

    Constructable ONLY via :func:`authorize_track_a_run` (a real, authorized run) or
    :meth:`for_synthetic_test` (a structurally-neutered token for synthetic unit tests).
    A direct ``RunToken(...)`` raises :class:`RunNotAuthorizedError`.
    """

    scientific_hash: str
    reviewer: str
    reviewed_utc: str
    manifest_status: dict[str, int]
    _guard: object = None
    for_synthetic_test_only: bool = False
    authorized_utc: str = field(default_factory=lambda: _dt.datetime.now(_dt.UTC).isoformat())

    def __post_init__(self) -> None:
        if self._guard is not _RUNTOKEN_GUARD:
            raise RunNotAuthorizedError(
                "RunToken may only be created by clsm.track_a_run.authorize_track_a_run() "
                "or, for synthetic unit tests, RunToken.for_synthetic_test()."
            )

    @classmethod
    def for_synthetic_test(cls) -> RunToken:
        """TEST-ONLY. A backend holding this token is structurally incapable of invoking
        the real ``llama-cli`` or verifying the real runtime: it MUST be given an injected
        fake invoker + fake version probe. It can NEVER authorize a scientific run."""
        return cls(
            scientific_hash="SYNTHETIC-TEST-ONLY-NOT-A-REAL-RUN",
            reviewer="synthetic-test",
            reviewed_utc="",
            manifest_status={},
            _guard=_RUNTOKEN_GUARD,
            for_synthetic_test_only=True,
        )


@dataclass(frozen=True)
class ReadinessReport:
    methodology_frozen: bool
    external_resources_cleared: bool
    human_authorization_present: bool
    methodology_unresolved: list[str]
    external_unresolved: list[str]
    human_authorization_error: str | None

    @property
    def all_pass(self) -> bool:
        return (
            self.methodology_frozen
            and self.external_resources_cleared
            and self.human_authorization_present
        )


def _check_human_authorization(
    expected_hash: str,
) -> tuple[bool, str | None, dict[str, Any] | None]:
    raw = os.environ.get(ENV_AUTH)
    if not raw:
        return False, f"{ENV_AUTH} is not set (fail-closed default)", None
    if raw.strip().lower() in {"true", "1", "yes", "y", "on"}:
        return False, f"{ENV_AUTH} must be a structured JSON payload, not a boolean toggle", None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return False, f"{ENV_AUTH} is not valid JSON", None
    if not isinstance(payload, dict) or not set(payload) >= _AUTH_REQUIRED_KEYS:
        return False, f"{ENV_AUTH} JSON must contain keys {sorted(_AUTH_REQUIRED_KEYS)}", None
    if payload["assertion"].strip() != _AUTH_ASSERTION:
        return False, f"{ENV_AUTH}.assertion does not match the required text verbatim", None
    if payload["scientific_hash"] != expected_hash:
        return (
            False,
            f"{ENV_AUTH}.scientific_hash ({payload['scientific_hash'][:12]}…) does not match "
            f"the config being run ({expected_hash[:12]}…) — re-authorize for THIS protocol",
            None,
        )
    return True, None, payload


def evaluate_readiness(
    manifest: TrackAPilotManifest | None = None,
    *,
    config_path: str | Path = "configs/track_a_pilot/pilot.yaml",
    runtime_path: str | Path = "configs/track_a_pilot/runtime_llamacpp.yaml",
) -> ReadinessReport:
    """Static, side-effect-free readiness evaluation across all three layers."""
    from clsm.track_a_manifest import BlockKind

    m = manifest or build_pilot_manifest(config_path)
    cfg = load_experiment_config(config_path)
    runtime = yaml.safe_load(Path(runtime_path).read_text())
    expected_hash = scientific_config_hash(cfg, runtime)

    meth = m.unresolved_by_kind(BlockKind.METHODOLOGY)
    ext = m.unresolved_by_kind(BlockKind.EXTERNAL_RESOURCE)
    human_ok, human_err, _ = _check_human_authorization(expected_hash)
    return ReadinessReport(
        methodology_frozen=not meth,
        external_resources_cleared=not ext,
        human_authorization_present=human_ok,
        methodology_unresolved=meth,
        external_unresolved=ext,
        human_authorization_error=human_err,
    )


def authorize_track_a_run(
    *,
    config_path: str | Path = "configs/track_a_pilot/pilot.yaml",
    runtime_path: str | Path = "configs/track_a_pilot/runtime_llamacpp.yaml",
    manifest: TrackAPilotManifest | None = None,
) -> RunToken:
    """Return a :class:`RunToken` iff ALL THREE readiness layers pass. Otherwise raise
    :class:`RunNotAuthorizedError` with every failure enumerated. Fail-closed."""
    m = manifest or build_pilot_manifest(config_path)
    cfg = load_experiment_config(config_path)
    runtime = yaml.safe_load(Path(runtime_path).read_text())
    expected_hash = scientific_config_hash(cfg, runtime)
    rep = evaluate_readiness(m, config_path=config_path, runtime_path=runtime_path)

    if not rep.all_pass:
        lines = ["Track-A run is NOT authorized. Failing layers:"]
        if not rep.methodology_frozen:
            lines.append(f"  methodology: unresolved {rep.methodology_unresolved}")
        if not rep.external_resources_cleared:
            lines.append(f"  external resources: unresolved {rep.external_unresolved}")
        if not rep.human_authorization_present:
            lines.append(f"  human authorization: {rep.human_authorization_error}")
        raise RunNotAuthorizedError("\n".join(lines))

    human_ok, _, payload = _check_human_authorization(expected_hash)
    assert human_ok and payload is not None
    _log.warning(
        "Track-A run AUTHORIZED for scientific_hash %s by %s (reviewed %s)",
        expected_hash[:12], payload["reviewer"], payload["reviewed_utc"],
    )
    return RunToken(
        scientific_hash=expected_hash,
        reviewer=payload["reviewer"],
        reviewed_utc=payload["reviewed_utc"],
        manifest_status=m.status_summary(),
        _guard=_RUNTOKEN_GUARD,
    )


# --------------------------------------------------------------------------------------
# Track-A run provenance (D-055) — a future reader can reconstruct the run from THIS,
# not from gitignored side files.
# --------------------------------------------------------------------------------------


def _git(*args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=10, check=False)
        return r.stdout.strip() or None
    except Exception:  # pragma: no cover
        return None


class TrackARunProvenance(BaseModel):
    """Complete, self-contained provenance for one Track-A generation run.

    Restores (and extends for llama.cpp) the enumerated requirement that the old
    PILOT_PREREGISTRATION §12 carried — see PILOT_PROTOCOL.md §12.
    """

    model_config = ConfigDict(extra="forbid")

    # identity / integrity
    schema_version: str = "track-a-run-provenance/1"
    scientific_config_hash: str
    experiment_id: str
    git_commit: str | None
    git_dirty: bool
    run_token_scientific_hash: str
    run_token_reviewer: str
    run_token_authorized_utc: str

    # generator + runtime
    model_repo: str
    model_revision: str
    tokenizer_revision: str
    gguf_filename: str
    gguf_sha256: str
    gguf_size_bytes: int
    gguf_sha256_verified: bool
    llama_cpp_repo: str
    llama_cpp_commit: str
    llama_cpp_version_string: str
    llama_cpp_build: str | None
    llama_cpp_identity_verified: bool
    backend: str

    # decoding
    temperature: float
    top_p: float
    top_k: int | None
    min_p: float
    presence_penalty: float
    repetition_penalty: float
    max_new_tokens: int
    n_ctx: int
    n_gpu_layers: int
    timeout_seconds: float
    llama_cli_extra_args: list[str]  # D-065: frozen empty; the command surface is fixed
    reasoning_format: str
    enable_thinking: bool
    force_think_prefix: bool
    system_prompt: str | None
    samples_per_condition: int
    seeds: list[int]

    # intervention / prompt
    prompt_template_version: str
    prompt_template_sha256: str
    cue_version: str
    cue_template_sha256: str
    cue_target_rule: str
    hint_seed: int

    # dataset
    dataset_repo: str
    dataset_revision: str | None
    dataset_config: str
    dataset_split: str
    datasets_library_version: str | None
    dataset_content_hash: str | None
    dataset_item_ids: list[str]
    dataset_schema_verified: bool

    # analysis
    parser_version: str
    cli_chrome_version: str
    metrics_version: str
    retry_policy_version: str
    bootstrap_seed: int
    bootstrap_n: int

    # host
    host_platform: str
    host_machine: str
    host_python: str

    # timing
    run_started_utc: str


def capture_track_a_provenance(
    token: RunToken,
    *,
    experiment_id: str,
    config_path: str | Path = "configs/track_a_pilot/pilot.yaml",
    runtime_path: str | Path = "configs/track_a_pilot/runtime_llamacpp.yaml",
    llama_cpp_version_string: str = "",
    llama_cpp_build: str | None = None,
    gguf_sha256_verified: bool = False,
    llama_cpp_identity_verified: bool = False,
    datasets_library_version: str | None = None,
    dataset_content_hash: str | None = None,
    dataset_item_ids: list[str] | None = None,
    dataset_schema_verified: bool = False,
) -> TrackARunProvenance:
    cfg = load_experiment_config(config_path)
    rt = yaml.safe_load(Path(runtime_path).read_text())
    d, dx, pr, mdl, rtc = (
        cfg.decoding, rt["decoding_extras"], rt["process"], rt["model"], rt["runtime"],
    )
    porcelain = _git("status", "--porcelain")
    return TrackARunProvenance(
        scientific_config_hash=scientific_config_hash(cfg, rt),
        experiment_id=experiment_id,
        git_commit=_git("rev-parse", "HEAD"),
        git_dirty=bool(porcelain),
        run_token_scientific_hash=token.scientific_hash,
        run_token_reviewer=token.reviewer,
        run_token_authorized_utc=token.authorized_utc,
        model_repo=cfg.model.id,
        model_revision=cfg.model.revision,
        tokenizer_revision=cfg.model.tokenizer_revision,
        gguf_filename=mdl["gguf_file"],
        gguf_sha256=mdl["sha256"],
        gguf_size_bytes=mdl["size_bytes"],
        gguf_sha256_verified=gguf_sha256_verified,
        llama_cpp_repo=rtc["source_repo"],
        llama_cpp_commit=rtc["commit"],
        llama_cpp_version_string=llama_cpp_version_string,
        llama_cpp_build=llama_cpp_build,
        llama_cpp_identity_verified=llama_cpp_identity_verified,
        backend=d.backend,
        temperature=d.temperature,
        top_p=d.top_p,
        top_k=d.top_k,
        min_p=float(dx["min_p"]),
        presence_penalty=float(dx["presence_penalty"]),
        repetition_penalty=d.repetition_penalty,
        max_new_tokens=d.max_new_tokens,
        n_ctx=int(pr["n_ctx"]),
        n_gpu_layers=int(pr["n_gpu_layers"]),
        timeout_seconds=float(pr["timeout_seconds"]),
        llama_cli_extra_args=[],  # D-065: no escape hatch
        reasoning_format=str(dx["reasoning_format"]),
        enable_thinking=bool(dx["enable_thinking"]),
        force_think_prefix=d.force_think_prefix,
        system_prompt=d.system_prompt,
        samples_per_condition=d.samples_per_condition,
        seeds=list(d.seeds),
        prompt_template_version=cfg.prompt_template_version,
        prompt_template_sha256=hashlib.sha256(cfg.prompt_template.encode()).hexdigest(),
        cue_version=cfg.cue.version,
        cue_template_sha256=hashlib.sha256(cfg.cue.template.encode()).hexdigest(),
        cue_target_rule=cfg.cue.target_rule,
        hint_seed=cfg.hint_seed,
        dataset_repo=cfg.dataset.id,
        dataset_revision=cfg.dataset.revision,
        dataset_config=cfg.dataset.config_name,
        dataset_split=cfg.dataset.split,
        datasets_library_version=datasets_library_version,
        dataset_content_hash=dataset_content_hash,
        dataset_item_ids=dataset_item_ids or [],
        dataset_schema_verified=dataset_schema_verified,
        parser_version=PARSER_VERSION,
        cli_chrome_version=CLI_CHROME_VERSION,
        metrics_version=METRICS_VERSION,
        retry_policy_version=RETRY_POLICY_VERSION,
        bootstrap_seed=cfg.bootstrap_seed,
        bootstrap_n=cfg.bootstrap_n,
        host_platform=platform.platform(),
        host_machine=platform.machine(),
        host_python=platform.python_version(),
        run_started_utc=_dt.datetime.now(_dt.UTC).isoformat(),
    )


__all__ = [
    "CLI_CHROME_VERSION",
    "ENV_AUTH",
    "METRICS_VERSION",
    "PARSER_VERSION",
    "RETRY_POLICY_VERSION",
    "ReadinessReport",
    "RunNotAuthorizedError",
    "RunToken",
    "TrackARunProvenance",
    "authorize_track_a_run",
    "capture_track_a_provenance",
    "evaluate_readiness",
    "scientific_config_dict",
    "scientific_config_hash",
]

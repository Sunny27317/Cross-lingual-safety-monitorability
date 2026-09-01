"""Config-driven execution.

Experiment-critical values are **never** hardcoded in source. They live in
``configs/milestone1/*.yaml`` and are loaded + validated here into typed models.

Composition: ``pilot.yaml`` names sibling files (``model``, ``decoding``,
``dataset``, ``cue``, ``judge``); :func:`load_experiment_config` reads them all,
merges, validates, and returns an :class:`ExperimentConfig`.

The disclosure judge is not locked yet (readiness §7a). Its config carries
``status: TODO``; :meth:`JudgeConfig.require_resolved` raises
:class:`UnresolvedProductionSettingError` if a real run tries to use it.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from clsm.errors import ConfigError, UnresolvedProductionSettingError

# Field-level validators raise plain ValueError so pydantic collects them into a
# ValidationError (which is itself a ValueError). The composition/loading layer
# (`load_experiment_config`) is what raises ConfigError, for file + structure problems.


class ModelConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    revision: str = Field(description="Exact HF commit hash — never a branch/tag.")
    tokenizer_revision: str
    base_model: str
    license: str
    provenance_tag: str = Field(description="e.g. 'blueprint Phase 5 + HF model card 2026-09-01'.")

    @field_validator("revision", "tokenizer_revision")
    @classmethod
    def _looks_like_commit(cls, v: str) -> str:
        if v in {"main", "master", "HEAD"} or len(v) < 7:
            raise ValueError(f"model revision must be a pinned commit hash, got {v!r}")
        return v


class DecodingConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    backend: Literal["vllm"] = "vllm"
    temperature: float = Field(description="Greedy (0.0) is forbidden for the distills; enforced below.")
    top_p: float = Field(gt=0.0, le=1.0)
    top_k: int | None = None
    repetition_penalty: float = 1.0
    max_new_tokens: int = Field(gt=0)
    force_think_prefix: bool = True
    system_prompt: str | None = None
    samples_per_condition: int = Field(gt=0, description="k")
    seeds: list[int] = Field(min_length=1)
    provenance_tag: str

    @field_validator("temperature")
    @classmethod
    def _no_greedy(cls, v: float) -> float:
        if v == 0.0:
            raise ValueError("temperature 0.0 (greedy) is forbidden for DeepSeek-R1 distills")
        return v

    @field_validator("seeds")
    @classmethod
    def _seeds_match_k(cls, v: list[int], info: Any) -> list[int]:
        k = info.data.get("samples_per_condition")
        if k is not None and len(v) != k:
            raise ValueError(f"need exactly {k} seeds for k={k}, got {len(v)}")
        if len(set(v)) != len(v):
            raise ValueError("seeds must be distinct")
        return v


class DatasetConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    config_name: str
    split: str
    revision: str | None = Field(default=None, description="HF dataset revision (commit hash).")
    license: str | None = Field(default=None, description="e.g. 'MIT'; recorded in provenance.")
    subjects: list[str] = Field(min_length=1)
    items_per_subject: int = Field(gt=0)
    max_chars: int = Field(gt=0)
    selection_rule: Literal["sha256_sorted_first_n"] = "sha256_sorted_first_n"
    source: Literal["hf_datasets", "local_jsonl"] = "hf_datasets"
    local_path: str | None = None
    provenance_tag: str

    @property
    def pilot_size(self) -> int:
        return len(self.subjects) * self.items_per_subject


class CueConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    cue_type: str
    version: str
    # Position-neutral deterministic selection: hash (experiment_id, item_id, version,
    # hint_seed) onto the incorrect-index set. See clsm.interventions.choose_hint_target
    # and DECISION_LOG D-017. No RNG.
    target_rule: Literal["hash_over_incorrect_indices"] = "hash_over_incorrect_indices"
    template: str = Field(description="Frozen hint text. MUST contain '{letter}' and no other field.")
    wording_policy: str
    provenance_tag: str

    @field_validator("template")
    @classmethod
    def _template_shape(cls, v: str) -> str:
        if "{letter}" not in v:
            raise ValueError("cue template must contain '{letter}'")
        # crude single-placeholder check
        stripped = v.replace("{letter}", "")
        if "{" in stripped or "}" in stripped:
            raise ValueError("cue template must contain exactly one placeholder: '{letter}'")
        return v


class JudgeConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["TODO", "RESOLVED"]
    reason: str
    monitor_id: str = "disclosure_v0"
    model: str | None = None
    revision: str | None = None
    temperature: float = 0.0
    rubric_version: str | None = None
    enable_thinking: bool = False
    keyword_prefilter: list[str] = Field(default_factory=list)

    def require_resolved(self) -> None:
        """Raise unless the judge is fully specified. Called before any real classification."""
        if self.status != "RESOLVED":
            raise UnresolvedProductionSettingError(
                f"disclosure judge is unresolved (status={self.status}): {self.reason}. "
                "Run the §7a verification checklist and set status: RESOLVED with a "
                "pinned model + revision + rubric_version before running."
            )
        missing = [k for k in ("model", "revision", "rubric_version") if getattr(self, k) is None]
        if missing:
            raise UnresolvedProductionSettingError(
                f"disclosure judge status=RESOLVED but missing: {', '.join(missing)}"
            )


class ExperimentConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    experiment_name: str
    role: Literal["pilot", "confirmatory"]
    language: Literal["en"] = "en"  # Milestone 1 is English only.
    prompt_template_version: str
    prompt_template: str = Field(description="MCQ instruction; must contain '{question}' and '{choices}'.")
    hint_seed: int = Field(
        description="Experiment-level seed for position-neutral hint-target selection "
        "(D-017). Changing it can change which wrong option each item's hint names."
    )
    bootstrap_seed: int
    bootstrap_n: int = Field(ge=1000)
    output_dir: str

    model: ModelConfig
    decoding: DecodingConfig
    dataset: DatasetConfig
    cue: CueConfig
    judge: JudgeConfig

    @field_validator("prompt_template")
    @classmethod
    def _prompt_shape(cls, v: str) -> str:
        for token in ("{question}", "{choices}"):
            if token not in v:
                raise ValueError(f"prompt_template must contain {token}")
        return v

    def config_hash(self) -> str:
        """Stable sha256 over the fully-resolved config (canonical JSON)."""
        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------------------
# Loading / composition
# --------------------------------------------------------------------------------------

_SUBCONFIG_KEYS = ("model", "decoding", "dataset", "cue", "judge")


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigError(f"config file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ConfigError(f"config file {path} must contain a mapping at the top level")
    return data


def load_experiment_config(pilot_path: str | Path) -> ExperimentConfig:
    """Load ``pilot.yaml`` and the sibling sub-configs it names, validate, return the model.

    ``pilot.yaml`` schema::

        experiment_name: ...
        role: pilot
        prompt_template_version: ...
        prompt_template: |
          ...
        bootstrap_seed: ...
        bootstrap_n: ...
        output_dir: ...
        includes:
          model: model.yaml
          decoding: decoding.yaml
          dataset: dataset.yaml
          cue: cue.yaml
          judge: judge.yaml
    """
    pilot_path = Path(pilot_path)
    root = pilot_path.parent
    top = _read_yaml(pilot_path)

    includes = top.pop("includes", None)
    if not isinstance(includes, dict) or set(includes) != set(_SUBCONFIG_KEYS):
        raise ConfigError(
            f"pilot config must have an 'includes' mapping with keys {_SUBCONFIG_KEYS}"
        )

    merged: dict[str, Any] = dict(top)
    for key, rel in includes.items():
        merged[key] = _read_yaml(root / rel)

    try:
        return ExperimentConfig.model_validate(merged)
    except Exception as exc:
        raise ConfigError(f"invalid experiment config ({pilot_path}): {exc}") from exc


# --------------------------------------------------------------------------------------
# Runtime environment spec (configs/milestone1/runtime.yaml) — the REQUIRED TARGET.
# The OBSERVED environment is captured by clsm.provenance at run time; a run-authorization
# step compares the two (PRE_RUN_READINESS.md §2, §5 of the locking plan).
# --------------------------------------------------------------------------------------


class VLLMEngineSpec(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_model_len: int = Field(gt=0)
    gpu_memory_utilization: float = Field(gt=0.0, le=1.0)
    enforce_eager: bool
    dtype: Literal["bfloat16", "float16"]


class RuntimeSpec(BaseModel):
    """Proposed target execution environment. ``runtime_role`` must be 'proposed' or
    'observed' — 'proposed' values are requirements, not measurements."""

    model_config = ConfigDict(frozen=True, extra="allow")  # allow free-form *_note keys

    runtime_role: Literal["proposed", "observed"]
    os: Literal["linux"]
    architecture: Literal["x86_64"]
    python: str
    cuda: str
    gpu_minimum: str
    gpu_preferred: str
    gpu_memory_min_gb: int = Field(gt=0)
    gpu_memory_preferred_gb: int = Field(gt=0)
    dtype: Literal["bfloat16", "float16"]
    quantization: Literal["none", "int8", "int4", "fp8"]
    vllm: str
    torch: str
    transformers: str
    datasets: str
    model: str
    model_revision: str
    dataset: str
    dataset_revision: str
    vllm_engine: VLLMEngineSpec

    @field_validator("model_revision", "dataset_revision")
    @classmethod
    def _pinned(cls, v: str) -> str:
        if len(v) < 7 or v in {"main", "master", "HEAD"}:
            raise ValueError(f"revision must be a pinned commit hash, got {v!r}")
        return v


def load_runtime_spec(path: str | Path) -> RuntimeSpec:
    data = _read_yaml(Path(path))
    try:
        return RuntimeSpec.model_validate(data)
    except Exception as exc:
        raise ConfigError(f"invalid runtime spec ({path}): {exc}") from exc


__all__ = [
    "CueConfig",
    "DatasetConfig",
    "DecodingConfig",
    "ExperimentConfig",
    "JudgeConfig",
    "ModelConfig",
    "RuntimeSpec",
    "VLLMEngineSpec",
    "load_experiment_config",
    "load_runtime_spec",
]

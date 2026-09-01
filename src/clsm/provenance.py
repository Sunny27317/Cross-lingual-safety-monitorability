"""Machine-readable provenance capture.

Every real run writes a ``manifest.json`` (validated) and a human-readable
``PROVENANCE.md``. An experiment without a complete manifest is invalid
(``REPRODUCIBILITY.md`` §8, this-turn Phase 11).

Required fields (raises :class:`IncompleteProvenanceError` if any is missing/blank):
    experiment_id, git_commit, git_state, timestamp_utc, python_version, os,
    cpu, gpu, cuda_version, vllm_version, torch_version, transformers_version,
    model_id, model_revision, tokenizer_revision, dataset_id, dataset_revision,
    config_hash, prompt_template_version, prompt_template_sha256, cue_version,
    cue_template_sha256, decoding, seeds, code_path, output_path

Library versions and GPU/CUDA are captured from the *live* environment at run time —
``None``/``"not available"`` is recorded honestly when a component is absent (the
scaffold environment has no torch/vllm; that is expected and the manifest says so).
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import platform
import subprocess
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from clsm.config import ExperimentConfig
from clsm.errors import IncompleteProvenanceError
from clsm.schemas import GitState

# Fields that must ALWAYS be present and non-blank (structural / code-side).
_REQUIRED_ALWAYS = (
    "experiment_id", "git_commit", "git_state", "timestamp_utc", "python_version", "os",
    "cpu", "gpu", "model_id", "model_revision", "tokenizer_revision", "dataset_id",
    "config_hash", "prompt_template_version", "prompt_template_sha256", "cue_type",
    "cue_version", "cue_template_sha256", "cue_target_rule", "code_path", "output_path",
)

# Additionally required for a REAL authorized run (env must actually have the libraries;
# the dataset revision must be pinned; a GPU must be present). Honestly `None` in the
# scaffold environment — checked only by :meth:`Provenance.validate_runtime_complete`.
_REQUIRED_FOR_REAL_RUN = (
    "cuda_version", "vllm_version", "torch_version", "transformers_version",
    "dataset_revision",
)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _pkg_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=10, check=False
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _gpu_info() -> tuple[str, str | None]:
    """Return (gpu_description, cuda_version). Honest 'not available' when absent."""
    try:
        import torch  # type: ignore[import-not-found]
    except ImportError:
        return "not available (torch not installed)", None
    if not torch.cuda.is_available():  # pragma: no cover - env dependent
        return "not available (no CUDA device)", getattr(torch.version, "cuda", None)
    n = torch.cuda.device_count()  # pragma: no cover
    names = sorted({torch.cuda.get_device_name(i) for i in range(n)})  # pragma: no cover
    return f"{n}x {', '.join(names)}", getattr(torch.version, "cuda", None)  # pragma: no cover


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    git_commit: str | None
    git_state: GitState
    timestamp_utc: str
    python_version: str
    os: str
    cpu: str
    gpu: str
    cuda_version: str | None
    vllm_version: str | None
    torch_version: str | None
    transformers_version: str | None
    datasets_version: str | None
    pydantic_version: str | None
    numpy_version: str | None

    model_id: str
    model_revision: str
    tokenizer_revision: str
    dataset_id: str
    dataset_revision: str | None

    config_hash: str
    prompt_template_version: str
    prompt_template_sha256: str
    cue_type: str
    cue_version: str
    cue_template_sha256: str
    cue_target_rule: str
    hint_seed: int
    decoding: dict[str, Any]
    seeds: list[int]
    bootstrap_seed: int

    code_path: str
    output_path: str
    extra: dict[str, Any] = Field(default_factory=dict)

    def _missing(self, names: tuple[str, ...]) -> list[str]:
        out = []
        for field_name in names:
            value = getattr(self, field_name, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                out.append(field_name)
        return out

    def validate_complete(self) -> None:
        """Structural completeness — always required. Used for every write."""
        missing = self._missing(_REQUIRED_ALWAYS)
        if missing:
            raise IncompleteProvenanceError(
                f"provenance manifest missing/blank required fields: {', '.join(missing)}"
            )

    def validate_runtime_complete(self) -> None:
        """Additionally require the real-run fields (env libs, pinned dataset, GPU).

        Called by the pipeline before a run that uses a real (non-mock) backend.
        """
        self.validate_complete()
        missing = self._missing(_REQUIRED_FOR_REAL_RUN)
        if self.gpu.startswith("not available"):
            missing.append("gpu (no CUDA device / torch)")
        if missing:
            raise IncompleteProvenanceError(
                "provenance is not runtime-complete for a real run — missing/blank: "
                f"{', '.join(missing)}. A real generation run must record library "
                "versions, a pinned dataset revision, and a GPU."
            )

    def to_markdown(self) -> str:
        d = self.model_dump(mode="json")
        lines = [
            f"# Provenance — {self.experiment_id}",
            "",
            "> Machine-readable copy: `manifest.json`. This experiment is INVALID without both.",
            "",
        ]
        for key in sorted(d):
            lines.append(f"- **{key}**: `{d[key]}`")
        lines.append("")
        return "\n".join(lines)


def capture_provenance(
    cfg: ExperimentConfig,
    *,
    experiment_id: str,
    output_path: str | Path,
    code_path: str | Path,
    extra: dict[str, Any] | None = None,
) -> Provenance:
    gpu, cuda = _gpu_info()
    git_commit = _git("rev-parse", "HEAD")
    porcelain = _git("status", "--porcelain")
    git_state = (
        GitState.UNKNOWN if porcelain is None
        else GitState.CLEAN if porcelain == "" else GitState.DIRTY
    )
    prov = Provenance(
        experiment_id=experiment_id,
        git_commit=git_commit,
        git_state=git_state,
        timestamp_utc=_dt.datetime.now(_dt.UTC).isoformat(),
        python_version=platform.python_version(),
        os=platform.platform(),
        cpu=platform.processor() or platform.machine(),
        gpu=gpu,
        cuda_version=cuda,
        vllm_version=_pkg_version("vllm"),
        torch_version=_pkg_version("torch"),
        transformers_version=_pkg_version("transformers"),
        datasets_version=_pkg_version("datasets"),
        pydantic_version=_pkg_version("pydantic"),
        numpy_version=_pkg_version("numpy"),
        model_id=cfg.model.id,
        model_revision=cfg.model.revision,
        tokenizer_revision=cfg.model.tokenizer_revision,
        dataset_id=f"{cfg.dataset.id}:{cfg.dataset.config_name}:{cfg.dataset.split}",
        dataset_revision=cfg.dataset.revision,
        config_hash=cfg.config_hash(),
        prompt_template_version=cfg.prompt_template_version,
        prompt_template_sha256=_sha256(cfg.prompt_template),
        cue_type=cfg.cue.cue_type,
        cue_version=cfg.cue.version,
        cue_template_sha256=_sha256(cfg.cue.template),
        cue_target_rule=cfg.cue.target_rule,
        hint_seed=cfg.hint_seed,
        decoding=cfg.decoding.model_dump(mode="json"),
        seeds=list(cfg.decoding.seeds),
        bootstrap_seed=cfg.bootstrap_seed,
        code_path=str(code_path),
        output_path=str(output_path),
        extra=extra or {},
    )
    return prov


def write_provenance(prov: Provenance, out_dir: str | Path) -> tuple[Path, Path]:
    """Validate then write ``manifest.json`` + ``PROVENANCE.md``. Raises if incomplete."""
    prov.validate_complete()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = out_dir / "manifest.json"
    md = out_dir / "PROVENANCE.md"
    manifest.write_text(
        json.dumps(prov.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8"
    )
    md.write_text(prov.to_markdown(), encoding="utf-8")
    return manifest, md


__all__ = ["Provenance", "capture_provenance", "write_provenance"]

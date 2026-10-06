"""Fail-closed helper for the human-authorized gated Gemma artifact."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

REPO_ID = "google/gemma-3-4b-it-qat-q4_0-gguf"
FILENAME = "gemma-3-4b-it-q4_0.gguf"
DEFAULT_OUTPUT_DIR = Path("/Users/sullah1/models/clsm")


def download_exact(*, revision: str, output_dir: Path, allow_download: bool = False) -> tuple[Path, str]:
    if not allow_download:
        raise PermissionError("explicit human authorization is required for gated Gemma download")
    if not revision or revision in {"main", "latest"}:
        raise ValueError("immutable Gemma revision required")
    try:
        from huggingface_hub import HfApi, hf_hub_download  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is required only after license/auth setup") from exc
    api = HfApi()
    try:
        # whoami checks either the private environment token or the user's HF CLI cache;
        # the token value is never read into logs or returned.
        if not (os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")):
            api.whoami()
        api.model_info(REPO_ID, revision=revision)
    except Exception as exc:
        raise PermissionError(
            "exact gated Gemma repository is not accessible; accept license and authenticate"
        ) from exc
    if output_dir != DEFAULT_OUTPUT_DIR and DEFAULT_OUTPUT_DIR not in output_dir.parents:
        raise ValueError(f"Gemma output must be under {DEFAULT_OUTPUT_DIR}")
    path = Path(
        hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            revision=revision,
            local_dir=output_dir,
        )
    )
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    (output_dir / "gemma_download_provenance.json").write_text(
        json.dumps(
            {
                "repo_id": REPO_ID,
                "revision": revision,
                "filename": FILENAME,
                "sha256": digest,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path, digest

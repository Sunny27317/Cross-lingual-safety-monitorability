"""Verification of manually supplied model artifacts; never downloads or infers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from clsm.workshop_v1.gemma_download import FILENAME, REPO_ID

GEMMA_QUANTIZATION = "Q4_0 QAT"
INDICTRANS_MODEL = "ai4bharat/indictrans2-indic-en-1B"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_gemma_local(
    path: Path, *, repo_id: str, revision: str, llama_cli: Path | None = None
) -> dict[str, Any]:
    if repo_id != REPO_ID or not revision or revision in {"main", "latest"}:
        raise ValueError("exact Gemma repository and immutable revision are required")
    if path.name != FILENAME or "q4_0" not in path.name.lower():
        raise ValueError("only the frozen Gemma Q4_0 GGUF filename is accepted")
    if not path.is_file():
        raise FileNotFoundError(path)
    compatibility = "NOT_CHECKED"
    if llama_cli is not None:
        if not llama_cli.is_file():
            raise FileNotFoundError(llama_cli)
        version = subprocess.run(
            [str(llama_cli), "--version"], capture_output=True, text=True, check=False, timeout=15
        )
        if version.returncode != 0:
            raise ValueError("llama.cpp --version failed")
        compatibility = "LLAMA_CPP_VERSION_OK"
    result = {
        "repo_id": repo_id,
        "revision": revision,
        "filename": path.name,
        "file_size": path.stat().st_size,
        "sha256": _sha256(path),
        "quantization": GEMMA_QUANTIZATION,
        "llama_cpp_compatibility": compatibility,
        "llama_cpp_version_output_hash": hashlib.sha256(
            version.stdout.encode("utf-8") if llama_cli is not None else b""
        ).hexdigest(),
    }
    path.parent.joinpath("gemma_local_provenance.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return result


def verify_indictrans_local(
    directory: Path, *, model_id: str = INDICTRANS_MODEL, revision: str,
    source_language: str = "urd_Arab", target_language: str = "eng_Latn"
) -> dict[str, Any]:
    if model_id != INDICTRANS_MODEL or not revision or revision in {"main", "latest"}:
        raise ValueError("exact IndicTrans2 identity and immutable revision are required")
    if (source_language, target_language) != ("urd_Arab", "eng_Latn"):
        raise ValueError("Workshop-v1 requires Urdu to English translation")
    if not directory.is_dir():
        raise FileNotFoundError(directory)
    required = ("config.json", "tokenizer_config.json")
    if any(not (directory / name).is_file() for name in required):
        raise ValueError("IndicTrans2 local directory lacks required tokenizer/config files")
    files = {
        str(file.relative_to(directory)): _sha256(file)
        for file in sorted(directory.rglob("*"))
        if file.is_file() and file.name != "indictrans2_local_provenance.json"
    }
    result = {
        "model_id": model_id,
        "revision": revision,
        "source_language": source_language,
        "target_language": target_language,
        "files": files,
    }
    directory.joinpath("indictrans2_local_provenance.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return result

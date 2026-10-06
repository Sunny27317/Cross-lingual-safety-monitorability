"""Record package/device metadata without loading a translator model."""

from __future__ import annotations

import argparse
import json
import platform
import sys


def version(package: str) -> str | None:
    try:
        import importlib.metadata
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    packages = {
        name: version(name)
        for name in (
            "transformers",
            "torch",
            "tokenizers",
            "sentencepiece",
            "sacremoses",
            "sacrebleu",
            "indic-nlp-library-itt",
            "IndicTransToolkit",
            "huggingface-hub",
            "accelerate",
        )
    }
    torch_info: dict[str, object] = {"imported": False}
    try:
        import torch

        torch_info = {
            "imported": True,
            "mps_available": bool(torch.backends.mps.is_available()),
            "mps_built": bool(torch.backends.mps.is_built()),
            "cuda_available": bool(torch.cuda.is_available()),
            "selected_device": "cpu",
            "selected_dtype": "float32",
        }
    except Exception as exc:  # pragma: no cover - optional heavy dependency
        torch_info = {"imported": False, "import_error": type(exc).__name__}
    result = {
        "schema_version": "indictrans2-runtime-inventory/1",
        "python": sys.version,
        "platform": platform.platform(),
        "packages": packages,
        "torch_runtime": torch_info,
        "device_policy": "record after approval; no implicit MPS fallback",
        "model_loaded": False,
    }
    pathlib = __import__("pathlib")
    pathlib.Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

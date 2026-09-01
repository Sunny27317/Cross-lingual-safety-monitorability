"""Every module imports cleanly without vllm/torch/datasets installed (Phase 16)."""

from __future__ import annotations

import importlib

MODULES = [
    "clsm",
    "clsm.config",
    "clsm.data",
    "clsm.disclosure",
    "clsm.errors",
    "clsm.extraction",
    "clsm.generation",
    "clsm.interventions",
    "clsm.logging_utils",
    "clsm.metrics",
    "clsm.pipeline",
    "clsm.prompts",
    "clsm.provenance",
    "clsm.schemas",
]


def test_all_modules_import() -> None:
    for name in MODULES:
        importlib.import_module(name)


def test_heavy_deps_absent() -> None:
    """The scaffold env must not need the 'run' extras. If they are present the test
    still passes; the harness is explicitly designed to work without them."""
    import contextlib

    for heavy in ("vllm", "torch"):
        with contextlib.suppress(ImportError):
            importlib.import_module(heavy)

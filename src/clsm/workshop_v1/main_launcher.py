"""Fail-closed main-run launch guard; no generator is implemented or invoked here."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from clsm.workshop_v1_main_preflight import preflight


def assert_main_authorized(root: Path) -> dict[str, Any]:
    report = preflight(root)
    if report["MAIN_GENERATION_READY"] is not True or report["scientific_execution_authorized"] is not True:
        raise PermissionError(f"main generation blocked: {report['blockers']}")
    return report


def main() -> None:
    raise SystemExit("use clsm.workshop_v1.main_generation through the guarded executor")

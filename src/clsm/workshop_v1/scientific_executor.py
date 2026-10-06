"""Fail-closed real-generation executor boundary.

The bounded excluded pilot is the only executor currently allowed to call a model.
This module supplies the main-run interface and refuses to execute until the
integrated preflight explicitly authorizes it; there is no bypass flag.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from clsm.workshop_v1.main_launcher import assert_main_authorized

Mode = Literal["pilot", "main"]


@dataclass(frozen=True)
class ExecutionPlan:
    mode: Mode
    expected_calls: int
    study_hash: str
    output_dir: Path
    final_study_hash: str | None = None
    authorization_file: Path | None = None


class ScientificGenerationExecutor:
    """Construction and authorization boundary for future scientific execution."""

    def __init__(self, *, root: Path, plan: ExecutionPlan) -> None:
        self.root, self.plan = root, plan
        if plan.mode not in {"pilot", "main"} or plan.expected_calls < 1:
            raise ValueError("invalid execution plan")
        if plan.mode == "main" and "pilot" in str(plan.output_dir).lower():
            raise ValueError("main plan cannot use a pilot output directory")

    def validate_execution_state(self) -> None:
        """Validate every non-model safety condition before a future backend is enabled."""
        if self.plan.mode != "main":
            raise PermissionError("only main plans reach the scientific authorization gate")
        if self.plan.expected_calls != 3312:
            raise ValueError("Workshop-v1 main executor requires exactly 3312 calls")
        if len(self.plan.study_hash) != 64:
            raise PermissionError("generation configuration hash is required")
        if self.plan.authorization_file is None or not self.plan.authorization_file.is_file():
            raise PermissionError("explicit investigator authorization file is required")
        authorization = json.loads(self.plan.authorization_file.read_text(encoding="utf-8"))
        authorized_hash = authorization.get("generation_config_hash", authorization.get("study_hash"))
        if authorized_hash != self.plan.study_hash:
            raise PermissionError("authorization generation hash mismatch")
        if authorization.get("authorized") is not True:
            raise PermissionError("authorization is not true")
        if self.plan.output_dir.exists() and any(self.plan.output_dir.iterdir()):
            raise FileExistsError("main output directory must be new or empty")

    def execute(self) -> dict[str, Any] | None:
        if self.plan.mode == "main":
            # The guard checks every frozen input and human authorization.  It is
            # intentionally called before any model or output operation.
            assert_main_authorized(self.root)
            self.validate_execution_state()
            from clsm.workshop_v1.main_generation import execute
            return execute(self.root, self.plan.output_dir)
        raise PermissionError("pilot execution is owned by the bounded excluded-pilot runner")


__all__ = ["ExecutionPlan", "ScientificGenerationExecutor"]

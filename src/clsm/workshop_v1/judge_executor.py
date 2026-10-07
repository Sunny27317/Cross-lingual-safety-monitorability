"""Scientific judge execution boundary; no calls are made during planning."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from clsm.downstream.contracts import object_hash
from clsm.workshop_v1.config import ModelSpec
from clsm.workshop_v1.judge import run_judge


class ScientificJudgeExecutor:
    """Uses the frozen Falcon request/parser contract when a caller supplies a backend."""

    def __init__(self, *, spec: ModelSpec, invoke: Callable[[str], dict[str, object]] | None = None) -> None:
        self.spec, self.invoke = spec, invoke

    def judge(
        self, *, prompt: str, generation_id: str, arm: str, trace_language: str
    ) -> list[dict[str, object]]:
        if self.invoke is None:
            raise RuntimeError("judge backend is not configured; dry planning performs no judge calls")
        return run_judge(self.invoke, spec=self.spec, prompt=prompt,
                         generation_id=generation_id, arm=arm, trace_language=trace_language)

    @staticmethod
    def task_id(*, generation_id: str, stage: str, translated_trace_id: str | None = None) -> str:
        return "judge-" + object_hash([generation_id, stage, translated_trace_id])

    @staticmethod
    def checkpoint_action(path: Path, *, task_id: str, study_hash: str) -> str:
        if not path.exists():
            return "RUN"
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("task_id") != task_id or value.get("study_hash") != study_hash:
            raise ValueError("judge checkpoint lineage/study hash changed")
        if value.get("immutable") is not True:
            raise ValueError("judge checkpoint is not immutable")
        return "SKIP" if value.get("technical_status") == "SUCCESS" else "RETRY"


__all__ = ["ScientificJudgeExecutor"]

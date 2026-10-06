import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from clsm.workshop_v1.config import ModelSpec
from clsm.workshop_v1.judge import run_judge
from clsm.workshop_v1.translated_judge_launcher import _atomic, retry_decision


def _spec() -> ModelSpec:
    config = yaml.safe_load(Path("configs/workshop_v1/judge_model.yaml").read_text())
    return ModelSpec.model_validate_json(json.dumps(config["spec"]))


def _runtime(success: bool) -> dict[str, Any]:
    return {
        "runtime_success": success,
        "generated_completion": "EVIDENCE: NONE\nLABEL: partial" if success else "",
        "raw_runtime_output": "synthetic",
        "metrics": {"stop_reason": "EOS", "prompt_tokens": 1, "completion_tokens": 1},
    }


def test_initial_runtime_failure_then_one_authorized_retry() -> None:
    calls = 0

    def invoke(_: str) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return _runtime(calls == 2)

    rows = run_judge(
        invoke, spec=_spec(), prompt="synthetic", generation_id="g", arm="translated", trace_language="en"
    )
    assert calls == 2
    assert retry_decision(rows) == "SUCCESS"


def test_second_failure_is_terminal_and_resume_has_no_retry() -> None:
    rows = [
        {"technical_status": "RUNTIME_ERROR", "attempt": 1},
        {"technical_status": "RUNTIME_ERROR", "attempt": 2},
    ]
    assert retry_decision(rows) == "RETRY_EXHAUSTED"
    assert retry_decision(rows) == "RETRY_EXHAUSTED"


def test_successful_record_is_idempotent() -> None:
    assert retry_decision([{"technical_status": "VALID_LABEL", "attempt": 1}]) == "SUCCESS"


def test_immutable_artifact_is_not_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "judge.json"
    _atomic(path, {"immutable": True, "value": 1})
    _atomic(path, {"immutable": True, "value": 1})
    with pytest.raises(ValueError, match="immutable"):
        _atomic(path, {"immutable": True, "value": 2})


def test_retry_limit_cannot_be_increased() -> None:
    with pytest.raises(ValueError, match="at most one retry"):
        run_judge(
            lambda _: _runtime(False),
            spec=_spec(),
            prompt="synthetic",
            generation_id="g",
            arm="translated",
            trace_language="en",
            max_attempts=3,
        )

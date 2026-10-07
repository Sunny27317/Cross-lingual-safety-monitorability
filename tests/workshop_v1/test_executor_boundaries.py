from pathlib import Path

import pytest

from clsm.workshop_v1.direct_judge_launcher import preflight as judge_preflight
from clsm.workshop_v1.scientific_executor import ExecutionPlan, ScientificGenerationExecutor
from clsm.workshop_v1.translation import IndicTrans2Spec
from clsm.workshop_v1.translator_executor import ScientificTranslatorExecutor
from clsm.workshop_v1.translator_launcher import (
    post_qc as translation_post_qc,
)
from clsm.workshop_v1.translator_launcher import (
    preflight as translation_preflight,
)
from clsm.workshop_v1.translator_launcher import resume_preflight
from clsm.workshop_v1.translator_launcher import (
    validate_authorization as validate_translation_authorization,
)


def test_main_executor_always_uses_fail_closed_guard(tmp_path: Path) -> None:
    executor = ScientificGenerationExecutor(
        root=tmp_path,
        plan=ExecutionPlan("main", 3312, "a" * 64, tmp_path / "main"),
    )
    with pytest.raises((PermissionError, RuntimeError, FileNotFoundError)):
        executor.execute()


def test_main_plan_cannot_use_pilot_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="pilot"):
        ScientificGenerationExecutor(
            root=tmp_path,
            plan=ExecutionPlan("main", 3312, "a" * 64, tmp_path / "pilot-v2"),
        )


def test_translation_revision_and_backend_are_explicit() -> None:
    executor = ScientificTranslatorExecutor(spec=IndicTrans2Spec())
    with pytest.raises(RuntimeError, match="not configured"):
        executor.translate(["synthetic Urdu"])


def test_downstream_launchers_are_non_executing_and_counted() -> None:
    translation = translation_preflight()  # type: ignore[no-untyped-call]
    judge = judge_preflight()
    assert translation["scientific_execution"] is False
    assert translation["tasks"] == 935
    assert judge["scientific_execution"] is False
    assert judge["english_direct"] == 936
    assert judge["urdu_direct"] == 935
    assert judge["total"] == 1871


def _amended_translation_authorization(tmp_path: Path) -> Path:
    import json

    import clsm.workshop_v1.translator_launcher as launcher

    value = json.loads(Path("engineering/INVESTIGATOR_TRANSLATION_AUTHORIZATION.json").read_text())
    value["translation_amendment_hash"] = launcher.EXPECTED_AMENDMENT
    value["effective_translation_config_hash"] = launcher.EXPECTED_EFFECTIVE
    path = tmp_path / "translation_authorization.json"
    path.write_text(json.dumps(value))
    return path


def test_translation_authorization_and_empty_output_are_ready(tmp_path: Path) -> None:
    # The pre-amendment authorization no longer validates (D-TR-1..6, 2026-10-05).
    authorization = Path("engineering/INVESTIGATOR_TRANSLATION_AUTHORIZATION.json")
    assert validate_translation_authorization(authorization)["valid"] is False  # type: ignore[no-untyped-call]
    result = validate_translation_authorization(_amended_translation_authorization(tmp_path))  # type: ignore[no-untyped-call]
    assert result["valid"] is True
    plan = translation_preflight()  # type: ignore[no-untyped-call]
    assert plan["ready"] is False
    qc = translation_post_qc()  # type: ignore[no-untyped-call]
    assert qc["expected_tasks"] == 935
    assert 0 <= qc["persisted_records"] <= 935


def test_translation_post_qc_rejects_duplicate_or_missing_population(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import clsm.workshop_v1.translator_launcher as launcher

    monkeypatch.setattr(launcher, "OUTPUT", tmp_path)
    value = {
        "immutable": True,
        "translation_id": "translation-one",
        "technical_status": "FAILED",
        "translation_config_hash": launcher.EXPECTED_CONFIG,
        "artifact_manifest_hash": launcher.EXPECTED_ARTIFACTS,
    }
    (tmp_path / "translation-one.json").write_text(__import__("json").dumps(value))
    qc = launcher.post_qc()  # type: ignore[no-untyped-call]
    assert qc["ready_for_seal"] is False
    assert qc["missing_ids"] == 935


def test_resume_preflight_accepts_failure_and_rejects_foreign_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json

    import clsm.workshop_v1.translator_launcher as launcher

    monkeypatch.setattr(launcher, "OUTPUT", tmp_path)
    manifest = json.loads(Path("engineering/workshop_v1_translation_task_manifest.json").read_text())
    task = manifest["tasks"][0]
    failure = {
        "immutable": True,
        "translation_id": task["translation_id"],
        "technical_status": "FAILED",
        "attempt": 1,
        "translation_config_hash": launcher.EXPECTED_CONFIG,
        "artifact_manifest_hash": launcher.EXPECTED_ARTIFACTS,
    }
    path = tmp_path / f"translation-failure-{task['translation_id']}-attempt-1.json"
    path.write_text(json.dumps(failure))
    auth_dir = tmp_path.parent / f"{tmp_path.name}-auth"
    auth_dir.mkdir(exist_ok=True)
    auth = _amended_translation_authorization(auth_dir)
    assert resume_preflight(auth)["ready"] is True  # type: ignore[no-untyped-call]
    (tmp_path / "foreign.tmp").write_text("partial")
    assert resume_preflight(auth)["ready"] is False  # type: ignore[no-untyped-call]


def test_stage_lock_rejects_second_executor_and_reuses_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import clsm.workshop_v1.translator_launcher as launcher

    monkeypatch.setattr(launcher, "OUTPUT", tmp_path)
    monkeypatch.setattr(launcher, "LOCK_PATH", tmp_path / ".translation_stage.lock")
    lock = launcher.StageLock("execute")  # type: ignore[no-untyped-call]
    lock.__enter__()  # type: ignore[no-untyped-call]
    try:
        with pytest.raises(RuntimeError, match="already locked"):
            launcher.StageLock("resume").__enter__()  # type: ignore[no-untyped-call]
    finally:
        lock.__exit__(None, None, None)  # type: ignore[no-untyped-call]
    with launcher.StageLock("resume"):  # type: ignore[no-untyped-call]
        pass

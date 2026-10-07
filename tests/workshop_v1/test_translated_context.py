from pathlib import Path

import pytest

from clsm.workshop_v1.translated_context import validate_translated_context
from clsm.workshop_v1.translated_judge_launcher import validate_task_context


def test_translated_context_changes_only_trace() -> None:
    direct = {"question": "Q", "options": ["A", "B", "C", "D"], "suggestion": "S", "trace": "اردو"}
    translated = {**direct, "trace": "English"}
    validate_translated_context(direct, translated)
    validate_task_context(direct, translated)


def test_translated_context_mismatch_fails_closed() -> None:
    direct = {"question": "Q", "options": ["A", "B", "C", "D"], "suggestion": "S", "trace": "اردو"}
    with pytest.raises(ValueError, match="options"):
        validate_translated_context(direct, {**direct, "options": ["A", "C", "B", "D"], "trace": "English"})


@pytest.mark.parametrize("field", ["question", "suggestion"])
def test_translated_context_non_trace_fields_fail_closed(field: str) -> None:
    direct = {"question": "Q", "options": ["A", "B", "C", "D"], "suggestion": "S", "trace": "اردو"}
    translated = {**direct, field: "changed", "trace": "English"}
    with pytest.raises(ValueError, match=field):
        validate_task_context(direct, translated)


def test_authorized_identity_translation_passes() -> None:
    direct = {"question": "Q", "options": ["A"], "suggestion": "S", "trace": "digits 123"}
    translated = {
        **direct,
        "translation_identity": True,
        "translation_changed": False,
        "identity_translation_reason": "zero_urdu_script_letters",
    }
    validate_translated_context(direct, translated)


def test_unexplained_identity_translation_fails_closed() -> None:
    direct = {"question": "Q", "options": ["A"], "suggestion": "S", "trace": "same"}
    with pytest.raises(ValueError, match="identity"):
        validate_translated_context(direct, {**direct})


def test_translated_judge_requires_translation_seal(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import clsm.workshop_v1.translated_judge_launcher as launcher

    manifest = {"count": 935, "tasks": [{} for _ in range(935)]}
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(__import__("json").dumps(manifest))
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(__import__("json").dumps({"status": "FROZEN"}))
    monkeypatch.setattr(launcher, "MANIFEST", manifest_path)
    monkeypatch.setattr(launcher, "TRANSLATION_CONTRACT", contract_path)
    import clsm.workshop_v1.translator_launcher as translator

    monkeypatch.setattr(translator, "OUTPUT", tmp_path / "no-translation-stage")
    result = launcher.preflight()
    assert result["ready"] is False
    blockers = result["blockers"]
    assert isinstance(blockers, list)
    assert "translation seal: canonical translation seal is missing" in blockers

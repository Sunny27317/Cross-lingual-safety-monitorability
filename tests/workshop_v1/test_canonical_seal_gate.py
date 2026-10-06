"""Canonical translation seal (single writer) and the translated-judge gate.

Synthetic only: no model, no translated judging, no real translation records are read
or written.  Every negative case asserts the judge backend was never called.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

import clsm.workshop_v1.post_translation_pipeline as pipeline
import clsm.workshop_v1.translated_judge_launcher as judge
import clsm.workshop_v1.translator_launcher as translator

ROOT = Path(__file__).resolve().parents[2]


def _qc(successes: int = 935, unresolved: int = 0) -> dict[str, Any]:
    ok = successes == 935 and unresolved == 0
    return {
        "launcher_post_qc": {
            "ready_for_seal": ok,
            "successful_records": successes,
            "unresolved_failures": unresolved,
        },
        "translation_qc": {
            "pass": ok,
            "identity_translation_count": 0,
            "identity_translation_ids": [],
            "unresolved_technical_failures": unresolved,
        },
        "pass": ok,
    }


class Backend:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, *args: object, **kwargs: object) -> list[dict[str, Any]]:
        self.calls += 1
        raise AssertionError("judge backend must not be called")


@pytest.fixture
def stage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    output = tmp_path / "translation"
    output.mkdir()
    for index in range(3):
        (output / f"translation-{index:04d}.json").write_text(json.dumps({"i": index}))
    (output / "translation-failure-0000-attempt-1.json").write_text("{}")
    monkeypatch.setattr(translator, "OUTPUT", output)
    monkeypatch.setattr(translator, "canonical_qc", lambda: _qc())
    manifest = tmp_path / "judge_manifest.json"
    manifest.write_text(json.dumps({"count": 935, "tasks": [{} for _ in range(935)]}))
    contract = tmp_path / "contract.json"
    contract.write_text(json.dumps({"status": "FROZEN"}))
    monkeypatch.setattr(judge, "MANIFEST", manifest)
    monkeypatch.setattr(judge, "TRANSLATION_CONTRACT", contract)
    backend = Backend()
    monkeypatch.setattr(judge, "run_judge", backend)
    monkeypatch.setattr(judge, "run_local", backend)
    value = translator.seal()  # type: ignore[no-untyped-call]
    return {"output": output, "seal": value, "backend": backend, "tmp": tmp_path}


def _authorization(tmp: Path, stage_hash: object) -> Path:
    path = tmp / "translated_judge_authorization.json"
    value: dict[str, object] = {
        "authorized": True,
        "status": "APPROVED",
        "translated_urdu_tasks": 935,
        "prompt_hash": judge.PROMPT_HASH,
        "output_directory": "experiments/_runs/workshop-v1-translated-urdu-judge",
    }
    if stage_hash is not None:
        value["translation_stage_hash"] = stage_hash
    path.write_text(json.dumps(value))
    return path


def _seal_path(stage: dict[str, Any]) -> Path:
    return Path(stage["output"]) / translator.SEAL_NAME


def _rewrite(stage: dict[str, Any], field: str, wrong: object) -> str:
    """Tamper a field AND recompute the stage hash, so only independent recomputation catches it."""
    path = _seal_path(stage)
    value = json.loads(path.read_text())
    value[field] = wrong
    body = {k: v for k, v in value.items() if k != "translation_stage_hash"}
    value["translation_stage_hash"] = translator._canonical_json_hash(body)  # type: ignore[no-untyped-call]
    path.write_text(json.dumps(value))
    return str(value["translation_stage_hash"])


def _assert_blocked(stage: dict[str, Any], stage_hash: str, fragment: str) -> None:
    auth = _authorization(stage["tmp"], stage_hash)
    result = judge.validate_authorization(auth)
    assert result["valid"] is False
    assert any(fragment in b for b in result["blockers"]), result["blockers"]  # type: ignore[attr-defined]
    with pytest.raises(SystemExit, match="FAIL_CLOSED"):
        judge.execute(auth)
    assert stage["backend"].calls == 0


# --- positive control -------------------------------------------------------------


def test_valid_seal_schema_and_authorization(stage: dict[str, Any]) -> None:
    seal = stage["seal"]
    assert seal["schema_version"] == "workshop-v1-translation-seal/2"
    assert seal["expected_tasks"] == 935 and seal["successful_records"] == 935
    assert seal["unresolved_failures"] == 0
    assert seal["task_manifest_hash"] == translator.EXPECTED_MANIFEST
    assert seal["translation_config_hash"] == translator.EXPECTED_CONFIG
    assert seal["translation_amendment_hash"] == translator.EXPECTED_AMENDMENT
    assert seal["effective_translation_config_hash"] == translator.EXPECTED_EFFECTIVE
    assert seal["executed_launcher_sha256"].startswith("8f7c241a")
    assert seal["current_launcher_sha256_at_seal"] != seal["executed_launcher_sha256"]
    assert seal["historical_authorization"]["status"] == "SUPERSEDED_HISTORICAL"
    assert seal["translation_population_hash"] == translator.translation_population_hash(  # type: ignore[no-untyped-call]
        stage["output"]
    )
    verified = translator.verify_translation_seal()  # type: ignore[no-untyped-call]
    assert verified == {
        "valid": True,
        "blockers": [],
        "translation_stage_hash": seal["translation_stage_hash"],
    }
    result = judge.validate_authorization(_authorization(stage["tmp"], seal["translation_stage_hash"]))
    assert result["valid"] is True, result["blockers"]
    assert stage["backend"].calls == 0


def test_population_hash_recipe_is_reproducible(stage: dict[str, Any]) -> None:
    output = Path(stage["output"])
    lines = "".join(
        f"{p.name}\t{hashlib.sha256(p.read_bytes()).hexdigest()}\n"
        for p in sorted(output.glob("translation-*.json"))
        if not p.name.startswith("translation-failure-")
    )
    assert stage["seal"]["translation_population_hash"] == hashlib.sha256(lines.encode()).hexdigest()


# --- single writer --------------------------------------------------------------------


def test_seal_is_immutable(stage: dict[str, Any]) -> None:
    before = _seal_path(stage).read_bytes()
    with pytest.raises(SystemExit, match="already exists"):
        translator.seal()  # type: ignore[no-untyped-call]
    assert _seal_path(stage).read_bytes() == before


def test_no_second_reachable_seal_writer() -> None:
    assert not hasattr(pipeline, "seal_translation")
    writers = [
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "src").rglob("*.py")
        if "translation_stage_seal" in p.read_text(encoding="utf-8")
    ]
    assert writers == ["src/clsm/workshop_v1/translator_launcher.py"]
    for doc in (
        "engineering/WORKSHOP_V1_POST_TRANSLATION_COMMANDS.md",
        "engineering/run_workshop_v1_post_translation.sh",
    ):
        commands = [
            line
            for line in (ROOT / doc).read_text(encoding="utf-8").splitlines()
            if line.startswith("PYTHONPATH=")
        ]
        assert not any("--seal-translation" in line for line in commands)
        assert all("post_translation_pipeline --seal" not in line for line in commands)


def test_removed_cli_flag_is_rejected() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "clsm.workshop_v1.post_translation_pipeline", "--seal-translation"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
    )
    assert result.returncode != 0
    assert "unrecognized arguments" in result.stderr


def test_seal_refuses_failed_qc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(translator, "OUTPUT", tmp_path)
    monkeypatch.setattr(translator, "canonical_qc", lambda: _qc(successes=934))
    with pytest.raises(SystemExit, match="post-QC"):
        translator.seal()  # type: ignore[no-untyped-call]
    assert not (tmp_path / translator.SEAL_NAME).exists()


# --- canonical QC ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("launcher", "stage_qc"),
    [
        ({"ready_for_seal": False, "successful_records": 934, "unresolved_failures": 0}, True),
        ({"ready_for_seal": True, "successful_records": 935, "unresolved_failures": 1}, True),
        ({"ready_for_seal": True, "successful_records": 935, "unresolved_failures": 0}, False),
    ],
)
def test_canonical_qc_requires_all_conditions(
    monkeypatch: pytest.MonkeyPatch, launcher: dict[str, object], stage_qc: bool
) -> None:
    monkeypatch.setattr(translator, "post_qc", lambda: launcher)
    monkeypatch.setattr(
        pipeline, "translation_qc", lambda *_: {"pass": stage_qc, "unresolved_technical_failures": 0}
    )
    assert translator.canonical_qc()["pass"] is False  # type: ignore[no-untyped-call]


# --- negative gate cases: backend call count must stay 0 ----------------------------------


def test_missing_seal_blocks(stage: dict[str, Any]) -> None:
    _seal_path(stage).unlink()
    _assert_blocked(stage, stage["seal"]["translation_stage_hash"], "seal is missing")


def test_malformed_seal_blocks(stage: dict[str, Any]) -> None:
    _seal_path(stage).write_text("[]")
    _assert_blocked(stage, stage["seal"]["translation_stage_hash"], "malformed")


def test_corrupt_seal_blocks(stage: dict[str, Any]) -> None:
    _seal_path(stage).write_text("{not json")
    _assert_blocked(stage, stage["seal"]["translation_stage_hash"], "corrupt")


def test_wrong_schema_blocks(stage: dict[str, Any]) -> None:
    stage_hash = _rewrite(stage, "schema_version", "workshop-v1-translation-seal/1")
    _assert_blocked(stage, stage_hash, "schema invalid")


def test_tampered_stage_hash_blocks(stage: dict[str, Any]) -> None:
    path = _seal_path(stage)
    value = json.loads(path.read_text())
    value["translation_stage_hash"] = "0" * 64
    path.write_text(json.dumps(value))
    _assert_blocked(stage, "0" * 64, "does not recompute")


def test_stale_seal_blocks(stage: dict[str, Any]) -> None:
    (Path(stage["output"]) / "translation-0001.json").write_text(json.dumps({"i": "changed"}))
    _assert_blocked(stage, stage["seal"]["translation_stage_hash"], "translation_population_hash")


@pytest.mark.parametrize(
    ("field", "fragment"),
    [
        ("task_manifest_hash", "task_manifest_hash"),
        ("translation_population_hash", "translation_population_hash"),
        ("translation_config_hash", "translation_config_hash"),
        ("translation_amendment_hash", "translation_amendment_hash"),
        ("effective_translation_config_hash", "effective_translation_config_hash"),
        ("executed_launcher_sha256", "executed launcher"),
        ("operative_authorization", "operative_authorization"),
        ("authorization_hash", "authorization_hash"),
        ("identity_translation_ids", "identity_translation_ids"),
    ],
)
def test_rehashed_wrong_binding_blocks(stage: dict[str, Any], field: str, fragment: str) -> None:
    stage_hash = _rewrite(stage, field, "f" * 64)
    _assert_blocked(stage, stage_hash, fragment)


def test_missing_operative_authorization_blocks(
    stage: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(translator, "OPERATIVE_AUTHORIZATION", Path(stage["tmp"]) / "missing.json")
    _assert_blocked(stage, stage["seal"]["translation_stage_hash"], "cannot be recomputed")


def test_authorization_binding_wrong_stage_hash_blocks(stage: dict[str, Any]) -> None:
    _assert_blocked(stage, "a" * 64, "translation stage hash mismatch")


def test_authorization_without_stage_hash_blocks(stage: dict[str, Any]) -> None:
    auth = _authorization(stage["tmp"], None)
    assert judge.validate_authorization(auth)["valid"] is False
    with pytest.raises(SystemExit, match="FAIL_CLOSED"):
        judge.execute(auth)
    assert stage["backend"].calls == 0


def test_unapproved_authorization_blocks(stage: dict[str, Any]) -> None:
    auth = _authorization(stage["tmp"], stage["seal"]["translation_stage_hash"])
    value = json.loads(auth.read_text())
    value["status"] = "DRAFT"
    auth.write_text(json.dumps(value))
    with pytest.raises(SystemExit, match="FAIL_CLOSED"):
        judge.execute(auth)
    assert stage["backend"].calls == 0


def test_incomplete_population_blocks(stage: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(translator, "canonical_qc", lambda: _qc(successes=934))
    _assert_blocked(stage, stage["seal"]["translation_stage_hash"], "QC does not pass")


def test_unresolved_failure_blocks(stage: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(translator, "canonical_qc", lambda: _qc(unresolved=1))
    _assert_blocked(stage, stage["seal"]["translation_stage_hash"], "QC does not pass")


def test_amendment_drift_blocks(stage: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        translator, "_amendment_blockers", lambda: ["translation contract amendment hash mismatch"]
    )
    _assert_blocked(stage, stage["seal"]["translation_stage_hash"], "amendment hash mismatch")


def test_contract_not_frozen_blocks(stage: dict[str, Any]) -> None:
    Path(judge.TRANSLATION_CONTRACT).write_text(json.dumps({"status": "DRAFT"}))
    _assert_blocked(stage, stage["seal"]["translation_stage_hash"], "not frozen")


# --- identity translations (C1) ------------------------------------------------------------


def _record(source: str, translated: str, **flags: object) -> dict[str, Any]:
    def digest(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    return {
        "translation_id": "translation-x",
        "translated_text": translated,
        "source_span_hash": digest(source),
        "translated_trace_hash": digest(translated),
        **flags,
    }


def test_identity_requires_zero_urdu_and_unchanged_bytes() -> None:
    assert judge.identity_translation(_record("B 42", "B 42"), "B 42") is True
    assert judge.identity_translation(_record("جواب", "answer"), "جواب") is False


def test_identity_with_urdu_letters_fails_closed() -> None:
    with pytest.raises(ValueError, match="unexplained identity"):
        judge.identity_translation(_record("جواب B", "جواب B"), "جواب B")


def test_identity_flag_disagreement_fails_closed() -> None:
    with pytest.raises(ValueError, match="disagrees"):
        judge.identity_translation(_record("جواب", "answer", translation_identity=True), "جواب")
    with pytest.raises(ValueError, match="disagrees"):
        judge.identity_translation(_record("B 42", "B 42", translation_identity=False), "B 42")

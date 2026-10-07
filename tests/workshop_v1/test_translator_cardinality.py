# ruff: noqa: RUF001 -- synthetic Urdu punctuation is test data.
"""Technical regression tests for the translation executor (synthetic text only)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import torch

from clsm.downstream.contracts import content_hash
from clsm.workshop_v1 import translator_launcher as launcher
from clsm.workshop_v1.translation import has_urdu_script_letter, reassemble, translation_units


class _Batch(dict[str, torch.Tensor]):
    def to(self, _device: str) -> _Batch:
        return self


class _Tokenizer:
    def __init__(self) -> None:
        self.calls: list[int] = []
        self.inputs: list[str] = []

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        return [0] * len(text.split())

    def __call__(self, items: list[str], **_kwargs: object) -> _Batch:
        self.calls.append(len(items))
        self.inputs.extend(items)
        return _Batch(input_ids=torch.ones((len(items), 3), dtype=torch.long))

    def batch_decode(self, generated: torch.Tensor, **_kwargs: object) -> list[str]:
        return [f"T{int(row[1])}" for row in generated]


class _Processor:
    def preprocess_batch(self, texts: list[str], **_kwargs: object) -> list[str]:
        return [f"urd_Arab eng_Latn {t}" for t in texts]

    def postprocess_batch(self, decoded: list[str], **_kwargs: object) -> list[str]:
        return list(decoded)


class _Model:
    class generation_config:
        eos_token_id = 2

    def __init__(self, length: int = 4, eos: bool = True) -> None:
        self.length, self.eos, self.counter = length, eos, 0

    def generate(self, input_ids: torch.Tensor, **_kwargs: object) -> torch.Tensor:
        rows = []
        for _ in range(input_ids.shape[0]):
            self.counter += 1
            row = torch.full((self.length,), 5, dtype=torch.long)
            row[1] = self.counter
            if self.eos:
                row[-1] = 2
            rows.append(row)
        return torch.stack(rows)


def _source(span: str, completion: str | None = None) -> tuple[dict[str, str], dict[str, object]]:
    return {"source_trace_hash": "h"}, {
        "raw_output_hash": "h",
        "qc": {"runtime_success": True},
        "generated_completion": completion if completion is not None else span + "\nFinal answer: B",
        "parsed": {"reasoning_span": span},
    }


def _run(span: str, tokenizer: _Tokenizer | None = None, model: _Model | None = None) -> dict[str, object]:
    return launcher._translate_task(  # type: ignore[no-untyped-call, no-any-return]
        *_source(span), tokenizer or _Tokenizer(), _Processor(), model or _Model()
    )


SYNTHETIC = (
    "**مرحلہ 1:**\n\nپانی ابلتا ہے۔ برف پگھلتی ہے۔\n\n---\n  \n"
    "Final answer line\nہوا ہلکی ہے، اور گرم۔\n"
)


def test_each_unit_is_generated_alone_and_cardinality_is_preserved() -> None:
    tokenizer = _Tokenizer()
    words = " ".join(["لفظ"] * 150)
    out = _run(f"{words}۔ {words}۔\n\n{words}", tokenizer)
    counts = out["technical_counts"]
    assert isinstance(counts, dict)
    assert counts["translate_units"] > 1
    assert tokenizer.calls == [1] * counts["translate_units"]


def test_structural_whitespace_is_never_sent_and_is_preserved() -> None:
    tokenizer = _Tokenizer()
    out = _run(SYNTHETIC, tokenizer)
    assert all(item.split(" ", 2)[2].strip() for item in tokenizer.inputs)
    translated = out["translated_text"]
    assert isinstance(translated, str)
    assert [i for i, ch in enumerate(SYNTHETIC) if ch == "\n"].__len__() == translated.count("\n")
    assert "\n\n" in translated and "\n  \n" in translated


def test_non_urdu_segments_bypass_and_are_preserved_exactly() -> None:
    tokenizer = _Tokenizer()
    out = _run(SYNTHETIC, tokenizer)
    translated = out["translated_text"]
    assert isinstance(translated, str)
    assert "---\n" in translated and "Final answer line\n" in translated
    assert not any("---" in item or "Final answer" in item for item in tokenizer.inputs)
    assert not has_urdu_script_letter("۔ ؟ ۱۲۳ ،")
    assert has_urdu_script_letter("ب")


@pytest.mark.parametrize(
    "text",
    [SYNTHETIC, "ایک\n\n\nدو  \n", "  پہلا جملہ۔ دوسرا\tجملہ؛ تیسرا  ", "\n\nصرف\n", "۔\n---\n"],
)
def test_reassembly_is_exact_with_identity_translation(text: str) -> None:
    units = translation_units(text, token_count=lambda s: len(s.split()), max_source_tokens=3)
    assert "".join(u.text for u in units) == text
    assert reassemble(units, [u.core for u in units if u.kind == "translate"]) == text
    assert all("\n" not in u.core for u in units)


def test_oversized_whitespace_free_run_is_resplit_preserving_characters() -> None:
    run = "ب" * 950
    units = translation_units(run, token_count=len, max_source_tokens=200)
    assert len(units) == 5
    assert "".join(u.text for u in units) == run
    assert all(u.source_token_count <= 200 for u in units)
    assert {u.boundary_level for u in units} == {"resplit"}


def test_unsatisfiable_resplit_still_fails_closed() -> None:
    with pytest.raises(ValueError, match="frozen limit"):
        translation_units("بب", token_count=lambda _: 201, max_source_tokens=200)


def test_source_is_the_reasoning_span_not_the_completion() -> None:
    span = "صرف یہ حصہ۔"
    out = _run(span)
    assert out["source_span"] == "parsed.reasoning_span"
    assert out["source_span_hash"] == content_hash(span)
    assert "Final answer" not in str(out["translated_text"])
    task, source = _source("")
    with pytest.raises(ValueError, match="reasoning span"):
        launcher._translate_task(  # type: ignore[no-untyped-call]
            task, source, _Tokenizer(), _Processor(), _Model()
        )


def test_generation_at_max_length_without_eos_fails_closed_with_counts() -> None:
    with pytest.raises(launcher.TranslationStageError, match="max_length") as info:
        _run("مختصر جملہ", model=_Model(length=256, eos=False))
    assert info.value.technical["stage"] == "generate"


def test_post_qc_counts_unique_failed_tasks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "translation"
    out.mkdir()
    for attempt in (1, 2):
        (out / f"translation-failure-translation-a-attempt-{attempt}.json").write_text(
            json.dumps({"translation_id": "translation-a", "technical_status": "FAILED"})
        )
    monkeypatch.setattr(launcher, "OUTPUT", out)
    monkeypatch.setattr(launcher, "_source_index", dict)
    qc = launcher.post_qc()  # type: ignore[no-untyped-call]
    assert qc["unresolved_failures"] == 1
    assert qc["unattempted"] == 934


def _authorization(tmp_path: Path) -> Path:
    value = json.loads(Path("engineering/INVESTIGATOR_TRANSLATION_AUTHORIZATION.json").read_text())
    value["translation_amendment_hash"] = launcher.EXPECTED_AMENDMENT
    value["effective_translation_config_hash"] = launcher.EXPECTED_EFFECTIVE
    path = tmp_path / "auth.json"
    path.write_text(json.dumps(value))
    return path


def test_pre_amendment_authorization_is_rejected(tmp_path: Path) -> None:
    old = Path("engineering/INVESTIGATOR_TRANSLATION_AUTHORIZATION.json")
    assert launcher.validate_authorization(old)["valid"] is False  # type: ignore[no-untyped-call]
    assert launcher.validate_authorization(_authorization(tmp_path))["valid"] is True  # type: ignore[no-untyped-call]


def _failure(task_id: str, attempt: int, amended: bool) -> dict[str, object]:
    value: dict[str, object] = {
        "immutable": True,
        "translation_id": task_id,
        "technical_status": "FAILED",
        "attempt": attempt,
        "translation_config_hash": launcher.EXPECTED_CONFIG,
        "artifact_manifest_hash": launcher.EXPECTED_ARTIFACTS,
    }
    if amended:
        value["translation_amendment_hash"] = launcher.EXPECTED_AMENDMENT
        value["effective_translation_config_hash"] = launcher.EXPECTED_EFFECTIVE
    return value


def _history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, records: dict[str, dict[str, object]]
) -> dict[str, object]:
    out = tmp_path / "out"
    out.mkdir()
    for name, value in records.items():
        (out / name).write_text(json.dumps(value))
    monkeypatch.setattr(launcher, "OUTPUT", out)
    return launcher.resume_preflight(_authorization(tmp_path))  # type: ignore[no-untyped-call, no-any-return]


def _task_id() -> str:
    manifest = json.loads(Path("engineering/workshop_v1_translation_task_manifest.json").read_text())
    return str(manifest["tasks"][0]["translation_id"])


def test_attempt_history_one_two_is_ready_for_attempt_three(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tid = _task_id()
    result = _history(tmp_path, monkeypatch, {
        f"translation-failure-{tid}-attempt-1.json": _failure(tid, 1, False),
        f"translation-failure-{tid}-attempt-2.json": _failure(tid, 2, False),
    })
    assert result["ready"] is True, result["blockers"]
    assert result["attempted_unresolved"] == 1
    assert result["unattempted"] == 934


@pytest.mark.parametrize(
    ("records", "blocker"),
    [
        ({"attempt-1": (1, False), "attempt-3": (3, False)}, "unexplained attempt numbering"),
        ({"attempt-1": (2, False)}, "attempt number mismatch"),
        ({"attempt-1": (1, True), "attempt-2": (2, False)}, "pre-amendment attempt after amended"),
    ],
)
def test_attempt_history_rejects_bad_numbering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, records: dict[str, tuple[int, bool]], blocker: str
) -> None:
    tid = _task_id()
    result = _history(tmp_path, monkeypatch, {
        f"translation-failure-{tid}-{suffix}.json": _failure(tid, attempt, amended)
        for suffix, (attempt, amended) in records.items()
    })
    assert result["ready"] is False
    assert any(blocker in b for b in result["blockers"])  # type: ignore[attr-defined]


def test_success_with_wrong_attempt_number_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tid = _task_id()
    success = {**_failure(tid, 2, True), "technical_status": "SUCCESS"}
    result = _history(tmp_path, monkeypatch, {
        f"translation-failure-{tid}-attempt-1.json": _failure(tid, 1, False),
        f"translation-failure-{tid}-attempt-2.json": _failure(tid, 2, False),
        f"{tid}.json": success,
    })
    assert any("conflicting success" in b for b in result["blockers"])  # type: ignore[attr-defined]


def _fake_qc() -> dict[str, object]:
    return {
        "launcher_post_qc": {"ready_for_seal": True, "successful_records": 935, "unresolved_failures": 0},
        "translation_qc": {
            "pass": True,
            "identity_translation_count": 0,
            "identity_translation_ids": [],
            "unresolved_technical_failures": 0,
        },
        "pass": True,
    }


def test_seal_records_operative_and_historical_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(launcher, "OUTPUT", tmp_path)
    monkeypatch.setattr(launcher, "canonical_qc", _fake_qc)
    value = launcher.seal()  # type: ignore[no-untyped-call]
    operative = launcher.OPERATIVE_AUTHORIZATION
    assert operative.name == "INVESTIGATOR_TRANSLATION_AUTHORIZATION_AMENDED_2026-10-05.json"
    assert value["operative_authorization"]["sha256"] == content_sha(operative)
    assert value["authorization_hash"] == content_sha(operative)
    assert value["historical_authorization"]["status"] == "SUPERSEDED_HISTORICAL"
    assert value["historical_authorization"]["sha256"] == content_sha(launcher.HISTORICAL_AUTHORIZATION)
    assert value["effective_translation_config_hash"] == launcher.EXPECTED_EFFECTIVE
    assert (tmp_path / "translation_stage_seal.json").exists()


def test_seal_fails_closed_on_invalid_operative_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(launcher, "OUTPUT", tmp_path)
    monkeypatch.setattr(launcher, "canonical_qc", _fake_qc)
    monkeypatch.setattr(launcher, "OPERATIVE_AUTHORIZATION", launcher.HISTORICAL_AUTHORIZATION)
    with pytest.raises(SystemExit, match="operative authorization invalid"):
        launcher.seal()  # type: ignore[no-untyped-call]
    assert not (tmp_path / "translation_stage_seal.json").exists()


def content_sha(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()

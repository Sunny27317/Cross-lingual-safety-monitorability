"""Loader tests on synthetic miniature stage directories (no real run file is read)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

import clsm.workshop_v1.final_analysis as fa
from clsm.workshop_v1.final_analysis_loader import load_observations, load_stage, script_fraction

QWEN, GEMMA = fa.MODELS
ITEMS: dict[str, dict[str, Any]] = {
    "i1": {"answer_key": "A", "target_letter_cue_a": "B", "target_letter_cue_b": "C", "in_cue_b": True},
    "i2": {"answer_key": "D", "target_letter_cue_a": "A", "target_letter_cue_b": None, "in_cue_b": False},
}


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False))


def _gen(
    gid: str,
    item: str,
    model: str,
    lang: str,
    cond: str,
    s: int = 0,
    ok: bool = True,
    span: str | None = "synthetic rationale",
) -> dict[str, Any]:
    return {
        "generation_id": gid,
        "source_item_id": item,
        "model": model,
        "language": lang,
        "condition": cond,
        "sample_index": s,
        "qc": {"runtime_success": ok},
        "parsed": {
            "final_answer": "A" if ok else None,
            "reasoning_span": span if ok else None,
            "language_compliance": "compliant" if ok else None,
        },
    }


def _task(gid: str, item: str, model: str, lang: str, cond: str, s: int = 0) -> dict[str, Any]:
    return {
        "judge_task_id": f"judge-{gid}",
        "generation_id": gid,
        "source_item_id": item,
        "model": model,
        "language": lang,
        "condition": cond,
        "sample_index": s,
        "translation_id": f"translation-{gid}",
    }


def _judge(
    task: dict[str, Any],
    status: str = "VALID_LABEL",
    label: str | None = "disclosed",
    attempt: int = 1,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "immutable": True,
        "task": task,
        "attempts": [{"attempt": attempt, "technical_status": status, "parsed_label": label}],
        **extra,
    }


@pytest.fixture
def stage_dirs(tmp_path: Path) -> dict[str, Any]:
    g, d, t, tr = (tmp_path / x for x in ("generation", "direct", "translated", "translation"))
    specs = [
        ("generation-en-a", "i1", QWEN, "en", "cue_a"),
        ("generation-ur-a", "i1", QWEN, "ur", "cue_a"),
        ("generation-ur-b", "i1", QWEN, "ur", "cue_b"),
        ("generation-ur-c", "i1", QWEN, "ur", "control"),
        ("generation-ur-a2", "i2", GEMMA, "ur", "cue_a"),
    ]
    for gid, item, model, lang, cond in specs:
        _write(g / f"{gid}.json", _gen(gid, item, model, lang, cond))
    _write(
        g / "generation-timeout.json", _gen("generation-timeout", "i2", QWEN, "ur", "cue_a", ok=False)
    )  # retained missing
    _write(g / "execution_manifest.json", {"note": "not a generation record"})
    for gid, item, model, lang, cond in specs:
        if cond == "control":
            continue
        task = _task(gid, item, model, lang, cond)
        _write(d / f"judge-{gid}.json", _judge(task))
        if lang == "ur":
            trans = {"translation_id": f"translation-{gid}", "translated_text": "synthetic"}
            _write(tr / f"translation-{gid}.json", trans)
            sha = hashlib.sha256((tr / f"translation-{gid}.json").read_bytes()).hexdigest()
            ident = gid == "generation-ur-a2"
            prov: dict[str, Any] = {
                "translation_id": f"translation-{gid}",
                "translation_identity": ident,
                "translation_changed": not ident,
                "identity_translation_reason": fa.IDENTITY_REASON if ident else None,
                "translation_stage_hash": "stage",
                "effective_translation_config_hash": "eff",
                "translation_record_sha256": sha,
            }
            if gid == "generation-ur-a":  # runtime error then one retry (separate .retry-2 file)
                _write(t / f"judge-{gid}.json", _judge(task, "RUNTIME_ERROR", None, 1, **prov))
                _write(
                    t / f"judge-{gid}.retry-2.json",
                    _judge(task, "VALID_LABEL", "partial", 2, retry_of=f"judge-{gid}.json", **prov),
                )
            else:
                _write(t / f"judge-{gid}.json", _judge(task, **prov))
    _write(tr / "translation-failure-x-attempt-1.json", {"translation_id": "x"})
    return {"generation_dir": g, "direct_judge_dir": d, "translated_judge_dir": t, "translation_dir": tr}


def _pool() -> dict[str, dict[str, Any]]:
    return {
        "b1": {"source_item_id": "i1", "model": QWEN, "cue": "cue_a", "sample_index": 0},
        "b2": {"source_item_id": "i2", "model": GEMMA, "cue": "cue_a", "sample_index": 0},
    }


def test_full_synthetic_stage_loads_one_row_per_trace(stage_dirs: dict[str, Any]) -> None:
    report, stage = load_observations(items=ITEMS, human_pool=_pool(), **stage_dirs)
    assert report.ok, report.errors
    assert [r["generation_id"] for r in report.rows] == sorted(
        [
            "generation-en-a",
            "generation-ur-a",
            "generation-ur-b",
            "generation-ur-c",
            "generation-ur-a2",
            "generation-timeout",
        ]
    )
    by = {r["generation_id"]: r for r in report.rows}
    assert (by["generation-ur-a"]["translated_status"], by["generation-ur-a"]["translated_label"]) == (
        "VALID_LABEL",
        "partial",
    )
    assert by["generation-ur-a"]["translated_attempts"] == 2  # retry collapsed, not a second row
    assert (
        by["generation-ur-a2"]["translation_identity"] is True
        and by["generation-ur-a"]["translation_identity"] is False
    )
    assert (
        by["generation-timeout"]["direct_missing_reason"] == "generation_runtime_failure"
    )  # retained missing
    assert by["generation-ur-c"]["direct_missing_reason"] == "control_not_monitored"
    assert by["generation-en-a"]["translated_missing_reason"] == "not_applicable_english"
    assert by["generation-ur-a"]["translated_missing_reason"] == "label_partial"
    assert by["generation-ur-a"]["human_missing_reason"] == "human_label_not_collected"
    assert by["generation-ur-b"]["human_missing_reason"] == "not_in_human_pool"
    assert stage.ignored == ["generation_dir:execution_manifest.json"]
    assert stage.counts["historical_translation_failure_records"] == 1
    assert (
        by["generation-ur-a"]["compliance_fraction"] == 0.0 and by["generation-ur-a"]["visible_trace"] is True
    )


def test_loading_is_deterministic(stage_dirs: dict[str, Any]) -> None:
    a, _ = load_observations(items=ITEMS, human_pool=_pool(), **stage_dirs)
    b, _ = load_observations(items=ITEMS, human_pool=_pool(), **stage_dirs)
    assert a.rows == b.rows and a.accounting == b.accounting


def test_human_files_are_joined(stage_dirs: dict[str, Any], tmp_path: Path) -> None:
    raters = tmp_path / "human"
    raters.mkdir()
    for rid, labels in (("r1", ("disclosed", "disclosed")), ("r2", ("disclosed", "not_disclosed"))):
        (raters / f"{rid}.jsonl").write_text(
            "\n".join(
                json.dumps({"blind_id": b, "rater_id": rid, "label": lab})
                for b, lab in zip(("b1", "b2"), labels, strict=True)
            )
        )
    adj = raters / "adjudication.jsonl"
    adj.write_text(
        json.dumps(
            {
                "blind_id": "b2",
                "rater_id": "adjudicator",
                "independent_label": "cannot_tell",
                "label": "unresolved",
            }
        )
    )
    report, _ = load_observations(
        items=ITEMS,
        human_pool=_pool(),
        rater_files=[raters / "r1.jsonl", raters / "r2.jsonl"],
        adjudication_file=adj,
        **stage_dirs,
    )
    by = {r["generation_id"]: r for r in report.rows}
    assert report.ok
    assert (by["generation-ur-a"]["human_label"], by["generation-ur-a"]["human_source"]) == (
        "disclosed",
        "agreed",
    )
    assert (by["generation-ur-a2"]["human_label"], by["generation-ur-a2"]["human_missing_reason"]) == (
        "unresolved",
        "human_unresolved",
    )


def test_duplicate_rater_label_is_an_error(stage_dirs: dict[str, Any], tmp_path: Path) -> None:
    f = tmp_path / "r1.jsonl"
    f.write_text(
        "\n".join(json.dumps({"blind_id": "b1", "rater_id": "r1", "label": "disclosed"}) for _ in range(2))
    )
    stage = load_stage(rater_files=[f], **stage_dirs)
    assert "rater:b1:r1:duplicate_label" in stage.errors


@pytest.mark.parametrize(
    ("mutate", "error"),
    [
        (
            lambda d: _write(
                d["generation_dir"] / "generation-wrong.json",
                _gen("generation-right", "i1", QWEN, "en", "control"),
            ),
            "filename_generation_id_mismatch",
        ),
        (lambda d: (d["generation_dir"] / "generation-bad.json").write_text("{"), "unreadable"),
        (
            lambda d: _write(
                d["direct_judge_dir"] / "judge-x.json",
                _judge(_task("generation-en-a", "i1", QWEN, "en", "cue_a")),
            ),
            "filename_task_id_mismatch",
        ),
        (
            lambda d: _write(
                d["translated_judge_dir"] / "judge-generation-ur-b.retry-2.json",
                _judge(_task("generation-ur-b", "i1", QWEN, "ur", "cue_b"), attempt=2),
            ),
            "retry_without_retry_of",
        ),
        (
            lambda d: _write(
                d["direct_judge_dir"] / "judge-generation-ur-b.json",
                {**_judge(_task("generation-ur-b", "i1", QWEN, "ur", "cue_b")), "immutable": False},
            ),
            "not_immutable",
        ),
        (
            lambda d: (d["translation_dir"] / "translation-generation-ur-b.json").write_text(
                '{"tampered": true}'
            ),
            "translation_record_sha256_mismatch",
        ),
        (
            lambda d: (d["translation_dir"] / "translation-generation-ur-b.json").unlink(),
            "translation_record_missing",
        ),
    ],
)
def test_loader_errors_are_explicit(stage_dirs: dict[str, Any], mutate: Any, error: str) -> None:
    mutate(stage_dirs)
    report, _ = load_observations(items=ITEMS, human_pool=_pool(), **stage_dirs)
    assert not report.ok and any(error in e for e in report.errors), report.errors


@pytest.mark.parametrize("field_name", ["language", "model", "condition", "source_item_id", "sample_index"])
def test_no_cross_language_model_condition_item_or_sample_join(
    stage_dirs: dict[str, Any], field_name: str
) -> None:
    task = _task("generation-ur-b", "i1", QWEN, "ur", "cue_b")
    task[field_name] = {
        "language": "en",
        "model": GEMMA,
        "condition": "cue_a",
        "source_item_id": "i2",
        "sample_index": 2,
    }[field_name]
    _write(stage_dirs["direct_judge_dir"] / "judge-generation-ur-b.json", _judge(task))
    report, _ = load_observations(items=ITEMS, human_pool=_pool(), **stage_dirs)
    assert "direct:generation-ur-b:task_metadata_mismatch" in report.errors


def test_guard_refuses_scientific_run_directories(tmp_path: Path) -> None:
    runs = tmp_path / "experiments" / "_runs" / "workshop-v1-main-attempt-2"
    runs.mkdir(parents=True)
    kwargs: dict[str, Any] = {"generation_dir": runs, "direct_judge_dir": runs, "translated_judge_dir": runs}
    with pytest.raises(PermissionError, match="unseal step"):
        load_stage(**kwargs)
    with pytest.raises(PermissionError, match="authorization"):
        load_stage(allow_scientific_runs=True, **kwargs)
    auth = tmp_path / "analysis_authorization.json"
    auth.write_text("{}")
    assert load_stage(allow_scientific_runs=True, authorization=auth, **kwargs).generations == []


def test_script_fraction_uses_frozen_parser_expressions() -> None:
    assert script_fraction("یہ جواب", "ur") == 1.0
    assert script_fraction("answer B", "ur") == 0.0
    assert script_fraction("answer B", "en") == 1.0
    assert script_fraction("1 2 3", "en") is None and script_fraction(None, "ur") is None

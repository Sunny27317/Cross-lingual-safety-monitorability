"""End-to-end synthetic worked example for the primary estimand G (files → loader → join → G).

Hand arithmetic is documented in research/WORKSHOP_V1_G_WORKED_EXAMPLE.md. Synthetic only.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

import clsm.workshop_v1.final_analysis as fa
from clsm.workshop_v1.final_analysis_loader import load_observations

QWEN, GEMMA = fa.MODELS
ITEMS: dict[str, dict[str, Any]] = {
    "i1": {"answer_key": "A", "target_letter_cue_a": "B", "target_letter_cue_b": "C", "in_cue_b": True},
    "i2": {"answer_key": "A", "target_letter_cue_a": "C", "target_letter_cue_b": None, "in_cue_b": False},
    "i3": {"answer_key": "D", "target_letter_cue_a": "A", "target_letter_cue_b": None, "in_cue_b": False},
}
# Fields: model, cue, item, sample, in_pool, rater1, rater2, adjudication,
# direct attempts, translated label, identity
SPEC: list[tuple[Any, ...]] = [
    (
        QWEN,
        "cue_a",
        "i1",
        1,
        True,
        "disclosed",
        "disclosed",
        None,
        [("VALID_LABEL", "disclosed")],
        "not_disclosed",
        False,
    ),
    (QWEN, "cue_a", "i1", 0, False, None, None, None, [("VALID_LABEL", "disclosed")], "disclosed", False),
    (
        QWEN,
        "cue_a",
        "i2",
        1,
        True,
        "disclosed",
        "disclosed",
        None,
        [("VALID_LABEL", "not_disclosed")],
        "not_disclosed",
        True,
    ),
    (
        QWEN,
        "cue_a",
        "i3",
        1,
        True,
        "partial",
        "partial",
        None,
        [("VALID_LABEL", "disclosed")],
        "disclosed",
        False,
    ),
    (
        QWEN,
        "cue_b",
        "i1",
        1,
        True,
        "disclosed",
        "not_disclosed",
        ("cannot_tell", "unresolved"),
        [("VALID_LABEL", "disclosed")],
        "disclosed",
        False,
    ),
    (
        GEMMA,
        "cue_a",
        "i1",
        1,
        True,
        "not_disclosed",
        "not_disclosed",
        None,
        [("RUNTIME_ERROR", None), ("VALID_LABEL", "disclosed")],
        "disclosed",
        False,
    ),
    (
        GEMMA,
        "cue_a",
        "i2",
        1,
        True,
        "abstain",
        "abstain",
        ("cannot_tell", "cannot_tell"),
        [("VALID_LABEL", "disclosed")],
        "disclosed",
        False,
    ),
    (
        GEMMA,
        "cue_a",
        "i3",
        1,
        True,
        "disclosed",
        "disclosed",
        None,
        [("MALFORMED_OUTPUT", None)],
        "disclosed",
        False,
    ),
]


def _w(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


@pytest.fixture(scope="module")
def report(tmp_path_factory: pytest.TempPathFactory) -> fa.JoinReport:
    root = tmp_path_factory.mktemp("worked")
    g, d, t, tr, h = (root / x for x in ("gen", "direct", "translated", "translation", "human"))
    pool: dict[str, dict[str, Any]] = {}
    raters: dict[str, list[str]] = {"r1": [], "r2": []}
    adjud: list[str] = []
    for model, cue, item, s, in_pool, r1, r2, adj, attempts, t_label, ident in SPEC:
        gid = f"generation-{model[-6:]}-{cue}-{item}-{s}"
        _w(
            g / f"{gid}.json",
            {
                "generation_id": gid,
                "source_item_id": item,
                "model": model,
                "language": "ur",
                "condition": cue,
                "sample_index": s,
                "qc": {"runtime_success": True},
                "parsed": {"final_answer": "A", "reasoning_span": "متن", "language_compliance": "compliant"},
            },
        )
        task = {
            "judge_task_id": f"judge-{gid}",
            "generation_id": gid,
            "source_item_id": item,
            "model": model,
            "language": "ur",
            "condition": cue,
            "sample_index": s,
            "translation_id": f"translation-{gid}",
        }
        _w(
            d / f"judge-{gid}.json",
            {
                "immutable": True,
                "task": task,
                "attempts": [
                    {"attempt": n + 1, "technical_status": st, "parsed_label": lab}
                    for n, (st, lab) in enumerate(attempts)
                ],
            },
        )
        _w(tr / f"translation-{gid}.json", {"translation_id": f"translation-{gid}"})
        sha = hashlib.sha256((tr / f"translation-{gid}.json").read_bytes()).hexdigest()
        _w(
            t / f"judge-{gid}.json",
            {
                "immutable": True,
                "task": task,
                "translation_id": f"translation-{gid}",
                "attempts": [{"attempt": 1, "technical_status": "VALID_LABEL", "parsed_label": t_label}],
                "translation_identity": ident,
                "translation_changed": not ident,
                "identity_translation_reason": fa.IDENTITY_REASON if ident else None,
                "translation_stage_hash": "s",
                "effective_translation_config_hash": "e",
                "translation_record_sha256": sha,
            },
        )
        if in_pool:
            bid = f"blind-{model[-6:]}-{cue}-{item}"
            pool[bid] = {"source_item_id": item, "model": model, "cue": cue, "sample_index": s}
            raters["r1"].append(json.dumps({"blind_id": bid, "rater_id": "r1", "label": r1}))
            raters["r2"].append(json.dumps({"blind_id": bid, "rater_id": "r2", "label": r2}))
            if adj:
                adjud.append(
                    json.dumps(
                        {
                            "blind_id": bid,
                            "rater_id": "adjudicator",
                            "independent_label": adj[0],
                            "label": adj[1],
                        }
                    )
                )
    h.mkdir()
    for rid, lines in raters.items():
        (h / f"{rid}.jsonl").write_text("\n".join(lines))
    (h / "adjudication.jsonl").write_text("\n".join(adjud))
    rep, _ = load_observations(
        items=ITEMS,
        human_pool=pool,
        generation_dir=g,
        direct_judge_dir=d,
        translated_judge_dir=t,
        translation_dir=tr,
        rater_files=[h / "r1.jsonl", h / "r2.jsonl"],
        adjudication_file=h / "adjudication.jsonl",
    )
    assert rep.ok, rep.errors
    return rep


def _cell(rep: fa.JoinReport, model: str, cue: str) -> list[dict[str, Any]]:
    items = frozenset(ITEMS) if cue == "cue_a" else frozenset(k for k, v in ITEMS.items() if v["in_cue_b"])
    return fa._cell(rep.rows, model=model, language="ur", condition=cue, items=items)


def test_join_shape(report: fa.JoinReport) -> None:
    assert len(report.rows) == len(SPEC)  # one row per trace; retries collapsed
    assert report.accounting["human_pool_rows"] == 7 and report.accounting["human_labelled_rows"] == 7


def test_g_primary_qwen_cue_a(report: fa.JoinReport) -> None:
    g = fa.gap_g(_cell(report, QWEN, "cue_a"))  # pairs: i1 (1-1)=0, i2 (1-0)=+1; i3 partial excluded
    assert (g.value, g.numerator, g.denominator) == (0.5, 1.0, 2)


def test_g_s1_s2_s3_qwen_cue_a(report: fa.JoinReport) -> None:
    cell = _cell(report, QWEN, "cue_a")
    assert (fa.gap_g(cell, "S1").value, fa.gap_g(cell, "S1").denominator) == (0.0, 3)  # i3: 0-1 = -1
    s2 = fa.gap_g(cell, "S2")
    assert s2.denominator == 3 and s2.value == pytest.approx(1 / 3)  # i3: 1-1 = 0
    assert fa.gap_g(cell, "S3").value == 0.5  # no Qwen judge failure


def test_g_undefined_when_no_pairs(report: fa.JoinReport) -> None:
    g = fa.gap_g(_cell(report, QWEN, "cue_b"))  # only i1, H unresolved -> no pair
    assert (g.value, g.denominator) == (None, 0)


def test_g_gemma_retry_abstain_malformed(report: fa.JoinReport) -> None:
    cell = _cell(report, GEMMA, "cue_a")
    by = {r["source_item_id"]: r for r in cell}
    assert (by["i1"]["direct_status"], by["i1"]["direct_attempts"]) == ("VALID_LABEL", 2)  # retry collapsed
    assert by["i2"]["human_label"] == "cannot_tell" and by["i2"]["human_source"] == "adjudicated"
    assert by["i3"]["direct_missing_reason"] == "technical_failure:MALFORMED_OUTPUT"
    g = fa.gap_g(cell)  # only i1: 0 - 1 = -1
    assert (g.value, g.denominator) == (-1.0, 1)
    s3 = fa.gap_g(cell, "S3")  # + i3: 1 - 0 = +1 -> (-1 + 1)/2
    assert (s3.value, s3.denominator) == (0.0, 2)


def test_r_and_exclude_six(report: fa.JoinReport) -> None:
    cell = _cell(report, QWEN, "cue_a")  # triples: i1 T-D = 0-1 = -1; i2 (identity) 0-0 = 0
    r = fa.recovery_r(cell)
    assert (r.value, r.denominator) == (-0.5, 2)
    rob = fa.exclude_six_robustness(cell)["robustness"]["R"]
    assert (rob.value, rob.denominator) == (-1.0, 1)


def test_clusters_and_cross_model_flag(report: fa.JoinReport) -> None:
    cell = _cell(report, QWEN, "cue_a")
    iv = fa.cluster_bootstrap(cell, lambda s: fa.gap_g(s).value, reps=200)
    assert iv.clusters == 3  # items i1, i2, i3 (the non-pool i1 row shares cluster i1)

    def g(sample: Any, model: str) -> float | None:
        return fa.gap_g(
            fa._cell(sample, model=model, language="ur", condition="cue_a", items=frozenset(ITEMS))
        ).value

    flag = fa.cross_model_flag(report.rows, g, reps=200)
    assert flag["point"] == {QWEN: 0.5, GEMMA: -1.0} and flag["flag"] == "differs"  # opposite signs (D-FA-6)


def test_non_pool_row_never_enters_g(report: fa.JoinReport) -> None:
    non_pool = [r for r in report.rows if not r["in_human_pool"]]
    assert len(non_pool) == 1 and non_pool[0]["human_missing_reason"] == "not_in_human_pool"

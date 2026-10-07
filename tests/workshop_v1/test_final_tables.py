"""Table and figure builders on a synthetic grid (no real result is read)."""

from __future__ import annotations

import json
import math
import random
from typing import Any

import pytest

import clsm.workshop_v1.final_analysis as fa
import clsm.workshop_v1.final_tables as ft
from clsm.workshop_v1.annotation_io import disagreements

REPS = 25
FORBIDDEN = ("specificity", "p_value", "pvalue", "alpha", "auroc", "f1", "precision", "recall", "significan")


def synthetic_rows(seed: int = 3, identity: int = 6) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    items = {
        f"i{n:02d}": {
            "answer_key": "A",
            "target_letter_cue_a": "B",
            "target_letter_cue_b": "C" if n < 6 else None,
            "in_cue_b": n < 6,
        }
        for n in range(16)
    }
    gens, direct, translated, pool = [], [], [], {}
    ident_left = identity
    for item, meta in items.items():
        conds = ["control", "cue_a"] + (["cue_b"] if meta["in_cue_b"] else [])
        for model in fa.MODELS:
            for lang in ("en", "ur"):
                for cond in conds:
                    for s in range(3):
                        gid = f"generation-{item}-{model[-6:]}-{lang}-{cond}-{s}"
                        ok = not (
                            item == "i15"
                            and model == fa.MODELS[0]
                            and lang == "ur"
                            and cond == "cue_a"
                            and s == 0
                        )  # one retained missing trace
                        gens.append(
                            {
                                "generation_id": gid,
                                "source_item_id": item,
                                "model": model,
                                "language": lang,
                                "condition": cond,
                                "sample_index": s,
                                "runtime_success": ok,
                                "final_answer": rng.choice("ABCD") if ok else None,
                                "compliance_flag": rng.choice(["compliant", "noncompliant"]) if ok else None,
                                "compliance_fraction": rng.random() if ok else None,
                                "visible_trace": ok,
                            }
                        )
                        if cond == "control" or not ok:
                            continue
                        task = {
                            "generation_id": gid,
                            "source_item_id": item,
                            "model": model,
                            "language": lang,
                            "condition": cond,
                            "sample_index": s,
                            "translation_id": f"t-{gid}",
                        }
                        status = "MALFORMED_OUTPUT" if rng.random() < 0.03 else "VALID_LABEL"
                        direct.append(
                            {
                                "task": task,
                                "attempts": [
                                    {
                                        "attempt": 1,
                                        "technical_status": status,
                                        "parsed_label": rng.choice(fa.JUDGE_LABELS)
                                        if status == "VALID_LABEL"
                                        else None,
                                    }
                                ],
                            }
                        )
                        if lang == "ur":
                            ident = ident_left > 0 and s == 2
                            ident_left -= int(ident)
                            translated.append(
                                {
                                    "task": task,
                                    "translation_id": f"t-{gid}",
                                    "translation_identity": ident,
                                    "translation_changed": not ident,
                                    "identity_translation_reason": fa.IDENTITY_REASON if ident else None,
                                    "attempts": [
                                        {
                                            "attempt": 1,
                                            "technical_status": "VALID_LABEL",
                                            "parsed_label": rng.choice(fa.JUDGE_LABELS),
                                        }
                                    ],
                                }
                            )
                for cue in conds[1:]:
                    pool[f"blind-{item}-{model[-6:]}-{cue}"] = {
                        "source_item_id": item,
                        "model": model,
                        "cue": cue,
                        "sample_index": 1,
                    }
    labels = ("disclosed", "not_disclosed", "partial", "cannot_tell", "abstain")
    raters = [
        {
            "blind_id": b,
            "rater_id": r,
            "label": rng.choice(labels[:2]) if rng.random() < 0.8 else rng.choice(labels),
        }
        for b in sorted(pool)
        for r in ("r1", "r2")
    ]
    flagged = disagreements(raters)
    adj = [
        {
            "blind_id": b,
            "rater_id": "adjudicator",
            "independent_label": "partial",
            "label": rng.choice(["disclosed", "not_disclosed", "unresolved"]),
        }
        for b in flagged
    ]
    report = fa.build_observations(
        generations=gens,
        items=items,
        direct_judge=direct,
        translated_judge=translated,
        human_pool=pool,
        rater_rows=raters,
        adjudications=adj,
    )
    assert report.ok, report.errors[:5]
    return fa.annotate_missingness(report.rows), raters


@pytest.fixture(scope="module")
def grid() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return synthetic_rows()


def _keys(obj: Any) -> set[str]:
    if isinstance(obj, dict):
        return set(obj) | {k for v in obj.values() for k in _keys(v)}
    if isinstance(obj, list):
        return {k for v in obj for k in _keys(v)}
    return set()


def _all_outputs(rows: list[dict[str, Any]], raters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        ft.table_1_study_flow(rows),
        ft.table_2_sample_composition(rows),
        ft.table_3_primary_g(rows, reps=REPS),
        ft.table_4_secondary(rows, reps=REPS),
        ft.table_5_language_contrasts(rows, reps=REPS),
        ft.table_6_cue_b_shared_subset(rows, reps=REPS),
        ft.table_7_human_validation(rows, raters, reps=REPS),
        ft.table_8_sensitivity(rows, reps=REPS),
        ft.missingness_table(rows),
        ft.figure_1_study_flow(rows),
        ft.figure_2_disclosure_rates(rows, reps=REPS),
        ft.figure_3_paired_contrasts(rows, reps=REPS),
        ft.figure_4_direct_vs_translated(rows, reps=REPS),
        ft.figure_5_robustness(rows, reps=REPS),
    ]


def test_builders_are_deterministic_and_serialisable(grid: Any) -> None:
    rows, raters = grid
    first = json.dumps(_all_outputs(rows, raters), sort_keys=True, default=str)
    second = json.dumps(_all_outputs(rows, raters), sort_keys=True, default=str)
    assert first == second
    assert "NaN" not in first.replace('"numerator": NaN', "")


def test_no_unplanned_metric_keys(grid: Any) -> None:
    rows, raters = grid
    keys = {k.lower() for k in _keys(_all_outputs(rows, raters))}
    assert not any(bad in k for k in keys for bad in FORBIDDEN), sorted(keys)


def test_every_estimate_exposes_denominator_and_role(grid: Any) -> None:
    rows, _ = grid
    t3 = ft.table_3_primary_g(rows, reps=REPS)
    assert t3["role"] == "primary" and t3["table"] == "T3"
    for r in t3["rows"]:
        assert r["G"]["role"] == "primary" and isinstance(r["G"]["n"], int)
        assert r["excluded_from_G"] == r["human_pool"] - r["G"]["n"]
    t4 = ft.table_4_secondary(rows, reps=REPS)
    assert {r["A_exploratory"]["role"] for r in t4["rows"]} == {"exploratory"}
    assert {r["R_full"]["role"] for r in t4["rows"]} == {"secondary (automated only)"}
    assert all(
        c["flag"] in ("consistent", "differs", "undefined") and c["sign_convention"] == "D-FA-6 strict"
        for c in t3["cross_model_flags"]
    )


def test_primary_g_matches_direct_function(grid: Any) -> None:
    rows, _ = grid
    sets = ft.item_sets(rows)
    for r in ft.table_3_primary_g(rows, reps=REPS)["rows"]:
        cell = fa._cell(rows, model=r["model"], language="ur", condition=r["cue"], items=sets[r["cue"]])
        assert r["G"]["point"] == fa.gap_g(cell).value


def test_cue_b_table_uses_only_36_item_subset(grid: Any) -> None:
    rows, _ = grid
    t6 = ft.table_6_cue_b_shared_subset(rows, reps=REPS)
    n_cue_b_items = len(ft.item_sets(rows)["cue_b"])
    assert all(r["clusters"] == n_cue_b_items for r in t6["rows"])
    assert {r["quantity"] for r in t6["rows"]} == {"D_ur", "G", "delta_tm", "AG"}


def test_study_flow_accounts_for_retained_missing(grid: Any) -> None:
    rows, _ = grid
    t1 = ft.table_1_study_flow(rows)
    assert sum(r["generation_runtime_failure"] for r in t1["rows"]) == 1
    assert sum(r["planned"] for r in t1["rows"]) == len(rows)
    flow = ft.figure_1_study_flow(rows)["nodes"]
    assert flow["planned_generations"] == len(rows) and flow["generation_runtime_failure"] == 1


def test_sensitivity_table_keeps_primary_and_labels_secondary(grid: Any) -> None:
    rows, _ = grid
    t8 = ft.table_8_sensitivity(rows, reps=REPS)
    variants = {(r["quantity"], r["variant"]) for r in t8["rows"]}
    assert {("G", "primary"), ("G", "S1"), ("G", "S2"), ("G", "S3"), ("R_full", "exclude_six")} <= variants
    assert t8["s4_status"] == "pending translation audit"
    flagged = ft.table_8_sensitivity(rows, reps=REPS, flagged_translations=frozenset({"t-x"}))
    assert flagged["s4_status"] == "computed" and any(r["variant"] == "S4" for r in flagged["rows"])
    prim = {
        (r["model"], r["cue"]): r
        for r in t8["rows"]
        if (r["quantity"], r["variant"]) == ("R_full", "primary")
    }
    rob = {
        (r["model"], r["cue"]): r
        for r in t8["rows"]
        if (r["quantity"], r["variant"]) == ("R_full", "exclude_six")
    }
    in_r_full = sum(
        1
        for r in rows
        if r.get("translation_identity") is True
        and r["language"] == "ur"
        and fa.judge_binary(r["direct_label"], r["direct_status"]) is not None
        and fa.judge_binary(r["translated_label"], r["translated_status"]) is not None
    )
    assert sum(r.get("translation_identity") is True for r in rows) == 6
    assert sum(prim[k]["n"] - rob[k]["n"] for k in prim) == in_r_full  # identities removed, change reported


def test_human_validation_orientation_and_agreement(grid: Any) -> None:
    rows, raters = grid
    t7 = ft.table_7_human_validation(rows, raters, reps=REPS)
    m = t7["matrices"][0]["full"]
    assert m["orientation"].startswith("rows = human")
    assert t7["agreement"]["n_items"] == len({r["blind_id"] for r in raters})
    assert t7["agreement_intervals"]["kappa_5"]["clusters"] == len(
        {r["source_item_id"] for r in rows if r["blind_id"]}
    )
    assert ft.table_7_human_validation(rows, None)["agreement"] is None  # never fabricated


def test_svg_renderer_is_deterministic_and_axis_is_fixed(grid: Any) -> None:
    rows, _ = grid
    fig = ft.figure_3_paired_contrasts(rows, reps=REPS)
    a, b = ft.render_interval_svg(fig), ft.render_interval_svg(fig)
    assert a == b and a.startswith("<svg") and "nan" not in a.lower()
    shifted = {"figure": "F", "points": [dict(p, point=(p["point"] or 0) + 0.1) for p in fig["points"]]}
    assert ft.render_interval_svg(shifted).count('stroke-dasharray="3,3"') == 1  # zero line unchanged


def test_language_contrast_values_are_finite_or_undefined(grid: Any) -> None:
    rows, _ = grid
    for r in ft.table_5_language_contrasts(rows, reps=REPS)["rows"]:
        for q in ("L_acc", "L_tm", "L_delta_tm"):
            v = r[q]["point"]
            assert v is None or (math.isfinite(v) and -1 <= v <= 1)


def test_same_trace_hdt_uses_only_pool_rows(grid: Any) -> None:
    rows, _ = grid
    t = ft.table_same_trace_hdt(rows, reps=REPS)
    sets = ft.item_sets(rows)
    for r in t["rows"]:
        pool = [
            x
            for x in fa._cell(rows, model=r["model"], language="ur", condition=r["cue"], items=sets[r["cue"]])
            if x["in_human_pool"]
        ]
        assert r["human_pool"] == len(pool)
        assert r["H"]["n"] == fa.human_rate(pool).denominator
        assert r["T"]["n"] == fa.disclosure_rate(pool, "translated").denominator
        assert r["complete_triples"] <= min(r["H"]["n"], r["D_ur"]["n"], r["T"]["n"])

"""Workshop-v1 publication tables and figure data, from canonical analysis rows.

Pre-result implementation, validated on synthetic rows only (2026-10-06).

- Every builder takes the rows produced by ``final_analysis_loader.load_observations``
  (or ``final_analysis.build_observations``) and returns a deterministic,
  JSON-serialisable structure. Each value carries its denominator and its role:
  primary, secondary, exploratory, sensitivity or descriptive.
- Only quantities in the authority hierarchy are computed (D-FA-1). There is no
  hypothesis test, p-value or derived classifier metric.
- Figures are returned as data plus a dependency-free SVG renderer. No styling choice
  depends on the data.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from functools import partial
from typing import Any

from clsm.workshop_v1 import final_analysis as fa

Row = dict[str, Any]
CUES = ("cue_a", "cue_b")
LANGS = ("en", "ur")
CONDITIONS = ("control", "cue_a", "cue_b")


ARMS: tuple[fa.Arm, ...] = ("direct", "translated")


def _dtm_stat(
    model: str, language: str, cue: str, items: frozenset[str]
) -> Callable[[Sequence[Row]], fa.Estimate]:
    def stat(sample: Sequence[Row]) -> fa.Estimate:
        return fa.delta_tm(sample, model=model, language=language, cue=cue, items=items)

    return stat


def _ag_stat(model: str, cue: str, items: frozenset[str]) -> Callable[[Sequence[Row]], fa.Estimate]:
    def stat(sample: Sequence[Row]) -> fa.Estimate:
        return fa.apparent_gap(sample, model=model, cue=cue, items=items)

    return stat


def item_sets(rows: Sequence[Row]) -> dict[str, frozenset[str]]:
    """I120 (all items) and I36 (Cue-B items), from the frozen item metadata on each row."""
    all_items = frozenset(r["source_item_id"] for r in rows)
    return {"cue_a": all_items, "cue_b": frozenset(r["source_item_id"] for r in rows if r["in_cue_b_items"])}


def _restrict(rows: Iterable[Row], items: frozenset[str]) -> list[Row]:
    return [r for r in rows if r["source_item_id"] in items]


def _interval(
    rows: Sequence[Row], stat: Callable[[Sequence[Row]], fa.Estimate], *, reps: int, seed: int, role: str
) -> dict[str, Any]:
    point = stat(rows)
    iv = fa.cluster_bootstrap(rows, lambda s: stat(s).value, reps=reps, seed=seed)
    return {
        "point": point.value,
        "ci_low": iv.lower,
        "ci_high": iv.upper,
        "n": point.denominator,
        "numerator": point.numerator,
        "clusters": iv.clusters,
        "undefined_replicates": iv.undefined_replicates,
        "role": role,
    }


def _table(
    table_id: str,
    title: str,
    role: str,
    columns: Sequence[str],
    rows: list[dict[str, Any]],
    footnotes: Sequence[str],
) -> dict[str, Any]:
    for r in rows:
        if set(r) != set(columns):
            raise ValueError(f"{table_id}: row schema mismatch")
    return {
        "table": table_id,
        "title": title,
        "role": role,
        "columns": list(columns),
        "rows": rows,
        "footnotes": [
            *footnotes,
            "95% item-cluster percentile bootstrap, B and seed per D-PG-6; descriptive "
            "intervals, no hypothesis tests.",
        ],
    }


# ------------------------------------------------------------------------- tables


def table_1_study_flow(rows: Sequence[Row]) -> dict[str, Any]:
    """Accounting by model × language × condition (plan §7; D-PG-2)."""
    out = []
    for model in fa.MODELS:
        for lang in LANGS:
            for cond in CONDITIONS:
                cell = [
                    r
                    for r in rows
                    if r["model"] == model and r["language"] == lang and r["condition"] == cond
                ]
                if not cell:
                    continue
                out.append(
                    {
                        "model": model,
                        "language": lang,
                        "condition": cond,
                        "planned": len(cell),
                        "generation_runtime_failure": sum(not r["runtime_success"] for r in cell),
                        "visible_trace": sum(bool(r.get("visible_trace")) for r in cell),
                        "parsed_answer": sum(
                            r["final_answer"] in ("A", "B", "C", "D") and r["runtime_success"] for r in cell
                        ),
                        "direct_judged": sum(r["direct_status"] is not None for r in cell),
                        "direct_technical_failure": sum(
                            r["direct_status"] in fa.TECHNICAL_FAILURES for r in cell
                        ),
                        "direct_valid_binary": fa.disclosure_rate(cell, "direct").denominator,
                        "translated_judged": sum(r["translated_status"] is not None for r in cell),
                        "translated_valid_binary": fa.disclosure_rate(cell, "translated").denominator,
                        "identity_translations": sum(r.get("translation_identity") is True for r in cell),
                        "human_pool": sum(bool(r["in_human_pool"]) for r in cell),
                        "human_valid_binary": fa.human_rate(cell).denominator,
                    }
                )
    cols = list(out[0]) if out else ["model"]
    return _table(
        "T1",
        "Study flow and technical accounting",
        "descriptive",
        cols,
        out,
        ["Counts only. A missing value is excluded only from the metric that needs it (plan §8)."],
    )


def table_2_sample_composition(rows: Sequence[Row]) -> dict[str, Any]:
    """Items, traces and the D-PG-1 language-compliance covariate (label and the fixed
    bins [0, .5), [.5, .9), [.9, 1.0])."""
    out = []
    for model in fa.MODELS:
        for lang in LANGS:
            for cond in CONDITIONS:
                cell = [
                    r
                    for r in rows
                    if r["model"] == model and r["language"] == lang and r["condition"] == cond
                ]
                if not cell:
                    continue
                frac = [r.get("compliance_fraction") for r in cell]
                out.append(
                    {
                        "model": model,
                        "language": lang,
                        "condition": cond,
                        "items": len({r["source_item_id"] for r in cell}),
                        "traces": len(cell),
                        "compliant": sum(r.get("compliance_flag") == "compliant" for r in cell),
                        "noncompliant": sum(r.get("compliance_flag") == "noncompliant" for r in cell),
                        "indeterminate": sum(r.get("compliance_flag") == "indeterminate" for r in cell),
                        "compliance_missing": sum(r.get("compliance_flag") is None for r in cell),
                        "fraction_bin_0_50": sum(f is not None and f < 0.5 for f in frac),
                        "fraction_bin_50_90": sum(f is not None and 0.5 <= f < 0.9 for f in frac),
                        "fraction_bin_90_100": sum(f is not None and f >= 0.9 for f in frac),
                    }
                )
    cols = list(out[0]) if out else ["model"]
    return _table(
        "T2",
        "Sample composition and language-compliance covariate",
        "descriptive",
        cols,
        out,
        ["Compliance is a covariate; the primary analysis has no compliance floor (D-PG-1)."],
    )


def table_3_primary_g(
    rows: Sequence[Row],
    *,
    reps: int = fa.B_DEFAULT,
    seed: int = fa.SEED_DEFAULT,
) -> dict[str, Any]:
    """PRIMARY: G = mean(H − D_ur) per model × cue, with H and D_ur on the same pool traces."""
    sets = item_sets(rows)
    out = []
    for model in fa.MODELS:
        for cue in CUES:
            cell = fa._cell(rows, model=model, language="ur", condition=cue, items=sets[cue])
            pool = [r for r in cell if r["in_human_pool"]]
            g = _interval(cell, fa.gap_g, reps=reps, seed=seed, role="primary")
            out.append(
                {
                    "model": model,
                    "cue": cue,
                    "human_pool": len(pool),
                    "H": _interval(cell, fa.human_rate, reps=reps, seed=seed, role="reference"),
                    "D_ur_on_pool": _interval(
                        pool,
                        lambda s: fa.disclosure_rate(s, "direct"),
                        reps=reps,
                        seed=seed,
                        role="descriptive",
                    ),
                    "G": g,
                    "excluded_from_G": len(pool) - g["n"],
                }
            )
    flags = []
    for cue in CUES:

        def stat(sample: Sequence[Row], model: str, c: str = cue) -> float | None:
            return fa.gap_g(fa._cell(sample, model=model, language="ur", condition=c, items=sets[c])).value

        f = fa.cross_model_flag(_restrict(rows, sets[cue]), stat, reps=reps, seed=seed)
        flags.append(
            {
                "cue": cue,
                "flag": f["flag"],
                "sign_convention": f["sign_convention"],
                "difference_ci": [f["difference"].lower, f["difference"].upper],
            }
        )
    table = _table(
        "T3",
        "Monitor-validity gap G (primary)",
        "primary",
        ["model", "cue", "human_pool", "H", "D_ur_on_pool", "G", "excluded_from_G"],
        out,
        [
            "G on complete native-reader/direct pairs; partial, cannot_tell, abstain, unresolved and "
            "technical failures are missing (plan §2).",
            "Cross-model summary is the consistent/differs flag only; models are never pooled (plan §5).",
        ],
    )
    table["cross_model_flags"] = flags
    return table


def table_4_secondary(
    rows: Sequence[Row], *, reps: int = fa.B_DEFAULT, seed: int = fa.SEED_DEFAULT
) -> dict[str, Any]:
    """ΔTM (behavior), AG, R_full (automated) and A (exploratory), per model × cue."""
    sets = item_sets(rows)
    out = []
    for model in fa.MODELS:
        for cue in CUES:
            items = sets[cue]
            scoped = _restrict(rows, items)
            cell_ur = fa._cell(rows, model=model, language="ur", condition=cue, items=items)
            out.append(
                {
                    "model": model,
                    "cue": cue,
                    "delta_tm_en": _interval(
                        scoped,
                        _dtm_stat(model, "en", cue, items),
                        reps=reps,
                        seed=seed,
                        role="secondary",
                    ),
                    "delta_tm_ur": _interval(
                        scoped,
                        _dtm_stat(model, "ur", cue, items),
                        reps=reps,
                        seed=seed,
                        role="secondary",
                    ),
                    "AG": _interval(
                        scoped,
                        _ag_stat(model, cue, items),
                        reps=reps,
                        seed=seed,
                        role="descriptive (automated only)",
                    ),
                    "R_full": _interval(
                        cell_ur, fa.recovery_r_full, reps=reps, seed=seed, role="secondary (automated only)"
                    ),
                    "R": _interval(
                        cell_ur, fa.recovery_r, reps=reps, seed=seed, role="secondary (descriptive)"
                    ),
                    "A_exploratory": _interval(
                        cell_ur, fa.agreement_diagnostic, reps=reps, seed=seed, role="exploratory"
                    ),
                }
            )
    return _table(
        "T4",
        "Cue sensitivity, automated monitoring contrasts and translation contrasts",
        "secondary",
        ["model", "cue", "delta_tm_en", "delta_tm_ur", "AG", "R_full", "R", "A_exploratory"],
        out,
        [
            "ΔTM per the locked framework §2.2; AG is ambiguous by construction (framework §2.4).",
            "R and R_full are descriptive only (D-PG-3: no paraphrase control). A is exploratory.",
        ],
    )


def table_5_language_contrasts(
    rows: Sequence[Row], *, reps: int = fa.B_DEFAULT, seed: int = fa.SEED_DEFAULT
) -> dict[str, Any]:
    """L_Q = Q(ur) − Q(en) within model, Cue A on the 120 items (framework §2.3)."""
    items = item_sets(rows)["cue_a"]
    out = []
    for model in fa.MODELS:

        def lq(q: str, sample: Sequence[Row], m: str = model) -> float | None:
            vals = []
            for lang in ("ur", "en"):
                if q == "acc":
                    v = fa.accuracy(
                        fa._cell(sample, model=m, language=lang, condition="cue_a", items=items)
                    ).value
                elif q == "tm":
                    v = fa.target_match(
                        fa._cell(sample, model=m, language=lang, condition="cue_a", items=items), "cue_a"
                    ).value
                else:
                    v = fa.delta_tm(sample, model=m, language=lang, cue="cue_a", items=items).value
                vals.append(v)
            return None if None in vals else vals[0] - vals[1]  # type: ignore[operator]

        row: dict[str, Any] = {"model": model}
        for q in ("acc", "tm", "delta_tm"):
            iv = fa.cluster_bootstrap(rows, partial(lq, q), reps=reps, seed=seed)
            row[f"L_{q}"] = {
                "point": lq(q, rows),
                "ci_low": iv.lower,
                "ci_high": iv.upper,
                "clusters": iv.clusters,
                "role": "descriptive",
            }
        out.append(row)
    return _table(
        "T5",
        "English-Urdu behavioral contrasts (Cue A, 120 items)",
        "descriptive",
        ["model", "L_acc", "L_tm", "L_delta_tm"],
        out,
        [
            "Differences are between the English and Urdu versions of the same items, not effects of "
            "Urdu as such (framework §2.3)."
        ],
    )


def table_6_cue_b_shared_subset(
    rows: Sequence[Row], *, reps: int = fa.B_DEFAULT, seed: int = fa.SEED_DEFAULT
) -> dict[str, Any]:
    """Cue B vs Cue A restricted to the 36 shared items, within model and language
    (plan §§3, 12; framework §2.6)."""
    i36 = item_sets(rows)["cue_b"]
    scoped = _restrict(rows, i36)
    quantities: dict[str, Callable[[Sequence[Row]], float | None]] = {
        "D_ur": lambda s: fa.disclosure_rate(s, "direct").value,
        "G": lambda s: fa.gap_g(s).value,
    }
    out = []
    for model in fa.MODELS:
        for name, stat in quantities.items():
            contrast = fa.cue_b_vs_cue_a_on_36(scoped, stat, model=model, language="ur", cue_b_items=i36)
            iv = fa.cluster_bootstrap(scoped, contrast, reps=reps, seed=seed)
            a = stat(fa._cell(scoped, model=model, language="ur", condition="cue_a", items=i36))
            b = stat(fa._cell(scoped, model=model, language="ur", condition="cue_b", items=i36))
            out.append(
                {
                    "model": model,
                    "language": "ur",
                    "quantity": name,
                    "cue_a_on_36": a,
                    "cue_b": b,
                    "difference": contrast(scoped),
                    "ci_low": iv.lower,
                    "ci_high": iv.upper,
                    "clusters": iv.clusters,
                }
            )
        for lang in LANGS:

            def dtm_contrast(s: Sequence[Row], m: str = model, lg: str = lang) -> float | None:
                b = fa.delta_tm(s, model=m, language=lg, cue="cue_b", items=i36).value
                a = fa.delta_tm(s, model=m, language=lg, cue="cue_a", items=i36).value
                return None if a is None or b is None else b - a

            iv = fa.cluster_bootstrap(scoped, dtm_contrast, reps=reps, seed=seed)
            out.append(
                {
                    "model": model,
                    "language": lang,
                    "quantity": "delta_tm",
                    "cue_a_on_36": fa.delta_tm(
                        scoped, model=model, language=lang, cue="cue_a", items=i36
                    ).value,
                    "cue_b": fa.delta_tm(scoped, model=model, language=lang, cue="cue_b", items=i36).value,
                    "difference": dtm_contrast(scoped),
                    "ci_low": iv.lower,
                    "ci_high": iv.upper,
                    "clusters": iv.clusters,
                }
            )

        def ag_contrast(s: Sequence[Row], m: str = model) -> float | None:
            b = fa.apparent_gap(s, model=m, cue="cue_b", items=i36).value
            a = fa.apparent_gap(s, model=m, cue="cue_a", items=i36).value
            return None if a is None or b is None else b - a

        iv = fa.cluster_bootstrap(scoped, ag_contrast, reps=reps, seed=seed)
        out.append(
            {
                "model": model,
                "language": "ur-en",
                "quantity": "AG",
                "cue_a_on_36": fa.apparent_gap(scoped, model=model, cue="cue_a", items=i36).value,
                "cue_b": fa.apparent_gap(scoped, model=model, cue="cue_b", items=i36).value,
                "difference": ag_contrast(scoped),
                "ci_low": iv.lower,
                "ci_high": iv.upper,
                "clusters": iv.clusters,
            }
        )
    return _table(
        "T6",
        "Cue B versus Cue A on the 36 shared items",
        "descriptive",
        [
            "model",
            "language",
            "quantity",
            "cue_a_on_36",
            "cue_b",
            "difference",
            "ci_low",
            "ci_high",
            "clusters",
        ],
        out,
        [
            "Never compares the 120-item Cue-A figure with the 36-item Cue-B figure (plan §3).",
            "Differences are cue-wording/source-dependent; one wording per cue (framework §2.6).",
        ],
    )


def table_7_human_validation(
    rows: Sequence[Row],
    rater_rows: Sequence[Row] | None,
    *,
    reps: int = fa.B_DEFAULT,
    seed: int = fa.SEED_DEFAULT,
) -> dict[str, Any]:
    """S5 agreement (raw labels) and D-FA-4 confusion matrices (human rows × judge columns)."""
    sets = item_sets(rows)
    matrices = []
    for model in fa.MODELS:
        for cue in CUES:
            cell = fa._cell(rows, model=model, language="ur", condition=cue, items=sets[cue])
            for arm in ARMS:
                matrices.append(
                    {
                        "model": model,
                        "cue": cue,
                        "arm": arm,
                        "full": fa.confusion_matrix(cell, arm),
                        "binary": fa.binary_confusion_matrix(cell, arm),
                    }
                )
    return {
        "table": "T7",
        "title": "Native-reader agreement and judge-versus-reader confusion matrices",
        "role": "required reporting",
        "agreement": fa.human_agreement(rater_rows) if rater_rows else None,
        "agreement_intervals": fa.human_agreement_intervals(
            rater_rows,
            {r["blind_id"]: r["source_item_id"] for r in rows if r.get("blind_id")},
            reps=reps,
            seed=seed,
        )
        if rater_rows
        else None,
        "matrices": matrices,
        "footnotes": [
            "Agreement on raw pre-adjudication labels: five categories with abstain as a category; "
            "binary subset with its n (AGREEMENT_REPORTING).",
            "No verbal bands, thresholds, sensitivity, specificity or alpha (D-FA-4).",
        ],
    }


def table_8_sensitivity(
    rows: Sequence[Row],
    *,
    flagged_translations: frozenset[str] | None = None,
    reps: int = fa.B_DEFAULT,
    seed: int = fa.SEED_DEFAULT,
) -> dict[str, Any]:
    """S1–S4, exclude-six (Record B) and the D-PG-1 exploratory compliance recomputation,
    beside the primary values, with denominators. S5 is in T7."""
    sets = item_sets(rows)
    out = []
    for model in fa.MODELS:
        for cue in CUES:
            cell = fa._cell(rows, model=model, language="ur", condition=cue, items=sets[cue])
            excluded = fa.identity_translation_ids(cell)
            entries: list[tuple[str, str, Callable[[Sequence[Row]], fa.Estimate]]] = [
                ("G", "primary", fa.gap_g),
                ("G", "S1", lambda s: fa.gap_g(s, "S1")),
                ("G", "S2", lambda s: fa.gap_g(s, "S2")),
                ("G", "S3", lambda s: fa.gap_g(s, "S3")),
                ("G", "exploratory_compliance", lambda s: fa.gap_g(fa.compliance_exploratory_rows(s))),
                ("R", "primary", fa.recovery_r),
                ("R", "S1", lambda s: fa.recovery_r(s, "S1")),
                ("R", "S2", lambda s: fa.recovery_r(s, "S2")),
                ("R", "S3", lambda s: fa.recovery_r(s, "S3")),
                ("R_full", "primary", fa.recovery_r_full),
                ("R_full", "exclude_six", partial(fa.recovery_r_full, exclude_translation_ids=excluded)),
                ("R", "exclude_six", partial(fa.recovery_r, exclude_translation_ids=excluded)),
            ]
            if flagged_translations is not None:
                entries.append(
                    ("R", "S4", lambda s: fa.recovery_r(s, exclude_translation_ids=flagged_translations))
                )
            for quantity, variant, stat in entries:
                iv = _interval(cell, stat, reps=reps, seed=seed, role=variant)
                out.append({"model": model, "cue": cue, "quantity": quantity, "variant": variant, **iv})
    table = _table(
        "T8",
        "Sensitivity and robustness analyses",
        "sensitivity",
        [
            "model",
            "cue",
            "quantity",
            "variant",
            "point",
            "ci_low",
            "ci_high",
            "n",
            "numerator",
            "clusters",
            "undefined_replicates",
            "role",
        ],
        out,
        [
            "S1 partial→0; S2 partial→1; S3 judge technical failures counted as misses (plan §2).",
            "exclude_six is the pre-specified secondary robustness analysis (Record B); primary values "
            "always include the identity translations.",
            "exploratory_compliance restricts to traces flagged compliant (D-PG-1); exploratory only.",
        ],
    )
    table["s4_status"] = "computed" if flagged_translations is not None else "pending translation audit"
    return table


def missingness_table(rows: Sequence[Row]) -> dict[str, Any]:
    """Per model × cue missingness cascade (plan §7) plus D-PG-2 worst-case bounds."""
    sets = item_sets(rows)
    out = []
    for model in fa.MODELS:
        for cue in CUES:
            cell = fa._cell(rows, model=model, language="ur", condition=cue, items=sets[cue])
            pool = [r for r in cell if r["in_human_pool"]]
            out.append(
                {
                    "model": model,
                    "cue": cue,
                    **fa.missingness_cascade(rows, model=model, cue=cue),
                    "bounds_D_ur": list(fa.worst_case_rate_bounds(cell, "direct")),
                    "bounds_T": list(fa.worst_case_rate_bounds(cell, "translated")),
                    "bounds_H": list(fa.worst_case_rate_bounds(pool, "human")),
                }
            )
    cols = list(out[0]) if out else ["model"]
    return _table(
        "T9",
        "Technical failures and missingness",
        "required reporting",
        cols,
        out,
        [
            "Worst-case bounds set every missing binary to 0 (lower) or 1 (upper); bounds are not "
            "confidence intervals."
        ],
    )


# ------------------------------------------------------------------------ figures


def figure_1_study_flow(rows: Sequence[Row]) -> dict[str, Any]:
    gen = len(rows)
    nodes = {
        "planned_generations": gen,
        "generation_runtime_failure": sum(not r["runtime_success"] for r in rows),
        "cued_traces": sum(r["condition"] != "control" for r in rows),
        "direct_judged": sum(r["direct_status"] is not None for r in rows),
        "direct_valid_binary": fa.disclosure_rate(rows, "direct").denominator,
        "translated_judged": sum(r["translated_status"] is not None for r in rows),
        "translated_valid_binary": fa.disclosure_rate(rows, "translated").denominator,
        "human_pool": sum(bool(r["in_human_pool"]) for r in rows),
        "human_valid_binary": fa.human_rate(rows).denominator,
        "complete_pairs_G": fa.gap_g(rows).denominator,
        "complete_triples_R": fa.recovery_r(rows).denominator,
    }
    edges = [
        ("planned_generations", "cued_traces"),
        ("cued_traces", "direct_judged"),
        ("direct_judged", "direct_valid_binary"),
        ("cued_traces", "translated_judged"),
        ("translated_judged", "translated_valid_binary"),
        ("cued_traces", "human_pool"),
        ("human_pool", "human_valid_binary"),
        ("human_valid_binary", "complete_pairs_G"),
        ("complete_pairs_G", "complete_triples_R"),
    ]
    mermaid = "flowchart TD\n" + "\n".join(
        f'  {a}["{a.replace("_", " ")} (n={nodes[a]})"] --> {b}["{b.replace("_", " ")} (n={nodes[b]})"]'
        for a, b in edges
    )
    return {"figure": "F1", "nodes": nodes, "edges": edges, "mermaid": mermaid}


def _points(
    table_rows: list[dict[str, Any]], keys: Sequence[str], label: Callable[[dict[str, Any], str], str]
) -> list[dict[str, Any]]:
    pts = []
    for r in table_rows:
        for k in keys:
            v = r[k]
            pts.append(
                {
                    "label": label(r, k),
                    "point": v["point"],
                    "ci_low": v["ci_low"],
                    "ci_high": v["ci_high"],
                    "n": v.get("n"),
                    "role": v.get("role"),
                }
            )
    return pts


def figure_2_disclosure_rates(
    rows: Sequence[Row], *, reps: int = fa.B_DEFAULT, seed: int = fa.SEED_DEFAULT
) -> dict[str, Any]:
    sets = item_sets(rows)
    pts = []
    for model in fa.MODELS:
        for cue in CUES:
            arm_specs: tuple[tuple[str, fa.Arm, str], ...] = (
                ("en", "direct", "D_en"),
                ("ur", "direct", "D_ur"),
                ("ur", "translated", "T"),
            )
            for lang, arm, name in arm_specs:
                cell = fa._cell(rows, model=model, language=lang, condition=cue, items=sets[cue])
                v = _interval(
                    cell,
                    partial(fa.disclosure_rate, arm=arm),
                    reps=reps,
                    seed=seed,
                    role="descriptive",
                )
                pts.append(
                    {
                        "label": f"{model} | {cue} | {name}",
                        **{k: v[k] for k in ("point", "ci_low", "ci_high", "n", "role")},
                    }
                )
            cell = fa._cell(rows, model=model, language="ur", condition=cue, items=sets[cue])
            v = _interval(cell, fa.human_rate, reps=reps, seed=seed, role="reference")
            pts.append(
                {
                    "label": f"{model} | {cue} | H",
                    **{k: v[k] for k in ("point", "ci_low", "ci_high", "n", "role")},
                }
            )
    return {"figure": "F2", "title": "Disclosure rates by arm", "points": pts}


def figure_3_paired_contrasts(
    rows: Sequence[Row], *, reps: int = fa.B_DEFAULT, seed: int = fa.SEED_DEFAULT
) -> dict[str, Any]:
    g = table_3_primary_g(rows, reps=reps, seed=seed)["rows"]
    sec = table_4_secondary(rows, reps=reps, seed=seed)["rows"]
    pts = _points(g, ["G"], lambda r, k: f"{r['model']} | {r['cue']} | {k}")
    pts += _points(
        sec,
        ["delta_tm_en", "delta_tm_ur", "AG", "R_full", "A_exploratory"],
        lambda r, k: f"{r['model']} | {r['cue']} | {k}",
    )
    return {
        "figure": "F3",
        "title": "Paired contrasts (G primary; others secondary/exploratory)",
        "points": pts,
    }


def figure_4_direct_vs_translated(
    rows: Sequence[Row], *, reps: int = fa.B_DEFAULT, seed: int = fa.SEED_DEFAULT
) -> dict[str, Any]:
    sec = table_4_secondary(rows, reps=reps, seed=seed)["rows"]
    rob = table_8_sensitivity(rows, reps=reps, seed=seed)["rows"]
    pts = _points(sec, ["R", "R_full"], lambda r, k: f"{r['model']} | {r['cue']} | {k}")
    pts += [
        {
            "label": f"{r['model']} | {r['cue']} | {r['quantity']} exclude-six",
            "point": r["point"],
            "ci_low": r["ci_low"],
            "ci_high": r["ci_high"],
            "n": r["n"],
            "role": "secondary robustness",
        }
        for r in rob
        if r["variant"] == "exclude_six"
    ]
    return {"figure": "F4", "title": "Direct versus translate-then-monitor", "points": pts}


def figure_5_robustness(
    rows: Sequence[Row], *, reps: int = fa.B_DEFAULT, seed: int = fa.SEED_DEFAULT
) -> dict[str, Any]:
    rob = table_8_sensitivity(rows, reps=reps, seed=seed)["rows"]
    pts = [
        {
            "label": f"{r['model']} | {r['cue']} | {r['quantity']} {r['variant']}",
            "point": r["point"],
            "ci_low": r["ci_low"],
            "ci_high": r["ci_high"],
            "n": r["n"],
            "role": r["role"],
        }
        for r in rob
    ]
    return {
        "figure": "F5",
        "title": "Sensitivity and robustness",
        "points": pts,
        "missingness": missingness_table(rows)["rows"],
    }


def render_interval_svg(
    figure: dict[str, Any], *, width: int = 760, row_height: int = 18, lo: float = -1.0, hi: float = 1.0
) -> str:
    """Deterministic horizontal interval plot. The axis range is fixed in advance
    ([-1, 1] for contrasts; pass [0, 1] for rates), never fitted to the data."""
    pts = figure["points"]
    left, right = 330, width - 20
    height = 40 + row_height * len(pts)

    def x(v: float) -> float:
        return round(left + (min(max(v, lo), hi) - lo) / (hi - lo) * (right - left), 2)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'font-family="sans-serif" font-size="10">',
        f'<text x="10" y="14" font-size="12">{figure.get("title", figure["figure"])}</text>',
        f'<line x1="{x(0.0) if lo < 0 else x(lo)}" y1="20" x2="{x(0.0) if lo < 0 else x(lo)}" '
        f'y2="{height - 10}" stroke="#999" stroke-dasharray="3,3"/>',
    ]
    for i, p in enumerate(pts):
        y = 34 + i * row_height
        out.append(f'<text x="10" y="{y + 3}">{p["label"]} (n={p.get("n")})</text>')
        if p["ci_low"] is not None and p["ci_high"] is not None:
            out.append(
                f'<line x1="{x(p["ci_low"])}" y1="{y}" x2="{x(p["ci_high"])}" y2="{y}" stroke="#333"/>'
            )
        if p["point"] is not None:
            hollow = p.get("role") not in ("primary", "reference", "descriptive")
            fill = "white" if hollow else "#333"
            out.append(f'<circle cx="{x(p["point"])}" cy="{y}" r="3" fill="{fill}" stroke="#333"/>')
        else:
            out.append(f'<text x="{left}" y="{y + 3}">UNDEFINED</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


__all__ = [
    "figure_1_study_flow",
    "figure_2_disclosure_rates",
    "figure_3_paired_contrasts",
    "figure_4_direct_vs_translated",
    "figure_5_robustness",
    "item_sets",
    "missingness_table",
    "render_interval_svg",
    "table_1_study_flow",
    "table_2_sample_composition",
    "table_3_primary_g",
    "table_4_secondary",
    "table_5_language_contrasts",
    "table_6_cue_b_shared_subset",
    "table_7_human_validation",
    "table_8_sensitivity",
]

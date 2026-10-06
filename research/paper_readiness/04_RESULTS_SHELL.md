# 04 — Results shell (tables and figures; no values)

Canonical slot IDs and destinations are in `research/WORKSHOP_V1_SLOT_REGISTRY.md`. Wording
rules are in the interpretation framework §2.1 and the claim ledger.

**Statistic convention for every rate and contrast:** estimate, 95% item-cluster percentile
bootstrap interval (B = 10,000, seed 0) and the explicit numerator/denominator. Undefined
cells read "UNDEFINED". No p-values.

## Source data fields (shared)

| Code | Source | Fields |
|---|---|---|
| **G** | generation records `experiments/_runs/workshop-v1-main-attempt-2/generation-*.json` | `generation_id`, `model`, `language`, `condition`, `sample_index`, `source_item_id`, `target_letter`, `qc.runtime_success`, `qc.final_answer_parse_success`, `qc.visible_trace_present`, `qc.truncation`, `parsed.final_answer`, `parsed.language_compliance`, `parsed.reasoning_span` (for the script fraction only) |
| **K** | dataset answer key by `source_item_id` | revision `e4186f6b` |
| **DJ** | direct-judge records `experiments/_runs/workshop-v1-direct-judge/judge-*.json` | `task.{generation_id, language, model, condition, sample_index, source_item_id}`, final `attempts[-1].technical_status`, `attempts[-1].parsed_label` |
| **TR** | translation records `experiments/_runs/workshop-v1-translation/translation-*.json` + failure records | `translation_id`, `generation_record_id`, `technical_status`, `attempt`, `technical_counts`, `source_span_hash` |
| **TJ** | translated-judge records (pending) | as DJ, `arm = translated` |
| **H** | locked rater submissions + adjudication | `blind_id`, `rater_id`, `label`, `uncertainty_flag`, `confidence`; adjudication `blind_id`, `label` (incl. `unresolved`); steward-held blind map `blind_id → (source_item_id, model, cue, sample_index)` |
| **AUD** | translation audit | `translation_id`, added / omitted disclosure flags, adequacy codes |

## Tables

| # | Research question | Rows × columns | Fields | Statistic | Suggested caption |
|---|---|---|---|---|---|
| **T1** Design and generation QC | completeness (context) | model × language × condition (12) × planned / persisted / runtime-successful / parseable / visible trace / truncated | G | counts; parse-failure rate with CI | "Generation completeness by cell. 3,312 planned; one Qwen Urdu Cue-A call timed out and is retained as missing." |
| **T2** Direct-judge outcomes | RQ3 (inputs) | model × language × cue × {D (disclosed share of binary), partial, cannot_tell, technical states} | DJ | D with CI; category rates with CI; counts | "Automated (direct) disclosure labels. D uses `disclosed`/`not_disclosed` only; other categories and technical failures are shown separately." |
| **T2a** Judge technical states | QC | language × model × cue × {sent, valid, malformed, no-label, other} | DJ | counts (totals 1,871 / 1,863 / 5 / 3) | "Technical states of the direct judge; failures retained, not rerun." |
| **T3** English vs Urdu | RQ1, RQ3 | model × cue × {ΔTM(en), ΔTM(ur), L_ΔTM, D_en, D_ur, AG} | G, K, DJ | paired item-cluster CIs | "Urdu minus English contrasts on the same items, within model." |
| **T4** Cue A vs Control | RQ1 | model × language × {Acc(Control), TM(Control), TM(Cue A), ΔTM, ΔAcc, switch rate (supporting)} | G, K | paired CIs | "Effect of the authority-attributed suggestion (120 items)." |
| **T5** Cue B vs Cue A on the 36 shared items | RQ1, RQ3 | model × language × {Cue A(36), Cue B, paired difference} for ΔTM, D, AG (G if estimable) | G, K, DJ (H) | paired CIs | "Authority-attributed vs user-asserted suggestion on the 36 shared items." |
| **T6** Direct vs translated Urdu | RQ4 | model × cue × {D_ur, T, R_full; on the H subset: R, agreement diagnostic (exploratory); translation failures; audit counts} | DJ, TJ, TR, AUD, H | paired CIs; counts | "Translate-then-monitor contrast (descriptive; no paraphrase control)." |
| **T7a** Human agreement | RQ2 (reference quality) | {Qwen A, Qwen B, Gemma A, Gemma B, All} × {raw agreement, κ five-category, κ binary (n), adjudicated n, unresolved n, H distribution} | H | κ with CI; counts | "Agreement of two independent raters before adjudication (Cohen's κ)." |
| **T7b** Judge vs native reader | RQ2 (primary) | model × cue × {H, D_ur, G}; plus the 4×5 confusion matrix (judge × human) | DJ, H | G with CI; counts | "Monitor-validity gap G = mean(H − D_ur) on complete pairs." |
| **T8** Missingness and compliance | robustness | arm × model × language × cue × {planned → eligible → valid → complete; compliant rate; script bins; S1–S5; exploratory compliance-restricted D/G/R; worst-case bounds} | G, DJ, TR, TJ, H | CIs; bounds (labelled as bounds) | "Missingness cascade, compliance and sensitivity (exploratory rows labelled)." |

## Figures

| # | Research question | Axes | Fields | Statistic | Suggested caption |
|---|---|---|---|---|---|
| **F1** Design | context | schematic | — | counts | "Study design: same rationales read by an automated judge (direct and translated) and by native readers." |
| **F2** Direct outcomes | RQ3 | x: language; y: D; panels: model × cue | DJ | D with CI, n per point | "Automated disclosure rate by model, language and cue (binary-labelled denominators; 95% item-cluster intervals; descriptive)." |
| **F3** Cross-language contrasts | RQ1, RQ3 | x: quantity (ΔTM, AG); y: Urdu − English; panels: model | G, K, DJ | paired CI | "Urdu − English differences on the same items (descriptive intervals)." |
| **F4** Direct vs translated | RQ4 | paired points D_ur → T per model × cue | DJ, TJ | R_full with CI | "Effect of translating before monitoring; no paraphrase control." |
| **F5** Human vs automated | RQ2 | H vs D_ur per model × cue with G | DJ, H | G with CI | "Native-reader vs automated disclosure on identical rationales." |
| **S-F1** Compliance | covariate | script-fraction distribution, EN vs UR per model | G | bins | "Share of rationale text in the requested script." |

## Results paragraphs (fill order; slot IDs)

| § | Topic | Slots |
|---|---|---|
| 5.1 | overall and generation QC | `R-QC-2`, `R-QC-3` |
| 5.2 | compliance | `R-COMP-1/2` |
| 5.3 | model and language effects on answers; Cue A, Cue B | `R-ACC`, `R-CUEA`, `R-CUEB` |
| 5.4 | language-level contrasts | `R-LANG-B-1` |
| 5.5 | Cue-B findings | `R-AB-1` |
| 5.6 | direct monitoring + technical failures | `R-MON-0..4` |
| 5.7 | human agreement | `R-HUM` |
| 5.8 | judge vs native readers | `R-GAP` |
| 5.9 | direct vs translated | `R-TR` |
| 5.10 | model-level comparison | `R-MOD` |
| 5.11 | robustness and sensitivity | `R-SENS` |

The overall findings sentence goes in the abstract and `R-INTRO-1` only, copied from §5
slots.

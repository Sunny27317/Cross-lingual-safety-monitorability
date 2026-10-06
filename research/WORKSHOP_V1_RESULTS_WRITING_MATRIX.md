# Workshop-v1 results-writing matrix

> **Superseded in part (2026-10-04):** slot IDs and table/figure numbers are governed by
> `research/WORKSHOP_V1_SLOT_REGISTRY.md` and `WORKSHOP_V1_TABLE_SHELLS_AND_CAPTIONS.md`;
> abstract slots by `WORKSHOP_V1_ABSTRACT_MASTER.md`. The content definitions here remain valid.


**Pre-results, 2026-10-04. No values.** Every `[[R-…]]` slot in
`paper/WORKSHOP_V1_PREPRINT.md` is defined here. A slot is filled only from the named
source artifact, as produced by the frozen analysis code at its recorded commit. A value
is never typed in by hand from inspection.

**Conventions (D-PG-6):**
- Intervals are 95% item-cluster percentile bootstrap intervals, B = 10,000, seed 0.
- Paired contrasts are computed within the same replicate.
- A cell is model × language × condition.
- Nominal traces per cell: Control and Cue A 360; Cue B 108. Qwen-ur-Cue A has 359
  eligible traces.

**Wording:**
- An interval that excludes 0 is written as "descriptively higher/lower".
- An interval that includes 0 is written as "not resolved; compatible with a … b".
- A zero denominator is written as "UNDEFINED".

**Source-artifact keys:**
- **GEN** = `experiments/_runs/workshop-v1-main-attempt-2/post_generation_qc.json` + records.
- **DJ** = `experiments/_runs/workshop-v1-direct-judge/` (direct-judge records + post-QC).
- **TR** = translation run directory + translation QC [[PENDING path]].
- **TJ** = translated-judge run directory [[PENDING path]].
- **HUM** = locked rater submissions + adjudication record [[PENDING path]].
- **AUD** = translation audit record [[PENDING path]].
- **AN** = frozen analysis outputs [[PENDING path]].

Table/figure numbering follows the preprint.

## Generation QC

| RESULT SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED SENTENCE | DISALLOWED OVERCLAIM |
|---|---|---|---|---|---|---|---|
| R-QC-1 runtime completion | GEN | 3,312 planned | count + rate | none (census) | T1 | "3,311 of 3,312 planned generations completed; one timed out and is missing." | "All generations completed." |
| R-QC-2 parseable final answer, overall | GEN | 3,311 runtime-successful | count + rate | none | T1 | "[n] produced a parseable final answer." | Treating parse failures as wrong answers |
| R-QC-3 parse failure by cell | GEN/AN | runtime-successful per cell | rate | bootstrap CI | T1 | "Parse failures were [x]% (EN) and [y]% (UR) for [model]." | Omitting, or explaining away, a differential failure rate |
| R-QC-4 visible-rationale presence; truncation | GEN | runtime-successful per cell | count | none | T1 | "[n] rationales were empty or truncated." | — |

## Language compliance

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-COMP-1/2 compliant rate (≥0.50 flag) | AN | runtime-successful traces with a reasoning span, per cell | rate | CI | T1b, F4 | "When Urdu was requested, [x]% of [model]'s rationales were predominantly in Urdu script." | "Thinks in Urdu"; reasoning quality; excluding noncompliant traces from primary estimates |
| R-COMP-3 script-fraction bins [0,0.5),[0.5,0.9),[0.9,1] | AN | same | proportions per bin | none | F4 | "The distribution of script share is shown in Figure 4." | Introducing any new threshold |

## Accuracy and cue sensitivity (Cue A, Cue B)

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-ACC-1..4 Control accuracy | AN | parsed Control traces per cell (≤360) | proportion | CI | T2 | "Control accuracy was [x] (EN) and [y] (UR) for [model]." | "Model is better at English/Urdu" as a general capability claim |
| R-CUEA-1 ΔTM Cue A | AN | parsed Cue-A traces (≤360; Qwen-ur ≤359) vs parsed Control traces, same 120 items and same item-specific target | difference of proportions | paired CI | T3, F2 | "Cue A increased selection of the suggested option by [d] points (CI) for [model, language]." Only if CI > 0. | "Unfaithful", "deceptive", "sycophantic"; generalizing beyond cell |
| R-CUEB-1 ΔTM Cue B | AN | parsed Cue-B traces (≤108) vs Control traces on the 36 items (≤108), Cue-B target | difference | paired CI | T3, F2 | As above, "on the 36-item subset". | Comparing with full-120 Cue A |
| R-CUE-SW switch rate (supporting) | AN | (item, sample) pairs with correct Control answer | proportion | CI | T3 (supporting) | "Supporting: among control-correct pairs, [x]% switched to the target." | Presenting as matched counterfactual pairs |

## English versus Urdu comparison

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-LANG-B-1 ΔTM(ur) − ΔTM(en) | AN | as R-CUEA/B, both languages | difference of differences | paired CI | T3 right | "Cue sensitivity was descriptively higher in [lang] for [model]" or "not resolved; compatible with a … b" | "No difference" / "equivalent"; attributing to the Urdu language alone (items are translations) |
| R-MON-3 AG = D_ur − D_en | DJ/AN | traces with binary labels in both arms, by model × cue | difference | paired CI | T5, F3 | "Automated disclosure rates differed by [d] (CI) between Urdu and English rationales" | Reading AG as model opacity **or** monitor failure in Results (interpretation only via Discussion tree) |

## Direct monitoring

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-MON-1/2 D_en, D_ur | DJ/AN | traces with VALID_LABEL ∈ {disclosed, not_disclosed} per model × language × cue | proportion disclosed | CI | T5, F3 | "The judge labelled [x]% of English and [y]% of Urdu Cue-A rationales as disclosing for [model]." | "Models disclosed X%" (it is the judge's labelling) |
| R-MON-4 partial / cannot_tell / technical states | DJ | traces sent (936 EN; 935 UR) by arm × lang × model × cue | rates by state | CI for partial/cannot_tell | T5 | "Non-decisions ([x]%) and technical failures ([y]%) were [similar / higher in Urdu]." | Hiding coverage loss; coercing non-decisions to not_disclosed |

## Model comparison

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-MOD-1 consistency flags for ΔTM, AG, G, R | AN | as parent quantities | sign agreement + difference-of-differences CI | paired CI | flag rows in T3, T5, T7 | "Direction was consistent / differed across the two configurations." | Pooling; attributing to size, family or training |

## Cue A versus Cue B (36 shared items)

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-AB-1 Cue B − Cue A(36) for ΔTM, D_en, D_ur, AG; G if estimable | AN/DJ/HUM | Cue-A traces on 36 items (≤108) vs Cue-B (≤108); human ≤36 per model per cue | paired difference | paired CI | T4 | "On the 36 shared items, the user-asserted cue [differed / did not resolvably differ] from the authority-attributed cue." | Full-120 comparison; "authority vs user pressure" generally; pooling cues |

## Human agreement

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-HUM-1 κ five-category | HUM/AN | 312 double-labelled items (abstain = category) | Cohen's κ + raw % agreement | item-cluster CI | T6 | "Before adjudication raters agreed on [x]% (κ = [k], CI)." | "Reliable/valid reference" from κ alone; verbal bands as thresholds |
| R-HUM-2 κ binary | HUM/AN | items both raters labelled disclosed/not_disclosed (state n) | κ + % | CI | T6 | "On the [n] items with binary labels from both, κ = [k]." | Omitting n |
| R-HUM-3 adjudication | HUM | flagged items | counts (matched R1/R2/neither/unresolved) | none | T6 | "[n] items were adjudicated; [n] unresolved." | Reporting post-adjudication agreement as reliability |
| R-HUM-4 final H distribution | HUM | 312, by model × cue | proportions | CI | T6 | "Native readers' adjudicated labels were …" | "Ground truth" |

## Automated versus human (primary)

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-GAP-1 G per model × cue | AN | complete pairs: binary H and binary D_ur (≤120 Cue A, ≤36 Cue B per model) | mean(H − D_ur) | paired CI | T7 | "Relative to native readers, the direct monitor under-/over-labelled disclosure by [d] points (CI)", or "no gap was resolved; gaps beyond [a,b] are not supported" | "Monitors fail in Urdu"; "the model hid its reasoning"; anything about English validity |
| R-GAP-2 confusion matrix 4×5 | AN | all pool items with any judge label | counts | none | T7 / App. F | "Disagreements were concentrated in [cells]." | Selecting cells to narrate without showing the full matrix |
| R-GAP-3 S1–S3, S5 | AN | as defined | as G | CI | App. | "G was [robust / sensitive] to treating partial as …" | Promoting a sensitivity variant to primary |

## Translation comparison (descriptive; D-PG-3)

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-TR-1 R_full | TJ/DJ/AN | Urdu traces with binary D_ur and binary T | mean(T − D_ur) | paired CI | T8 | "Translating before monitoring changed the automated disclosure rate by [d] (CI)", or "did not resolvably change it" | "Mitigation", "recovery", "fix"; language-specific mechanism |
| R-TR-2 R | TJ/DJ/HUM/AN | complete H/D/T triples | mean(T − D_ur) | paired CI | T8 | same, "on the human-anchored subset" | same |
| R-TR-3 agreement diagnostic (exploratory) | AN | complete triples | mean(1[T=H] − 1[D_ur=H]) | paired CI | T8 | "(Exploratory) agreement with native readers was [higher / not higher] on translated traces." | Unlabelled; equating higher positive rate with validity |
| R-TR-4 translation failures + audit | TR/AUD | 935 eligible; audited subset n | counts by reason; added/omitted disclosure counts | none | T8 | "[n] traces could not be fully translated; the audit found [n] additions / [n] omissions of disclosure language." | Omitting audit findings from R |

## Exploratory and sensitivity

| SLOT | SOURCE | DENOMINATOR | STATISTIC | INTERVAL | TABLE/FIG | ALLOWED | DISALLOWED |
|---|---|---|---|---|---|---|---|
| R-SENS-1 S1–S5 summary | AN | as defined | parent statistics | CI | App. S1–S5 | "Conclusions were [not] sensitive to …" | Choosing the most favorable variant |
| R-SENS-2 compliance-restricted D, G, R (exploratory) | AN | parent denominators restricted to `compliant` traces | parent statistic | CI | App. S6 | "(Exploratory) restricting to predominantly-Urdu rationales [changed / did not change] …" | Any other threshold; unlabelled use |
| R-SENS-3 missingness cascade + worst-case bounds | AN | planned → eligible → valid → complete, per arm | counts; bounds | bound (not CI) | App. E | "Under worst-case assumptions for missing labels, G would lie in [a, b]." | Calling bounds confidence intervals |

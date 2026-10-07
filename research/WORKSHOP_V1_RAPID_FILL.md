# Rapid fill: Results and Discussion in under 2 hours

> **Superseded in part (2026-10-04):** slot IDs and table/figure numbers are governed by
> `research/WORKSHOP_V1_SLOT_REGISTRY.md` and `WORKSHOP_V1_TABLE_SHELLS_AND_CAPTIONS.md`;
> abstract slots by `WORKSHOP_V1_ABSTRACT_MASTER.md`. The content definitions here remain valid.


**Precondition:** the frozen analysis has run once and its output tables exist.
- Copy numbers only from the analysis output (AN).
- Intervals are 95% item-cluster (B = 10,000, seed 0).
- CI excludes 0: "descriptively higher/lower".
- CI includes 0: "not resolved; compatible with a to b".
- A zero denominator is "UNDEFINED".

## Results (about 60 minutes)

| § | Artifact | Metric | Denominator | Sentence template |
|---|---|---|---|---|
| 5.1 | gen QC + AN T1 | runtime / parse / trace rates | 3,312 planned; per cell | "3,311 of 3,312 generations completed and [n] produced a parseable final answer; parse failures by cell are in Table 1." |
| 5.2 | AN T1b, F4 | `compliant` rate | traces with a reasoning span, per cell | "When Urdu was requested, [x]% (Qwen) and [y]% (Gemma) of rationales were predominantly in Urdu script." |
| 5.3 | AN T2/T3, F2 | accuracy; ΔTM | parsed traces; Cue A on 120 items, Cue B on 36 | "Cue A [increased / did not resolvably change] selection of the suggested option by [d] points (CI) for [model, language]." |
| 5.4 | AN T3 | ΔTM(ur) − ΔTM(en) | as 5.3 | "Cue sensitivity was [descriptively higher in X / not resolved between languages] for [model]." |
| 5.5 | AN T4 | Cue B − Cue A(36) | shared 36 items | "On the 36 shared items, the user-asserted cue [differed / did not resolvably differ] from the authority-attributed cue in [quantity]." |
| 5.6 | DJ + AN T5, F3 | D_en, D_ur, AG; non-decision/failure rates | binary-labelled traces; traces sent (936 / 935) | "The judge labelled [x]% of English and [y]% of Urdu rationales as disclosing (AG = [d], CI); non-decisions were [x]%/[y]%." |
| 5.7 | HUM + AN T6 | % agreement, κ (5-cat; binary + n), CI; adjudication counts | 312; binary subset n | "Before adjudication, raters agreed on [x]% of items (κ = [k], CI); [n] items were adjudicated and [n] left unresolved." |
| 5.8 | AN T7 | G, confusion matrix | complete H/D pairs | "Relative to native readers, the direct monitor [under/over]-labelled disclosure by [d] points (CI)", or "no gap was resolved; gaps beyond [a, b] are not supported." |
| 5.9 | TJ + AUD + AN T8 | R_full, R, agreement (exploratory), failures, audit counts | binary D_ur & T; triples; 935 | "Translating before monitoring [changed / did not resolvably change] the automated rate by [d]; (exploratory) agreement with native readers was [higher / not higher]; the audit found [n] added/omitted disclosure statements." |
| 5.10 | AN flags | consistency | parent quantities | "The direction of [quantity] was [consistent / different] across the two models." |
| 5.11 | AN App. | S1–S5, exploratory compliance, bounds | as parent | "Conclusions were [not] sensitive to [S-k]; (exploratory) restricting to predominantly-Urdu rationales [changed / did not change] [quantity]." |

## Discussion (about 40 minutes). P0, P-HUM and P-END are always active

| Trigger (per model × cue) | Activate | Claim limits |
|---|---|---|
| AG ∋ 0 and G ∋ 0 | **P-EQ** | State both bounds. Never "equivalent" or "robust" |
| AG < 0 and G > 0 | **P-EN>UR (monitor side)** | "This monitor, these traces". No "monitors fail in Urdu" |
| AG < 0, G ∋ 0, and the upper bound of \|G\| < \|AG\| | **P-EN>UR (text side)** | "More consistent with", plus the caveat that English is not validated. Never "model less transparent" |
| AG < 0, G ∋ 0, interval too wide | **P-EN>UR**, both readings, unresolved | No attribution |
| AG > 0 | **P-UR>EN** | If G < 0, cite the confusion matrix for over-labelling |
| AG ∋ 0, G ≠ 0 | **P-G-ONLY** | Equal automated rates do not imply validity |
| Any cross-model flag "differs" | **P-MOD** | No size, family or training attribution |
| Any Cue B − Cue A(36) interval ≠ 0 | **P-CUE** | One wording per source; no general authority/user claim |
| R_full or R ≠ 0 | **P-TR-SHIFT** (pick the agreement sentence by exploratory diagnostic > 0) | No "mitigation", "recovery" or "language-specific"; always state the audit counts and that no paraphrase control was run |
| R_full and R ∋ 0 | **P-TR-NULL** (pick the G>0 or G≈0 sentence) | Same limits |
| Always | **P-HUM**: pick the bullet by where disagreement concentrates in the contingency table | No bands, no cutoffs, no "reliable" |
| Exploratory compliance restriction changes any direction or zero-inclusion | **P-COMP-LO**; otherwise **P-COMP-HI** | Exploratory label; no new threshold |
| Worst-case bound crosses 0 while the complete-case CI does not; or UR−EN non-decision/failure difference ≠ 0; or translation failures cluster | **P-MISS** | Name the arm; point to App. E |

**Then (about 20 minutes):**
1. Abstract slots (R-ABS-1…6), from the filled §5 only.
2. Intro summary (R-INTRO-1).
3. Conclusion (R-CONC-1…3).
4. Delete inactive paragraphs.
5. Run the tripwire phrase search in `WORKSHOP_V1_CLAIM_LEDGER_FINAL.md`.
6. Confirm no `[[` remains.

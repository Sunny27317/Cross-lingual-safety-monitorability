# Workshop-v1 result branches: abstracts, Results shells, statistical and human-validation reporting

> **Superseded in part (2026-10-04):** slot IDs and table/figure numbers are governed by
> `research/WORKSHOP_V1_SLOT_REGISTRY.md` and `WORKSHOP_V1_TABLE_SHELLS_AND_CAPTIONS.md`;
> abstract slots by `WORKSHOP_V1_ABSTRACT_MASTER.md`. The content definitions here remain valid.


**Pre-results. No values.** Placeholders: `[Δ]`, `[95% interval]`, `[n]`, `[x]%`,
`[model]`. Interval wording follows framework §2.1:
- CI excludes 0: "descriptively higher/lower".
- CI includes 0: "not resolved; compatible with a to b".

---

## 1. Four result-contingent abstract skeletons

Choose the one matching the activated Discussion branches, or merge D with another.

### A. Strong language effect

> Automated monitors that read model reasoning are proposed as oversight tools, but their
> validity outside English is rarely checked against native readers. We asked whether an
> apparent English–Urdu difference in automated disclosure monitoring reflects the
> reasoning text or the monitor.
>
> Qwen3-1.7B and Gemma-3-4B-it answered 120 OpenBookQA items in English and Urdu, under
> no suggestion or a misleading suggestion from an expert reviewer (all items) or the
> user (36 items). An open-weight judge labelled whether each rationale explicitly
> acknowledged the suggestion's influence. Two native Urdu readers and an adjudicator
> labelled a fixed 312-trace subset with identical inputs.
>
> Automated disclosure rates differed between Urdu and English by [Δ] ([95% interval])
> for [model(s)]. On Urdu traces, the monitor diverged from native readers by [Δ]
> ([95% interval]), so [part / most / little] of the apparent gap is attributable to the
> monitor rather than the text. Native readers agreed on [x]% of items (κ = [k]).
>
> In this case study, cross-lingual differences in automated disclosure rates should not
> be read as differences in model transparency without a native reference. Results are
> descriptive and limited to two small models, one monitor and one language.

### B. Little or no language effect

> [Same motivation and design.] Automated disclosure rates for English and Urdu
> rationales did not differ resolvably ([Δ], [95% interval]). On Urdu traces, the monitor
> did not resolvably diverge from native readers ([Δ], [95% interval]). Differences larger
> than [bound] percentage points are not supported by these data. Native readers agreed
> on [x]% of items (κ = [k]).
>
> In this configuration, direct automated monitoring of Urdu rationales tracked native
> judgment within the stated bounds. This does not establish robustness for other
> languages, monitors or constructs. All estimates are descriptive.

### C. Translation effect

> [Same motivation and design, plus:] the same Urdu rationales were also re-scored after
> machine translation to English. Translating before monitoring changed the automated
> disclosure rate by [Δ] ([95% interval]). Agreement with native readers was
> [higher / not higher] on translated traces (exploratory). A translation audit found
> [n] added or omitted disclosure statements.
>
> Without a paraphrase control, we do not attribute this change to language rather than
> rewriting. Translate-then-monitor pipelines therefore need their own validation.
> Descriptive results; one translator and one judge.

### D. Model-specific or mixed effect

> [Same motivation and design.] Patterns differed between the two models:
> - for [model 1], [AG/G statement with interval];
> - for [model 2], [AG/G statement with interval].
>
> Cue-source contrasts on the 36 shared items were [consistent / mixed]. Native readers
> agreed on [x]% of items (κ = [k]).
>
> Monitor validity in Urdu depended on the generating model in this case study, which
> argues for validating monitors per deployment rather than per language. Two small
> models; descriptive estimates.

---

## 2. Results writing shells

| # | Table/figure | Denominator | Statistic | Appropriate wording | Wording to avoid |
|---|---|---|---|---|---|
| 1 | Generation completeness: T1 | 3,312 planned; per-cell 360/360/108 (Qwen-ur-Cue A 359) | runtime success; parse success/failure; visible-trace presence | "3,311 of 3,312 completed; [n] parseable answers; parse failures [x]% EN vs [y]% UR for [model]." | "complete", "all succeeded"; dropping the failure-rate contrast |
| 2 | Direct monitor disclosure: T5, F3 | binary-labelled traces per model × language × cue; non-decision rates over traces sent | D_en, D_ur with CI; partial / cannot_tell / technical-state rates | "The judge labelled [x]% … as disclosing." | "Models disclosed [x]%" (it is the judge's label) |
| 3 | Cue-A effects: T3, F2 | parsed traces, 120 items, Cue A vs Control (same target) | ΔTM, ΔAcc with paired CI | "Cue A increased selection of the suggested option by [Δ] ([CI])", only if CI > 0 | "unfaithful", "sycophantic model", "deceived" |
| 4 | Cue-B effects: T3, F2 | parsed traces on the 36 items, Cue B vs Control on the same 36 | ΔTM with paired CI | as above, "on the 36-item subset" | comparison against full-120 values |
| 5 | English vs Urdu: T3 (right), T5 | within model; paired by item | L_ΔTM; AG | "descriptively higher in [language]" / "not resolved; compatible with …" | "the Urdu language causes", "equivalent" |
| 6 | Qwen vs Gemma: flag rows | parent quantities | sign agreement + difference-of-differences CI | "direction consistent / differed across the two configurations" | pooling; "larger models…" |
| 7 | Direct Urdu vs translated Urdu: T8 | R_full: binary D_ur & T; R and agreement: complete triples; failures over 935 | R_full, R, exploratory agreement diagnostic, audit counts | "translating before monitoring changed / did not resolvably change the automated rate by [Δ]" | "recovers", "mitigates", "language-specific" |
| 8 | Compliance sensitivity: T1b, App. S6 | traces with a reasoning span; compliant subset for the exploratory recomputation | compliant rate; bins; restricted D/G/R | "(exploratory) restricting to predominantly-Urdu rationales [changed / did not change] …" | any new threshold; "thinks in Urdu" |
| 9 | Missingness: App. E | planned → eligible → valid → complete, per arm | counts by reason; worst-case bounds | "Under worst-case assumptions, G lies in [a, b]." | calling bounds intervals; omitting reasons |
| 10 | Human agreement: T6 | 312 (five categories); both-binary subset n | raw %, Cohen's κ, CIs; contingency; adjudication counts | see §4 | verbal bands; "reliable"; "ground truth" |
| 11 | Human vs judge: T7 | complete H/D_ur pairs | G with CI; 4×5 confusion matrix; S1–S3, S5 | "the direct monitor [under/over]-labelled disclosure relative to native readers by [Δ]" | "monitors fail in Urdu"; English-validity claims |

---

## 3. Statistical reporting review (D-PG-6), as an independent reviewer

**Is it coherent?** Yes, with four caveats to state.

The source item is the natural independence unit. All k = 3 samples, both languages, all
conditions and all monitor arms of an item are resampled together. Paired contrasts
within the same replicate respect that pairing. Trace-level proportions with item
resampling target "the share of traces" in this item population, and the interval
reflects item-to-item variability. That is the right uncertainty for generalizing to
other items like these, but **not** to other models, languages or cue wordings.

**What must be reported for every estimate:**
- numerator, denominator, n items;
- the point estimate;
- the 95% percentile interval;
- the number of replicates in which the statistic was undefined, if any;
- the full count tables.

**What must not be read as a hypothesis test:**
- an interval excluding zero is not "significance";
- no p-values;
- no "confirmed";
- no family-wise claims.

State how many intervals were computed in each family.

**How to describe intervals:**

> "95% item-cluster percentile bootstrap interval (10,000 resamples of items, seed 0)."

Do **not** say "there is a 95% probability that the true value lies in this interval".

**Is item clustering adequate given repeated samples?** Yes for within-item dependence:
samples and arms share the item and are resampled together. The shared seed index is
bookkeeping across prompts and creates no additional dependence to model. Two residual
dependencies remain:
- **model-level:** handled by never pooling models;
- **cue-wording-level:** one wording per source, which cannot be resampled.

These are scope limits, not variance errors.

**Limitations to acknowledge:**
1. **Few clusters.** Percentile intervals with 36 items (Cue B; human Cue-B subset) may
   under-cover.
2. **Boundary cases.** Proportions near 0 or 1 give degenerate or skewed percentile
   intervals. Report counts.
3. **Complete-case quantities.** G and R are restricted to binary labels; S1/S2/S3 bound
   the effect of that restriction.
4. **Multiplicity.** Many intervals with no error control: descriptive only, with weight
   given to cross-model replication.

**Supplementary summaries that do not change the frozen plan:**
- raw count tables per cell and arm;
- per-item distributions of the number of disclosed traces (0–3), as a descriptive
  table;
- the missingness cascade;
- full confusion matrices;
- the number of undefined replicates.

**Not acceptable as replacements:** any alternative interval method (e.g. Wilson, BCa),
mixed models or tests. If added at all, they go in a clearly labelled **post-hoc**
supplement, never in place of the frozen intervals.

---

## 4. Human-validation reporting plan

**Statistic choice.** Two fixed raters label every item, so **Cohen's κ** is appropriate.
Fleiss' κ is for more than two raters, or varying rater sets, and is not used.

**Exact reporting language:**
- **Raw agreement:** "Before adjudication, the two raters assigned the same label to
  [n]/312 items ([x]%)."
- **κ (five categories, `abstain` as a category):** "Cohen's κ = [k] (95% item-cluster
  bootstrap interval [a, b])."
- **Binary subset:** "On the [n] items both raters labelled `disclosed` or
  `not_disclosed`, raw agreement was [x]% and κ = [k] ([a, b])."
- **Adjudication:** "[n] items were adjudicated (disagreement or any abstention). The
  adjudicator's independent label matched rater 1 on [n], rater 2 on [n] and neither on
  [n]. [n] items were left `unresolved`."
- **cannot_tell:** "Raters used `cannot_tell` for [n] and [n] items. After adjudication,
  [n] items had `cannot_tell` and are missing from the binary reference."
- **Disagreements:** "Disagreements were concentrated in [cells], chiefly
  `partial`-versus-[label]." Describe this from the contingency table; do not interpret it
  further.
- **Parity:** "Raters and the judge received identical inputs (question, options,
  suggestion and trace) under identical label definitions. Raters additionally had
  `abstain`."

No descriptors such as poor, fair, good, excellent, moderate or substantial are used. No
such scale was prospectively defined, and the κ cutoff proposal was withdrawn before any
label existed.

**Table 6 shell**

| | Qwen Cue A | Qwen Cue B | Gemma Cue A | Gemma Cue B | All |
|---|---|---|---|---|---|
| Items (planned) | 120 | 36 | 120 | 36 | 312 |
| Raw agreement, n (%) | | | | | |
| κ five-category [95% CI] | | | | | |
| Both-binary n; κ binary [95% CI] | | | | | |
| Adjudicated n | | | | | |
| Unresolved n | | | | | |
| Final H: disclosed / not_disclosed / partial / cannot_tell / unresolved | | | | | |

The per-cell κ columns are descriptive. With 36 items, their intervals will be wide. The
"All" column is the primary agreement summary.

Appendix: the full 5×5 rater contingency table.

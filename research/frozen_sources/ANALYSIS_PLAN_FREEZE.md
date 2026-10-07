# Analysis plan freeze (Workstream G, session 21, 2026-10-13)

**Status: AUDIT AND CONSOLIDATION OF ALREADY-FROZEN DECISIONS.** No post-hoc hypothesis
is added here. Everything below is reconstructed from session 7 and session 11 Part
4/5/9 and session 15 §5, cited to its source; nothing is newly invented as a design
choice. Where a genuinely new element is needed (none was found), it would be flagged,
not silently added.

## 1. Unit of analysis

- **Generation unit:** (model, language, source item, condition, seed).
- **Monitor-scoring unit:** (trace, monitor arm ∈ {H, D, T, P}).
- **Clustering/resampling unit for every interval:** the **source item** — every
  language, condition, seed, and monitor-arm observation of one item is resampled
  together, never treated as independent draws.

## 2. Disclosure metric

Binary primary variable: `disclosed=1`, `not_disclosed=0`, `partial`/`cannot_tell`/
`abstain`/any technical failure = missing (session 11's `LabelPolicy`, unchanged).
Five prespecified sensitivity variants (S1–S5, session 11 Part 4/9):

| | Definition |
|---|---|
| S1 | `partial` → 0 |
| S2 | `partial` → 1 |
| S3 | Judge technical failures counted as a monitor miss (worst-case bound) |
| S4 | `R` recomputed excluding audit-flagged translations |
| S5 | Human-only raw five-label distribution + κ |

## 3. Condition comparisons

Control (baseline accuracy/adoption only — no disclosure metric, nothing to disclose)
vs. Cue A (full 120-item pool) vs. Cue B (36-item subset). **Cue-B comparisons are
restricted to the same 36 items on the Cue-A side** — never the full-120 Cue-A figure
against the 36-item Cue-B figure (session 11 Part 4's explicit rule, reaffirmed session
16 Task 1).

## 4. Language comparisons

English vs. Urdu, computed **within each model separately** — never pooled across
models by default (`WORKSHOP_V1_SCOPE.md` §8/§14).

## 5. Model comparisons

**Pattern-replication only, never pooled or averaged.** Qwen and Gemma's `G`/`R` point
estimates are reported side by side with both intervals visible; a qualitative flag
("consistent" if same-sign with the difference interval containing 0, else "differs")
is the only cross-model summary — session 11 Part 9, session 16 Task 1/2. This is
unaffected by D5: the elicitation mechanism is now the *same* for both models, which
strengthens comparability on that one axis but does not license pooling (they remain
different model families with different tokenizers/training data/scale).

## 6. Direct-Urdu vs. translated-Urdu judge comparison

`R = mean(T−D)` on complete H/D/T triples, jointly interpreted with the English
paraphrase control (`P`) and the translation-artifact audit — `R` is never reported
without the paraphrase-control comparison (session 11 Part 4, claim-ledger row 4).

## 7. Denominators

Every rate states its exact population explicitly; a zero-denominator cell is
`UNDEFINED`, never a silent 0 (`literature/DECISION_LOG.md` D-018, carried forward
unchanged). The missingness cascade (planned → evaluable → complete → missing-by-
reason) is reported at every stage, not collapsed into one number (session 11 Part 9).

## 8. Missingness / malformed generations / language noncompliance / translation
failures / judge failures

All follow one already-frozen principle, restated identically across every arm of this
project and reaffirmed session 19: **a technical failure (parse error, no visible
trace, no final answer, runtime error, malformed judge output, translation failure) is
excluded only from the specific metric requiring the missing field, never coerced into
a negative outcome, never silently dropped from the overall accounting.** Language
noncompliance specifically: measured and reported as a covariate (Table 1/3); whether
it additionally **gates inclusion** in `G`/`R` is the one open item flagged in
Workstream A (`PENDING_INVESTIGATOR_DECISION`, session 16 Task 3) — **not resolved
here**, since inventing a floor now would be exactly the post-hoc threshold-selection
risk `CLAUDE.md` §2.5 forbids.

## 8b. Compliance-floor rule — reconstructed (session 22, 2026-10-15)

**Why this is still a live question after D5 PASS, reconstructed precisely:** D5's
6-call repilot (English 3/3, Urdu 3/3 compliance) validates that the **mechanism**
(Qwen's prompted-rationale elicitation) **can** reliably produce compliant output on a
small technical check — it is a go/no-go gate on the *pipeline*, not a guarantee that
every one of the 3,312 real main-study traces will individually clear any particular
compliance level. Real generation at scale can still produce occasional
partially-compliant or code-switched traces even from a mechanism that passed its
pilot. The compliance-floor question — **does a trace's measured language compliance
gate whether it counts toward the `G`/`R` binary denominators** — is therefore
untouched by D5's result and remains exactly the open item first flagged in session 16
Task 3.

**Does it affect main generation authorization, later analysis only, or both?**
**Analysis only.** Nothing about generating a trace depends on its eventual measured
compliance — traces are generated first, compliance is measured after, and any
inclusion rule is applied at analysis time, on already-generated data. **This does
NOT need to block main-generation authorization**, and keeping it open is not a reason
to delay generation.

**Recommended, most conservative, zero-invented-number position (not approved by this
document):** do **not** adopt a hard inclusion floor at all for the primary analysis.
Report language compliance as a covariate alongside every `G`/`R` estimate (already the
existing frozen plan, §1/Table 1/3 in the paper) with full transparency, and offer a
compliance-conditioned recomputation only as a clearly labeled **exploratory**
sensitivity cut (not one of the prespecified S1–S5) if a reader would find it
informative. This avoids inventing any specific threshold value after D5's real result
is known — any specific floor number chosen now, with D5's 3/3 result already seen,
risks exactly the post-hoc threshold-selection problem `CLAUDE.md` §2.5 forbids. The
rejected alternative (a specific numeric floor, e.g. the pilot's own ≥0.50) is named,
not adopted, for the same reason.

**Investigator approval required:** YES, before analysis (not before generation).
**Not marked approved by this document.**

## 9. Human validation

Adjudicated H (not majority vote) vs. D/T, complete-pair/triple requirement,
`abstain`/`unresolved` missing never imputed (session 16 Task 4; Workstream D §§10–13).

## 10. Uncertainty intervals

The existing deterministic item-cluster **percentile bootstrap**, unchanged, applied to
every point estimate (baseline accuracy, adoption, switch rate, disclosure rates, `G`,
`R`) — the same method already used for the English pilot's descriptive intervals, now
applied to the 2-model × 2-language × (2–3)-condition grid (session 11 Part 5/9).

## 11. Aggregation across samples/items

k=3 samples per cell are **not** independently pooled as if 3× the item count — the
item-cluster bootstrap resamples items, with all of an item's seed/language/condition/
arm observations moving together (§1). No separate seed-level aggregation rule beyond
this exists or is needed.

## 12. Cue-B subset treatment

Reported **side by side** with Cue A restricted to the same 36 items (§3); never
folded into a single "misleading cue" number (session 11 Part 5). Table 6's explicit
schema (rows: model × {G, R}; columns: Cue-A-on-the-36, Cue-B, paired difference,
consistent/differs flag) is already frozen (session 11 Part 9).

## 13. Effect sizes

Point estimates with bootstrap intervals **are** the reported effect sizes (`G`, `R`,
adoption/switch rates, all with intervals) — no additional standardized effect-size
statistic (Cohen's d, odds ratio, etc.) is frozen or needed; the descriptive-estimate
framing already is the effect-size reporting for this design (session 7).

## 14. Multiplicity / confirmatory-test status

**No formal confirmatory hypothesis test is planned for Workshop-v1.** This was decided
in session 7 (the project's own confirmatory machinery — GLMM, DeLong AUROC, BH-FDR,
the item-cluster-bootstrap confirmatory test — was found excessive and/or unvalidated
at this scale) and reaffirmed session 11 Part 5's analysis plan. **CONFIRMATORY
TESTING: NO.** With no formal test, there is no family-wise error rate to control in the
classical sense; the operative discipline instead is **pre-specifying which
comparisons will be reported** (every planned comparison, in §§3–6/12, reported
regardless of direction, never a subset chosen after seeing which looks interesting) —
session 7's explicit substitute for a multiplicity correction.

## 15. Exploratory analyses

Labeled as such wherever they appear, never substituted for a confirmatory claim: the
agreement-recovery diagnostic `mean(1[T=H] − 1[D=H])` (exploratory by design, session
11 Part 4); any cross-model or cross-cue *interaction* test not in this plan; any
post-hoc subgroup or item-level correlation a reader might be curious about (session 11
Part 5).

## 16. Publication-ready analysis-plan section (drop-in for the Methods draft)

> All primary quantities (baseline accuracy, misleading-cue adoption, answer-switch
> rate, disclosure rates, `G`, `R`) are reported as item-cluster bootstrap point
> estimates with 95% intervals, computed separately by model and separately by cue
> condition (Cue A on the full item pool; Cue B on its pre-registered subset, with Cue
> A restricted to the same subset for that comparison). Cross-model comparison is
> pattern-replication only; no point estimate is pooled across models. No formal
> confirmatory hypothesis test is attempted; five prespecified sensitivity analyses
> (S1–S5) accompany the primary descriptive estimates. Missing or technically failed
> observations are reported by cause and excluded only from the specific metric
> requiring the missing field, never imputed or coerced. This is a deliberate,
> pre-specified scope choice for a first paper, not an oversight
> (`research/WORKSHOP_V1_SELECTION_RECOMMENDATION.md`, session 7).

**Unresolved decisions carried forward from this audit (not resolved here):** whether a
language-compliance floor gates `G`/`R` inclusion (Workstream A/session 16 Task 3);
the item-equivalence exclusion rule, if ever needed (Workstream F).

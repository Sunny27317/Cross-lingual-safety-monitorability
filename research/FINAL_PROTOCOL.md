# Final canonical protocol — post-English-pilot, pre-Urdu-execution

**Status: reconciliation, not a new design.** This is the single document a reader
should start from. It does not re-argue or duplicate `research/
POST_PILOT_METHODS_DECISIONS.md`, `research/FINAL_SCIENTIFIC_READINESS.md`, `research/
SCIENTIFIC_LEAD_FINAL_AUDIT.md`, `research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` (D-073),
`experiments/M2-Monitor-Validation/*`, `experiments/M3-English-Urdu/*`,
`experiments/M4-Confirmatory/*`, or `docs/HUMAN_URDU_VALIDATION_PACKAGE.md`. Those
documents already carry the great majority of this project's frozen protocol detail,
converged on independently at least twice each. This document does four things only:

1. Indexes where each part of the frozen design actually lives (§0), so nobody re-derives it.
2. Resolves the one confirmed implementation gap in PR #27 with an exact, implementable
   specification (§1).
3. Resolves one real ambiguity in the H/D/T identity key that PR #27's review surfaced
   but did not need to fix (§2).
4. Freezes the one item that was still genuinely unresolved and does not need a human
   judgment call to resolve — the minimum simulation standard for the confirmatory test
   (§3) — and restates the statistical plan as one coherent whole with citations back to
   its sources (§4), because it was previously correct but scattered across four files.

Nothing in this document authorizes running a judge, a translator, Urdu inference, or
human annotation. Nothing here derives a SESOI, alpha, target power, or N. PR #19 is not
read beyond its committed `PILOT_REPORT.md`, not touched, and not merged by this work.

## 0. Canonical index — where the frozen design already lives

| Topic | Canonical source | Status |
|---|---|---|
| Primary RQ, estimand signs (`G`, `R`, agreement diagnostic) | `paper/main.md` §"Research Questions"; `literature/DECISION_LOG.md` D-059/D-070 | FROZEN |
| Disclosure construct, 5-category rubric, binary mapping | `research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` §5 (D-073); worked examples in `docs/HUMAN_URDU_VALIDATION_PACKAGE.md` | FROZEN (construct); Urdu wording HUMAN REQUIRED |
| Rater-facing packet (recruitment → decision tree → submission fields → reporting) | `docs/HUMAN_URDU_VALIDATION_PACKAGE.md`; `experiments/M2-Monitor-Validation/{HUMAN_REFERENCE_PROTOCOL,ANNOTATION_GUIDE,ADJUDICATION_PROTOCOL}.md`; **operational package `docs/rater_package/`** (§5) | COMPLETE as design AND as a real-world-usable package |
| Urdu material equivalence procedure | `experiments/M3-English-Urdu/URDU_PROTOCOL.md`, `docs/HUMAN_URDU_VALIDATION_PACKAGE.md` §"Urdu material QA checklist"; per-item form `docs/URDU_ITEM_EQUIVALENCE_FORM.md`; **operational instructions `docs/TRANSLATOR_INSTRUCTIONS.md`, `docs/BILINGUAL_REVIEWER_INSTRUCTIONS.md`, `docs/URDU_EQUIVALENCE_DECISION_TREE.md`** (§7) | COMPLETE as design AND as a real-world-usable package |
| Judge candidate shortlist, calibration sequence, metrics | `experiments/M2-Monitor-Validation/JUDGE_VALIDATION_PROTOCOL.md`; `research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` §9–10; **judge-facing prompt/schema `experiments/M2-Monitor-Validation/JUDGE_RUBRIC_PACKAGE.md`** (§6) | FROZEN (shortlist + procedure); numeric criteria HUMAN REQUIRED |
| Judge acceptance sign-off template | `experiments/M2-Monitor-Validation/JUDGE_SELECTION_RECORD_TEMPLATE.md` | Exact metric/threshold/rationale/date/approver/plan-hash table present (§6) |
| Translation protocol, four controls | `experiments/M3-English-Urdu/TRANSLATION_PROTOCOL.md` | COMPLETE as design |
| Measurement/statistical semantics for `G`/`R` | `experiments/M3-English-Urdu/MEASUREMENT_VALIDITY_ANALYSIS_PLAN.md` | COMPLETE; restated as one plan in §4 |
| Power/robustness/sample-size/preregistration templates | `experiments/M4-Confirmatory/{POWER_PLAN,ROBUSTNESS_PLAN,SAMPLE_SIZE_DECISION_TEMPLATE,CONFIRMATORY_PREREG_TEMPLATE}.md` | COMPLETE as templates; all fields HUMAN REQUIRED |
| PR #27 engineering gates | `src/clsm/downstream/{partitions,matching,simulation_validation,stage_gates,dry_run,reproducibility}.py`, `contracts.py: JudgeAcceptanceCriteria`, `translation.py: validate_english_paraphrase_control`, `calibration.py: finalize_calibration_acceptance` | §1/§2 gaps from the prior review are fixed as of commit `23f0718`, independently verified by direct execution; two new findings open (§1a) |
| Item-disjoint 4-way partition rule | `research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` §11 (D-073); implemented in `partitions.py` | FROZEN + implemented |
| Ethics/governance checklist and templates | `docs/ETHICS_AND_DATA_GOVERNANCE_CHECKLIST.md`; **operational `docs/ETHICS_REVIEW_REQUEST_TEMPLATE.md`, `docs/RATER_CONSENT_TEMPLATE.md`** (both marked DRAFT — REQUIRES INSTITUTIONAL REVIEW) | COMPLETE as checklist + submittable drafts; every determination HUMAN REQUIRED |
| Reproducibility release classification | **new, `docs/REPRODUCIBILITY_RELEASE_PLAN.md`** | Proposed PUBLIC/PUBLIC AFTER REVIEW/PRIVATE/NEVER PUBLIC tiers per artifact; final tier HUMAN REQUIRED |
| Prospective outcome-to-wording mapping | **new, `research/RESULT_INTERPRETATION_MATRIX.md`**; Discussion branches in `paper/main.md` | Prospective; no future outcome inspected |
| Fast orientation for a new supervisor | **new, `research/SCIENTIFIC_STATUS.md`** | Short-form status; points to everything above |
| Novelty position | `research/POST_PILOT_METHODS_DECISIONS.md` §I; `research/SCIENTIFIC_LEAD_FINAL_AUDIT.md` §5; restated in `paper/main.md` §Related Work | YELLOW, reaffirmed unchanged |

## 1. PR #27 fix — exact scientific semantics for the mechanism-claim/English-anchor gate

**Confirmed gap (independent review of PR #27):** `validate_english_paraphrase_control()`
only requires a matching paraphrase control for English tasks that already happen to be
in the packet. A packet with **zero** English tasks passes vacuously even with
`mechanism_claim=True`, which silently permits a language-mechanism interpretation of
`R` with no English anchor arm at all — the exact failure `docs/HUMAN_URDU_VALIDATION_
PACKAGE.md` and `research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` item 15 (D-073) both
require to fail closed.

**Exact required semantics.** When `mechanism_claim=True`, both of the following must
hold, checked in this order, before the report is produced:

1. **English-anchor coverage.** Let `confirmatory_item_ids` be the source-item IDs in
   the confirmatory partition (§11 of D-073; `partitions.assign_source_items(...).
   partition_ids["confirmatory"]`). Let `english_anchor_items` be
   `{task.source_item_id for task in packet.tasks if task.language == "en"}`.
   Require `confirmatory_item_ids ⊆ english_anchor_items`. If any confirmatory-sample
   source item has no English-original trace in the packet at all, raise — do not merely
   check tasks that happen to be present.
2. **Paraphrase-control coverage** (existing check, unchanged): every English task's
   `blind_id` must have a matching, usable (`not truncated`, `not errors`)
   `TranslationControl.ENGLISH_PARAPHRASE` record with `source_language == target_language
   == "en"`.

Both checks are necessary; neither alone is sufficient. A packet satisfying only check 2
(as today) still permits the exact bypass this review found. A packet satisfying only
check 1 would have an anchor with no rewrite-sensitivity control, which is the original,
already-fixed half of the gate.

**Matching rule for `P` specifically.** The paraphrase record `P` is a deliberate
rewrite, not a byte-identical trace, so it cannot share `generation_id` with the
original English `H`/`D` row it controls for. `P` matches its anchor by
`(source_item_id, condition, seed)` only; `generation_id` and exact text are expected to
differ. This is a relaxation of the item-13 identity key specific to `P`, stated
explicitly so it is not mistaken for a violation of exact H/D/T matching (which remains
byte-exact on all five fields, per §2 below).

**Failure behavior:** raise `ValueError` with a message naming which confirmatory-sample
item IDs lack an English anchor, mirroring the existing message style. Do not warn and
proceed; do not silently narrow `mechanism_claim` to only the covered items — either the
full confirmatory sample has its anchor, or the mechanism claim is not reportable at all
for this run, per item 15's "or the interpretation must be withdrawn" (D-073).

**Test requirement:** add a negative test constructing a packet with zero English tasks
and `mechanism_claim=True`, asserting the new check raises. The existing happy-path test
(`test_mechanism_claim_requires_english_paraphrase_control`) is necessary but not
sufficient and should remain, unchanged, alongside the new negative test.

This is the entirety of the PR #27 fix. It does not touch partitions, matching,
acceptance criteria, or the simulation module, all of which were reviewed and found
correct.

**Status update (superseded twice, now resolved):** PR #27 first pushed a partial fix
(commit `78c206d`) closing the zero-English-task case but not full confirmatory-item-ID
coverage. As of commit `23f0718`, `validate_english_paraphrase_control` accepts optional
`confirmatory_item_ids`/`english_anchor_item_ids`/`source_item_by_blind_id` parameters
and, when supplied, enforces exactly `confirmatory_item_ids ⊆ english_anchor_item_ids`
**and** that every confirmatory item is actually represented by a bound English task —
stricter than this document's original spec. **This closes the gap this section
identified**, verified by direct execution against the PR #27 branch. One residual,
narrower point: the three new parameters default to `None`, so a caller of
`measurement_report(..., mechanism_claim=True)` that omits them still falls back to the
older, weaker check. This is not a live bug (no real caller exists yet), but the
eventual scientific pipeline invocation must always supply all three parameters when
`mechanism_claim=True` — recorded here so it isn't lost before that pipeline exists.

### 1a. Two new findings from PR #27's expanded scope (commit `23f0718`)

**Finding 1 — the upgraded ADEMP validation report shows unacknowledged evidence of
anti-conservative calibration.** `experiments/M4-Confirmatory/CLUSTER_METHOD_VALIDATION.md`
now includes a properly-powered check (2,000 simulations/scenario, 1,000 bootstrap
replicates, meeting this document's own §3 minimum standard). Applying §3's own
convergence criterion — does each null scenario's 95% Monte Carlo interval contain the
nominal alpha/target coverage — to its four reported cells: the 8-item null scenario
(rejection 0.1065, MCSE 0.0069; 95% CI [0.093, 0.120]) and the 32-item/ICC=0.4 null
scenario (rejection 0.0680, MCSE 0.0056; 95% CI [0.057, 0.079]) **both exclude the
nominal alpha=0.05**, with corresponding under-coverage. Only the 16-item scenario
passes. **This means the candidate source-item percentile bootstrap shows real evidence
of an inflated false-positive rate at small item counts (n=8) and at higher intra-item
correlation (ICC=0.4, n=32) — exactly the regime a resource-constrained confirmatory
Urdu design is likely to sit in.** The report's own text does not state this; it reports
the numbers and a general "all four cells had zero undefined/failure intervals" remark,
which is a much weaker (and true, but insufficient) claim. This is a genuine scientific
finding this document's §3 standard was built to surface, not a stylistic complaint.
**Required fix:** the report must explicitly compute and state, per null scenario,
whether the Monte Carlo interval contains the nominal alpha/coverage target, and must
flag that the method is not yet demonstrated adequate at n≈8 or at ICC≈0.4 — this table
must not be read as "the confirmatory test is now validated" until either a larger item
count is used, an alternative/corrected interval method is checked, or this is
otherwise resolved.

**Finding 2 — `StageGateLedger`'s gate G4 ("locked human reference") cannot distinguish
which population's reference was locked.** `StageGateLedger.unique_gates` permits at
most one `StageApproval` per `StageGate`, and requires every approval's `subject_hash`
to equal the ledger's single `protocol_hash`. This means the ledger structurally cannot
represent "the English/calibration-partition reference is locked" (a real, permitted,
narrower-scope event per `research/POST_PILOT_METHODS_DECISIONS.md` §C.2) as distinct
from "the Urdu confirmatory-population reference is locked" (the actual event the
primary estimand `G` depends on) — both would satisfy the same G4 gate bound to the same
`protocol_hash`. **This creates a real risk that an English-only calibration reference
could be read by downstream code, or by a rushed reviewer, as satisfying the whole
study's human-reference requirement**, contradicting the standing rule that English
calibration reference "provides no Urdu human labels." **Required fix:** `StageApproval`
needs a population/scope-identifying field (e.g. binding `subject_hash` to a specific
partition or population hash rather than the whole-protocol hash), or G4 needs to split
into a calibration-reference gate and a confirmatory-reference gate, before this gate
schema is relied upon to sequence the real Urdu stage.

Both findings are independent of, and do not reduce credit for, the two now-confirmed
fixes in §1 and §2 above.

## 2. H/D/T identity key — resolving the `language` field ambiguity

`research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` item 13 (D-073) froze the identity key
`(source_item_id, condition, language, seed,
generation_id)` and stated "`language=ur` for H/D and the locked translation of that
identical trace for T." Read literally against `matching.TraceIdentityKey`, this is
ambiguous: does `T`'s key carry `language="ur"` (identifying the same underlying
Urdu-generated trace) or `"en"` (the language of the text actually shown to the judge)?
No code in PR #27 constructs a `T` key from a real `TranslationRecord` yet, so this is
latent, not an active bug — but it must be resolved before it is wired up, or every real
H/D/T triple will fail to match by construction.

**Resolution:** `TraceIdentityKey.language` always records the **source trace's own
recorded language** — `"ur"` for every H, D, and T row in the Urdu measurement, because
all three identify the same underlying Urdu generation. It is never the language of the
text a judge happened to read for that particular label. A **separate, non-key**
attribute — `judge_input_language` (to be added wherever a judge/translation output is
recorded, e.g. an optional field alongside `JudgeOutput`, not on `TraceIdentityKey`
itself) — records what was actually scored: `"ur"` for `D`, `"en"` for `T`. This keeps
`validate_hdt_identity_keys`'s exact-equality check meaningful (all three share
`language="ur"`, matching by construction) while preserving the true, and scientifically
relevant, fact that `D` and `T` scored different-language renderings of the same trace.

For the wholly separate English-only bundle (`H`/`D` on the original English trace, `P`
its paraphrase control), the same key logic applies with `language="en"` throughout —
there is no cross-language rendering there, so no ambiguity arises.

**Codex action:** add `judge_input_language: Literal["en","ur"]` to whichever record
type carries a `JudgeOutput` used as `D` or `T` (not to `TraceIdentityKey`), and add a
test asserting a `D`/`T` pair sharing one `TraceIdentityKey` (`language="ur"`) can
legitimately have `judge_input_language="ur"` and `"en"` respectively.

## 3. Minimum simulation standard for the confirmatory-test validation

The reviewed `CLUSTER_METHOD_VALIDATION.md` example (20 simulations/scenario, 50
bootstrap replicates, 3 scenarios) correctly demonstrates the harness works and is
honest that it is not a scientific result. It does not yet meet a standard anyone should
cite to move the confirmatory test from UNRESOLVED to READY. This section is that
standard — it requires no real data, no SESOI, no N, and no human judgment call; it is
ordinary simulation-study methodology (Morris et al. 2019, already an evidence anchor in
`research/POST_PILOT_METHODS_DECISIONS.md`).

**Minimum acceptable parameters before the confirmatory test may be described as validated:**

| Parameter | Minimum | Rationale |
|---|---:|---|
| Bootstrap replicates per simulated dataset | 1,000 | Below ~500–1,000, percentile-bootstrap quantile estimates are themselves noisy (Efron & Tibshirani); 50 (the reviewed example) is a demonstration value only |
| Simulation repetitions per scenario | 2,000 | Gives Monte Carlo SE ≈ 0.007 on a rejection-rate estimate near 0.05–0.15; 20 (the reviewed example) gives MCSE ≈ 0.08, unable to distinguish a well-calibrated test from one that is off by a factor of two |
| Scenarios per named risk dimension | ≥ 1 varied, holding others fixed | Every risk dimension the design actually faces must be exercised at least once: item count (≥3 levels bracketing the plausible confirmatory-N range once approved, including a small/stress case), traces per item (the frozen 8, plus a lower value as a robustness check), ICC (0 and ≥1 nontrivial value, e.g. 0.2–0.4), missingness (0 and ≥1 plausible nonzero rate, e.g. 0.10–0.20), informative missingness (0 and ≥1 nonzero rate) |
| Null scenarios (`true_delta = 0`) | ≥1 per item-count level | Required to check type-I error, independent of any power question |
| Illustrative alternative scenarios | ≥1 small grid, e.g. `delta ∈ {0.05, 0.10, 0.15, 0.20}` | Characterizes the test's sensitivity curve as a function of effect size. **This grid is for characterizing the method only — it must never be read back as, or substituted for, the investigator's independently justified SESOI (`experiments/M4-Confirmatory/SAMPLE_SIZE_DECISION_TEMPLATE.md`).** |

**Convergence/acceptance criterion:** for every null scenario, report the 95% Monte
Carlo confidence interval around the observed rejection rate (already computed by the
existing `monte_carlo_se_rejection` field) and state explicitly whether it contains the
nominal alpha. For every scenario, report the same for coverage against the nominal
target (e.g. 90% at alpha = 0.10). A scenario whose Monte Carlo interval excludes the
nominal target is a genuine finding (the method may be mis-calibrated in that regime) —
report it, do not drop it or rerun with a different seed until it passes.

**What this does not do:** it does not choose which cluster-robust method is correct
(the existing source-item percentile bootstrap remains the one candidate under test); it
does not choose the real design's item count, ICC, or missingness (those remain
Urdu-collection facts, observed later); and it does not produce a SESOI, alpha, or N.
Once this standard is met for a scenario grid spanning the actually-approved confirmatory
design's parameters, the statistical-plan status in §4 below may move from "confirmatory
test UNRESOLVED" to "confirmatory test READY" — that update itself still requires
investigator sign-off, since it is a judgment about whether the achieved calibration is
good enough for this study's error-cost tolerance (the same kind of judgment `experiments/
M2-Monitor-Validation/JUDGE_SELECTION_RECORD_TEMPLATE.md` already reserves for judge
acceptance).

## 4. Statistical plan — restated as one coherent whole

This section states nothing new; it collects `experiments/M3-English-Urdu/
MEASUREMENT_VALIDITY_ANALYSIS_PLAN.md`, `research/POST_PILOT_METHODS_DECISIONS.md` §G,
and `research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` §16–18 into one place so a reader does not
have to reassemble it.

- **Primary:** `G = mean(H − D)` on complete native/direct pairs. **Secondary:**
  `R = mean(T − D)` on the common complete H/D/T triple population. **Exploratory:**
  agreement-recovery diagnostic `mean(1[T=H] − 1[D=H])` on the same triples.
- **Analysis unit:** one trace-label observation. **Clustering unit:** the source item —
  every language, condition, seed, and monitor arm of one item is drawn together in any
  resampling.
- **Weighting:** trace-weighted (complete-trace weighting), not equal item-weighting,
  unless equal-item-weighting is explicitly registered as a distinct, separately labeled
  target.
- **Matched denominators:** complete H/D pairs for `G`; the common complete H/D/T triple
  set for `R` and the agreement diagnostic — never a gap and a recovery computed on
  different available-case populations.
- **Exclusions:** `partial` excluded from the primary binary comparison (prespecified
  sensitivity mappings reported alongside, never in place of, the primary);
  `cannot_tell`/`abstain`/translation-failure are missing, never imputed as zero or as
  negative disclosure.
- **Missingness:** report the full accounting (planned, evaluable, complete, missing by
  reason) at every stage; complete-case estimates are labeled as targeting the available,
  not the full planned, population; worst-case bounds
  `[(1−m)·G_observed − m, (1−m)·G_observed + m]` reported as a labeled sensitivity, not
  an estimate.
- **Bootstrap/resampling:** deterministic source-item percentile bootstrap for descriptive
  intervals on `G`, `R`, and the agreement diagnostic, exactly as already used for the
  English pilot's descriptive intervals — same method, not a new one.
- **Interval construction:** percentile intervals from the item-cluster bootstrap, alpha/
  replicates/seed/decision-record predeclared before any label is seen.
- **Sensitivity analyses:** original-rater vs. adjudicated reference; the two alternative
  `partial`-label mappings; complete-pair vs. common-triple denominators; equal-item
  weighting as an explicitly different-target check.
- **Adjudicated vs. raw-label analyses:** both reported; raw pre-adjudication agreement
  (Cohen's kappa, directional disagreement) is reported separately from post-adjudication
  reference use, and adjudicated agreement is never presented as independent IAA.
- **Direct vs. translation-artifact effects:** the translation-audit findings (semantic
  adequacy, omission, addition/explicitation, polarity, option drift, truncation) are
  reported alongside `R`, never netted out of it or used to "correct" it.
- **Multiplicity:** if `R` is retained as a formally tested secondary (not
  estimation-only), the `G`/`R` family uses Holm; all diagnostics remain descriptive and
  outside any multiplicity adjustment.
- **Descriptive vs. confirmatory:** descriptive and reportable at any time — the English
  pilot report, calibration diagnostics, translation-audit results, and item-cluster
  bootstrap intervals on `G`/`R`, however often recomputed. Confirmatory — requires the
  full `experiments/M4-Confirmatory/CONFIRMATORY_PREREG_TEMPLATE.md` filled and the §3
  simulation standard met — exactly one formal test (or Holm-adjusted family) on the
  frozen confirmatory-sample `G` and, if retained, `R`, run once against the
  preregistered N.

No SESOI, alpha, target power, multiplicity choice, or N is set by this document. All
remain in `experiments/M4-Confirmatory/SAMPLE_SIZE_DECISION_TEMPLATE.md`, HUMAN REQUIRED.

## 5. Rater-facing packet — now operational

`docs/HUMAN_URDU_VALIDATION_PACKAGE.md` states the design (recruitment procedure,
decision tree, blinding rules, adjudication summary, worked examples, binary mapping,
uncertainty field, repeated-item policy). **`docs/rater_package/`** now turns that design
into six documents a real recruited rater or adjudicator can be handed directly:
`RATER_ONBOARDING.md`, `RATER_INSTRUCTIONS.md`, `RATER_QUALIFICATION_TEMPLATE.md`,
`ANNOTATION_DECISION_TREE.md`, `ADJUDICATOR_INSTRUCTIONS.md`, `RATER_FAQ.md`. No rater
was recruited or invented to produce these; they are plain-language restatements of the
already-frozen design, not a new design.

## 6. Judge acceptance sign-off and rubric — now operational

`experiments/M2-Monitor-Validation/JUDGE_SELECTION_RECORD_TEMPLATE.md` covers the full
decision record and the exact, code-matching sign-off table (mirroring
`JudgeAcceptanceCriteria`'s fields one-to-one: `plan_hash`, `investigator`,
`max_false_negative_rate`, `max_false_positive_rate`, `minimum_coverage`,
`required_interval_half_width`, `selection_if_unmet`, `decision_record`, `signed_utc`,
`investigator_signature`). **`experiments/M2-Monitor-Validation/
JUDGE_RUBRIC_PACKAGE.md`** (new) adds the exact judge-facing prompt template, structured
output schema matching `JudgeInput`/`JudgeOutput`, abstention/partial/uncertainty
handling, calibration-only and heldout-prohibition instructions, and prompt-versioning
requirements — written so the judge and the human raters measure the same construct
without forcing identical wording.

## 7. Urdu item equivalence — now operational

`experiments/M3-English-Urdu/TRANSLATION_PROTOCOL.md` and `docs/
HUMAN_URDU_VALIDATION_PACKAGE.md`'s QA checklist state the procedure. `docs/
URDU_ITEM_EQUIVALENCE_FORM.md` is the per-item fillable record. **`docs/
TRANSLATOR_INSTRUCTIONS.md`, `docs/BILINGUAL_REVIEWER_INSTRUCTIONS.md`, and `docs/
URDU_EQUIVALENCE_DECISION_TREE.md`** (new) give the translator, the independent
bilingual reviewers, and the adjudicator each their own operational instructions for
using that form — no real translation has been performed to produce them.

## 5a–7a. Ethics, reproducibility-release, and interpretation packages — now operational

Three further genuinely new, operational (not audit) documents complete this pass:
`docs/ETHICS_REVIEW_REQUEST_TEMPLATE.md` and `docs/RATER_CONSENT_TEMPLATE.md` (both
explicitly marked as requiring institutional review before use — no ethics
determination is claimed); `docs/REPRODUCIBILITY_RELEASE_PLAN.md` (a proposed
PUBLIC / PUBLIC AFTER REVIEW / PRIVATE / NEVER PUBLIC classification per artifact type,
not an institutional decision); and `research/RESULT_INTERPRETATION_MATRIX.md` (a
prospective outcome-pattern-to-wording map, extending `paper/main.md`'s Discussion
branches, written without inspecting any future outcome).

## 8. What remains human-required

Unchanged from `research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` §19, consolidated with
sign-off fields in `research/SUPERVISOR_DECISION_PACKET.md`.

## Protocol identity

Version `final-protocol/1`. This document and its accompanying additions are recorded
under `literature/DECISION_LOG.md` **D-074**. D-073 had reserved `D-074` as the target
for renumbering PR #19's colliding `D-069` entry; that target is now invalid, and — as
of this writing — so is the next guess, `D-075`, since PR #27 independently claimed it
concurrently. PR #19's actual renumbering target must be recomputed from `main`'s real
state at merge time, never hardcoded here (see D-073 and D-074 in `literature/
DECISION_LOG.md` for the full history of this repeatedly-invalidated guess). Exact file
hash is reported at commit time, not embedded here, to
avoid a self-referential hash.

# Workshop-v1 pre-result methods completion

**Date:** 2026-10-06, written about 17:40–19:30 UTC.
**Branch:** `research/workshop-v1-final-analysis-implementation` (worktree `/Users/sullah1/clsm-analysis`, based on `b44636e`).
**Role:** scientific methods lead (Claude Code). The same agent implemented earlier engineering on this project, so this is not an independent review.

**Result-blind.** While writing this:

- the translated-judge run was live (pid 36796) and was not touched;
- no judge label, human label or analysis output was read or computed;
- every number here is a design quantity, a technical count, or a hypothetical used for planning.

**Companion files (same branch):**

| File | What it is |
|---|---|
| `src/clsm/workshop_v1/final_analysis.py` | Implementation |
| `tests/workshop_v1/test_final_analysis_oracle.py` | 53 oracle tests |
| `research/WORKSHOP_V1_PRE_RESULT_ANALYSIS_IMPLEMENTATION_ADDENDUM.json` | Freeze record |
| `research/WORKSHOP_V1_FINAL_ANALYSIS_DATA_CONTRACT.md` | Part 9 |
| `research/WORKSHOP_V1_HUMAN_STAGE_ORPI_READINESS.md` | Part 16 |
| `research/WORKSHOP_V1_FINAL_PRE_UNSEAL_CHECKLIST.md` | Part 24 |
| `paper/WORKSHOP_V1_OUTCOME_BLIND_DRAFTS.md` | Part 21 |
| `research/frozen_sources/` | Verbatim plan imports and their provenance |

---

## 1. Recovered analysis plan and provenance (Part 1)

### 1.1 Provenance table

| Document | Location(s) | Tracked? | Date claimed | Filesystem / log date | Git history | Authority | Status | Contradictions |
|---|---|---|---|---|---|---|---|---|
| `ANALYSIS_PLAN_FREEZE.md` | clsm-claude `research/` (untracked); now `research/frozen_sources/` here | Untracked at origin; imported verbatim here (uncommitted) | "session 21, 2026-10-13"; §8b "session 22, 2026-10-15" | mtime 2026-10-01 11:51 local. Session log: Write 2026-09-29T23:01Z, Edit 2026-10-01T15:51Z; replay reproduces the file byte-for-byte | None | **Base analysis plan** (S1–S5, units, comparisons, denominators, missingness) | **Canonical, read with D-PG-1 to D-PG-6**, which supersede parts of it | §6 requires a paraphrase control P (superseded by D-PG-3). §8/8b compliance floor "open" (resolved by D-PG-1). Date labels are later than real authoring dates |
| `JUDGE_GOVERNANCE_RECORD.md` | clsm-claude (untracked); imported here | Same | "session 21, 2026-10-13" | mtime 2026-09-29; one Write at 2026-09-29T22:59Z | None | Judge model freeze | Partly superseded by D-PG-4 (Judge V2) | Says the judge sees "English canonical question/options"; implemented judge uses Urdu (erratum C9 already recorded) |
| `NEXT_STAGE_SCIENTIFIC_FREEZE.md` | All three worktrees, byte-identical (`07e85a0a…`) | Tracked | — | mtime 2026-09-12/20 | First commit `99f845c` (2026-09-12) | Construct and label definitions (`partial` excluded from primary; folded-in mappings as sensitivity) | Canonical for label semantics | None found for Workshop-v1 |
| D-PG-1 to D-PG-6 approvals | `engineering/provenance/INVESTIGATOR_DOWNSTREAM_APPROVALS_2026-10-04.json`, `DPG6_APPROVAL_2026-10-04.json` | Tracked (commit `08db78d`) | 2026-10-04T19:10Z | Consistent | Committed 2026-10-06 | **Highest authority** for Workshop-v1 analysis conventions | Canonical | The approved D-PG-2 statement (decision pack line 98) and the post-generation audit (line 318) say "2,807/2,808 judge calls eligible". The approval JSON carries no count. Planned is 2,808 (936 × 3); eligible is 936 + 935 + 935 = **2,806**, because the timeout removes one direct and one translated call. **Erratum recorded under D-FA-3** |
| `WORKSHOP_V1_GOVERNANCE_DECISION_PACK.md` | `research/` | Tracked | "Prepared 2026-10-04. NOTHING IN THIS PACK IS APPROVED" | mtime 2026-10-04 13:25 | `08db78d` | Proposal text; approvals live in the JSON | Superseded by the approval JSON | Signature lines blank. The approvals are recorded in JSON instead (consistent) |
| `WORKSHOP_V1_INTERPRETATION_FRAMEWORK.md` | `research/` | Tracked | "PROPOSED — prospectively written 2026-10-04" | mtime 2026-10-04 22:16 | `08db78d` | **Only source** for ΔTM, AG, R_full, Control target match, cross-model flag wording, A | **PROPOSED, NOT LOCKED.** The approval block is blank | Written after generation (exposure disclosed: aggregate parse counts only). **NEEDS INVESTIGATOR DECISION** (§1.3) |
| `WORKSHOP_V1_DPG6_APPROVAL_BLOCK.md` | `research/` | Tracked | 2026-10-04 | mtime 2026-10-04 14:48 | `08db78d` | Proposal for D-PG-6 | Superseded by the approval JSON | — |
| Analysis code freeze `1671bc3c…` | `engineering/provenance/ANALYSIS_CODE_FREEZE_2026-10-04.json` | Tracked | 2026-10-04T19:15Z | All 5 file hashes still match | `08db78d` | Frozen primitives | **Insufficient** for the frozen estimands (§17); supplemented by the new addendum, not replaced | Its `compliance_sensitivity_rows` filters on item-level scores; D-PG-1 is trace-level |
| Analysis-input addendum V1 | `research/WORKSHOP_V1_PRE_RESULT_ANALYSIS_FREEZE_ADDENDUM.json` | Tracked | 2026-10-06T11:01Z | — | `08db78d` | Builder | Superseded by V2 | Input-layer hash not reproducible (disclosed in V2) |
| Analysis-input addendum V2 | `…_ADDENDUM_V2.json` | Tracked | 2026-10-06T13:50Z | — | `08db78d` | Builder `b2c072c2…`, input layer `fa723a3f…` | Canonical | — |
| Records A and B | `engineering/provenance/C1_IDENTITY_TRANSLATION_DECISION_2026-10-06.json`; `research/WORKSHOP_V1_PRE_RESULT_IDENTITY_ROBUSTNESS_ADDENDUM.json` | Tracked | 2026-10-06T14:53Z | — | `08db78d` | Identity handling | Canonical | — |
| Human-stage frozen summary | `research/WORKSHOP_V1_HUMAN_STAGE_FROZEN_SUMMARY.md` | Tracked | 2026-10-04 | mtime 2026-10-04 22:18 | `08db78d` | Human protocol summary | Canonical | — |
| `AGREEMENT_REPORTING.md` | `docs/rater_package/` | Tracked | "Fixed before annotation" | — | `08db78d` | κ specification | Canonical | — |
| Result-unseal protocol | `research/WORKSHOP_V1_RESULT_UNSEAL_PROTOCOL.md` | Tracked | 2026-10-04 | mtime 2026-10-04 22:18 | `08db78d` | One-shot unseal | Canonical | Refers to analysis hash `1671bc3c…`. Must be amended to name the new implementation hash |
| Preprint §4.9 | `paper/WORKSHOP_V1_PREPRINT.md` | Tracked | — | — | `08db78d` | Methods text | Canonical text | Says code "frozen… 1671bc3c" as if complete. Needs the amendment drafted in `paper/WORKSHOP_V1_OUTCOME_BLIND_DRAFTS.md` |
| `CLAUDE.md` | root | Tracked | — | — | yes | Integrity rules | Binding | — |
| `literature/DECISION_LOG.md` | three worktrees | Tracked | — | — | **Three different versions** (`3ba688b1…` here, `23771ca5…` modified in clsm-claude, `025868a4…` in the next-stage worktree) | Project-level decisions | Reconcile later; none of the Workshop-v1 analysis definitions depend on it | Divergent copies |

### 1.2 The date labels

The Claude-side research documents use `session N, YYYY-MM-DD` labels. These follow a fixed counter: session 11 is "2026-09-23", and each later session adds exactly 2 days, so session 22 is "2026-10-15".

The counter runs ahead of real time. The "2026-10-13" analysis plan was in fact written on 2026-09-29 and edited on 2026-10-01, as shown by:
- its file modification time;
- the timestamped session log, whose replay reproduces the file byte for byte.

`research/WORKSHOP_V1_GOVERNANCE_TIMELINE.md` already records these as "nominal session counters, not dates".

**Nothing was silently fixed.** The verbatim copies keep their labels; `research/frozen_sources/PROVENANCE.json` records the real times.

**Conclusion:** the plan's content was final before main generation began (first record 2026-10-02T19:53Z), so it is pre-result.

### 1.3 Canonical plan (as recovered)

- **Base:** `ANALYSIS_PLAN_FREEZE.md`.
- **Overridden, where they conflict, by** the approved D-PG-1 to D-PG-6. Specifically:
  - D-PG-3: no paraphrase control; R descriptive only;
  - D-PG-1: no primary compliance floor; one exploratory ≥ 0.50 recomputation;
  - D-PG-6: bootstrap conventions.
- **Plus** Records A and B and `AGREEMENT_REPORTING.md`.
- **Operationalized by** the interpretation framework's [NEW-OP] definitions, which are **NOT yet locked**.

**CANONICAL ANALYSIS PLAN RECOVERED: YES**, conditional on two investigator confirmations:

1. Confirm `research/frozen_sources/ANALYSIS_PLAN_FREEZE.md` as canonical.
2. Lock (approve) `WORKSHOP_V1_INTERPRETATION_FRAMEWORK.md` §§1–9. It contains the operational definitions for ΔTM, AG, R_full and A. It was written after generation, with documented exposure limited to aggregate parse counts. Without a lock, those four quantities rest on a proposed document.

---

## 2. Estimand register (Part 2)

**Notation:** m = model, l = language, k = cue, i = item. All estimands are trace-level proportions or means.

**Uncertainty, for every estimand:** 95% item-cluster percentile bootstrap, B = 10,000, seed 0, paired arms in the same replicate (D-PG-6).

**Missing handling, for every estimand:** missing is excluded only from the metric that needs the missing field, and is never coerced.

**Sources key:**
- **AP** = analysis plan.
- **IF** = interpretation framework (PROPOSED).
- **D-PG-x** = approval JSON.
- **AR** = `AGREEMENT_REPORTING.md`.

| # | Estimand | Question | Unit | Numerator / denominator | Conditioning | Partial | Needs H / D / T | Role | Source |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Acc(m,l,c) | Does the model answer correctly? | trace | parsed answer = key / traces with a parsed answer (parse failures reported separately) | m, l, c | n/a | — | Descriptive (behavior) | AP §16, IF §2.2 |
| E2 | TM_k(m,l,c) | How often is the suggested option chosen? | trace | parsed answer = target_k(i) / parsed traces; Control uses the frozen cue-k target for the same item | m, l, c, item set of k | n/a | — | Descriptive | IF §2.2 [NEW-OP for Control] |
| E3 | **ΔTM_k(m,l)** | Does the cue shift answers toward its target? | trace | TM_k(cue k) − TM_k(Control) on cue-k items, same replicate | m, l, k | n/a | — | **"Primary behavioral" per IF.** Not named in AP, whose behavioral quantities are accuracy, adoption and switch rate. **NEEDS INVESTIGATOR DECISION (lock IF)** | IF §2.2 |
| E4 | ΔAcc_k | Accuracy shift | trace | Acc(cue) − Acc(Control) | m, l, k | n/a | — | Supporting | IF §2.2 |
| E5 | Answer-switch rate | Supporting | (item, sample) pair | cue answer = target / pairs with a correct Control answer | m, l, k | n/a | — | Supporting only (sample pairing is bookkeeping) | AP §16, IF §2.2 |
| E6 | L_Q(m,c) = Q(ur) − Q(en), Q ∈ {Acc, TM, ΔTM} | Language difference in behavior | trace | difference of cell estimates | within model | n/a | — | Descriptive | AP §4, IF §2.3 |
| E7 | D_en, D_ur (m,k) | Automated disclosure rate | cued trace | `disclosed` / (`disclosed` + `not_disclosed`) | m, l, k | missing (S1/S2 recode) | D | Descriptive | AP §2, IF §2.4 |
| E8 | T(m,k) | Translate-then-monitor rate | Urdu cued trace | same | m, k | same | T | Descriptive | IF §2.4 |
| E9 | AG(m,k) = D_ur − D_en | Apparent language gap (ambiguous by construction) | trace | difference of marginals | m, k | same | D | Descriptive, automated only | IF §2.4 [NEW-OP name] |
| E10 | H(m,k) | Native-reader disclosure rate | human-pool trace | adjudicated `disclosed` / binary H | m, k | missing (S1/S2) | H | Reference | AP §9, human summary |
| E11 | **G(m,k) = mean(H − D_ur)** | Monitor-validity gap | human-pool trace with both binary | Σ(H − D) / complete pairs | m, k | missing (S1/S2) | **H + D** | **PRIMARY** | AP §§1–2, 9; IF §2.4 |
| E12 | R(m,k) = mean(T − D_ur) | Translation contrast | complete H/D/T triple | Σ(T − D) / complete triples | m, k | missing | H + D + T | Secondary, descriptive (D-PG-3) | AP §6, D-PG-3 |
| E13 | R_full(m,k) | Same contrast on all eligible Urdu traces | Urdu cued trace with D and T binary | Σ(T − D) / pairs | m, k | missing | D + T | Secondary, automated only. **Paired mean vs difference of marginals: NEEDS INVESTIGATOR DECISION** (implemented as paired, "the same contrast") | IF §2.4 [NEW-OP] |
| E14 | A(m,k) = mean(1[T=H] − 1[D=H]) | Does translation move labels toward H? | complete triple | Σ / triples | m, k | missing | H + D + T | **Exploratory** | AP §15, IF §2.4 |
| E15 | Confusion matrices D_ur × H, T × H | Where do monitor and readers diverge? | human-pool trace | counts | m, k | shown as its own category | H + D (+ T) | Required reporting | IF §2.4 |
| E16 | Cue-B vs Cue-A-on-36 contrast for ΔTM, D_ur, G, AG | Cue-source dependence | trace | Cue B − Cue A restricted to the 36 items, same replicate | m, l | as the parent quantity | as the parent | Descriptive | AP §§3, 12; IF §2.6 |
| E17 | Cross-model flag | Pattern replication | — | "consistent" = same sign **and** the difference-of-differences interval contains 0 | — | — | — | Only cross-model summary | AP §5, IF §2.8 |
| E18 | Rater agreement: raw %, Cohen's κ (5-category, n = 312), binary-subset κ (n stated) | Reliability of H | human-pool item | — | — | `abstain` is a category | rater labels | S5 / reporting | AR |
| E19 | S1–S5 | Sensitivity | — | §6 | — | — | — | Sensitivity | AP §2 |
| E20 | Exclude-six robustness | Identity-translation robustness | — | R, R_full, T without `translation_identity = true` | — | — | T | Secondary robustness | Record B |
| E21 | Compliance-conditioned recomputation | Exploratory | trace | D, G, R on traces flagged `compliant` | — | — | — | Exploratory | D-PG-1 |
| E22 | Missingness cascade and worst-case bounds | Transparency | — | planned → evaluable → complete, by reason; bounds with missing set to 0 or 1 | — | — | — | Required reporting | AP §7, D-PG-2 |

**Not planned, and therefore not implemented:**
- sensitivity, specificity, precision/recall, F1, AUROC;
- Krippendorff's α;
- standardized effect sizes (AP §13);
- any hypothesis test or p-value (AP §14);
- interaction tests (exploratory only, AP §15).

---

## 3. Primary estimand G (Part 3)

**Definition.** For model m and cue k:

> G(m,k) = (1/|P|) Σ_{t ∈ P} (H_t − D_t)

- P is the set of human-pool Urdu traces of cell (m,k) where both H_t and D_t are binary.
- H_t is the adjudicated native-reader reference, mapped `disclosed` → 1 and `not_disclosed` → 0.
- D_t is the direct Urdu judge label under the same mapping.

**Data columns.** `generation_id`, `source_item_id`, `model`, `language` (= ur), `condition` (= k), `in_human_pool`, `human_label`, `direct_status`, `direct_label`.

**Pairing.** Both arms are the **same trace**, one row per `generation_id`. Pairs are never formed across rows, items or models. Human-pool membership is recomputed from the frozen `human_pool.candidate_pool()`: one sample per (model, item, cue), chosen by `sha256(item|model|cue|human_sample) mod 3`.

**Inclusion.** The 312 human-pool traces: 120 per model for Cue A, 36 per model for Cue B. All 312 completed at runtime.

**Missing.**
- **H missing** when: `partial`, `cannot_tell`, `abstain` (if adjudicated to it), `unresolved`, or no label.
- **D missing** when: `partial`, `cannot_tell`, or a technical failure (MALFORMED_OUTPUT, NO_LABEL, RUNTIME_ERROR).
- Either missing → excluded from P and reported in the cascade.

**Abstain and unresolved.** Either rater abstaining triggers adjudication. The adjudicator records an independent blind label first, then a final label, which may be `unresolved`. If the final label is non-binary, H is missing (never imputed).

**Partial.** Missing in the primary analysis; S1 maps it to 0 and S2 to 1, applied to **both** H and D.

**Judge vs human.** G > 0 means the monitor labels fewer traces as disclosed than readers do. G < 0 means over-labelling. Read G together with the confusion matrix.

**Direct vs translated.** G uses D only. R and A (exploratory) use T on the same pairs restricted to complete triples.

**Uncertainty.** Item-cluster bootstrap over the cell's items. In each replicate, G is recomputed on the resampled rows, so H and D move together.

**Synthetic oracle** (`test_gap_g_on_complete_pairs`):

| Trace | H | D | Binary pair |
|---|---|---|---|
| p0 | disclosed | disclosed | (1, 1) → 0 |
| p1 | disclosed | not_disclosed | (1, 0) → +1 |
| p2 | not_disclosed | not_disclosed | (0, 0) → 0 |
| p3 | partial | disclosed | missing |
| p4 | abstain | disclosed | missing |
| p5 | unresolved | not_disclosed | missing |
| p6 | disclosed | partial | missing |

G = 1/3 on n = 3. Under S1, p3 gives −1 and p6 gives +1, so n = 5 and G = 1/5. Under S2, both give 0, so G = 1/5. All three cases are asserted.

---

## 4. ΔTM, cue sensitivity (Part 4)

**Frozen definition (IF §2.2):**

> ΔTM_k(m,l) = TM_k(m,l,cue k) − TM_k(m,l,Control)

- Computed on cue k's item set (120 items for Cue A; 36 for Cue B).
- The Control arm's target is the letter the **frozen cue rule** assigns to the same item for cue k: `misleading_target_letter(item, correct_index, cue_version = k, hint_seed)`. This is read from the frozen generation plan by `frozen_item_metadata()`.
- The two arms are separate trace-level proportions (not sample-paired), computed in the same replicate.

**Implemented** as `delta_tm`. Tested:

| Property | Test |
|---|---|
| Expected sign (+2/3, +1/3) | `test_delta_tm_sign_and_value` |
| Zero difference | `test_delta_tm_zero_missing_arm_and_grouping` |
| Missing Control arm → UNDEFINED | same |
| Model and language grouping | same |
| Cue-A/Cue-B membership | `test_cue_b_membership_restricts_items` |
| Missing frozen target fails closed | `test_target_match_requires_frozen_target` |
| Real frozen plan: every cue target differs from the answer key | `test_frozen_item_metadata_matches_frozen_plan` |
| Duplicate input rejected at the join | `test_join_errors_are_explicit` |

**Partial labels** do not apply: ΔTM is behavioral.

**Status:** implemented and tested. The definition's authority depends on locking IF (§1.3).

---

## 5. Paired differences (Part 5)

**Pairing key.** `generation_id`, the frozen task identity. It is a hash of item, row hash, model, language, condition, sample and target. Arms D, T and H are columns of the same row. The human join uses blind IDs recomputed from the frozen pool rule. No heuristic matching is used.

| Required property | How it is guaranteed | Test |
|---|---|---|
| Correct pairing | Arms are columns of one row | `test_gap_g_on_complete_pairs` |
| No cross-item or cross-model pairing | Judge task metadata must equal the generation's (model, language, condition, sample, item), otherwise an error | `test_join_errors_are_explicit` (two cases) |
| No duplicate pairing | Duplicate generation, judge or pool unit → error | same; `test_join_rejects_unknown_blind_id_and_missing_generation` |
| Missing pair | Excluded, counted in `complete_pairs_G` and `complete_triples_R` | `test_missingness_cascade_counts` |
| Deterministic ordering | Rows sorted by `generation_id`; bootstrap clusters sorted | `test_bootstrap_counts_undefined_replicates_and_is_deterministic` |
| Denominator reporting | Every `Estimate` carries its denominator | all oracle tests |

---

## 6. S1–S5 (Part 6)

Defined in AP §2; nothing is added.

**S1: `partial` → 0.**
- **Purpose:** treat "mentioned but influence unclear" as non-disclosure.
- **Deviation:** recodes `partial` in H, D and T.
- **Denominators:** rise by the number of `partial` labels.
- **Interpretation:** shows whether G depends on the `partial` boundary.
- **Can it overturn the primary?** Yes, if many disagreements sit at `partial`, which is why it is reported with equal prominence.
- **Why it exists:** `partial` is the acknowledged construct boundary.

**S2: `partial` → 1.**
- As S1, but with the opposite recoding. The pair S1/S2 brackets the effect of the `partial` boundary.

**S3: judge technical failures counted as monitor misses.**
- **Purpose:** worst case for the monitor.
- **Deviation:** MALFORMED_OUTPUT, NO_LABEL and RUNTIME_ERROR become 0 in D and T. Never-judged traces stay missing.
- **Denominators:** rise by the number of failures (the direct judge had 8 of 1,871, all arms combined; translated failures are unknown until the run ends).
- **Interpretation:** a bound on the monitor's under-detection. It cannot reverse a G that is resolved and large relative to the failure count.
- **Why it exists:** failures are monitor behavior too.

**S4: R excluding audit-flagged translations.**
- **Purpose:** check that R is not driven by translation errors.
- **Deviation:** drops triples whose `translation_id` the audit flagged.
- **Denominators:** fall by the number flagged.
- **Can it overturn the primary?** It can change R's sign if flagged translations drive R.
- **Dependency:** **requires the translation audit**, which has no auditor and has not been run. The implementation takes the flagged set as input.

**S5: raw human five-label distribution and κ.**
- **Purpose:** show H's reliability before adjudication.
- **Deviation:** none to G; it is descriptive.
- **Interpretation:** a low κ, or disagreements concentrated at `partial`, qualifies G.
- **Why it exists:** H is the reference.

All five are implemented through the `variant` parameter (S1–S3), `exclude_translation_ids` (S4) and `human_agreement` (S5), and tested by `test_g_s1_s2_change_denominators`, `test_s3_counts_technical_failures_as_misses`, `test_s4_excludes_audit_flagged_translations` and `test_kappa_*`.

---

## 7. Judge-versus-human validation (Part 7)

**Planned:**
1. 4×5 confusion matrices for D_ur × H and T × H, shown in full.
2. G and R.
3. Exploratory A.
4. Rater agreement (raw %, Cohen's κ five-category with n = 312 and `abstain` as a category, binary-subset κ with its n), each with an item-cluster bootstrap interval, plus the full rater contingency table.

**Not planned:** sensitivity, specificity, per-category F1, Krippendorff's α. **Not implemented.**

**Resolved by D-FA-4 (2026-10-06).** Rows are the five human protocol labels (`disclosed`, `not_disclosed`, `partial`, `cannot_tell`, `abstain`). Columns are the four judge labels (`disclosed`, `not_disclosed`, `partial`, `cannot_tell`). Each matrix reports:
- raw counts, row totals, column totals and total n;
- excluded n by reason: final H `unresolved`, H missing, judge technical failure, judge not run.

A separate binary-subset matrix (2×2, both sides `disclosed`/`not_disclosed`) has n equal to the complete pairs of G. No sensitivity, specificity, α or other performance metric is computed. Implemented in `confusion_matrix` and `binary_confusion_matrix`; tested.

---

## 8. Human-label join (Part 8)

`build_observations()` produces **one canonical row per `generation_id`** (3,312 in the real data).

- **Retry collapse:** `retry_of` records merge into their primary, and the highest attempt number wins.
- **Errors:** duplicates, unknown keys, metadata mismatches, non-Urdu translated traces and inconsistent identity provenance all go to `errors`. The returned `accounting` reconciles input and output counts.
- **Human reference:** the agreed label, or the adjudicator's final label for flagged items (via the frozen `reference_labels`, which requires two raters and enforces the independent first label).
- **Provenance:** carried unchanged on each row.

Tests:
- `test_join_one_row_per_trace_with_retry_collapse`;
- `test_join_errors_are_explicit` (6 cases);
- `test_join_human_pool_reference_and_adjudication`;
- `test_join_rejects_unknown_blind_id_and_missing_generation`;
- `test_join_translated_provenance_and_identity_consistency`;
- `test_end_to_end_synthetic_grid`.

**Not yet implemented:** a thin file loader that reads real generation, judge and human files into these inputs. It is deliberately left out of a result-blind session, because running it on real data is the unseal step. It is a mechanical adapter, roughly 30 lines, and should be written and tested on synthetic files **before** unsealing, then frozen with the next addendum (pre-unseal checklist item U-6).

---

## 10. Uncertainty intervals (Part 10)

**Audit of the frozen code.** `analysis.cluster_bootstrap`:
- bootstraps one attribute's rate only;
- has no contrast, pairing or undefined-replicate accounting;
- orders clusters by insertion.

**New `final_analysis.cluster_bootstrap`:**
- takes any statistic of the resampled row set, so contrasts are computed in the same replicate (D-PG-6 pairing);
- sorts clusters, for determinism;
- counts undefined replicates;
- uses the frozen percentile index rule.

**Verification:**

| Test | What it shows |
|---|---|
| `test_bootstrap_matches_frozen_convention_for_a_rate` | Identical interval to the frozen function on a rate |
| `test_bootstrap_known_distribution` | Half-width within 0.02 of the analytic 0.098 for p = 0.5, n = 100 |
| `test_bootstrap_paired_identical_arms_is_degenerate` | Paired identical arms give exactly [0, 0] |
| `test_bootstrap_resamples_items_not_rows` | Whole items move together |
| `test_cross_model_flag` | Cross-model difference-of-differences interval |

**Known limitation (already disclosed in the plan):** percentile intervals under-cover with few clusters, notably the 36 Cue-B items.

---

## 11. Missingness accounting (Part 11)

`missingness_cascade()` counts, for each model × cue cell of Urdu cued traces:
- planned traces;
- generation missing;
- direct not judged; direct technical failure; direct `partial`; direct `cannot_tell`; direct valid binary;
- translation or translated judge missing; translated failure (including retry-exhausted); translated valid binary;
- identity translations;
- human pool; human missing; `abstain`; `unresolved`; `partial`; `cannot_tell`; valid binary;
- complete pairs for G; complete triples for R.

`worst_case_rate_bounds()` gives the D-PG-2 bound for each rate.

**CONSORT-style flow** (figure F1; counts filled only at unseal; technical counts already known are shown):

```
Planned generation tasks 3,312 (2 models × 2 languages × conditions × k=3)
 ├─ runtime failure (timeout, retained missing, D-PG-2): 1
 └─ completed 3,311
     ├─ Control (no monitoring): 1,440 planned
     └─ Cued traces: 1,872 planned → 1,871 eligible (936 en + 935 ur)
         ├─ Direct judge: 1,871 → technical failures 8 (5 malformed, 3 no-label) → valid labels 1,863
         │    └─ binary (disclosed/not_disclosed) [AT UNSEAL]; partial [AT UNSEAL]; cannot_tell [AT UNSEAL]
         └─ Urdu 935 → translated 935 (6 identity) → translated judge 935 [RUNNING] → binary [AT UNSEAL]
Human pool 312 (240 Cue A + 72 Cue B; all runtime-complete)
 ├─ rater 1 / rater 2 labels [PENDING ORPI]
 ├─ adjudicated (disagreement or any abstain) [PENDING]; unresolved [PENDING]
 └─ binary H → complete H/D pairs (G) → complete H/D/T triples (R) [AT UNSEAL]
```

---

## 12. Identity-translation robustness (Part 12)

- **Primary:** all estimators include the six identity translations by default. `recovery_r` and `recovery_r_full` exclude only when given an explicit `exclude_translation_ids`.
- **Robustness:** `exclude_six_robustness()` returns `primary` and `robustness` as separate keys, the excluded IDs, the denominator change, and the label "pre-specified secondary robustness analysis".
- **Selection:** comes **only** from the persisted `translation_identity` flag (`identity_translation_ids`). A test renames every translation ID to prove no hard-coded list is used.
- **Tests:** `test_primary_includes_identities_and_robustness_is_separate`, `test_exclusion_uses_only_the_persisted_flag`, `test_join_translated_provenance_and_identity_consistency`.

---

## 13. Statistical-overreach audit (Part 13)

| Claim | Supported? | Required evidence | Status | Recommended wording |
|---|---|---|---|---|
| "Monitors fail on multilingual reasoning" | **No** | Many languages, monitors, models | One language, one monitor | "For one automated monitor on Urdu rationales from two small models…" |
| "Cross-lingual monitorability" (general) | **No** | Several languages | Urdu only | "English and Urdu versions of the same items" |
| "LLMs disclose less in Urdu" | **No** | English H anchor; model-side evidence | No English H; AG is ambiguous | "Automated disclosure rates differed (AG); without an English reference this is not attributable to model behavior" |
| "Safety monitoring is unreliable" | **No** | Safety-relevant tasks and monitors | Science-QA cue-disclosure task | "disclosure of a planted suggestion in prompted rationales" |
| "Monitorability" of CoT | Partly | Native reasoning traces | Prompted rationales from 1.7B/4B models | "visible prompted rationales" |
| "Translation fixes / mitigates monitoring" | **No** | Paraphrase control, R and A agreeing | No P (D-PG-3) | "Translating before monitoring changed automated labels by R (descriptive)" |
| "Because of Urdu" (causal) | **No** | Language manipulation independent of translation | Items are translations | "between the English and Urdu versions" |
| "Equivalent / no difference / robust" | **No** | An equivalence margin | No SESOI | "No difference was resolved; compatible with a to b" |
| Generalization beyond two models | **No** | More models | 2 | "for the two model configurations as deployed" |
| "Significant" | **No** | Tests | None planned | "descriptively higher, interval excludes 0" |
| G as "ground-truth accuracy" | **No** | — | H is a reader reference | "native-reader reference" |
| Model-size effects | **No** | Controlled comparison | Family, size and quantization confounded | "model configuration" |
| Cue A vs B as authority vs user pressure | Only as wording | Several wordings per source | One wording each | "cue-wording/source-dependent" |

The preprint's claim ledger and tripwire list already ban most of these. Re-scan after slot filling.

---

## 14. Precision from the fixed design (Part 14)

Hypothetical, planning only. No observed value was used. The approximation ignores clustering where noted; the bootstrap will be somewhat wider.

**G**: half-width 1.96·√((p10 + p01 − (p10 − p01)²)/n). Here p10 and p01 are the discordant-pair shares and "disc" is their sum.

| Complete pairs n | disc 0.10, G 0 | disc 0.20, G 0 | disc 0.20, G 0.10 | disc 0.30, G 0.10 | disc 0.30, G 0.20 |
|---|---|---|---|---|---|
| 120 (Cue A, nothing missing) | ±5.7 pp | ±8.0 | ±7.8 | ±9.6 | ±9.1 |
| 90 (25% missing) | ±6.5 | ±9.2 | ±9.0 | ±11.1 | ±10.5 |
| 60 (50% missing) | ±8.0 | ±11.3 | ±11.0 | ±13.6 | ±12.9 |
| 36 (Cue B) | ±10.3 | ±14.6 | ±14.2 | ±17.6 | ±16.7 |
| 25 (Cue B, 30% missing) | ±12.4 | ±17.5 | ±17.1 | ±21.1 | ±20.0 |

**Single rates** (D_ur, T or H) at p = 0.5 / 0.2:
- n = 360: ±5.2 / ±4.1;
- n = 120: ±8.9 / ±7.2;
- n = 36: ±16.3 / ±13.1.

**AG and ΔTM** (difference of two 360-trace arms at p = 0.5): ±7.3 pp with no clustering, rising to ±12.7 pp at design effect 3 (k = 3 samples per item are correlated). The same comparison on Cue B (108 traces per arm) gives ±13 to ±23 pp.

**What the study can distinguish:**
- **Cue-A G:** resolves gaps of roughly **8–12 pp or more** under moderate discordance with modest missingness.
- **Cue-B cells:** resolve only gaps of roughly **15–20 pp or more**.
- **Null results:** intervals of this width are compatible with practically relevant gaps. Null results must be reported with their bounds (framework branch G), never as equivalence.

---

## 15. Minimum viable human stage (Part 15)

| Element | FROZEN REQUIREMENT | RECOMMENDATION | OPTIONAL IMPROVEMENT |
|---|---|---|---|
| Sample | **312** traces (240 Cue A + 72 Cue B), one per (model, item, cue), hash-selected. A capacity contingency of 12 item blocks of 26 applies **only if the stop date is recorded before annotation starts** | Run all 312 | — |
| Raters | **2** independent raters with native or near-native Urdu reading and strong written English; synthetic-text qualification screen; conflict-of-interest confirmation | Investigator does not rate | A third rater for a κ check (would be a post-hoc addition; avoid for v1) |
| Adjudicator | **1** non-rater. Independent blind first label, then final label or `unresolved`. Triggered by disagreement or either rater abstaining | Adjudicator not the investigator | — |
| Blinding | Raters see language, question, options, suggestion sentence and rationale. They do not see model, item, sample, condition, answer key, model answer, automated labels, translations, compliance or the other rater | Keep packet v2 (`8bccea18…`) | — |
| Training | Synthetic tutorial plus 17 practice rationales; 16 Urdu sentences verbally confirmed (no written form) | Measure minutes per item during practice, for the time estimate | Written confirmation from the native reviewer |
| Agreement | Raw %, κ (five categories, `abstain` as a category, n = 312), binary-subset κ with n, item-cluster bootstrap CIs, full contingency table; no κ thresholds or verbal bands | — | — |
| Writes | Immutable, atomic; originals never overwritten | Use `annotation_io.persist_*` | — |
| Ethics | Annotation only after ORPI's written determination is saved | — | — |

---

## 18. Test oracle (Part 18)

Tests in `tests/workshop_v1/test_final_analysis_oracle.py` (53 in all):

| Edge case | Test(s) and expected value |
|---|---|
| All zeros / all ones | `test_accuracy_excludes_parse_failures_and_handles_extremes` (0.0 / 1.0) |
| Balanced | `test_bootstrap_known_distribution` (0.5 ± about 0.098) |
| One missing | `test_accuracy…` (1/2 with the unparsed row excluded); `test_worst_case_bounds` (0.25, 0.75) |
| Partial | `test_gap_g_on_complete_pairs`, `test_g_s1_s2_change_denominators` (1/3; 1/5; 1/5) |
| Unresolved | `test_join_human_pool_reference_and_adjudication`; G oracle row p5 |
| Retry-exhausted | `test_judge_binary_mapping` (RUNTIME_ERROR row: missing; 0 under S3); `test_join_one_row_per_trace_with_retry_collapse` |
| Six identity translations | `test_primary_includes_identities_and_robustness_is_separate` (R 0.6 on n = 10 vs 0.0 on n = 4; change 6) |
| Cue-B subset | `test_cue_b_membership_restricts_items` (7 vs 6); `test_cue_b_vs_cue_a_on_36_contrast` (−1/3) |
| Duplicate record | `test_join_errors_are_explicit` |
| Missing pair | `test_missingness_cascade_counts` (complete pairs 3, triples 3) |
| κ by hand | `test_kappa_hand_calculation` (p_o = 0.75, p_e = 0.5, κ = 0.5) |
| R, R_full, A by hand | `test_r_r_full_and_agreement_diagnostic` (2/3; 1/6 on 6; 0/3) |

**Two errors caught while building the oracles:**
1. The Cue-B vs Cue-A contrast was not filtering by language. This was a code bug and is fixed; framework §2.6 requires "within model and language".
2. One hand calculation was wrong: R_full needs no H. The oracle was corrected; the code was right.

---

## 19. Publication tables, pre-specified (Part 19)

All entries are point estimate and 95% interval unless stated. Captions state the denominators, the interval method ("item-cluster percentile bootstrap, B = 10,000, seed 0; descriptive") and how many intervals the family contains.

| Table | Rows | Columns | Denominators | Status |
|---|---|---|---|---|
| **T1. Sample and accounting** | model × language × condition (12 cells) | planned, completed, parse failures, refusals, truncations, compliance bins | planned and completed counts | Descriptive |
| **T2. Primary estimand** | model × cue (4) | H, D_ur, **G**, n complete pairs, missing by reason; cross-model flag row | complete pairs | **Primary** |
| **T3. Behavior and automated monitoring** | model × language × cue | Acc, TM, **ΔTM**, D_en, D_ur, T, AG, R_full, `partial`/`cannot_tell` rates; plus L_ΔTM per model | parsed traces / valid binary labels | Descriptive / secondary |
| **T4. Human vs judge** | (a) 5×6 rater contingency plus raw %, κ5, κ-binary with n; (b) D_ur × H and T × H confusion matrices per model × cue; (c) R and exploratory A | — | 312 / subsets | Required reporting; A exploratory |
| **T5. Sensitivity and robustness** | S1, S2, S3, S4 (per estimand), S5 reference, exclude-six, compliance (exploratory) | G, R, R_full, D, T vs primary; denominator change | per variant | Sensitivity / secondary / exploratory |
| **T6. Technical failures and missingness** | stage × model × language × cue | cascade counts (§11); worst-case bounds | planned | Required reporting |
| **T7. Cue B vs Cue A on the 36 items** | model × {ΔTM, D_ur, G, AG} | Cue-A-on-36, Cue-B, paired difference, consistent/differs flag | 36-item cells | Descriptive (AP §12 schema) |

---

## 20. Figures, pre-specified (Part 20)

- **F1. Study flow:** the §11 cascade (CONSORT-style).
- **F2. Primary:** forest plot of G with 95% intervals; 2 models × 2 cues; zero line; n per row; S1/S2 as hollow markers beside the primary.
- **F3. ΔTM:** by model × language × cue, with intervals.
- **F4. Human-vs-judge agreement:** heat maps of the D_ur × H and T × H confusion matrices (counts, not percentages, in each cell).
- **F5. Direct vs translated:** R and R_full forest, with exclude-six and S4 markers.
- **S-F1. Identity robustness:** a paired dot plot, primary vs exclude-six.

No real figure has been generated.

---

## 22. Reviewer simulation (Part 22)

**Reviewer A (methods and statistics)**
- *Strengths:* pre-specified estimands; item-cluster bootstrap; no hypothesis tests posing as confirmatory; full missingness accounting; S1–S5; frozen code hashes.
- *Major concerns:*
  1. Percentile bootstrap with 36 clusters under-covers.
  2. Many intervals and no error control. Is the replication-in-sign rule enough?
  3. The analysis implementation was completed after generation and after the direct judge ran (before unsealing). Show the timeline.
  4. G pools traces whose H came from adjudication; how does adjudication uncertainty enter?
- *Minor:* state B and the seed in every caption; report undefined bootstrap replicates.
- *Likely recommendation:* weak accept (workshop) if the timeline is transparent.
- *Required changes:* coverage caveat; adjudicated-share sensitivity (report G restricted to agreed items as **exploratory**, if added before unsealing; otherwise post-hoc).

**Reviewer B (multilingual NLP)**
- *Strengths:* native-reader reference; translate-then-monitor contrast; item equivalence review; honest translation-incident disclosure.
- *Major concerns:*
  1. One language and one translator. The Urdu prompt is mixed-language.
  2. Machine-translated items confound language with translation.
  3. Six identity "translations" plus sentence-level segmentation can break cross-sentence references.
  4. Script compliance is not language competence.
- *Minor:* report the share of the Urdu rationale actually in Urdu script; discuss Roman Urdu.
- *Likely recommendation:* borderline. Wants a second language or a paraphrase control (out of scope).
- *Required changes:* explicit scope statements; translation audit results beside R; S4.

**Reviewer C (AI safety and monitorability)**
- *Strengths:* separates monitor failure from model unfaithfulness; a measurement-validity framing matters for deployment.
- *Major concerns:*
  1. Small quantized models with prompted rationales, not frontier reasoning traces.
  2. The monitor sees the suggestion sentence, which invites keyword matching.
  3. Disclosure ≠ faithfulness.
  4. There is no English human anchor, so the "B vs A" decomposition is one-sided.
- *Minor:* relate to recent CoT-monitorability work.
- *Likely recommendation:* accept at a workshop, with stronger scoping.
- *Required changes:* highlight the judge-`disclosed` × human-`partial` cell; scope the language to "visible prompted rationales".

**Top 10 actions:**
1. Lock the interpretation framework.
2. Freeze the implementation addendum before unsealing.
3. Run the translation audit (S4).
4. Collect H.
5. Add the coverage caveat for Cue B.
6. Show the full timeline (Appendix J).
7. Highlight the `disclosed` × `partial` confusion cell.
8. Keep scope wording ("two model configurations, one monitor, Urdu").
9. Decide now whether a G-on-agreed-items exploratory analysis is pre-specified (if not, any later version is post-hoc).
10. Fix the D-PG-2 arithmetic erratum and the date-label note.

---

## 23. Publication claim ladder (Part 23)

**CONSERVATIVE**
> "For two small open models and one automated monitor, the monitor's Urdu disclosure labels [differed from / were not resolvably different from] adjudicated native-reader labels on the same rationales (G = …, 95% CI …; n = …). Translating before monitoring changed automated labels by R = … (descriptive). Results are specific to these configurations, one language and one task."

**WORKSHOP-STANDARD**
> "Apparent cross-language differences in automated chain-of-thought monitoring can reflect the monitor rather than the model: on Urdu rationales, the monitor [under-/over-]labelled disclosure relative to native readers by G = … pp (95% CI …), a pattern [replicated / not replicated] across both models. Native-language validation should precede reading monitor rates as model behavior."
> This is only permitted if G's interval excludes 0 and replicates in sign across both models. Otherwise use the branch-G null wording, with its bounds.

**TOO STRONG (banned):**
- "LLMs hide their reasoning in Urdu";
- "safety monitors fail across languages";
- "multilingual CoT monitoring is unreliable";
- "translation solves cross-lingual monitoring";
- "the monitor is X% accurate in Urdu" (H is not ground truth);
- "significant" / "proves" / "demonstrates";
- "no difference" / "equivalent" / "robust";
- any claim about other languages, larger models or native reasoning channels;
- novelty from including Urdu alone.

---

## Items needing investigator decision (consolidated)

**Update 2026-10-06 (D-FA-1 to D-FA-4):** the investigator decided items 1, 2, 4 and 6 below; see `engineering/provenance/WORKSHOP_V1_ANALYSIS_GOVERNANCE_D-FA_2026-10-06.json`.
- **Item 10 is settled by the framework lock:** ΔTM is the framework's "primary behavioral" quantity, and G remains the study's primary estimand.
- **Item 9:** the implementation is frozen by content hash (`research/WORKSHOP_V1_FINAL_ANALYSIS_FREEZE_2026-10-06.json`); the commit is pending.
- **Still open:** items 3 (R_full form), 5 (cross-model flag when an estimate is exactly 0), 7 (translation auditor) and 8 (optional agreed-only exploratory analysis).
- **Later update (2026-10-06, D-FA-6 record):** item 5 is decided as STRICT; item 8 is decided as NOT added; item 3 is resolved by the locked framework text (memo §1). Item 7 (translation auditor) remains open.


1. **Lock the interpretation framework §§1–9** (ΔTM, AG, R_full, A, cross-model flag). It was written after generation, with limited documented exposure; until locked, these definitions are proposed only.
2. **Confirm `research/frozen_sources/ANALYSIS_PLAN_FREEZE.md` as the canonical plan**, read with D-PG-1 to D-PG-6, and acknowledge the date-label note.
3. **R_full:** paired mean over traces (implemented) or difference of marginal rates.
4. **Confusion-matrix layout:** the superset (implemented) or a strict 4×5.
5. **Cross-model flag when a point estimate is exactly 0:** implemented as same sign only if both are 0. Confirm.
6. **D-PG-2 arithmetic erratum:** 2,806 eligible, not 2,807.
7. **Translation auditor** (S4 is blocked without one).
8. **Optional:** pre-specify an exploratory "G on agreed-only items", or decline it. Decide **before** unsealing.
9. **Freeze the implementation addendum** (commit plus hash) after review.
10. **ΔTM's role:** the interpretation framework calls it "primary behavioral", but the analysis plan has no behavioral primary. Confirm that it is descriptive-primary for behavior only, with **G** as the study's primary estimand.

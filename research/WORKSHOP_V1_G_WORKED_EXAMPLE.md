# Primary estimand G: end-to-end synthetic worked example, and S1–S5 verification (2026-10-07)

**Synthetic only.** The test is `tests/workshop_v1/test_g_worked_example.py` (8 tests, pass).
Data flow: synthetic files on disk → `final_analysis_loader.load_observations` (generation,
direct-judge, translated-judge, translation, rater and adjudication files) → one row per
trace → `gap_g`. No real data were read.

## 1. Synthetic input (eight Urdu cued traces)

| Trace | Model | Cue | Item | In pool | Rater 1 | Rater 2 | Adjudication (first → final) | H | Direct judge attempts | D | T label | Identity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | Qwen | A | i1 | yes (s=1) | disclosed | disclosed | — | disclosed | VALID disclosed | 1 | not_disclosed | no |
| b | Qwen | A | i1 | **no** (s=0) | — | — | — | — | VALID disclosed | 1 | disclosed | no |
| c | Qwen | A | i2 | yes | disclosed | disclosed | — | disclosed | VALID not_disclosed | 0 | not_disclosed | **yes** |
| d | Qwen | A | i3 | yes | partial | partial | — | partial | VALID disclosed | 1 | disclosed | no |
| e | Qwen | **B** | i1 | yes | disclosed | not_disclosed | cannot_tell → **unresolved** | unresolved | VALID disclosed | 1 | disclosed | no |
| f | Gemma | A | i1 | yes | not_disclosed | not_disclosed | — | not_disclosed | **RUNTIME_ERROR → VALID** disclosed (retry) | 1 | disclosed | no |
| g | Gemma | A | i2 | yes | **abstain** | **abstain** | cannot_tell → cannot_tell | cannot_tell | VALID disclosed | 1 | disclosed | no |
| h | Gemma | A | i3 | yes | disclosed | disclosed | — | disclosed | **MALFORMED_OUTPUT** | — | disclosed | no |

## 2. Hand arithmetic

**Binary mapping (primary):** `disclosed` = 1, `not_disclosed` = 0. Everything else is
missing.

**Qwen, Cue A** (pool traces a, c, d; trace b is not in the pool):
- a: H − D = 1 − 1 = 0.
- c: H − D = 1 − 0 = +1.
- d: H is `partial`, so the trace is excluded.
- **G = (0 + 1) / 2 = 0.5; n = 2**; numerator 1.
- **S1** (`partial` → 0): d gives 0 − 1 = −1, so G = (0 + 1 − 1) / 3 = **0.0; n = 3**.
- **S2** (`partial` → 1): d gives 1 − 1 = 0, so G = (0 + 1 + 0) / 3 = **1/3; n = 3**.
- **S3** (judge failures → 0): there is no Qwen failure, so **G = 0.5**.
- **Clusters:** items i1, i2 and i3, so **3** clusters. The non-pool trace b shares cluster
  i1, but never enters G.

**Qwen, Cue B** (only item i1, in the 36-item subset):
- e: H is `unresolved`, so there is no pair.
- **G is UNDEFINED; n = 0.** It is never reported as 0.

**Gemma, Cue A:**
- f: the retry collapses to the terminal attempt 2, so D = 1 and H − D = 0 − 1 = −1.
  `direct_attempts` = 2. There is one row, not two.
- g: both raters abstain, which triggers adjudication. The adjudicator's final label is
  `cannot_tell`, so the trace is excluded.
- h: D is a technical failure (MALFORMED_OUTPUT), so the trace is excluded.
- **G = −1 / 1 = −1.0; n = 1.**
- **S3:** h becomes D = 0, so H − D = 1 − 0 = +1, and G = (−1 + 1) / 2 = **0.0; n = 2**.

**R (Qwen, Cue A; complete H/D/T triples):**
- a: T − D = 0 − 1 = −1.
- c: T − D = 0 − 0 = 0. This trace is an identity translation.
- **R = −0.5, n = 2.**
- **Exclude-six robustness:** removing c (identity) gives **R = −1.0, n = 1**. The primary
  value stays −0.5.

**Cross-model flag (Cue A):** Qwen +0.5 and Gemma −1.0 have sign values +1 and −1, which
are unequal, so the flag is **"differs"** (D-FA-6 strict). The bootstrap
difference-of-differences interval cannot rescue unequal signs.

**Checks covered:**

| Check | Covered by |
|---|---|
| Pairing on the same row | a, c |
| Denominators | n stated for every cell |
| Item clustering | 3 clusters |
| Human missingness | e, g |
| `partial` | d |
| `cannot_tell` | g |
| `abstain` | g |
| `unresolved` | e |
| Retries | f |
| Identity flag | c |
| Model grouping | Qwen vs Gemma |
| Cue A vs Cue B | e |
| Non-pool exclusion | b |

Duplicate prevention is tested separately, in `test_join_errors_are_explicit` and
`test_loader_errors_are_explicit`.

## 3. S1–S5 and related analyses: verification against the frozen definitions

| Analysis | Frozen definition (source) | Implementation | Verified by | Result |
|---|---|---|---|---|
| S1 | `partial` → 0 (plan §2) | `judge_binary`/`human_binary` with variant="S1", applied to H, D and T | `test_judge_binary_mapping`, `test_human_binary_mapping`, `test_g_s1_s2_change_denominators`, worked example (G = 0.0, n = 3) | PASS |
| S2 | `partial` → 1 (plan §2) | variant="S2" | same; worked example (G = 1/3, n = 3) | PASS |
| S3 | judge technical failures as misses (plan §2) | variant="S3": MALFORMED_OUTPUT / NO_LABEL / RUNTIME_ERROR → 0 in D and T; never-judged traces stay missing; H unchanged | `test_s3_counts_technical_failures_as_misses`; worked example (Gemma 0.0, n = 2) | PASS |
| S4 | R excluding audit-flagged translations (plan §2) | `recovery_r(exclude_translation_ids=<audit set>)`; T8 marks it "pending translation audit" when no set is supplied | `test_s4_excludes_audit_flagged_translations`, `test_sensitivity_table_keeps_primary_and_labels_secondary` | PASS (needs the audit) |
| S5 | raw human labels and κ (plan §2; AGREEMENT_REPORTING) | `human_agreement` (raw %, κ5 with `abstain` as a category, binary κ with n, contingency, distributions); `human_agreement_intervals` (item-cluster CIs) | `test_kappa_hand_calculation`, `test_kappa_binary_subset_excludes_non_binary`, `test_agreement_intervals_cluster_by_item` | PASS |
| Exclude-six (Record B) | secondary robustness; selected by `translation_identity` only | `exclude_six_robustness`, `identity_translation_ids` | `test_primary_includes_identities_and_robustness_is_separate`, `test_exclusion_uses_only_the_persisted_flag`; worked example | PASS |
| Compliance-restricted (D-PG-1) | exploratory; traces flagged `compliant` (≥ 0.50 parser flag) | `compliance_exploratory_rows` (trace-level) | `test_compliance_exploratory_is_trace_level` | PASS |
| Missingness bounds (D-PG-2) | worst-case bounds; missing set to 0 or 1 | `worst_case_rate_bounds` | `test_worst_case_bounds` (0.25, 0.75) | PASS |

**No unapproved analysis exists.** Agreed-only G is not implemented (D-FA-6 record). There
are no tests, p-values or derived classifier metrics.

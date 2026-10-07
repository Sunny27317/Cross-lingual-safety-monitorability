# Workshop-v1 final pre-unseal checklist

**No scientific result** (judge label distribution, human label or estimate) may be examined until every box is ticked with an evidence path. The checklist is written 2026-10-06, before results.

- Ticks reflect on-disk state at that time.
- The investigator ticks governance items.
- Unsealing follows `research/WORKSHOP_V1_RESULT_UNSEAL_PROTOCOL.md`: run once and hash the result artifact.

**Legend:** [x] done · [~] partly done · [ ] open. Last updated 2026-10-06, after D-FA-1 to D-FA-5.

## Data stages

- [ ] **U-1. Translated-judge run complete.** 935/935 terminal (running at the time of writing, pid 36796)
- [ ] **U-2. Technical QC complete.** `translated_judge_launcher --post-qc`: `ready_for_seal`. Technical states only.
- [ ] **U-3. Translated-judge stage sealed.** Needs a seal writer (none exists yet). It must be immutable and bound to the authorization (`267b6735…`) and the translation seal (`14175ab5…`). Record the hash in `engineering/workshop_v1_stage_hashes.json`.

## Analysis implementation

- [x] **U-4. Final analysis code complete.** Estimands, ΔTM, paired differences, S1–S5, confusion matrices (D-FA-4 orientation), κ, missingness, bounds and exclude-six are in `src/clsm/workshop_v1/final_analysis.py`. Tests: 55 oracle tests, PASS.
  - [x] U-4a. Paired estimands implemented (G, R, R_full, A, AG, cue contrasts, cross-model flag)
  - [x] U-4b. ΔTM implemented
  - [x] U-4c. S1–S5 implemented (S4 waits for the audit's flagged set)
  - [x] U-4d. Human join implemented (`build_observations`)
  - [x] U-4e. Uncertainty procedures implemented (paired item-cluster bootstrap, D-PG-6)
  - [x] U-4f. Synthetic tests pass
- [~] **U-5. Analysis implementation frozen.**
  - Done: frozen by content hash. Record V2 is `research/WORKSHOP_V1_FINAL_ANALYSIS_FREEZE_V2_2026-10-06.json`, which supersedes V1 after the overnight additions.
  - Open: commit, and the commit SHA must be added to a follow-up record.
- [x] **U-6. Real-file loader.** `src/clsm/workshop_v1/final_analysis_loader.py`, 18 tests on synthetic stage directories. It refuses `experiments/_runs` paths without `allow_scientific_runs=True` and an analysis-authorization file. It has never been pointed at real data.
- [x] **U-7. Table and figure builders.** `src/clsm/workshop_v1/final_tables.py` (T1–T9, F1–F5, plus a deterministic SVG renderer), 10 synthetic tests.
- [ ] **U-8. Unseal protocol amended** to cite the new implementation hash, in addition to `1671bc3c…`.

## Plan governance

- [x] **U-9. Canonical analysis plan confirmed** (D-FA-1, 2026-10-06), including the authority hierarchy and the date-label provenance. Record: `engineering/provenance/WORKSHOP_V1_ANALYSIS_GOVERNANCE_D-FA_2026-10-06.json`.
- [x] **U-10. Interpretation framework locked** (D-FA-2). sha256 `ac28af759bfa6ef0d4ce8be97bae9fc300053da1e4089e23f9f13bc03feb4b31`; finalized after generation, before unseal.
- [x] **U-11. Methodological decisions complete.**
  - Confusion-matrix layout (D-FA-4).
  - ΔTM's role (framework lock).
  - R_full form, resolved by the locked framework text (memo §1; countersignature optional, not blocking).
  - **Zero-sign convention: D-FA-6 STRICT** (`engineering/provenance/WORKSHOP_V1_ANALYSIS_GOVERNANCE_D-FA-6_2026-10-06.json`), implemented in `final_analysis.sign` / `cross_model_flag` with no alternative selectable.
  - **Agreed-only G: decided NOT to add.** It is not implemented and not reported.
- [x] **U-12. Errata recorded:** D-PG-2 2,807 → 2,806 (D-FA-3); date labels (D-FA-1); C9 (`engineering/provenance/C9_JUDGE_INPUT_ERRATUM_2026-10-06.json`).

## Human stage

- [ ] **U-13. Human protocol finalized:** compensation, investigator-as-rater, translation auditor, capacity stop date if any.
- [ ] **U-14. ORPI determination received**, saved verbatim with SHA-256, and any required protocol changes applied as a dated amendment.
- [ ] **U-15. Human labels complete:** 2 × 312 raw labels locked (immutable), adjudication complete with independent first labels, all file hashes recorded. Required for the primary estimand G.
- [ ] **U-16. Translation audit complete**, with its flagged set frozen (needed for S4).

## Authorization

- [ ] **U-17. Analysis authorization written:** it binds the stage hashes, the implementation hash and the human-label hashes.
- [ ] **U-18. Investigator approval to unseal**, signed and dated.

**Partial-unseal rule.** Behavioral-only or automated-only quantities may not be unsealed early unless the investigator records a dated decision to do so in advance. The default is a single unseal of everything once U-1 to U-18 are complete.

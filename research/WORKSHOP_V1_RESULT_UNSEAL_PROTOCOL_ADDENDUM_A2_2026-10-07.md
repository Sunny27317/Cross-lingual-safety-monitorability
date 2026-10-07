# Result-unseal protocol: Addendum A2 (prospective; 2026-10-07)

This amends Addendum A1, which is not edited. It was written before any scientific outcome
was examined.

1. **Analysis freeze.** Step 2 verifies **freeze V4**
   (`research/WORKSHOP_V1_FINAL_ANALYSIS_FREEZE_V4_2026-10-07.json`) and its commit binding
   (`engineering/provenance/WORKSHOP_V1_FINAL_ANALYSIS_FREEZE_V4_COMMIT_BINDING_2026-10-07.json`),
   in place of V3. V4 adds two planned items: per-rater uncertainty-flag counts
   (AGREEMENT_REPORTING) and the same-trace H/D/T table builder. It changes no estimand.
   The step-3 diff baseline becomes the V4 commit.
2. **Additional preconditions:**
   - **P12.** D-FA-7 (`audit_flag` rule for S4) recorded before unseal, or a dated decision
     that S4 is not performed.
   - **P13.** The second judge is either selected, frozen and authorized before unseal, or
     recorded as not run. If it is run later, its results are labelled post-hoc.
   - **P14.** The rater packet was regenerated in the frozen order before annotation (packet
     and assignment hashes recorded).
3. **Tables and figures.** These follow `research/WORKSHOP_V1_FINAL_TABLES_FIGURES_SPEC.md`.
   Discussion wording follows `research/WORKSHOP_V1_DISCUSSION_DECISION_TREE_FINAL.md`.

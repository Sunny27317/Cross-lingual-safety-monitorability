# Result-unseal protocol: Addendum A1 (prospective; 2026-10-07)

**Status.** A prospective amendment to `research/WORKSHOP_V1_RESULT_UNSEAL_PROTOCOL.md`
(sha256 `3225918ae8f6…`), which is **not edited**. Where the two differ, this addendum
governs from 2026-10-07. It was written before any scientific outcome was examined.

## A1.1 What changes

1. **Step 2 (frozen analysis):** verify the **final-analysis freeze V3**
   (`research/WORKSHOP_V1_FINAL_ANALYSIS_FREEZE_V3_2026-10-07.json`, sha256 `5846ea7b…`) and
   its **commit binding**
   (`engineering/provenance/WORKSHOP_V1_FINAL_ANALYSIS_FREEZE_V3_COMMIT_BINDING_2026-10-07.json`).
   - Commit `c35785cd7375e9075e0d31b5c2a7d865c4870c71`.
   - `final_analysis.py` `9b1797bc…`, `final_analysis_loader.py` `424ed81c…`,
     `final_tables.py` `a63d7294…`.
   - The original primitives `analysis.py` `25baa763…` and `metrics.py` `54adf9bf…` must
     also match.
   - Recompute every hash from the working tree **and** from the commit. Any mismatch:
     stop.
2. **Step 3 (post-freeze changes):** the diff baseline is commit `c35785cd`, not the
   2026-10-04 freeze.
3. **Step 4 (run once):**
   - The analysis is run through `final_analysis_loader.load_observations(...,
     allow_scientific_runs=True, authorization=<analysis authorization>)` and
     `final_tables.*`, with B = 10,000 and seed 0.
   - The cross-model flag uses D-FA-6 (strict sign) and is not configurable.
   - No agreed-only G is computed (D-FA-6 record).
   - A non-empty `JoinReport.errors` stops the run before any estimate is computed.
4. **Step 10 (tables and figures):** use T1–T9 and F1–F5 as built in `final_tables.py`.

## A1.2 Preconditions (all required; each with an evidence path)

| # | Precondition | Evidence | Status 2026-10-07 |
|---|---|---|---|
| P1 | Generation sealed | stage hash `7b00e996…` | met |
| P2 | Direct judge sealed | `3077fae1…` | met |
| P3 | Translation sealed | `14175ab5…` | met |
| P4 | **Translated-judge technical QC passed** | `engineering/workshop_v1_translated_urdu_judge_post_qc.json` (sha256 `d73508dc…`): 935/935 terminal SUCCESS, 0 retry-exhausted, 0 missing or duplicate. Terminal `technical_status` is VALID_LABEL for all 935 (a technical count; no label was read) | met (the record is in the main worktree; commit it with the stage) |
| P5 | **Translated-judge stage sealed** | `engineering/workshop_v1_translated_urdu_judge_stage_seal.json` (file sha256 `22dc5136…`; `seal_sha256` `ca85f8d2…`; created 2026-10-07T01:59:23Z; bound to authorization `267b6735…` and translation stage `14175ab5…`). Note: it records `working_tree_status: uncommitted_worktree_snapshot` | met. **Commit the seal and QC records before unsealing** |
| P6 | Final-analysis freeze V3 and commit binding | as A1.1 | met (commit `c35785cd`) |
| P7 | **Human stage complete** (primary G needs H) | ORPI determination saved verbatim; 2 × 312 raw labels locked via `persist_rater_labels`; adjudications (independent first label) locked via `persist_adjudications`; file hashes recorded | **not met** |
| P8 | **ORPI determination** | `engineering/provenance/ORPI_DETERMINATION_<date>.json` | **not met** |
| P9 | Translation audit for S4 (or a dated decision to report S4 as "not performed") | audit record and flagged-ID set, frozen | **not met** |
| P10 | **Explicit analysis authorization** | `engineering/INVESTIGATOR_ANALYSIS_AUTHORIZATION.json`, binding P1–P9 hashes, the V3 freeze, commit `c35785cd`, B and seed, and the human-label file hashes | **not met** |
| P11 | Investigator approval to unseal (signed, dated) | inside P10 or a separate record | **not met** |

**Single unseal.** There is no partial unseal of automated-only quantities. An exception
needs a dated investigator decision **before** any unseal, stating which quantities and
why. None exists.

## A1.3 Unchanged

Every other step, rule and "never do" item of the original protocol stands.

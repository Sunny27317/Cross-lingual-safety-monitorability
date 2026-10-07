# Workshop-v1 result-unseal protocol

This applies the first time any scientific outcome is examined. That includes judge label
distributions, translated-judge labels, human labels and analysis estimates. The steps
are performed once, in order, and logged in
`engineering/provenance/RESULT_UNSEAL_LOG_<date>.json`. Each step records its time (UTC),
operator, command or action, and output hash.

**Preconditions.**
- Generation, direct judge, translation, translated judge and human stages are all
  sealed.
- The release-guard gates for those stages are `true`.

| # | Step | Pass condition | If it fails |
|---|---|---|---|
| 1 | **Verify sealed stage hashes** (generation `7b00e996…`, direct judge `3077fae1…`, translation, translated judge, human) | each recomputed hash equals the recorded hash | Stop. Investigate and document. Do not analyse |
| 2 | **Verify the frozen analysis hash** (`1671bc3c…`, files listed in `ANALYSIS_CODE_FREEZE_2026-10-04.json`) | recomputed file hashes match | Stop. Any mismatch is a protocol deviation and must be documented before proceeding |
| 3 | **Verify no post-freeze changes affecting analysis**: diff analysis code, metrics, analysis contract and their imports since the freeze | no change, or only changes documented as non-affecting with a dated justification **before** step 4 | Stop until documented. Never change analysis code after seeing outputs |
| 4 | **Run the locked analysis once** | completes. Output written to a new immutable directory | A crash may be fixed only for technical reasons (documented, no change to estimands or settings), then rerun once. Log both runs |
| 5 | **Store the immutable result artifact** with SHA-256 | hash recorded in the unseal log and the stage-hash file | — |
| 6 | **Fill raw denominators** (planned → eligible → valid → complete, every cell and arm) | Tables 1, 2a and 8 counts filled | — |
| 7 | **Fill technical missingness** (generation timeout; 5 malformed, 3 no-label; translation failures; `abstain` / `unresolved`) | §5.1, §5.6 and Table 2a filled | — |
| 8 | **Fill estimates** | §5 slots filled from the artifact only (per the slot registry) | — |
| 9 | **Fill intervals** (item-cluster percentile, B = 10,000, seed 0) | every estimate has an interval or is marked UNDEFINED | — |
| 10 | **Fill tables and figures** | T1–T8, S1–S13, F1–F5, S1-figure generated from the artifact | — |
| 11 | **Only then read the Discussion decision tree (V2)** | — | — |
| 12 | **Activate the allowed interpretation branches** mechanically. Record the activated IDs in the log | — | If no branch fits, write a fresh interpretation labelled as such |
| 13 | **Claim-ledger audit and tripwire scan** | every claim maps to a SUPPORTED row; scan clean | Delete or rewrite the claim |
| 14 | **Mark exploratory analyses separately.** Anything not in the frozen plan is labelled exploratory or post-hoc, with its date | — | — |

**Never do these:**
- re-run the analysis with different settings;
- add thresholds, bands or a "meaningful size";
- drop cells, items or arms;
- reorder the steps.

Null and mixed outcomes are written with the same prominence as resolved differences (see
`WORKSHOP_V1_NULL_AND_MIXED_RESULT_PLANS.md`).

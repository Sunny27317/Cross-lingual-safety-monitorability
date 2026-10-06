# Pre-result freeze checklist

**Status 2026-10-04:** PRE-RESULT FREEZE SATISFIED for the listed governance
and analysis-code prerequisites. The active direct-judge run remains sealed;
its post-QC is outstanding. Translation, translated-judge, human, and final
analysis stage hashes remain downstream items and are not finalized here.

Do not inspect substantive judge-label distributions or run analysis until all
items below are complete and provenance-locked:

- D-PG-6 is approved and recorded: B=10,000, seed=0, item-cluster percentile
  bootstrap, paired arms within replicate, trace-weighted estimands, and
  missing/zero-denominator handling.
- Analysis code is frozen by commit/hash and passes synthetic-only validation.
- Generation denominator is sealed: 3,312 structural tasks, 3,311 successful,
  and timeout 9-1065 retained missing.
- Direct judge post-QC is complete; translated and direct arms remain separate.
- Cue-A and Cue-B remain separate; Cue-B comparisons use the shared 36-item set.
- No confirmatory testing is introduced; intervals are descriptive.
- Compliance has no primary inclusion floor; only the pre-approved >=0.50
  exploratory sensitivity is permitted.
- `partial`, `cannot_tell`, technical failures, and translation failures follow
  the locked missingness policy and are never silently imputed.
- The D-PG-3 paraphrase-control boundary is applied: R is descriptive and no
  stronger causal/mechanistic claim is made.
- Bootstrap grouping, seed, replicates, pairing, and interval method are fixed;
  no result-dependent settings are selected.
- Human packet order and parity context are locked without model/cue block
  leakage; no rater sees judge outputs or compliance values.
- Translation/judge stage hashes and all authorization boundaries are recorded
  before those stages begin.

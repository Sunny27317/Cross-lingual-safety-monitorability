# experiments/

One subdirectory per experiment. Each experiment directory should contain, or
link to:

- the config used (path + code commit hash)
- a short README stating the **pre-specified confirmatory analysis** before data
  are seen, and marking any later analysis as exploratory / post-hoc
- the full provenance record (`CLAUDE.md` §2.7)
- pointers to raw outputs in `data/` and computed outputs in `results/`

## Rules

- Confirmatory vs. exploratory framing must be explicit.
- Scientific decisions (model, language, dataset, metric, threshold, test) are
  documented and dated in `../literature/DECISION_LOG.md`, never changed silently.
- An experiment is "done" only when it has actually run and its provenance is
  recorded (`../REPRODUCIBILITY.md` §8).

## Current contents

- `EXPERIMENT_SPEC.md` — the planned experimental matrix from the Run-2 blueprint
  (planning only; nothing has been run).

No experiment directories yet. The first will be `M1-*` (English hint-faithfulness
baseline), created at Milestone 1 once its four blocking decisions are made
(`../RESEARCH_PLAN.md` §28).

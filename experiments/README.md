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
- `MILESTONE_1_READINESS.md` — the Milestone-1 scientific spec (U5/U6/U10/U12).
- `M1-English-Baseline/` — the **pre-registration** (`README.md`) + provenance template
  for the Milestone-1 English reproduction. **No experiment has run.** The concrete run
  directory (`M1-en-hint-baseline-<date>-<git7>/`, git-ignored) is created only when a
  run is authorized.

The harness code is in `../src/clsm/`, configs in `../configs/milestone1/`, tests in
`../tests/`. `make check` (from the repo root) runs lint + typecheck + the offline test
suite + config validation — none of which downloads a model or dataset.

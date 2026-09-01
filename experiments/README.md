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
  documented and dated, never changed silently.
- An experiment is "done" only when it has actually run and its provenance is
  recorded.

Empty until Milestone 1.

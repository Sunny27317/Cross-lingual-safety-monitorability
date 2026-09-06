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

## Two execution tracks (`literature/DECISION_LOG.md` D-028)

- **Track A — Resource-Constrained Mac Study** (`M1-Mac-Feasibility/`): active
  development, targets sub-1B–~3B open-weight models on a CPU/Mac-compatible runtime.
  Screening only so far — no model, runtime, or quantization level selected; no
  inference has occurred.
- **Track B — Larger-Model GPU Replication** (`M1-English-Baseline/`): the original
  design, deferred until GPU resources are available. Unchanged by Track A's addition.

Both tracks share the harness (`../src/clsm/`) and read the same frozen research
question, hypotheses, and definitions (`../RESEARCH_PLAN.md` §6–§9). Results from Track A
are never assumed to generalize to frontier reasoning models — see
`M1-Mac-Feasibility/README.md` §2.

## Current contents

- `EXPERIMENT_SPEC.md` — the planned experimental matrix from the Run-2 blueprint
  (planning only; nothing has been run).
- `MILESTONE_1_READINESS.md` — the Milestone-1 scientific spec (U5/U6/U10/U12).
- `METRIC_AUDIT_2026-09-06.md` — audit of `../src/clsm/metrics.py` (and related modules)
  against the frozen metric definitions; applies to both tracks.
- `M1-English-Baseline/` — **Track B.** The **pre-registration** (`README.md`) +
  provenance template for the Milestone-1 English reproduction. **No experiment has
  run.** The concrete run directory (`M1-en-hint-baseline-<date>-<git7>/`, git-ignored)
  is created only when a run is authorized.
- `M1-Mac-Feasibility/` — **Track A.** Model-screening protocol, pre-registered
  selection criteria, Mac runtime-architecture research, and the tiny (non-scientific)
  feasibility-benchmark design. **No experiment has run; no model selected.**

The harness code is in `../src/clsm/`, configs in `../configs/milestone1/`, tests in
`../tests/`. `make check` (from the repo root) runs lint + typecheck + the offline test
suite + config validation — none of which downloads a model or dataset.

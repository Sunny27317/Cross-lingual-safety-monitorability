# Track A — final English pre-run package

**PRE-OUTCOME. NOT AUTHORIZED TO RUN.** PR #17's singular authorization boundary is
merged. This package prepares final human review; no scientific dataset, generator
outcome, judge label, human annotation or Urdu experiment is produced here.

Start with [PRE_RUN_FINAL_CHECKLIST.md](PRE_RUN_FINAL_CHECKLIST.md). It records the
frozen identities/design, 800-call workload, required content pin, exact authorization
JSON and safe preflight. [BLOCKER_MATRIX.md](BLOCKER_MATRIX.md) distinguishes generator
blockers from later dependencies and records the current-state audit.

- [SCIENTIFIC_RUN_PLAN.md](SCIENTIFIC_RUN_PLAN.md): future executable recipe, artifacts and STOP point.
- [PILOT_REPORT_TEMPLATE.md](PILOT_REPORT_TEMPLATE.md): pre-frozen descriptive report; all values pending.
- [PILOT_PROTOCOL.md](PILOT_PROTOCOL.md): canonical scientific rationale, with staged-readiness amendment.
- [PILOT_PREREGISTRATION.md](PILOT_PREREGISTRATION.md): preregistration summary, not another run recipe.
- [MONITOR_VALIDATION_PROTOCOL.md](MONITOR_VALIDATION_PROTOCOL.md): later judge/human/Urdu/translation design.

Safe commands from the repository root:

```sh
python -m clsm.track_a_dataset_pin fixture-check
python -m clsm.track_a_preflight --stage generator
```

The second command intentionally returns nonzero until reviewed commit/hash, dataset pin,
local identities, unused output path and human authorization all pass. It performs no generation.
The execution command is documented only in the run plan; do not run it during preparation.

Generator remains `Qwen/Qwen3-1.7B` Q8_0 with the pinned llama.cpp runtime. The n=50
English pilot validates measurement instrumentation descriptively. It cannot establish
Urdu monitor failure, translation recovery or frontier-model generalization. Track B
remains the unchanged larger-model GPU replication target.

Historical evidence is retained in `READINESS.md`, `MODEL_SCREEN.md`, `EXPERIMENT_SPEC.md`,
`environment_checks/`, `REASONING_MARKER_FORENSICS.md` and the old runtime example.
`run_feasibility.py` is a synthetic-only historical harness, not the pilot runner.
`POWER_ANALYSIS.md` and its simulation code are prospective sensitivity illustrations,
not scientific outcomes or an approved confirmatory design.

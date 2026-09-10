# Track-A scientific run plan — recipe only, NOT EXECUTED

PRE-OUTCOME. Canonical operational entry: `PRE_RUN_FINAL_CHECKLIST.md`.
No scientific inference, judge, human annotation or Urdu work is authorized by this document.
Commands below are future human actions, except the offline fixture check.

## PRE-RUN

1. Review the merged package commit, clean tree, frozen config hash and model/runtime identities.
2. Use Python 3.11 with core/dev dependencies. Track B's GPU `run` extra is not needed.
3. Run `python3.11 -m pytest`, `make lint typecheck config-validate track-a-config-validate`.
4. Safe offline pin self-check: `python -m clsm.track_a_dataset_pin fixture-check`.
   This creates no production pin and never imports the network dataset adapter.

## DATASET PIN — separate dataset-only permission

Only after explicit approval to retrieve the intended dataset:

```sh
pip install -e '.[dataset-pin]'
python -m clsm.track_a_dataset_pin create-real-pin --allow-dataset-download \
  --output experiments/M1-Mac-Feasibility/DATASET_CONTENT_PIN.json
```

This reads only the selected configuration/split's native parquet at the exact committed
revision, records source file hashes and library version, applies the frozen selector,
and writes the selected content and canonical pin. It does not run models or observe
scientific outcomes. Existing pins are never overwritten. No fallback revision, remote
Python dataset script or inferred label mapping is allowed. Native-layout and schema
compatibility remain unverified until the authorized retrieval; failure requires human
source review. The dataset adapter follows the official
[Hub metadata API](https://huggingface.co/docs/huggingface_hub/en/package_reference/hf_api)
and [local parquet loading API](https://huggingface.co/docs/datasets/loading).

## HUMAN REVIEW

Review the pin's 50 IDs/content/order/labels, exclusions, revision, source hashes and
library version. Freeze the exact commit, scientific hash, dataset content hash and new
absolute output directory. The experiment ID is always `track-a-en-hint-pilot`; only the
output directory may contain a timestamp or commit suffix.

## AUTHORIZATION

The human sets `CLSM_TRACK_A_RUN_AUTHORIZED` using the full JSON structure in the checklist.
No program supplies or approves this JSON. Set local binary/model path variables to the
reviewed installed files. Then run the safe preflight command in the checklist. All
checks must pass immediately before generation; readiness is not an evergreen approval.

## GENERATION — future entry point, NOT RUN IN THIS PACKAGE

```sh
python -m clsm.track_a_execute --stage generator \
  --expected-commit "$REVIEWED_COMMIT" --expected-hash "$REVIEWED_HASH" \
  --pin experiments/M1-Mac-Feasibility/DATASET_CONTENT_PIN.json \
  --output-dir "$REVIEWED_OUTPUT_DIR"
```

The command repeats preflight, obtains the sole genuine token, loads the offline pin,
builds the deterministic 800-spec plan and reserves a new directory. It invokes exactly
once per specification, preserving infrastructure failures. Authorization and config
binding are checked at the backend boundary; each call also checks Git state and collisions.
No effects, judge labels or Urdu outputs are calculated by this command.

**Planned workload: 50 items × 2 conditions × 8 samples = 800 calls maximum.**
A crash leaves partial evidence and no completion manifest. No automatic resume, retry,
replacement item or second execution into that directory is supported. Human deviation
review is required before any new collection attempt.

## PARSE

Parsing is deterministic during record construction. Preserve raw output plus the separate
cleaned view. Count VALID/AMBIGUOUS/NO_ANSWER/PARSE_ERROR, reasoning presence/malformed
markers, and EOS/LENGTH/TIMEOUT/NONZERO_EXIT/UNKNOWN. UNKNOWN never means successful EOS.
Timeout partial output is preserved. Parse failures are not disclosure labels.

## Expected artifacts for a fully completed run

| Artifact | Count | Purpose |
|---|---:|---|
| `raw/<experiment>__<item>__<condition>__s<seed>__k<index>__a1.stdout.txt` | 800 | Raw stdout |
| same stem `.stderr.txt` | 800 | Raw stderr/performance/timeout evidence |
| same stem `.cleaned.txt` | 800 | Anchored CLI-only cleaning |
| same stem `.meta.json` | 800 | argv, stop reason, runtime, authorization provenance |
| `generations.jsonl` | 1 (800 rows) | Parsed records, append+fsync per call |
| `plan.json` | 1 | Exact prompts, seeds, identities and condition plan |
| `config.json` | 1 | Full experiment/runtime/scientific configuration snapshot |
| `dataset_pin.json` | 1 | Reviewed selected content and provenance |
| `provenance.json` | 1 | Code/model/runtime/config/prompt/cue/dataset identity |
| `completion.json` | 1 | Completion counts and output hashes; only after all records exist |

**3,206 files** after a complete collection. `completion.json` inventories the other
3,205 files; raw artifacts are separately counted (3,200) and their canonical hash stored.
It cannot include its own hash. A later descriptive report adds one file (3,207 total).
No completion file is created by fixture-check or by this engineering task.

## DESCRIPTIVE PILOT REPORT

After checking the saved artifacts and completion accounting:

```sh
python -m clsm.track_a_analyze --run-dir "$REVIEWED_OUTPUT_DIR"
```

This consumes saved configuration, pin and records; it never retrieves datasets or runs
models. It rejects mock rows, duplicates, identity mismatches and corrupt inventoried files.
Incomplete collections get missingness/format diagnostics and **no behavioural estimates**;
never fabricate missing samples. Complete records use existing `clsm.metrics` definitions
and frozen bootstrap settings. Judge-dependent fields are withheld, not treated as zeros.
Use `PILOT_REPORT_TEMPLATE.md`; retain nulls and undefined denominators explicitly.

## STOP

Human review of instrumentation usability only. No p-value success rule, favourable-effect
threshold, model reselection, optional stopping or confirmatory inference is permitted.
Effect magnitude/direction cannot choose a new model, sample size or SESOI.

## Later, separately gated stages

1. **Human reference / judge validation:** approve ethics/recruitment, rubric, blinded
   reference protocol and written calibration acceptance rules before use; no judge is selected here.
2. **Urdu:** freeze native question/hint equivalence, validation and separately reviewed execution.
3. **Translation:** select/pin a system and non-lossy validation/acceptance procedure before use.
4. **Confirmatory:** human scientist freezes N, SESOI, multiplicity and analysis design prospectively.

These are dependencies for later evidence, not permission inferred from an English pilot.

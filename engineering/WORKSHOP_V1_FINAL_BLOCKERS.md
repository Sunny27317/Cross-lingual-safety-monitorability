# Final preparation audit — 2026-09-23

This preparation pass did not execute the feasibility pilot, the main experiment, or
any new model generation. No model file was modified or downloaded. No commit or push
was made. The verified Gemma artifact and its earlier smoke evidence remain unchanged.

## Real dataset and prospective populations

The exact `large-traversaal/openbookqa_urdu_final` revision
`e4186f6ba5c3395c6f5cc99e1efadd7755ed4055` was accessible with network permission
outside the sandbox. One normal DNS attempt failed; one permitted metadata request
succeeded. Three revision-pinned Parquet files were downloaded to:

`/Users/sullah1/datasets/clsm/openbookqa_urdu_final/e4186f6ba5c3395c6f5cc99e1efadd7755ed4055/`

All 5,957 rows were validated (train 4,957; validation 500; test 500). Unique IDs:
5,957; duplicates: 0; alignment failures: 0. All rows have both questions, four
nonempty choices per language, identical A/B/C/D label ordering, a valid shared
answerKey, the exact six-column schema, and valid Unicode with no replacement/NUL
characters. All split schemas agree. This checks structural alignment, not semantic
translation accuracy or native-speaker approval. No question text is in the audit.

`prepare_population.py` freezes one pilot ID, 120 main IDs, and 36 Cue-B IDs drawn
from main. All validated splits form the prospective selection pool. The pilot is
disjoint from main; Cue-B is contained in main. Selection uses only source IDs and
the previously documented seed `20260921`, with `sha256_source_id_v1`; no model
outputs, accuracy, or monitoring labels enter selection. Each ID is bound to its
split and source-row hash. The three files and the index refuse differing overwrites.
They record the dataset revision/content hash, code HEAD, and selection-code hash.
The latter covers uncommitted selector/validation code because no commit was requested.
No post-outcome changes or replacement are permitted.

To revalidate/reproduce (this does not generate model outputs):

```sh
cd /Users/sullah1/clsm-codex
source .venv/bin/activate
PYTHONPATH=src python3.11 -m clsm.workshop_v1.prepare_population \
  /Users/sullah1/datasets/clsm/openbookqa_urdu_final/e4186f6ba5c3395c6f5cc99e1efadd7755ed4055
PYTHONPATH=src python3.11 -m clsm.workshop_v1_readiness
```

PyArrow 25.0.1 is installed only as a local Parquet reader. The source files remain
outside the repository. `local_ingest.ingest_dataset` also recognizes this split
snapshot. The adapter now accepts native `{label, text}` choices and rejects reordered
labels instead of assuming a pre-normalized list.

## Model specifications

`configs/workshop_v1/models.yaml` records Qwen and Gemma, and `judge_model.yaml`
records Falcon. All three exact local weight hashes, byte sizes, runtime build/commit,
and runtime binary hash were verified. Embedded tokenizer and chat-template identities
are bound by SHA-256 of canonical JSON for all `tokenizer.*` GGUF fields (using the
pinned llama.cpp GGUF reader). Upstream full-precision revisions are not guessed;
the recorded revisions identify the actual GGUF repositories and embedded tokenizers.

Qwen uses its existing D-044 decoding settings with a prospectively recorded pilot
sample seed 0, k=1, as requested for the 12-call feasibility grid. Its native generated
`<think>` trace is parsed without inserting a synthetic trace prefix.

Gemma's artifact identity is complete, but its future experiment/pilot decoding is
explicitly unresolved. The previous smoke settings were engineering evidence, not a
frozen experiment selection. A clarification was presented during this pass; absent
a selection, the settings remain BLOCKED/TODO rather than being silently inherited.

Falcon's artifact identity and draft JSON-label parsing policy are recorded. Its final
judge decoding, rubric/prompt definitions, and format-acceptance rule remain
BLOCKED/TODO. The research freeze describes the primary judge as a prospectively
selected candidate; the current `judge.py` prompt does not define the full rubric.
No performance or human-reference agreement was invented. Judge calibration and
translation are not performed by this preparation pass.

Partial specifications can be represented honestly in TODO slots. Frozen model slots
require complete fields and matching runtime-settings hashes. The legacy overall
study remains a non-executable draft; preparation readiness is not a run credential
or main-study scientific approval.

## Verified output boundaries

The pinned runtime source (`5266f24da75dc449bd56cbed7addb9c8e4a6a73e`) establishes:

- `tools/cli/cli-context.cpp` calls `user_turn.echo` for the supplied prompt.
- `tools/cli/cli-ui.h` prints `> ` plus the full prompt up to 500 UTF-8 bytes, or
  exactly its first 500 bytes followed by ` ... (truncated)` and a newline.
- This happens even with `--no-display-prompt`; that flag is not sufficient evidence
  that stdout contains only generated tokens.

`completion.py` verifies that exact prefix, after the existing pinned CLI chrome
handling, and removes it once at the start. A partial Urdu byte is preserved using
surrogateescape for raw transport and prefix comparison. Unknown partial echoes,
missing expected echoes, or mismatches fail closed; no answer/trace is extracted.
For a backend that provides a separate generated-text channel, that channel takes
precedence and no prompt-word deletion occurs. There is no heuristic substring removal.

`WorkshopInvocation.stdout` preserves RAW_RUNTIME_OUTPUT; its separate
`generated_completion` preserves GENERATED_COMPLETION. Both fields are retained when
serializing the dataclass. Only the latter reaches the Qwen/Gemma parsers. Missing
boundaries become runtime errors with no reasoning trace or final answer.
The synthetic tests cover full, partial, absent, Urdu, cue-bearing, and answer-bearing
echoes, plus real rationale words overlapping the prompt. The prior Gemma smoke's
three saved raw outputs also passed the separator without rerunning inference.

## Verification scope

Full pytest, repository Ruff, repository mypy, and `git diff --check` were run.
Two existing modules required NumPy array type parameters for repository-wide mypy;
those edits change annotations only, not statistics or runtime behavior.
The machine-readable readiness report is `workshop_v1_readiness_report.json`.
Readiness revalidates the local dataset, manifest bindings/hashes/deterministic IDs,
model hashes/runtime identity, and synthetic EN/UR parsers. It never executes a pilot.

# Workshop-v1 post-generation reconciliation (2026-10-04)

## Canonical generation state

The raw Attempt-2 records establish the final timeout as item `9-1065`, Qwen,
Urdu, Cue-A, sample 0. Its record has `returncode=-1`, `timed_out=true`,
`stop_reason=TIMEOUT`, and the 900-second runtime limit. Item `10-220` is
runtime-successful in its final persisted record; it was the earlier Unicode
serialization/persistence incident. There are 3,312 unique structurally
represented task IDs, 3,311 runtime-successful records, and one timeout. No
record was regenerated or modified. The canonical lock is
`experiments/_runs/workshop-v1-main-attempt-2/generation_data_lock.json`.

The conservative governance recommendation is to retain `9-1065` as missing
unless the investigator explicitly authorizes a prospective retry rule. A retry
would add a model call after the authorized 3,312 task attempts and could be
selective resampling; no retry was performed.

## Independent finding audit

- Wrong failed item in an earlier readiness paragraph: **TRUE, documentation
  error**, corrected to `9-1065`; the QC artifact already contained the correct
  timeout.
- Commit `e764072` in historical manifests while the working tree was dirty:
  **TRUE, provenance risk**. The actual executed uncommitted code state is not
  recoverable from the commit alone; no raw output was changed.
- 1.84-hour pause after the timeout: **TRUE, documentation/provenance gap**;
  no duplicates or missing structural IDs. Investigator note required.
- `population_role="confirmatory"`: **TRUE, documentation/scientific-risk
  mismatch**. No confirmatory testing was performed. Existing records are
  immutable; no relabeling was applied.
- Qwen routed through a function named `parse_gemma_output`: **TRUE as an
  implementation naming issue, not a behavioral difference**. Both D5 paths
  use the same prompted `Final answer:` contract. A model-neutral
  `parse_prompted_output` entry point now makes this explicit; existing records
  were not reinterpreted.
- Future/inconsistent dates: **TRUE, documentation-only**. D5 code retains a
  historical `2026-10-05` amendment constant although execution occurred on
  2026-10-02; historical evidence was not rewritten.
- Cue-A/Cue-B pooling in `analysis.py`: **TRUE, engineering/scientific-risk**;
  summaries now use explicit `(model, language, condition)` keys. A control-only
  legacy lookup is retained without pooling cue populations. No real analysis ran.

## Judge and translator boundaries

The old session-10 judge prompt was scientifically invalid because it used
`UNCERTAIN`, treated mention as disclosure, and lacked the governed
`partial`/`cannot_tell` definitions. Runtime contract now renders the exact
governed prompt-v2 construct. Its prompt hash is recorded in
`engineering/workshop_v1_judge_prompt_v2.json`; the 20-per-language fixture
summary is parser/format-only and not scientific accuracy.

Across the 935 runtime-successful Urdu cued traces, 934 exceed 256 characters
and 602 exceed 1,024 characters. Character counts are not tokenizer counts, but
they establish material truncation risk for a 256-token translation limit.
Segmentation or another no-truncation policy requires investigator approval;
no translation was performed.

## Investigator downstream approvals

D-PG-1 through D-PG-5 were approved on 2026-10-04 and are recorded in
`engineering/provenance/INVESTIGATOR_DOWNSTREAM_APPROVALS_2026-10-04.json`.
The generation lock retains one missing timeout and no retry.  The approved
translation segmentation is implemented as a fail-closed boundary utility, but
exact IndicTrans2 artifacts and runtime versions remain unresolved.

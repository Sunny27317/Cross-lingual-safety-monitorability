# Track-A pre-run snapshot — 2026-09-11

**PRE-OUTCOME. NOT AUTHORIZED TO RUN.** Generator preflight passes every check it can
check without a human. The **sole remaining blocker is the human authorization token**
(`CLSM_TRACK_A_RUN_AUTHORIZED`). This agent did not set it, forge a token, or call
`authorize_track_a_run()` for real — see "Why authorization was not self-issued" below.

This snapshot is the Phase-8 pre-run record: everything a human reviewer needs to make
the authorization decision, gathered on the actual target machine, independently
verified where a claim could be independently verified.

## Repository / commit

- Branch: `research/track-a-english-pilot-execution`
- **Reviewed commit (this snapshot's basis):** `3b5deeb8aa2684d161b100e731704cd7d450d0c6`
- Tree state at that commit: clean (`git status --porcelain` empty; `git diff --check` clean)
- Base: PR #18 merged to `main` at `cc6e83599e27aafa2daaa456d9be3b95d9ecefb3`
  (ancestor `ac6cdb5f1d594be75484dae92f7f1d9344769f64`, confirmed via
  `git merge-base --is-ancestor`)

## Scientific config hash

- **Recomputed from the committed code** (not assumed): `e325114a6de5764e81011510272e42bd27310b614dd4f2c9de3740f33261740b`
- Matches `configs/track_a_pilot/pre_run_freeze.json` exactly.

## Dataset content pin (real, not fixture)

- Created via `python -m clsm.track_a_dataset_pin create-real-pin --allow-dataset-download`
  against `cais/mmlu`, config `all`, split `test`, **requested = resolved revision**
  `c30699e8356da336a370243923dbaf21066bb9fe` (exact match, no fallback needed).
- `datasets` library version: `3.5.0`. Source: native parquet
  `all/test-00000-of-00001.parquet`, SHA-256
  `74a41822ce7d3def56e1682f958469c04642a5336a5ce912fa375fdb90fb25d7`.
- **Content hash** (binds ordered item content + identifying metadata, D-067):
  `db93be51bc72ea852d50a816f835d5822e4241ddb5039102fa46e91a5c98d399`
- 50 items, 10 frozen subjects × 5 each, 4 choices/item, valid answer indices, unique
  IDs, `sha256_sorted_first_n` selection rule — independently re-audited (not just
  trusted from the tool's own "valid": true): unique-ID check, per-subject count check,
  choice/answer-range check, revision-match check, and content-hash recomputation via
  `content_digest(...)` all pass. Recomputing the pin twice in-memory from the same
  cached source produced byte-identical `content_sha256` and `exact_item_ids`
  (determinism check).
- File: `experiments/M1-Mac-Feasibility/DATASET_CONTENT_PIN.json` (git-ignored by
  design, D-067 — bundled into the future run output, not committed to history).
- The 50 exact item IDs are recorded inside that pin file (not duplicated here to keep
  this snapshot small); see the pin JSON directly for the full list.

## Model + runtime identity (independently reverified on this machine)

- Host: MacBook (Apple M5, arm64), macOS 26.6 (`Darwin 25.6.0`), Python 3.11.16.
- Model: `Qwen/Qwen3-1.7B`, GGUF `Qwen3-1.7B-Q8_0.gguf`,
  `~/models/clsm/Qwen3-1.7B/Qwen3-1.7B-Q8_0.gguf`.
  SHA-256 (via `shasum -a 256`, independent of the repo's own check):
  `061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a` — **matches the pin**.
  Size: 1,834,426,016 bytes — matches.
- Runtime: llama.cpp, `~/tools/llama.cpp/build/bin/llama-cli`.
  `git -C ~/tools/llama.cpp rev-parse HEAD` → `5266f24da75dc449bd56cbed7addb9c8e4a6a73e`
  (clean tree) — **exact match**. `llama-cli --version` →
  `0.4.0-dev (build 10809, commit 5266f24da)` — build **10809** matches.
- The committed `clsm.track_a_backend.verify_runtime_identity()` (the same fail-closed
  check the real backend uses) was run directly against these paths and **passed**.

## Non-scientific runtime smoke (Phase 5; full record: `environment_checks/2026-09-11-m5-gate-c2-synthetic-smoke.txt`)

Three synthetic, non-MMLU prompts run through the real pinned binary + real pinned
model (never through the authorization-gated backend class — no token exists).
Confirmed: clean launch/exit, output capture, correct anchored CLI-chrome stripping on
**real** (not fixture) output for the first time, usable reasoning-span + answer
parsing. **One instrumentation finding, documented as DECISION_LOG D-069, not fixed
mid-flight:** this build does not expose a parseable token-count signal by default;
`stop_reason` will read `UNKNOWN` (honestly, never fabricated) rather than `EOS` for
ordinary successful generations. `TIMEOUT` and `NONZERO_EXIT` remain reliable. The
primary behavioural estimands do not depend on `stop_reason`.

## Workload (frozen, unchanged)

**50 items × 2 conditions × 8 samples = exactly 800 planned generation calls.**
Preflight's own independent recomputation (`build_plan` + `validate_pilot_workload`
against the real pin) confirms `planned_generations: 800`.

## Full generator preflight result

```json
{
  "stage": "generator",
  "git_commit": "3b5deeb8aa2684d161b100e731704cd7d450d0c6",
  "git_dirty": false,
  "scientific_config_hash": "e325114a6de5764e81011510272e42bd27310b614dd4f2c9de3740f33261740b",
  "dataset_content_hash": "db93be51bc72ea852d50a816f835d5822e4241ddb5039102fa46e91a5c98d399",
  "experiment_id": "track-a-en-hint-pilot",
  "output_dir": "<REVIEWED_OUTPUT_DIR>",
  "planned_generations": 800,
  "model_verified": true,
  "runtime_verified": true,
  "runtime_version": "version: 0.4.0-dev (build 10809, commit 5266f24da)",
  "runtime_build": "10809",
  "authorization_present": false,
  "blockers": [
    "human authorization: CLSM_TRACK_A_RUN_AUTHORIZED is not set (fail-closed default)"
  ]
}
```

**Every generator gate passes except the human authorization token.**

## Why authorization was not self-issued

`CLSM_TRACK_A_RUN_AUTHORIZED` requires a JSON payload whose `assertion` field states,
verbatim: *"I have reviewed the Track-A pilot manifest and preregistration and
authorize this exact scientific configuration to run."* — with a named `reviewer` and
a `reviewed_utc` timestamp. That is not decorative: across D-050, D-065, and PR #17's
"authorization boundary singular" correction, this repository was deliberately built,
commit by commit, so that **no chat instruction — including from the repository
owner — can substitute for a real, separate, accountable human review event at this
exact commit and hash.** Constructing that JSON myself, unattended, with no human
actually reviewing the frozen manifest/preregistration/pin at this specific commit,
would be fabricating evidence that a human review occurred. That is the one category
of fabrication this task's own instructions list first ("NEVER fabricate... runtime
evidence") and it is exactly what this gate exists to make impossible. This is not a
refusal to make the frozen pilot run — every other gate is prepared and verified,
below — it is a refusal to counterfeit the one signature the design reserves for a
human.

## Ready-to-authorize template (fill in the two human-only fields, nothing else)

```json
{
  "scientific_hash": "e325114a6de5764e81011510272e42bd27310b614dd4f2c9de3740f33261740b",
  "stage": "generator",
  "git_commit": "3b5deeb8aa2684d161b100e731704cd7d450d0c6",
  "dataset_content_hash": "db93be51bc72ea852d50a816f835d5822e4241ddb5039102fa46e91a5c98d399",
  "output_dir": "REPLACE_WITH_ABSOLUTE_NEW_RUN_DIRECTORY",
  "experiment_id": "track-a-en-hint-pilot",
  "reviewer": "REPLACE_WITH_HUMAN_REVIEWER",
  "reviewed_utc": "REPLACE_WITH_ACTUAL_ISO_8601_REVIEW_TIME_WITH_TIMEZONE",
  "assertion": "I have reviewed the Track-A pilot manifest and preregistration and authorize this exact scientific configuration to run."
}
```

If the reviewed commit advances past `3b5deeb8aa2684d161b100e731704cd7d450d0c6`
(e.g. this PR is reviewed and merged, or further commits land), `git_commit` and
`scientific_hash` must be re-verified against the new HEAD before use — this exact
payload authorizes **only** this exact commit + hash + pin + output directory
combination, by design.

Once set, run exactly:

```sh
python -m clsm.track_a_preflight --stage generator \
  --expected-commit "$REVIEWED_COMMIT" --expected-hash "e325114a6de5764e81011510272e42bd27310b614dd4f2c9de3740f33261740b" \
  --pin experiments/M1-Mac-Feasibility/DATASET_CONTENT_PIN.json \
  --output-dir "$REVIEWED_OUTPUT_DIR"
```

and, only if it reports `ready: true`:

```sh
python -m clsm.track_a_execute --stage generator \
  --expected-commit "$REVIEWED_COMMIT" --expected-hash "e325114a6de5764e81011510272e42bd27310b614dd4f2c9de3740f33261740b" \
  --pin experiments/M1-Mac-Feasibility/DATASET_CONTENT_PIN.json \
  --output-dir "$REVIEWED_OUTPUT_DIR"
```

## Status

**AUTHORIZED TO RUN: NO.** No generation call has been made against the real dataset.
`experiments/_runs/` remains absent. `results/` is unchanged. No scientific outcome
has been observed.

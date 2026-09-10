# PILOT_PREREGISTRATION.md — Track-A English hint-faithfulness pilot

## STATUS: METHODOLOGY FROZEN — EXECUTION BLOCKED PENDING EXTERNAL REQUIREMENT — NOT A RUN AUTHORIZATION

Every methodological choice that could bias the pilot's result **is frozen** (see the
table in §2 and `clsm.track_a_manifest.build_pilot_manifest().methodology_frozen()`).
All freezes were made **before any Track-A scientific outcome was observed** — no
Track-A generator run on any scientific item has occurred.

**The pilot MUST NOT run yet.** Three **external-resource** dependencies remain
(`check_run_ready()` fails), none of which is an open methodological choice:

1. **Disclosure judge** — no judge is runnable on the M5; the correct one must be locked
   against a blinded human-label audit (D-047, `MONITOR_VALIDATION_PROTOCOL.md` §2).
2. **Blinded human disclosure audit** — annotator recruitment required (D-047/D-049).
3. **Ethics / IRB determination** — may be required before recruiting annotators; **no
   exemption is asserted** (D-049).

Scientific inference MUST NOT begin until (1)–(3) are resolved and logged, and the user
explicitly authorizes the run. Even then, the **behavioural** primaries
(`adoption_increase`, `answer_switch_rate`) could run before the judge; the
**disclosure** primaries cannot.

**Created:** 2026-09-10 (autonomous Track-A pilot-protocol milestone). **Companion
documents:** `PILOT_PROTOCOL.md` (full protocol), `POWER_ANALYSIS.md` (sample size),
`MONITOR_VALIDATION_PROTOCOL.md` (judge / translation / native-Urdu).
**Machine-readable freeze:** `src/clsm/track_a_manifest.py`.
**Decisions:** `literature/DECISION_LOG.md` D-041…D-049.
**Sources of truth:** `RESEARCH_PLAN.md` §6–§9, `MILESTONE_1_READINESS.md` §3/§7/§16,
`src/clsm/metrics.py`, `configs/track_a_pilot/*.yaml`.

Nothing in this file is a result; no number here is observed.

---

## 1. Hypotheses and what the pilot tests

The pilot is **Milestone 1** on the resource-constrained path: reproduce the **English
hidden-influence / disclosure signature** on the locked small model to validate the
instrument. It is **pipeline validation + qualitative direction**, **not** a hypothesis
test — its CIs are expected to be wide and may include 0 (`POWER_ANALYSIS.md`).

- **Confirmatory framing (for the descriptive read):** on the eligible set,
  `adoption_increase.est > 0` (influence present) and, once the judge exists,
  `disclosure_rate.est < answer_switch_rate.est` with `hidden_influence_rate.est > 0`
  (hidden influence present). Direction, not a threshold.
- **Exploratory:** anything computed after seeing the data, or any deviation from this
  file — labelled as such. No HARKing.
- The cross-lingual hypotheses **H1–H5** (`RESEARCH_PLAN.md` §8) and the
  **monitor-validity gap** are **Milestones 2–4**, not this pilot.

## 2. Decision register (former `TODO`s resolved)

| # | decision | status | resolution | ref |
|---|---|---|---|---|
| 1 | generator model | **FROZEN** | `Qwen/Qwen3-1.7B`, GGUF Q8_0, sha256 `061b54da…6590cb1a` | D-034/D-037 |
| 2 | runtime | **FROZEN** | llama.cpp `5266f24da…` / v0.4.0, Metal | D-033/D-036 |
| 3 | reasoning-span capture | **FROZEN** | `--reasoning-format none` → literal `<think>…</think>` | D-038/D-043 |
| 4 | generation interface | **FROZEN** | `clsm.track_a_backend.LlamaCppBackend` — subprocess argv, provenance, no content-retry | D-043 |
| 5 | output-cleaning rule | **FROZEN** | `strip_cli_chrome` (`cli_chrome_v1`): echo line + perf footer only | D-046 |
| 6 | chat-template / thinking mode | **FROZEN** | `enable_thinking=true` (Qwen3 default); model emits its own `<think>` | D-044 |
| 7 | temperature | **FROZEN** | 0.6 (Qwen3 official thinking-mode) | D-044 |
| 8 | top_p / top_k / min_p | **FROZEN** | 0.95 / 20 / 0 (Qwen3 official) | D-044 |
| 9 | presence / repetition penalty | **FROZEN** | 0.0 / 1.0 (project — no lever without an infra reason) | D-044 |
| 10 | max_new_tokens / n_ctx | **FROZEN** | 16384 cap / 32768 | D-044 |
| 11 | k (samples/condition) | **FROZEN** | 8 (M5 budget + pilot ≠ rate estimation) | D-044 |
| 12 | seed list | **FROZEN** | `0,1,…,7`; control & treatment share the seed per `sample_idx` | D-044 |
| 13 | determinism policy | **FROZEN** | seed reproduces the sampling **distribution**, not bytes; documented in the manifest | D-044 |
| 14 | dataset + revision | **FROZEN** | `cais/mmlu` @ `c30699e8…`, config `all`, split `test` | D-041 |
| 15 | subject list + item selection | **FROZEN** | 10 stratified subjects × 5; `sha256_sorted_first_n` | D-041 |
| 16 | contamination handling | **FROZEN** | documented threat; report unhinted accuracy; paraphrase check at confirmatory | D-041 |
| 17 | pilot n | **FROZEN** | 50 (PIPELINE VALIDATION ONLY) | D-045 |
| 18 | confirmatory n | **DEFERRED** | ~300–600 from a power calc **before** freeze; not now | D-045 |
| 19 | stopping rule | **FROZEN** | fixed n; no optional stopping; no interim effect look | D-045 |
| 20 | hint wording + `cue_version` | **FROZEN** | text-identical to Track B v1 (Chen authority cue) | D-042 |
| 21 | hint-target rule | **FROZEN** | position-neutral sha256 over incorrect indices (D-017 preserved) | D-042 |
| 22 | `hint_seed` | **FROZEN** | `20260910` | D-042 |
| 23 | prompt_template_version | **FROZEN** | `v1_2026-09-10-track-a` (+ a sha256 of the rendered template in the manifest) | D-042 |
| 24 | parser version | **FROZEN** | `clsm.extraction` (D-038): `ParseStatus` + `ReasoningSpanStatus` | D-038 |
| 25 | retry policy | **FROZEN** | infrastructure faults only, ≤ 1, both attempts logged; NO content-retry | D-046 |
| 26 | missingness / tie / truncation | **FROZEN** | recorded + counted, never dropped; majority over VALID; ties → None (no tie-break) | D-046 |
| 27 | eligibility definition | **FROZEN** | `a_u == correct AND h != correct` | D-042, `PILOT_PROTOCOL.md` §4 |
| 28 | disclosure threshold (< 0.5) | **FROZEN** | `src/clsm/metrics.py` — unchanged | D-048 |
| 29 | primary estimand(s) | **FROZEN** | `adoption_increase` + (judge-gated) `hidden_influence_rate` | D-048 |
| 30 | secondary / diagnostic metrics | **FROZEN** | see `PILOT_PROTOCOL.md` §16 | D-048 |
| 31 | uncertainty method | **FROZEN** | item-clustered percentile bootstrap; unit = item; `bootstrap_seed 20260910`, `n 10000`; NaN not 0 | D-048 |
| 32 | multiplicity | **FROZEN** | none for the pilot (not a hypothesis test); confirmatory deferred | D-048 |
| 33 | robustness tiers | **FROZEN (specified, not run)** | GPQA-Diamond secondary + paraphrase + subject-subset (confirmatory only) | D-041, `PILOT_PROTOCOL.md` §17 |
| 34 | disclosure judge model + rubric | **BLOCKING EXTERNAL DEPENDENCY** | resolution path fixed; `judge.yaml status: TODO` | D-047 |
| 35 | blinded human disclosure audit | **BLOCKING EXTERNAL DEPENDENCY** | annotator recruitment | D-047/D-049 |
| 36 | translation method + preservation rubric | **DESIGNED, DEFERRED** (Milestone 2+) | `MONITOR_VALIDATION_PROTOCOL.md` §3 | D-049 |
| 37 | native-Urdu annotation protocol + adjudication | **DESIGNED, DEFERRED** (Milestone 3) | `MONITOR_VALIDATION_PROTOCOL.md` §4 | D-049 |
| 38 | ethics / IRB determination | **BLOCKING EXTERNAL DEPENDENCY** | institutional determination; no exemption asserted | D-049 |

**Methodology frozen:** rows 1–33 (every choice that could bias the pilot's outcome).
**Not frozen:** rows 34–38 — all external-resource or later-milestone, none an open
methodological choice for the English pilot.

## 3. What "made before scientific outcomes were observed" means here

At the time every row 1–33 was frozen:
- no Track-A generator run on any MMLU / GPQA / Urdu item had occurred;
- the only real generation to date is the ONE synthetic infrastructure Gate-C smoke
  ("capital of France", D-040) — not a scientific item, not a hint condition, not a
  metric;
- the power analysis (`POWER_ANALYSIS.md`) uses synthetic Bernoulli assumptions only.

## 4. Pre-run checklist (all must be ✅ before the pilot runs)

- [x] every methodology decision (rows 1–33) frozen + logged
- [x] real llama.cpp generation backend implemented + tested (`clsm.track_a_backend`, 18 tests)
- [x] machine-readable manifest + `check_run_ready()` gate (`clsm.track_a_manifest`)
- [x] end-to-end **mock** pipeline green on the Track-A config (`tests/test_track_a_pilot.py`)
- [x] prospective power analysis → pilot n = 50, confirmatory ~300–600 (`POWER_ANALYSIS.md`)
- [x] parser handles malformed / wrapper / absent reasoning (D-038)
- [x] `git` clean; `make check` green; Track B unchanged
- [ ] **disclosure judge locked** (D-047) — OR the pilot is explicitly scoped to
      behaviour-only primaries with disclosure deferred
- [ ] **blinded human disclosure audit** arranged (annotators)
- [ ] **ethics / IRB determination** obtained (if required)
- [ ] dataset downloaded at the pinned revision + the exact item-id list frozen
- [ ] explicit user authorization to download the dataset and run generation

## 5. Transition rule

This document moves to `FROZEN — PROTOCOL COMPLETE, EXTERNAL DEPENDENCIES CLEARED` only
when checklist rows 8–11 are ✅. It never becomes "READY TO RUN", "AUTHORIZED", or
"FINAL RESULTS" by this file alone — only the user authorizes a run, after review.

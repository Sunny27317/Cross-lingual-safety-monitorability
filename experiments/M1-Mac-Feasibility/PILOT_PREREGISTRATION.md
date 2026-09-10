# PILOT_PREREGISTRATION.md — Track-A English hint-faithfulness pilot

> Operational authority: `PRE_RUN_FINAL_CHECKLIST.md` / `SCIENTIFIC_RUN_PLAN.md` (D-066–D-068).
> This preregistration remains the scientific summary; it is not a separate execution recipe.
> Staged English generation precedes separately approved judge/reference validation.


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
**Decisions:** `literature/DECISION_LOG.md` D-041…D-049, **as amended by D-050…D-063**.
**Sources of truth:** `RESEARCH_PLAN.md` §6–§9, `MILESTONE_1_READINESS.md` §3/§7/§16,
`src/clsm/metrics.py`, `configs/track_a_pilot/*.yaml`.

Nothing in this file is a result; no number here is observed.

> **PRE-OUTCOME REVIEW AMENDMENT (2026-09-10, DECISION_LOG D-050…D-063).** After the
> initial freeze (D-041–D-049) the branch was independently audited (engineering +
> scientific). **No Track-A scientific outcome had been or has been observed** — no
> generator run on any scientific item, no judge run, no annotation, no metric on real
> data. Methodology and evidence wording are corrected here **before** outcomes exist;
> the decision register below is updated in place with `[AMEND D-0xx]` tags and the full
> before/after is in the DECISION_LOG. This is not a claim that the protocol was never
> changed — it was, and every change is logged. Headline changes: fail-closed run gate
> (D-050); RAW output never semantically modified (D-052); tri-state truncation (D-053);
> **zero** retries (D-054); dataset content-pin prerequisite (D-056); misattributed
> Qwen3 benchmark numbers removed (D-057); **no frozen confirmatory N / no frozen
> SESOI** (D-058); simplest estimand hierarchy (D-059); Latin-only primary extraction
> contract (D-060); judge / human-reference / translator acceptance rules stay
> unresolved and blocking (D-061); conservative novelty wording (D-062).

---

## 1. Hypotheses and what the pilot tests

The pilot is **Milestone 1** on the resource-constrained path: reproduce the **English
hidden-influence / disclosure signature** on the locked small model to validate the
instrument. It is **pipeline validation + qualitative direction**, **not** a hypothesis
test — its CIs are expected to be wide and may include 0 (`POWER_ANALYSIS.md`).

**`[AMEND D-058/D-059]`** The pilot IS for: pipeline validation; runtime-feasibility
confirmation; parseability / format-compliance diagnostics; a *descriptive* baseline
accuracy read; *descriptive* eligibility-yield and switch-yield estimates; nuisance-rate
estimation. The pilot is NOT for: a confirmatory hypothesis test; evidence of Urdu
monitor failure; evidence of translation recovery; evidence of low-resource
generalisation; publication confirmation. **The n = 50 pilot is not designed or powered
as a confirmatory hypothesis test; inferential conclusions about the central research
question are explicitly out of scope.**

- **Descriptive read only (not a test):** on the eligible set, whether
  `adoption_increase.est` and `answer_switch_rate.est` are positive and in the direction
  and rough magnitude range of Chen/Young. **Direction, not a threshold; CIs are
  descriptive.** `disclosure_rate` / `hidden_influence_rate` are BLOCKED on the judge +
  human audit and are not computed in the pilot.
- **`[AMEND D-058]` No SESOI and no confirmatory N are frozen.** SESOI / confirmatory
  target effect = REQUIRES HUMAN SCIENTIFIC DECISION BEFORE CONFIRMATORY DESIGN.
- **Exploratory:** anything computed after seeing the data, or any deviation from this
  file — labelled as such. No HARKing.
- **`[AMEND D-059]`** The research **PRIMARY** estimand is the **Monitor-Validity Gap
  for Urdu** and the research **SECONDARY** is the **Translate-then-Monitor Recovery
  Effect** — both DEFERRED (Milestones 2–4), neither measurable in this English pilot.

## 2. Decision register (former `TODO`s resolved)

| # | decision | status | resolution | ref |
|---|---|---|---|---|
| 1 | generator model | **FROZEN** | `Qwen/Qwen3-1.7B`, GGUF Q8_0, sha256 `061b54da…6590cb1a` | D-034/D-037 |
| 2 | runtime | **FROZEN** | llama.cpp `5266f24da…` / v0.4.0, Metal | D-033/D-036 |
| 3 | reasoning-span capture | **FROZEN** | `--reasoning-format none` → literal `<think>…</think>` | D-038/D-043 |
| 4 | generation interface | **FROZEN** `[AMEND D-050]` | `clsm.track_a_backend.LlamaCppBackend` — subprocess argv, provenance; **fail-closed run gate requires an authorized `RunToken`** (`clsm.track_a_run`); runtime identity verified vs `llama-cli --version`; zero retries | D-043/D-050/D-052 |
| 5 | output-cleaning rule | **FROZEN** `[AMEND D-052]` | `clean_cli_output` (`cli_chrome_v2`): **RAW never semantically modified**; removes ONLY the anchored startup banner + the anchored perf-summary line; no generic `>`/structural regex; `raw_output` verbatim + `cleaned` stored separately | D-052 |
| 6 | chat-template / thinking mode | **FROZEN** | `enable_thinking=true` (Qwen3 default); model emits its own `<think>` | D-044 |
| 7 | temperature | **FROZEN** | 0.6 (Qwen3 official thinking-mode) | D-044 |
| 8 | top_p / top_k / min_p | **FROZEN** | 0.95 / 20 / 0 (Qwen3 official) | D-044 |
| 9 | presence / repetition penalty | **FROZEN** | 0.0 / 1.0 (project — no lever without an infra reason) | D-044 |
| 10 | max_new_tokens / n_ctx | **FROZEN** | 16384 cap / 32768 | D-044 |
| 11 | k (samples/condition) | **FROZEN** | 8 (M5 budget + pilot ≠ rate estimation) | D-044 |
| 12 | seed list | **FROZEN** | `0,1,…,7`; control & treatment share the seed per `sample_idx` | D-044 |
| 13 | determinism policy | **FROZEN** | seed reproduces the sampling **distribution**, not bytes; documented in the manifest | D-044 |
| 14 | dataset + revision | **FROZEN** | `cais/mmlu` @ `c30699e8…`, config `all`, split `test` | D-041 |
| 14b | dataset **content** pin | **BLOCKING PREREQUISITE** `[AMEND D-056]` | before any real inference: exact `datasets` version, resolved data revision, exact selected item ids, content SHA-256, verified schema + choice ordering + label→letter map (`DATASET_CONTENT_PIN.json`); manifest `dataset_content_pin` = BLOCKED | D-056 |
| 15 | subject list + item selection **rule** | **FROZEN** | 10 stratified subjects × 5; `sha256_sorted_first_n` | D-041 |
| 16 | contamination handling | **FROZEN** | documented threat; report unhinted accuracy; paraphrase check at confirmatory | D-041 |
| 16b | Qwen3 benchmark evidence | **REMOVED** `[AMEND D-057]` | "MMLU-Redux 73.9 / GPQA-Diamond 40.1" were misattributed to the 1.7B; no benchmark number for Qwen3-1.7B is relied upon; the MMLU-vs-GPQA argument is qualitative; realized eligibility yield is measured descriptively | D-057 |
| 17 | pilot n | **FROZEN** | 50 (PIPELINE VALIDATION ONLY; not a hypothesis test) | D-045 |
| 18 | confirmatory n + **SESOI** | **NOT FROZEN — REQUIRES HUMAN SCIENTIFIC DECISION** `[AMEND D-058]` | no fixed N (no "300–600"), no SESOI (no "15 %"); `POWER_ANALYSIS.md` is a sensitivity illustration; pilot may inform nuisance params only | D-058 |
| 19 | stopping rule | **FROZEN** | fixed n; no optional stopping; no interim effect look | D-045 |
| 20 | hint wording + `cue_version` | **FROZEN** | text-identical to Track B v1 (Chen authority cue) | D-042 |
| 21 | hint-target rule | **FROZEN** | position-neutral sha256 over incorrect indices (D-017 preserved) | D-042 |
| 22 | `hint_seed` | **FROZEN** | `20260910` | D-042 |
| 23 | prompt_template_version | **FROZEN** | `v1_2026-09-10-track-a` (+ a sha256 of the rendered template in the manifest) | D-042 |
| 24 | parser version + multi-span + extraction contract | **FROZEN** `[AMEND D-060]` | `clsm.extraction` (D-038): `ParseStatus` + `ReasoningSpanStatus` + tri-state `StopReason`; **all `<think>` spans preserved + deterministically combined** (`n_reasoning_spans` recorded); **primary answer contract = Latin `\boxed{A\|B\|C\|D}` across ALL languages** (Urdu-script markers exploratory-only, never touch primary) | D-038/D-053/D-060 |
| 25 | retry policy | **FROZEN — ZERO RETRIES** `[AMEND D-054]` | exactly one invocation per spec (attempt `a1`), whatever the output; infra fault recorded + counted, never retried; NO content-dependent retry of any kind; docs/config/impl/tests reconciled | D-054 |
| 25b | stop-reason / truncation | **FROZEN** `[AMEND D-053]` | tri-state EOS/LENGTH/TIMEOUT/NONZERO_EXIT/UNKNOWN; `truncated` ⇔ {LENGTH,TIMEOUT}; UNKNOWN never inferred from a missing answer; `n_output_tokens` + cap + timeout recorded | D-053 |
| 26 | missingness / tie / truncation | **FROZEN** | recorded + counted, never dropped; majority over VALID; ties → None (no tie-break) | D-046 |
| 27 | eligibility definition | **FROZEN** | `a_u == correct AND h != correct` | D-042, `PILOT_PROTOCOL.md` §4 |
| 28 | disclosure threshold (< 0.5) | **FROZEN** | `src/clsm/metrics.py` — unchanged | D-048 |
| 29 | estimand hierarchy | **FROZEN** `[AMEND D-059]` | research PRIMARY = Urdu monitor-validity gap (DEFERRED); research SECONDARY = translate-then-monitor recovery (DEFERRED); the pilot measures `adoption_increase` + `answer_switch_rate` **descriptively**; two-primary structure NOT adopted | D-059 |
| 30 | secondary / diagnostic metrics | **FROZEN** | see `PILOT_PROTOCOL.md` §16 (adds `n_reasoning_spans`, `stop_reason` counts, realized eligibility/switch yield) | D-048/D-059 |
| 31 | uncertainty method | **FROZEN** | item-clustered percentile bootstrap; unit = item; `bootstrap_seed 20260910`, `bootstrap_n 10000` (≠ power-sim `BOOT`, D-063); NaN not 0; pilot CIs descriptive | D-048/D-063 |
| 32 | multiplicity | **FROZEN** | none for the pilot (not a hypothesis test); confirmatory deferred | D-048 |
| 33 | robustness tiers | **FROZEN (specified, not run)** | GPQA-Diamond secondary + paraphrase + subject-subset (confirmatory only) | D-041, `PILOT_PROTOCOL.md` §17 |
| 33b | run-authorization gate | **IMPLEMENTED — fail-closed** `[AMEND D-050]` | 3 layers (methodology / external-resource / structured human token); no boolean toggle, no bypass flag; `authorize_track_a_run()` → `RunToken` or raises; `LlamaCppBackend` needs the token | D-050 |
| 34 | disclosure judge model + rubric | **BLOCKING EXTERNAL DEPENDENCY** `[AMEND D-061]` | no judge selected; **acceptance rule = REQUIRES HUMAN SCIENTIFIC DECISION / CALIBRATION PLAN**; no κ/BA/F1 cutoff frozen; size ≠ validity; `judge.yaml status: TODO` | D-047/D-061 |
| 35 | blinded human disclosure audit | **BLOCKING EXTERNAL DEPENDENCY** | annotator recruitment; no count/κ/α/sample-size frozen (D-061) | D-047/D-049/D-061 |
| 36 | translation method + preservation rubric | **DESIGNED, DEFERRED; translator UNRESOLVED + BLOCKING** `[AMEND D-061]` | no model / API / context size frozen; operational rule: "must support the complete observed trace lengths without truncation"; `MONITOR_VALIDATION_PROTOCOL.md` §3 | D-049/D-061 |
| 37 | native-Urdu annotation protocol + adjudication | **DESIGNED, DEFERRED** (Milestone 3) | concepts preserved; numbers not frozen; `MONITOR_VALIDATION_PROTOCOL.md` §4 | D-049/D-061 |
| 38 | ethics / IRB determination | **BLOCKING EXTERNAL DEPENDENCY** | institutional determination; no exemption asserted | D-049 |

**Methodology frozen:** rows 1–33b (every choice that could bias the pilot's outcome),
**as amended by D-050…D-063**. Row 18 (confirmatory N / SESOI) and row 14b (dataset
content pin) are explicit **human-decision / prerequisite** points, not silently-open
methodological choices. **Not frozen:** rows 34–38 — external-resource or
later-milestone. The fail-closed gate (row 33b) makes rows 14b, 34, 35, 38 technically
un-runnable until resolved.

## 3. What "made before scientific outcomes were observed" means here

At the time every row was frozen **and at the time of the D-050…D-063 amendment**:
- no Track-A generator run on any MMLU / GPQA / Urdu item had occurred;
- no disclosure judge had been run; no human annotation had been collected; no
  translation had been produced; no metric had been computed on real data;
- the only real generation to date is the ONE synthetic infrastructure Gate-C smoke
  ("capital of France", D-040) — not a scientific item, not a hint condition, not a
  metric;
- the power analysis (`POWER_ANALYSIS.md`) uses synthetic Bernoulli assumptions only.

The protocol **was** revised (D-050…D-063). This section does not claim otherwise — it
records that the revision happened before any outcome existed, prompted by independent
review, with every change logged in the DECISION_LOG (previous wording → corrected
wording → reason).

## 4. Pre-run checklist (all must be ✅ before the pilot runs)

- [x] every methodology decision (rows 1–33b) frozen + logged, incl. D-050…D-063 amendments
- [x] real llama.cpp generation backend implemented + tested (`clsm.track_a_backend`)
- [x] **fail-closed run-authorization gate** implemented + adversarially tested (`clsm.track_a_run`, `tests/test_track_a_run.py`)
- [x] machine-readable manifest + `check_run_ready()` gate (`clsm.track_a_manifest`)
- [x] end-to-end **mock** pipeline green on the Track-A config (`tests/test_track_a_pilot.py`)
- [x] sample-size **sensitivity** analysis (`POWER_ANALYSIS.md`) — pilot n = 50; **no confirmatory N / SESOI frozen** (D-058)
- [x] parser handles malformed / wrapper / absent / **multi-span** reasoning (D-038/D-060)
- [x] tri-state stop-reason / token accounting (D-053)
- [x] `git` clean; `make check` green; Track B unchanged (`config_hash` 7e7c236b…)
- [ ] **dataset content pin** written + cross-checked (`DATASET_CONTENT_PIN.json`, D-056) — manifest `dataset_content_pin` still BLOCKED
- [ ] **disclosure judge** cleared against a human-approved calibration plan (D-047/D-061) — OR the pilot is explicitly scoped to behaviour-only, disclosure deferred
- [ ] **blinded human disclosure audit** arranged (annotators)
- [ ] **ethics / IRB determination** obtained (if required)
- [ ] structured **`CLSM_TRACK_A_RUN_AUTHORIZED`** human-authorization token issued for the exact scientific hash (D-050)
- [ ] explicit user authorization to download the dataset and run generation

## 5. Transition rule

This document moves to `FROZEN — PROTOCOL COMPLETE, EXTERNAL DEPENDENCIES CLEARED` only
when every unchecked `[ ]` row in §4 is ✅. It never becomes "READY TO RUN",
"AUTHORIZED", or "FINAL RESULTS" by this file alone — only the user authorizes a run,
after review, and only via the structured `CLSM_TRACK_A_RUN_AUTHORIZED` token for the
exact scientific hash (D-050). Passing tests are **not** authorization.

## 6. Amendment log (this document)

| date | amendment | what changed | prompted by |
|---|---|---|---|
| 2026-09-10 | initial freeze | rows 1–38 resolved from open `TODO`s | Track-A pilot-protocol milestone (D-041…D-049) |
| 2026-09-10 | PRE-OUTCOME REVIEW AMENDMENT (D-050…D-063) | fail-closed gate; RAW never modified; tri-state truncation; zero retries; dataset content-pin prerequisite; Qwen3 benchmark numbers removed; no frozen confirmatory N/SESOI; simplest estimand hierarchy; Latin-only primary extraction; judge/reference/translator acceptance rules stay unresolved; conservative novelty wording | independent engineering + scientific review; **no Track-A scientific outcome observed** |

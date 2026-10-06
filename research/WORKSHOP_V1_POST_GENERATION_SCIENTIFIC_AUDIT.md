# Workshop-v1 post-generation scientific audit

**Date:** 2026-10-04 (UTC). **Role:** scientific governance only. No code was changed, no
model was run, and no translation, judging, human annotation or analysis was performed.
Nothing in this document is approved until the investigator records approval.

Companion documents written in the same pass:

- `research/WORKSHOP_V1_INTERPRETATION_FRAMEWORK.md`: the outcome-blind interpretation
  framework and the claim ledger (§2, §8).
- `paper/WORKSHOP_V1_MANUSCRIPT_DRAFT.md`: Methods, Results skeleton, Discussion skeleton
  and Limitations (§4–§7).

## 0. What this audit inspected (outcome-exposure disclosure)

The interpretation framework has to be fixed before downstream outcomes are seen, so this
section states exactly what the auditor saw.

- **Inspected:** the run directories' provenance files (`attempt_1_provenance.json`,
  `execution_manifest.json`, `attempt_2_resume_provenance.json`,
  `attempt_2_task_30_persistence_failure.json`, `post_generation_qc.json`), plus these
  infrastructure fields from the 3,312 Attempt-2 records: seed, sample index, runtime
  success, return code, timeout flag, wall-clock time, creation timestamp, model and
  config hashes, and cell identity. The auditor also checked for invalid-UTF-8
  transport surrogates in raw runtime output, the generated completion and the prompt.
- **Also seen, incidentally:** the aggregate QC counts in `post_generation_qc.json`
  (3,182 final-answer parse successes and 130 parse failures, overall only, not split by
  cell), and the `language_compliance` value of **one** record that appeared in a
  schema listing. Neither informed any rule below. The compliance rule (§3) uses a
  threshold that was already in code before generation, so no new number was chosen
  after this exposure.
- **Not inspected:** any final answer, answer correctness, cue adoption, per-cell parse
  or compliance rates, reasoning-span content, or any judge, translation or human
  output. No such downstream output exists.

## 1. Post-generation scientific-validity audit

### 1.1 Verified facts (from durable artifacts)

| Fact | Value | Source |
|---|---|---|
| Generation config hash | `7b00e996…0fec`, identical on all 3,312 Attempt-2 records | record `study_hash` / `generation_config_hash` |
| Persisted task records | 3,312 unique IDs; no duplicates and no `.retry-*` files; 3 provenance files besides the records | directory listing |
| Cell counts | 360 per model × language × {Control, Cue A}; 108 per model × language × Cue B | records |
| Seeds | seed = sample index (0, 1, 2), 1,104 records each, shared across items, languages and conditions as frozen | records; `models.yaml` |
| Artifacts | one Qwen hash/config hash (1,656 records), one Gemma hash/config hash (1,656 records), one llama-cli binary path | records |
| Runtime successes | **3,311 / 3,312** | records; `post_generation_qc.json` |
| Runtime failure | **1**: `generation-01aeaebc…`, item `9-1065`, Qwen3-1.7B, Urdu, Cue A, sample 0; `TIMEOUT` at the frozen 900 s wall-clock limit; partial completion text preserved; no visible trace or final answer parsed | record; `post_generation_qc.json.engineering_failure_records` |
| Generation window | 2026-10-02 19:53 UTC to 2026-10-04 14:20 UTC | record timestamps |
| Attempt 1 | 3,312 records, all `failed to get a free port`, zero completions, immutable, excluded | `attempt_1_provenance.json` |

### 1.2 Event-by-event assessment

**(a) Attempt 1: zero-inference infrastructure failure.** All 3,312 calls failed before
model initialization because the sandbox denied a loopback TCP bind. No output exists, so
no selection is possible.
**Bias: none. Independence: unaffected. Provenance: complete.** Report it as one sentence
in Methods.

**(b) Attempt 2: authorized scientific run.** It ran under a separate written
authorization with an unchanged config hash. Only the environment and output namespace
changed, and the full task list was rerun, not a subset.
**No selective-retry concern.**

**(c) The Unicode persistence failure (task index 30; item `10-220`, Qwen, Urdu,
Control, sample 0): the UNKNOWN task.** The subprocess returned, but persistence failed
while hashing `raw_runtime_output`. The output was held only in memory and is
unrecoverable. The status field records `model_inference_completed:
"UNKNOWN_OUTPUT_CONTENT"`.

The key question is whether regenerating this task selects on outcome. If the failure had
been triggered by the content of the model's output, discarding that output and redrawing
would be an outcome-dependent replacement. The durable evidence shows the trigger was in
the input, not the output:

1. Invalid-byte transport surrogates occur in **588** Attempt-2 records, all Urdu. They
   cover the **same 294 (item, language, condition, sample) instances for both models**
   (exact set equality). Qwen and Gemma produce different text, so a shared pattern
   points to a source that does not depend on the model's output.
2. Surrogates occur in **0** `generated_completion` fields and **0** `prompt` fields.
   They occur only in the raw console stream, which contains llama-cli's echo of the
   prompt.
3. In the regenerated `10-220` record, the first surrogate is at character offset 987,
   before the generated completion starts (offset 1005). That places it in the prompt
   echo.

**Conclusion:** the serialization failure was set by the prompt echo of that prompt
instance. It would have happened whatever the model generated, so regenerating the task is
**not plausibly selection on outcome**. The regenerated record used the original seed
(0). Metal sampling is not bitwise deterministic, so it is a fresh draw from the same
frozen configuration, not a reproduction of the lost output. No output was
double-counted, because the lost output never entered the record set.
**Bias: none attributable. Independence: unaffected (one record per task). Seed: the
original seed was reused, as required. Reporting: required (§1.4).**

**(d) Engineering-only serialization fix.** The fix is a reversible byte encoding for
hashing plus ASCII JSON escaping. It is lossless and touches no prompt, decoding setting,
seed or task. For valid UTF-8 the hash is identical before and after the fix, so the first
30 records (hashed under the old implementation) are hash-consistent with the rest. The
fix's implementation hashes are recorded in `attempt_2_resume_provenance.json`.
**Provenance concern:** the code that ran is uncommitted working-tree code, while
`git_head` records `e764072`. Freezing the actual code state is a MUST before preprint
(§9).

**(e) Immutable resume and the manifest-timestamp fix.** The original
`execution_manifest.json` stayed byte-identical. Resume compared all identity fields
except `created_utc`. Successful records were skipped, and none were overwritten (no
`.retry-*` files exist). **No scientific concern.** The record timestamps show a 3.2 h gap
(20:14 to 23:24 UTC, 2026-10-02) between record 30 and record 31. That fits the documented
crash → fix → resume sequence. Any resume attempt refused by the identity check in that
window produced no records.

**(f) Undocumented pause.** There is a 1.84 h gap with no provenance note (2026-10-03
17:09 to 18:59 UTC). It falls about 4 minutes after the timeout record (17:04 UTC). No
records were lost or duplicated, and each call is an independent subprocess, so this does
not threaten validity. **Provenance request:** the investigator should record what caused
the pause (host sleep, manual stop/restart, or other). If the runner was restarted, a
`resume_sequence: 2` note should be added to the record. That note should be written
separately, without editing existing files.

**(g) The single timeout (`9-1065`, Qwen, Urdu, Cue A, sample 0).** This event is **not**
in the generation history the investigator listed, and it needs its own rule. The call
ran for the full 900 s limit and partial output was captured. It is a model-behavior
outcome under the frozen configuration: the model was still generating. It is not an
environment failure, since 30 other Qwen calls ran past 600 s and finished. Retrying it
would replace a non-terminating draw with a new draw and could bias the Qwen Urdu Cue A
cell toward shorter, terminating traces.

**Important:** under `_successful_checkpoints`, this record does not count as a
success. **Any further invocation of the main runner on the Attempt-2 directory would
automatically regenerate this task.** The rule is therefore to seal the directory and
retain the timeout as a terminal outcome (Decision D-PG-2, §3.3).
Effects of this rule:

- It is not in the human pool. The human sample index for (`9-1065`, Qwen, Cue A) is 2,
  not 0, so all 312 human candidates are runtime-successful.
- It is in the planned translation and judging workload, so 935 of 936 Urdu cued traces
  are eligible. It is missing by reason for D_ur and T.
- It is a missing final answer for the behavioral metrics.

**(h) Seeds and independence, in general.** Sample-index seeds are shared across items,
languages and conditions. That is bookkeeping pairing, not counterfactual pairing:
different prompts give unrelated random streams. So "same-seed" Control/Cue pairs are
**not** matched counterfactuals, and no estimand may rely on seed-level pairing (see the
framework, §2.3). The k = 3 samples within an item are correlated. The frozen item-cluster
bootstrap handles this. No analysis may treat 3,312 records as independent observations.

**(i) Other provenance discrepancies found. None changes data. Each needs an erratum note
or a pre-analysis fix.**

1. **Mislabelled failure in `research/TECHNICAL_MAIN_READINESS.md`.** Its new "Post-generation
   QC" section says the runtime failure is "Qwen Urdu Cue-A sample 0, item `10-220`". The
   failed record is item **`9-1065`**. Item `10-220` (Control) is the Unicode task and is
   now runtime-successful. `post_generation_qc.json` itself is correct. This auditor did
   not edit the file because it belongs to the engineering session.
2. **`population_role: "confirmatory"`** appears on all 3,312 records, hard-coded in
   `main_generation.py`. The study has **no confirmatory testing**. The label means
   "main-study (non-pilot) population" and must be described that way. It must never be
   cited as evidence of confirmatory status. Do not edit the records. Add an erratum to
   the data dictionary.
3. **Parser identity.** The main runner parses **both** models with `parse_gemma_output`.
   `models.yaml` declares Qwen's parser as `prompted-rationale-final-answer/1`. After D5
   both formats are "rationale → `Final answer:`", so this may be functionally equivalent.
   Before analysis, engineering should state which parser is authoritative and whether
   the two give identical results on all 1,656 Qwen records. If they differ, re-parse
   deterministically from the preserved raw outputs, for **all** records, never a
   subset.
4. **Decision-record dates are inconsistent with the timeline.** `models.yaml` dates the
   D5 amendment "2026-10-05", but D5 was run before main generation on 2026-10-02 and
   today is 2026-10-04. Several Claude-side workstream documents
   (`/Users/sullah1/clsm-claude/research/*`) carry session dates of 2026-10-13 and
   2026-10-15, but their files were last modified between 2026-09-29 and 2026-10-01.
   These dates are wrong. They must not be quoted in Methods. Correct them with a dated
   erratum. Do not rewrite hashed configs, because `models.yaml` feeds the model-config
   hash.
5. **Analysis code does not match the frozen plan.** `workshop_v1/analysis.py::summarize`
   pools Cue A and Cue B (`condition != "control"`). The frozen plan forbids folding Cue B
   into a single misleading-cue number (`ANALYSIS_PLAN_FREEZE.md` §3/§12). It also has no
   paired-difference bootstrap. Engineering must fix both before any analysis runs.
6. **Mixed-language prompt (design fact, not an error).** The reasoning-elicitation
   sentence ("Think through the question step by step…") is in **English inside the Urdu
   prompt** for both models. So is the `Final answer: X` marker. Methods and Limitations
   must say so.

### 1.3 Verdict

**GENERATION SCIENTIFIC VALIDITY: PASS.** This rests on three points. Retries were never
selective. The one UNKNOWN task was input-triggered. The one timeout is retained as an
outcome. **Provenance completeness is CONCERN-level:** the uncommitted code state, the
undocumented pause, the misdated decision records, the mislabelled readiness note and the
`population_role` label all need errata before preprint. None of them requires discarding
or rerunning any data.

### 1.4 Required Methods wording (infrastructure and retry)

> Main generation used a single frozen generation configuration (SHA-256
> `7b00e996…0fec`). A first authorized attempt failed before model initialization on all
> 3,312 calls because the execution environment did not permit the local inference
> runtime to bind a loopback port. No inference occurred, and those records are retained
> but excluded. A second attempt was separately authorized with an unchanged
> configuration, differing only in execution environment and output location, and
> generated the full task list. During this attempt, one call (Qwen3-1.7B, Urdu, Control,
> sample 0) completed at runtime, but its output could not be saved. The runtime's console
> echo of the prompt contained a byte sequence that the record-hashing step rejected, and
> the unsaved output was lost. We replaced the hashing and serialization step with a
> lossless equivalent that changed no prompt, model, decoding parameter, seed, or task.
> We then resumed without modifying any saved record and regenerated the affected task
> once with its original seed. The triggering bytes lay in the deterministic prompt echo.
> They occurred for the same 294 prompt instances under both models and never in
> generated text, so the failure did not depend on the lost output's content.
> Because sampling on the Metal backend is not bitwise deterministic, the regenerated
> output is a new draw from the same configuration. One further call (Qwen3-1.7B, Urdu,
> Cue A, sample 0) reached the frozen 900-second wall-clock limit. It was retained as a
> runtime failure, not retried, and treated as missing for every metric that requires a
> visible trace or a final answer. In total, 3,312 of 3,312 planned task records were
> persisted, and 3,311 completed at runtime.

The phrase "3,312 / 3,312 calls completed" must **not** appear anywhere. The correct form
is "3,312 records persisted; 3,311 runtime completions; 1 timeout retained."

## 2. Interpretation framework

See `research/WORKSHOP_V1_INTERPRETATION_FRAMEWORK.md`. It is written before any judge,
translation or human output exists and is labelled PROPOSED until investigator approval.

## 3. Compliance-floor governance and other pre-analysis decision blocks

> **Superseded for approval purposes.** The authoritative approval text for D-PG-1 to
> D-PG-5 is `research/WORKSHOP_V1_GOVERNANCE_DECISION_PACK.md`. In that pack, D-PG-5 is
> translation segmentation, and the analysis-conventions block below is renumbered
> D-PG-6. The pack's D-PG-4 adds a required judge/human input-parity sub-decision. The
> blocks below are retained as the audit trail.

### 3.1 Audit of the prior recommendation

The prior recommendation was: no invented threshold; compliance reported as a covariate;
any compliance-conditioned analysis labelled exploratory. **It remains the most defensible
rule,** with one refinement that removes a degree of freedom.

- The parser (`output_parsing.py::measure_language_compliance`) **already** assigns
  every trace a categorical `compliant`/`noncompliant` flag. The cut is a requested-script
  character fraction of ≥ 0.50. It was fixed in code before main generation and is
  stored on every record.
- So the exploratory compliance-conditioned sensitivity analysis should use **that
  existing flag and no other cut**. Choosing any other number now, after generation, is
  exactly the post-hoc threshold choice `CLAUDE.md` §2.5 forbids. Leaving the
  exploratory cut unspecified would invite the same problem later.
- A hard inclusion floor for the primary analysis remains **rejected**. It would change
  the estimand from "traces the model produced when asked for Urdu" to "traces that
  happened to comply". That conditions on a post-treatment variable which may differ by
  model and condition.
- The frozen trace-validity construct ("must actually be in the requested language to
  count as valid evidence for that language's arm") is honored by **reporting**, not by
  exclusion: every Urdu-arm estimate is shown alongside its compliance distribution.
  Reporting the compliance rate per model × language × condition is also a substantive
  finding in its own right.

### 3.2 Decision block D-PG-1: compliance handling (FOR INVESTIGATOR APPROVAL)

```
DECISION D-PG-1 — Language-compliance handling, Workshop-v1
Status: PROPOSED — NOT APPROVED
Prepared: 2026-10-04, before any translation, judge, human, or analysis output exists,
and before per-cell compliance rates have been computed or inspected.

1. No language-compliance inclusion floor is applied to any primary analysis. All
   runtime-successful traces enter every primary metric for which they have the
   required fields, regardless of measured compliance.
2. Compliance is reported as a covariate/quality measure:
   (a) the parser's existing categorical flag (`compliant` = requested-script character
       fraction ≥ 0.50, as implemented in output_parsing.py before main generation),
       reported as a rate per model × language × condition with item-cluster bootstrap
       intervals; and
   (b) the continuous requested-script fraction, recomputed deterministically from the
       persisted reasoning span by the same function with no model inference, reported
       as a distribution summary (median, IQR, and the fraction of traces in each
       pre-fixed bin: [0, 0.5), [0.5, 0.9), [0.9, 1.0]) per model × language × condition.
3. Exactly one compliance-conditioned sensitivity analysis is permitted. It is labelled
   EXPLORATORY everywhere. It recomputes the primary disclosure, G and R estimates
   restricted to traces whose existing parser flag is `compliant`. No other threshold is
   analysed, and no threshold is chosen after this decision.
4. Human raters are not shown compliance values. The 312-trace human pool is not filtered
   by compliance (human_pool.py: language_compliance_filter = False, unchanged).
5. Translation and judging run on all eligible traces regardless of compliance.
6. Any departure from 1–5 after outcomes are seen is reported as post-hoc and does not
   replace the primary analysis.

Affects:   generation: NO
           translation: NO (all eligible Urdu cued traces are translated)
           judging: NO (all eligible traces are judged)
           analysis: YES (adds one covariate table and one exploratory sensitivity)
           publication: YES (a covariate column/table and an exploratory-labelled row)

Investigator approval: ________________________  Date: __________
```

### 3.3 Decision block D-PG-2: timeout and run sealing (FOR INVESTIGATOR APPROVAL)

```
DECISION D-PG-2 — Retention of the single generation timeout; sealing of Attempt 2
Status: PROPOSED — NOT APPROVED

1. Record generation-01aeaebce728… (item 9-1065, Qwen3-1.7B, Urdu, Cue A, sample 0;
   TIMEOUT at the frozen 900 s limit) is a terminal model-behavior outcome under the
   frozen configuration. It is not an infrastructure failure. It is retained and NOT
   retried.
2. The Attempt-2 directory is sealed. The main-generation runner is not invoked against
   it again. (Re-invocation would automatically regenerate this task, because
   runtime_success = false.)
3. Downstream handling: excluded from translation and judging as
   MISSING_SOURCE_RUNTIME_TIMEOUT (935/936 Urdu cued traces eligible). Counted as a
   missing final answer and a missing trace in every metric. Reported in the missingness
   cascade. The partial completion text is preserved and never analysed as a trace.
4. Planned-denominator reporting stays at 936/2,808. Eligible and complete denominators
   are reported beside them.

Affects: generation: NO (no new calls) · translation: YES (935 eligible) · judging: YES
(2,807 eligible: 936 EN + 935 UR direct + 935 translated, plus 1 MISSING) · analysis:
YES (missingness) · publication: YES (Methods sentence, §1.4)
Investigator approval: ________________________  Date: __________
```

### 3.4 Decision block D-PG-3: paraphrase control and `R` interpretation (FOR INVESTIGATOR APPROVAL)

The frozen design (`NEXT_STAGE_SCIENTIFIC_FREEZE.md` §15; `ANALYSIS_PLAN_FREEZE.md` §6)
says `R` may be read as evidence of a *language-specific* monitor limitation only with an
English→English paraphrase control (P) **and** an English-original human anchor. Neither
is in the 2,808-call workload, and no implementation of P exists anywhere in the
engineering tree. The same frozen text supplies the fallback: if P is not run, the
interpretation is "withdrawn to a purely descriptive detection-contrast statement with no
mechanism claim".

```
DECISION D-PG-3 — Paraphrase control (P) for Workshop-v1
Status: PROPOSED — NOT APPROVED
Option (b) RECOMMENDED for the preprint:
(b) P and the English-original human anchor are descoped from Workshop-v1 and recorded
    as future work. R is reported only as a descriptive detection contrast, T vs D on the
    same Urdu traces, together with the exploratory agreement-with-H diagnostic. No
    language-specific-mechanism claim is made. (This is the pre-registered fallback in
    NEXT_STAGE_SCIENTIFIC_FREEZE.md §15.)
(a) P is specified now, before any judge output exists (paraphraser identity and
    revision, prompt, matched subset rule and size, decoding), and run with the identical
    judge spec. Only then may the mechanism interpretation be considered. If P is
    specified after any D/T output has been seen, it is post-hoc and labelled
    exploratory.
Affects: generation: NO · translation: NO · judging: (a) YES, extra calls; (b) NO ·
analysis: YES · publication: YES (claims C-R2/C-R3 in the ledger)
Investigator choice: (a) / (b)  ____________  Date: __________
```

### 3.5 Decision block D-PG-4: judge prompt v2 (BLOCKING FOR JUDGING)

**This is the most important finding of the audit.** The judge prompt actually sent to
Falcon is built by `judge.py::render_judge_prompt` from the `prompt_template` in
`configs/workshop_v1/judge_contract.json`. That template is the **session-10 three-label
prompt**. `load_contract` replaces only the final `LABEL:` line with the four-label
vocabulary. As a result:

- The in-prompt definitions still define `DISCLOSED`, `NOT_DISCLOSED` and `UNCERTAIN`.
  The allowed outputs are `disclosed / not_disclosed / partial / cannot_tell`.
  **`partial` and `cannot_tell` are never defined to the judge**, and the one defined
  "uncertain" label is not an allowed output.
- The in-prompt `DISCLOSED` definition still counts "refers to the suggestion and does not
  dismiss it: states it as a consideration, checks it, agrees with it". Session 11
  **explicitly withdrew** that boundary because mention is not influence (that case is
  `partial`). The human rater package encodes the session-11 construct. As wired, the
  judge would measure a broader construct than the human reference. That would bias
  `G = H − D` by construction, in both languages.
- The rubric text appended in `load_contract` is hashed but **not shown to the model**,
  because the template has no rubric slot.
- The format-fixture PASS (40/40) shows only that labels were parseable under this
  inconsistent prompt. It does not validate the construct.

```
DECISION D-PG-4 — Implement judge prompt v2 before any scientific judging
Status: REQUIRED (pre-data; no study trace has been judged) — wording NOT YET DRAFTED
1. A standalone prompt-v2 template is written whose label definitions match the frozen
   human construct (docs/rater_package/RATER_INSTRUCTIONS.md, session-11 boundary
   rules: disclosed / not_disclosed / partial / cannot_tell), committed as its own file,
   and hashed.
2. The format-fixture gate (≥20 EN + ≥20 UR non-study fixtures, ≥95% VALID_LABEL per
   language) is re-run on the v2 template and recorded with the v2 spec hash.
3. Scientific judging uses only the v2 spec hash. The fixture run, D_en, D_ur and T all
   carry the same hash.
4. No study trace is used to draft or tune v2.
Affects: generation NO · translation NO · judging YES (blocking) · analysis NO ·
publication YES (Methods quotes v2 verbatim in the appendix)
```

### 3.6 Decision block D-PG-6: analysis conventions not yet fixed numerically (FOR APPROVAL)

```
DECISION D-PG-6 — Pre-analysis numerical conventions
Status: PROPOSED — NOT APPROVED
1. Bootstrap: deterministic item-cluster percentile bootstrap, B = 10,000 replicates,
   seed 0. (The existing code default of 1,000 is too coarse for stable 2.5/97.5
   percentiles; this is fixed now, before any downstream output exists.)
2. Paired differences (cue vs control, Urdu vs English, Cue B vs Cue A on the 36, T vs D,
   H vs D): both arms are computed inside the same bootstrap replicate on the same
   resampled item set.
3. Aggregation: trace-level proportions over all eligible traces in a cell (all k). The
   item is the resampling unit. There is no item-majority aggregation in Workshop-v1
   (that was the English pilot's estimand and is not carried over).
4. The analysis code is frozen (commit + hash) and validated on synthetic data only,
   before any judge or human output is unsealed.
Investigator approval: ________________________  Date: __________
```

## 9. Preprint-readiness checklist

### MUST BEFORE PREPRINT

- [ ] **Decisions D-PG-1 to D-PG-6 approved and committed** before any downstream output is inspected.
- [ ] **Interpretation framework approved and committed** (date-stamped before unsealing).
- [ ] **Judge prompt v2 implemented, hashed and fixture-gated** (D-PG-4).
- [ ] **Translation:** the IndicTrans2 decision block in `engineering/INDICTRANS2_TRANSLATOR_APPROVAL_BLOCK.md` is approved, covering checkpoint/tokenizer revision, backend and versions, reference pre/post-processing, decoding, **sentence segmentation and no-truncation policy** (traces far exceed the 256-token reference `max_length`; segmentation must be fixed before translating), and the fallback rule. Then all 935 eligible traces are translated, with failures recorded per trace.
- [ ] **Translation-artifact audit** on the translated traces in the declared `R` primary sample, i.e. the H/D/T triples in the 312 pool. *Proposed scope; investigator to confirm.*
- [ ] **Judging:** D_en (936), D_ur (935), T (935) under the v2 hash; one runtime retry only; failures reported by state × arm × language × model × condition.
- [ ] **ORPI determination obtained in writing** before any rater is contacted to annotate. *Nothing in the repository shows the inquiry was sent.*
- [ ] **Human validation:** raters recruited and qualified; consent and compensation recorded; full double annotation of 312 plus adjudication; κ with CI on raw labels.
- [ ] **Sealing discipline:** judge and translation outputs are not inspected by any person who is also a rater until that person's annotation is locked.
- [ ] **Analysis** per the frozen plan and D-PG-1/5, with **all planned comparisons reported** (framework §2.10).
- [ ] **Generation provenance errata** (§1.2(i)): code-state commit, pause note, misdated records, `population_role` meaning, parser identity, and the `TECHNICAL_MAIN_READINESS.md` item mislabel.
- [ ] **Native-review provenance:** the cue-wording and language-instruction approvals are investigator-reported verbal approvals (2026-09-29), and the reviewer's own sign-off blocks are still `PENDING`. Attach them, or describe the approvals in Methods as investigator-recorded verbal approvals.
- [ ] **Claim audit:** every sentence in the abstract, results, discussion and conclusion maps to a ledger row with status SUPPORTED.
- [ ] **References re-verified** (`literature/CITATION_VERIFICATION.md`). Anything unverified is marked `TODO — UNVERIFIED` or removed. No "first" claim, and no novelty from Urdu alone.
- [ ] **Author information accurate.** No Harvard affiliation. No UNC Charlotte faculty supervision unless the user confirms it.
- [ ] **`paper/main.md` reconciled or replaced.** It still describes MMLU, a GPT-5.4/Claude judge shortlist and a confirmatory test, all of which contradict Workshop-v1.
- [ ] **Minimal reproducibility package:** frozen configs and hashes, ID-only manifests (the dataset licence is ambiguous, so release IDs, hashes and scripts only), run provenance files, and analysis code with its commit.

### SHOULD BEFORE PREPRINT

- [ ] Figures (F1 design schematic; F2 behavioral rates; F3 D_en/D_ur/T/H by model × cue; F4 compliance distribution) and Tables 1–8 (manuscript Results).
- [ ] Appendix: verbatim prompts (EN/UR), cue texts, judge prompt v2, rater rubric summary, missingness cascade, full confusion matrices, S1–S5.
- [ ] Translation-equivalence spot check of the chosen backend against the reference stack, on non-study sentences.
- [ ] Data dictionary for record fields (including the `population_role` erratum).
- [ ] Wall-clock and resource summary for the generation, translation and judge stages (operational, non-scientific).

### CAN WAIT FOR SUBMISSION VERSION

- [ ] Paraphrase control and English human anchor, if option (a) of D-PG-3 is later chosen. Any such analysis is exploratory if specified after D/T outputs are seen.
- [ ] Backup-translator robustness (NLLB) and back-translation diagnostic.
- [ ] Venue formatting, camera-ready figures, extended related-work section.
- [ ] Full public release with archival DOI.

## 10. Fastest credible path to preprint

**Critical path:** ORPI → recruitment → 312 × 2 annotations → adjudication → analysis.
Everything automated can finish while human work is pending, provided its outputs stay
**sealed** from anyone who rates.

**Can start now, in parallel (none depends on another):**

1. **Send the ORPI inquiry today.** The text is ready in the Claude-side
   `research/ETHICS_ORPI_CLASSIFICATION.md` §4b. In parallel, identify candidate rater 2
   and the adjudicator. Recruit or onboard no one until the determination arrives.
2. Approve D-PG-1 to D-PG-6 and the interpretation framework, then commit them
   (governance and timestamp).
3. Judge prompt v2: draft from the rater package, hash it, re-run the 40-fixture gate.
4. Translator freeze: approve the IndicTrans2 block (including segmentation), install,
   pin hashes, and run the equivalence spot check on non-study text.
5. Analysis pipeline: fix the Cue-A/B pooling, add the paired bootstrap and missingness
   cascade, freeze it, and validate it on synthetic data.
6. Provenance errata and a code-state commit (on approval).
7. Manuscript: finalize Methods, re-verify citations, build figure and table templates.

**Order:**

1. Approve and commit the governance artifacts (framework, D-PG-1 to D-PG-6, errata). **Day 0.**
2. Send ORPI. **Day 0.**
3. Implement judge v2, run the fixture gate, freeze the hash.
4. **Run D_en + D_ur judging (1,871 calls) as soon as v2 is frozen.** Translation is not
   needed for this. Seal the outputs.
5. Freeze the translator, translate 935, freeze the translation hashes. **Run T judging
   (935 calls).** Seal the outputs.
6. **After the ORPI determination:** consent, qualification check, onboarding on non-study
   practice items, double annotation of 312, adjudication, κ.
7. Translation-artifact audit on the R primary sample. It can run alongside step 6 using a
   different bilingual reviewer, or after rating if the same person rates, so that rating
   is not contaminated by seeing translations.
8. Freeze the analysis code, then unseal and run the full planned analysis once.
9. Fill the Results slots, select the Discussion branch(es) by framework rules, run the
   claim audit.
10. Internal review, then preprint.

**Do not trade away for speed:** human double annotation and adjudication of all 312 (the
12-block contingency is only for genuine capacity failure and must be date-fixed before
annotation begins); judge prompt v2; sealing; reporting every planned comparison.

## Project-completion estimate (reasoning, not a measurement)

The estimate is about **50% (range 45–55%) of the work to a credible preprint**. Weights
reflect effort and risk, not hours:

| Component | Weight | Done |
|---|---|---|
| Design, governance, native item/cue review | 25 | ~24 (signed cue blocks and errata outstanding) |
| Generation | 20 | 20 |
| Judging (incl. prompt v2 + fixture gate) | 10 | ~1 (format harness only) |
| Translation (+ audit) | 10 | ~1 (adapter only) |
| Human reference (ORPI → κ) | 20 | ~2 (rater package only) |
| Analysis | 7 | ~1 (code exists, nonconformant) |
| Writing + claim audit + package | 8 | ~3 (this pass) |

Total ≈ 52. The remaining half sits mostly on the human-reference critical path, whose
duration depends on the ORPI response and rater availability. Neither can be estimated
from the repository.

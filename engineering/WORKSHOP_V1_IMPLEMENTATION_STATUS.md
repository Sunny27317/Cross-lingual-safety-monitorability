# Workshop-v1 implementation status

**Updated 2026-09-21 (implementation-freeze session).** No Workshop-v1 scientific
outcome exists. No model was run against real (OpenBookQA/UrduBench) items, no judge
was run against a real trace, no translator call was made, and no human annotation was
collected. Two real model artifacts were downloaded/verified for **engineering smoke
testing only** (see §"Real artifacts" below); every prompt used against them this
session was a trivial, clearly non-scientific string.

## Real artifacts (this session)

| Artifact | Status | Detail |
|---|---|---|
| `Qwen/Qwen3-1.7B` (Model A) | Already present, re-verified | `/Users/sullah1/models/clsm/Qwen3-1.7B/Qwen3-1.7B-Q8_0.gguf`, SHA-256 `061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a` (unchanged from the existing pin; byte-identical). |
| `google/gemma-3-4b-it` (Model B) | **BLOCKED — not downloaded** | The exact frozen artifact, `google/gemma-3-4b-it-qat-q4_0-gguf` / `gemma-3-4b-it-q4_0.gguf`, is a **gated** Hugging Face repository (HTTP 401 without an accepted-license, authenticated request; verified via a direct HEAD/GET this session). No `HF_TOKEN` or equivalent credential exists in this environment (confirmed present/absent check, no values inspected). Per instruction, **no alternate Gemma quantization or mirror was substituted.** This is a human decision, not an engineering one: either the investigator creates a free Hugging Face account, accepts Google's Gemma license, and supplies a token, or explicitly authorizes a named alternate source (e.g. a specific community GGUF mirror) as a new, dated decision. |
| `tiiuae/Falcon-H1-7B-Instruct` (primary judge) | **Downloaded and verified** | `Falcon-H1-7B-Instruct-Q4_K_M.gguf` from the **official** `tiiuae/Falcon-H1-7B-Instruct-GGUF` repository (not gated; confirmed via the HF API: `"gated": false`), repo commit `058c8c8f08e57da131ba5f070f9ff1280d141c39`. Saved to `/Users/sullah1/models/clsm/Falcon-H1-7B-Instruct/Falcon-H1-7B-Instruct-Q4_K_M.gguf`. Size 4,598,344,960 bytes (matches the HF-reported `x-linked-size` exactly). **SHA-256 (computed locally, not invented):** `145def0b4cd36500bf538ed7ac895b5c1851e02e802b2d1c12ffa6afdbaff25d`. Downloaded 2026-09-21T00:34–00:43 UTC (approximate, from local file timestamps). License: TII Falcon-LLM License 2.0 (Apache-2.0-based with an added acceptable-use policy, `https://falconllm.tii.ae/falcon-terms-and-conditions.html`). |

## Falcon-H1 llama.cpp compatibility — the prior session's remaining execution blocker

**RESOLVED, with real evidence.** The pinned runtime (`/Users/sullah1/tools/llama.cpp/build/bin/llama-cli`, `v0.4.0-dev`, build 10809, commit `5266f24da`) was invoked directly against the real downloaded Falcon-H1-7B-Instruct GGUF with three trivial, non-scientific prompts:

1. `"Say OK."` — model loaded, produced `"OK"`. **Load + basic inference: PASS.**
2. A structured-classification prompt ("Classify the following text as either DISCLOSED or NOT_DISCLOSED... ") — the model returned exactly `"DISCLOSED"`, a well-formed single-label response. **Structured classification: PASS.**
3. An Urdu-language prompt (asking, in Urdu, for Pakistan's capital) — the model returned a fluent, correctly-encoded Urdu sentence (`پاکستان کا دارالحکومت اسلام آباد ہے۔`, "Pakistan's capital is Islamabad") with no encoding corruption. **Urdu passthrough: PASS.**

None of these three prompts is scientific data; none touches OpenBookQA, the frozen cue text, or any real study item. **FALCON LOAD TEST: PASS.**

## Gemma-3 smoke test (Phase 3) — BLOCKED, not FAIL

Cannot be attempted: no Gemma weights are available under the current credential-free
environment (see the artifacts table above). This is reported as **BLOCKED** (access
prerequisite unmet), not **FAIL** (a load/inference attempt that did not work) — no
attempt was made against a Gemma binary at all.

## DONE (this session, additive to the existing scaffold)

- **`cue_rule.py`** — the frozen misleading-target-selection rule
  (`literature/DECISION_LOG.md` D-017) reused verbatim as a pure function, plus the
  frozen Cue-B 30% subset selection rule
  (`research/WORKSHOP_V1_SELECTION_RECOMMENDATION.md`). Both are deterministic,
  outcome-free, and structurally incapable of consulting a model output (tested).
- **`prompt_contract.py`** — the exact frozen Control/Cue A/Cue B text (English and
  Urdu, transcribed verbatim from `research/WORKSHOP_V1_SELECTION_RECOMMENDATION.md`,
  not reworded) and the authoritative D5 prompted-rationale clause for Qwen3 and
  Gemma-3, assembled into the frozen prompt structure.
- **`output_parsing.py`** — model-specific visible-reasoning-trace/final-answer
  parsers reporting one shared status vocabulary (`PARSE_OK` / `NO_VISIBLE_TRACE` /
  `NO_FINAL_ANSWER` / `INVALID_OPTION` / `RUNTIME_ERROR`), plus separate
  language-compliance, refusal, and truncation fields (never conflated with parse
  status). Historical D1 records retain the Qwen `<think>` extractor path; the
  authoritative D5 Qwen path uses the prompted-rationale splitter on the frozen
  `"Final answer: X"` marker, as Gemma does.
- **`openbookqa_adapter.py`** — turns one aligned English/Urdu OpenBookQA-schema row
  into a `SourceItem` (model-facing text only) plus a separate `TaskMetadata` (answer
  key, per-cue misleading letter) — resolving the engineering-plan's own flagged gap
  ("the generic serialized-text schema does not provide these task-specific semantics
  by itself"). Never fetches, caches, or embeds real dataset content; operates only on
  caller-supplied rows. Equivalence status defaults to `"pending"`, never `"accepted"`,
  until this project's own native-equivalence-review sign-off is recorded explicitly.
- **`llamacpp_generation.py`** — reuses Track-A's already fail-closed runtime-identity
  verification (`verify_runtime_identity`) and argv construction (`build_argv`)
  unchanged; adds a Workshop-v1-owned invocation/parse path that does **not** require
  Track-A's `RunToken` (Workshop-v1 has its own `Study`/`preflight` authorization
  layer). `smoke_test()` is the function actually used for the Falcon/Gemma checks
  above — it verifies runtime identity before ever invoking the model.
- **`synthetic_adapter_e2e.py`** — a labeled, `synthetic-`-namespaced end-to-end
  exercise of the REAL prompt contract and REAL parsers (not the older generic
  transport-marker passthrough) across 2 fake items × 2 models × 2 languages × 3
  conditions = 24 cells, with a deterministic fake backend shaped like each model's
  real output convention. Verifies pairing completeness, prompt-hash integrity,
  per-model trace-extraction behavior (D5 prompted rationale for Qwen and Gemma), and
  language-compliance measurement — all on data the label makes unmistakably synthetic.
- 52 new tests (5 new test files), all passing; full repository suite: **589 passed**
  (was 537 before this session), Python 3.11.16, `PYTHONPATH=".:src"` (the same
  pre-existing pytest-path workaround noted in the prior scientific-freeze audit — not
  introduced or fixed by this session, out of scope). New-code Ruff and targeted strict
  mypy (`--follow-imports=silent`) both pass with zero findings on every new file.
  Repository-wide Ruff retains exactly the same 5 pre-existing, untouched diagnostics
  in `experiments/M1-Mac-Feasibility/run_feasibility.py` noted by the prior audit — not
  fixed here (out of scope; not this session's code).

## PARTIAL

- The strict `Study`/`configs/workshop_v1/*.yaml` contracts from the prior scaffold are
  unchanged and **not yet populated with the exact frozen Workshop-v1 values** (model
  specs, cue specs, dataset spec, monitoring specs). This was deliberately not done
  this session: `ModelSpec` requires a real `checkpoint_hash`/`revision` for **both**
  active model families before the `Study` can reach `status: frozen`
  (`Study.generation_blockers()` already enforces "exactly two active model families"
  with real specs) — Model B's real identity does not exist yet (blocked, above). Wiring
  Model A's real values into `models.yaml` alone would leave the `Study` in a
  half-frozen state that is more confusing than informative; better to wire both real
  model specs at once once Gemma is unblocked.
- The dataset adapter (`openbookqa_adapter.py`) is implemented and unit-tested against
  synthetic fixture rows only — it has **not** been exercised against a real fetch of
  `allenai/openbookqa` + `large-traversaal/openbookqa_urdu_final` this session (no
  `datasets`/`huggingface_hub` package is installed in this environment, and doing so
  was judged out of scope for an engineering-freeze session already carrying two large
  model downloads). This is a real, named gap, not a silent one.
- `synthetic_adapter_e2e.py` exercises the real prompt/parser code but still uses a
  deterministic **fake** generation backend, not `llamacpp_generation.smoke_test()`
  itself, for the 24-cell grid — the real-runtime smoke test (Falcon, and Qwen already
  proven by the existing pilot) is validated separately, above, on trivial prompts, not
  fused into the 24-cell synthetic grid. Fusing the two was judged unnecessary
  complexity for this session (Codex's own prior audit already warns against building
  more framework than the minimal design needs).

## BLOCKED

- **Model B (Gemma-3-4B-it) download** — gated HF repository, no credential available
  in this environment. `HUMAN DECISION REQUIRED`: obtain a token (accept the Gemma
  license) or authorize a named alternate source.
- **Gemma-3 runtime smoke test** — blocked on the above.
- **Real dataset fetch/validation** against the actual `large-traversaal/
  openbookqa_urdu_final` schema — not attempted this session (see PARTIAL, above).
- **Every scientific stage** (generation on real items, judge calibration, real
  translation, human annotation, analysis) — unchanged from the prior audit: no
  executor is authorized to run against real items, and none of the still-open
  scientific decisions (final N, SESOI/alpha/power, ethics/IRB, rater identities) has
  been resolved by this or any prior engineering session.

## HUMAN DECISION REQUIRED

- Resolve the Gemma-3 gated-repository access question (credential vs. named alternate
  source) before Model B can be downloaded, hashed, or smoke-tested.
- Authorize (or decline) a real, small fetch of `allenai/openbookqa` +
  `large-traversaal/openbookqa_urdu_final` metadata to validate the dataset adapter
  against the actual live schema, beyond synthetic fixtures.
- All prior human-decision items (final N, SESOI/alpha/power, ethics/IRB, judge
  numeric acceptance criteria, rater identities, translator final lock) remain
  unresolved and are unchanged by this session.

## Pipeline completion phase (2026-09-21)

### READY

- Live dataset schema inspection confirms `large-traversaal/openbookqa_urdu_final`
  exposes `id`, `question_stem`, `choices`, `urdu_question_stem`, `urdu_choices`,
  and `answerKey`; the viewer reports train/dev/test splits and four answer classes.
  `dataset_validation.py` validates these fields from a caller supplied stream and
  returns IDs/hashes/counts only. No dataset text was written to this repository.
- Deterministic ID-only pilot/main/Cue-B partitioning is available: pilot is
  configurable, main is 120, and Cue-B is 36 selected from main without replacement.
- Synthetic-only annotation exchange, strict judge-format parsing, source-item cluster
  bootstrap summaries, publication table/figure contracts, append-only checkpoints,
  and runtime call-count arithmetic are implemented.
- IndicTrans2 adapter contract is available for the official `ai4bharat/indictrans2-indic-en-1B`
  model, with Urdu `urd_Arab` to English `eng_Latn`,
  batching, injectable fake backend, and frozen-revision requirement.

### BLOCKED

- Gemma remains blocked by the official gated repository. `gemma_download.py` refuses
  unauthenticated or non-explicit downloads and accepts only the exact repository,
  filename, and immutable revision. No download was attempted in this phase.
- A complete frozen dataset snapshot and project-level Urdu-equivalence acceptance
  manifest remain uncreated; these are required before scientific generation.
- No scientific judge, translation, human annotation, generation, or analysis was run.

### HUMAN ACTION REQUIRED

- Accept Google's Gemma license and provide Hugging Face authentication privately;
  then run the exact gated download helper with the frozen revision. For example,
  after replacing the shell-local placeholder (never committing it):
  `.venv/bin/python -c 'from pathlib import Path; from clsm.workshop_v1.gemma_download import download_exact; print(download_exact(revision="<FROZEN_COMMIT>", output_dir=Path.home()/"models/clsm/Gemma-3-4B-it", allow_download=True))'` (with the private HF credential already configured in the environment).
- Freeze the IndicTrans2 revision, judge rubric/acceptance rule, annotation protocol,
  dataset revision, and population authorization before real generation.

### Machine-readable live-schema summary (metadata only)

```json
{"dataset_id":"large-traversaal/openbookqa_urdu_final","viewer_splits":["train","validation","test"],"fields":["id","question_stem","choices","urdu_question_stem","urdu_choices","answerKey"],"choice_representation":"dict(label,text), four ordered choices","answer_key_classes":4,"alignment_key":"id","content_persisted":false}
```

## Final pre-feasibility audit (2026-09-21)

- The dataset HEAD revision was obtained with `git ls-remote`: `e4186f6ba5c3395c6f5cc99e1efadd7755ed4055`.
  The HF viewer reports 5,957 total rows and three splits, but this environment could
  not resolve `huggingface.co` for direct row retrieval. Therefore split counts and all
  row-level integrity checks remain explicitly blocked; no IDs or population manifests
  were fabricated.
- The metadata-only record is `engineering/workshop_v1_dataset_summary.json`.
- `python -m clsm.workshop_v1_readiness` now reports all ten bounded readiness states
  without invoking models, translation, judges, or downloads.
- Main-record validation now requires model/dataset/prompt/cue/study/raw-output hashes,
  rejects synthetic and pilot records, and rejects mixed study hashes. Annotation
  contracts now include disagreement and adjudication validation.
- IndicTrans2 is officially identified as `ai4bharat/indictrans2-indic-en-1B` (MIT,
  Transformers/PyTorch, `urd_Arab` → `eng_Latn`), but the exact commit could not be
  obtained without authenticated access to the gated model repository; it remains a
  human-action item rather than an invented pin.

## Last offline engineering task (2026-09-21)

### READY

- `local_ingest.py` accepts a user-supplied JSON, JSONL, or Parquet snapshot plus a
  sidecar `dataset_metadata.json`; it requires repository
  `large-traversaal/openbookqa_urdu_final` and revision
  `e4186f6ba5c3395c6f5cc99e1efadd7755ed4055`, validates rows in memory, and returns
  only counts and content/ID hashes. `freeze_population_from_rows` writes IDs and
  hashes only, with the explicit label `POPULATION FREEZE — NOT AN EXPERIMENT RUN`.
- `local_artifacts.py` verifies a manually supplied exact Gemma Q4_0 GGUF (filename,
  size, SHA-256, repository/revision metadata, llama-cli presence) and a manually
  supplied IndicTrans2 directory (model/revision, tokenizer/config hashes, and
  `urd_Arab` → `eng_Latn`). No downloads or inference occur.
- The smallest proposed permanent pilot uses one pilot ID and one sample across
  2 models × 2 languages × control/Cue-A/Cue-B = **12 calls**. It is feasibility-only,
  permanently excluded from main analysis, and tests prompt rendering, parsing,
  language compliance, cue rendering, and checkpoint/resume.
- The post-access sequence is: local dataset ingest → ID-only population freeze →
  local Gemma verification and non-scientific smoke test → local IndicTrans2 identity
  verification → readiness report. It never starts the scientific experiment.

### HUMAN / NETWORK INPUT REQUIRED

- Sana must provide a local export of the exact dataset revision with a metadata sidecar
  containing `dataset_repo`, `dataset_revision`, and optional split.
- Sana must provide the exact Gemma file after accepting Google’s terms, its immutable
  repository revision, and a working local llama.cpp binary.
- Sana must provide the locally downloaded IndicTrans2 files and authenticated exact
  revision. The official model is gated; no revision was guessed.

### Final offline readiness

| Component | Status |
|---|---|
| LOCAL DATASET INGEST | READY for user-supplied exact snapshot; network fetch remains unavailable |
| LOCAL GEMMA INGEST | READY; requires human-supplied exact GGUF and revision |
| LOCAL INDIC TRANS2 INGEST | READY; requires human-supplied files and revision |
| POST-ACCESS WORKFLOW | READY and non-scientific |
| TINY PILOT CONFIG | READY: 1 permanent pilot ID × 2 models × 2 languages × 3 conditions × 1 sample = 12 calls |

## Recommended next engineering task

Once Gemma-3-4B-it is unblocked (a human decision, not an engineering one): download
and hash it exactly as Falcon was handled here (STOP-and-report discipline unchanged);
run the same three-prompt smoke test used for Falcon (load, structured task, Urdu
passthrough); then wire both real `ModelSpec`s into `configs/workshop_v1/models.yaml`
so the `Study` can progress toward `status: frozen`. Independently, a small, explicitly
scoped real-dataset-schema validation pass (fetching a handful of `large-traversaal/
openbookqa_urdu_final` rows to confirm the adapter's `AlignedRow` shape matches
production reality) is worth doing before committing to the adapter's exact field
names.

## Codex recovery checkpoint (2026-09-24)

Partial runtime, excluded-pilot, judge, fixture, and readiness implementations have been recovered and compile. The active Claude session-11 freeze is recorded in `configs/workshop_v1/judge_contract.json`; its four lowercase scientific labels remain separate from technical parse states. Next steps are targeted lint/type checks, readiness, the authorized 12-call excluded pilot only, checkpoint/resume verification, and a compact operational report. The 120-item main run, scientific judging/translation, and human annotation remain disabled.

The future machine-readable result contract uses `generation_qc.json`, `judge_qc.json`, `translation_qc.json`, `human_agreement.json`, `analysis_summary.json`, `bootstrap_intervals.json`, plus `tables/*.csv` and `figures/data/*.csv`. Each artifact must carry dataset revision, manifest hash, study hash, code HEAD, and a `data_kind`/stage marker; no result values are created in this recovery step.

## Excluded pilot checkpoint (2026-09-24)

The authorized excluded pilot completed 12/12 generator calls. All records are permanently marked `FEASIBILITY_ONLY` and are structurally excluded from main analysis. Qwen completed all six calls but produced noncompliant Urdu language output on three; Gemma completed all six with compliant language. Runtime completion, prompt rendering, exact boundary separation, visible trace presence, final-answer parsing, and truncation checks passed for the completed records. A second invocation attempted zero calls and skipped all 12 successful records with the unchanged study hash, demonstrating resume behavior.

Operational totals were approximately 215.86 seconds for Qwen (35.98 seconds/call) and 60.40 seconds for Gemma (10.07 seconds/call); llama.cpp did not expose reliable generated-token or tokens/sec metrics in these records. Peak RSS observed was about 5.73 GB for Qwen and 3.66 GB for Gemma. A rough linear 3312-call planning estimate from these per-call means is approximately 25.6 hours for Qwen, 9.3 hours for Gemma, or 34.9 hours combined; one-item timing is noisy and may change with thermal throttling, batching, or cache behavior.

The 40 non-study Falcon format fixtures completed (20 English, 20 Urdu; empty traces withheld) but produced `MALFORMED_OUTPUT` for all calls because the runtime emitted uppercase labels while the frozen session-11 contract requires exact lowercase labels. This is a judge-stage technical FAIL and does not block generator readiness; no study trace was judged and no scientific label was produced.

Arithmetic checkpoint: expected human candidate pool is 120×2 + 36×2 = 312 Urdu traces. The frozen k=3 design implies 936 Urdu generation traces and therefore 936 translation calls; direct and translated judge passes imply 936 + 936 = 1,872 judge calls. The prior ≈2,808 estimate counts an additional 936 judge pass not represented by the current direct/translated routing and is not adopted without a frozen design update. Historical SESOI, alpha, power, multiplicity, and formal judge-accuracy gates are superseded or not applicable to this descriptive Workshop-v1 generator stage; source provenance remains intact.

## Diagnostic audit checkpoint (2026-09-24)

The frozen design explicitly includes three automated judge populations: English direct baseline, Urdu direct, and Urdu translated to English. With 2 models × (120 Cue-A + 36 Cue-B) × 3 samples, each population is 936 calls: 936 English direct + 936 Urdu direct + 936 translated Urdu = 2,808 total judge calls. The repository contains lineage schemas for all four H/D/T/English paths but no real judge scheduler; the earlier 1,872 arithmetic omitted the English direct population and is a planning bug, not a frozen-design choice.

The three preserved Qwen Urdu pilot records had successful runtime, intact Unicode, visible traces, parseable final answers, and correct prompt hashes. Control and Cue-B traces were English-script outputs; Cue-A was mixed script but below the Urdu compliance threshold. All final answer markers were present as Latin option tokens. This is model language noncompliance, not a checker, prompt-rendering, Unicode, or chat-template failure. The frozen prompt already contains `اردو میں جواب دیں۔`; adding stronger wording or changing decoding would require scientific approval.

The 40 synthetic Falcon outputs each had one evidence line and one uppercase canonical label, with no extra-label or missing-label pattern. The exact frozen technical rule currently forbids case folding, so normalization requires governance approval; no parser change was applied. Main-generation blockers remain native Urdu cue-equivalence review, Urdu item-equivalence spot-check or prospective deferral/exclusion, recorded pilot disposition including Qwen compliance, the prepared launch manifest, and explicit human authorization. ORPI is a later human-annotation gate unless governance updates that ordering.

## Planning checkpoint (2026-09-25)

Added the non-executing `judge_plan` planner. Its dry run validates 936 English-direct, 936 Urdu-direct, 936 translated-Urdu, 2,808 total judge records, and 936 translation lineages with deterministic IDs, pilot exclusion, and duplicate checks. The main launch manifest is explicitly `NOT_AUTHORIZED_FOR_EXECUTION` and records expected generation 3,312, translation 936, and judge 2,808. Artifact envelope validation now covers the six JSON result families without inventing values. Readiness exposes independent main, translation, direct-judge, translated-judge, human, and analysis stages plus pending governance blockers.

## Session-12 amendment checkpoint (2026-09-27)

The approved Falcon parser amendment is implemented as exact ASCII case-insensitive matching of the stripped LABEL value only. Raw output and raw label text remain preserved; parser version `workshop-judge-parser-v2-case-normalization/1` is included in the judge specification hash. Existing immutable synthetic fixture files were not regenerated; deterministic re-parsing now yields 20/20 valid English and 20/20 valid Urdu format labels.

The approved language-control sentence is integrated for both models, both languages, and all conditions before the question. English and Urdu are native-reviewed and frozen. Amended pilot v2 has a separate immutable namespace; the original pilot remains unchanged and excluded.

The human pool contract now deterministically plans all 312 candidates (240 Cue-A, 72 Cue-B), never filters by language compliance, and records the fixed 12-block capacity contingency without executing annotation. Readiness distinguishes engineering support from scientific authorization and exposes native-language review, cue/item equivalence, human authorization, and Falcon normalization governance blockers.

Validation after the session-12 amendments: 670 tests passed, Ruff PASS, mypy PASS, and `git diff --check` PASS. Falcon format reparse is 20/20 English and 20/20 Urdu. The amended pilot v2 was subsequently run under session-14 authorization and is recorded below; no main generation, translation, scientific judging, or annotation occurred.

## Session-14 technical readiness update

Claude session-14 explicitly authorized the native-reviewed amended 12-call pilot. It
was run once through the real pinned llama.cpp harness in the immutable
`experiments/_runs/workshop-v1-excluded-feasibility-v2/` namespace. All 12 calls
completed and resume immediately skipped all 12 successful records. Gemma passed the
fixed language thresholds; Qwen had 0/3 Urdu-script-compliant calls, so the frozen
outcome is `FAIL_STOP` and no second wording attempt is allowed. Raw outputs and QC
are preserved in `pilot_qc.json` (QC SHA-256
`aa57ba8a6b8de40a8806ae20391f960d9abe5aabbf0c300e7d485b590cbc55ef`); the original
pilot remains untouched and excluded.

The main generation executor boundary is now implemented fail-closed, with no bypass;
translator and judge boundaries are explicit but do not execute without their frozen
backend/revision and authorization. Main preflight includes pilot PASS, executor,
Amna packet, frozen-input, output-safety, and authorization gates. Workload remains
3312 generation + 936 translation + 2808 judge calls. No main, translation, scientific
judge, or human annotation data were generated.

## D5 governance closure

The original native-thinking Qwen Urdu pilot `FAIL_STOP` and the first D5 TCP-bind
failure (zero scientific outputs) remain immutable historical evidence. D5 was the
prospectively frozen Option-B amendment; after investigator authorization from an
unrestricted environment, its unchanged six-call run completed with all P1-P9 checks
and language criteria passing. D5 study hash:
`d3af8414fa4be82565d04ebf4bdf9323421a2135a762702728e3aaaad002c014`.

D5 prompted/non-thinking Qwen is authoritative going forward: `enable_thinking=false`,
no forced `<think>`, the exact frozen prompted-rationale sentence, D5 decoding
(temperature 0.7, top-p 0.8, top-k 20, min-p 0), and reasoning extraction before
`Final answer:`. The amended-pilot gate is CLOSED/PASSED, while main generation
remains explicitly unauthorized.

## Comprehensive pre-main engineering sprint

The formal Amna packet and investigator-recorded telephone clarification are now
ingested; the item-equivalence gate is closed. The ingester now
validates all 120 IDs, Cue-B membership, dataset/manifest/source-row hashes,
reviewer/date metadata, allowed statuses, and required notes, with synthetic failure
fixtures. `workload.py` deterministically plans 3,312 generation tasks (1,656 per
model), 936 translations, 2,808 judge calls, and 312 human candidates. The synthetic
rehearsal validates these counts and lineage without model/service calls.

IndicTrans2 remains blocked on an investigator-selected exact checkpoint/revision,
backend, preprocessing/postprocessing, decoding, and runtime provenance. Judge format
and planning are ready but no scientific judge call is authorized. Human export/import
is blinded and deterministic but no annotation has occurred. The main executor now
checks final study hash, authorization-file hash, exact count, output safety, and pilot
exclusion before any future backend call; its scientific backend remains disabled.

Validation after this sprint: 679 tests collected and passed, Ruff PASS, mypy PASS,
and `git diff --check` PASS. Main preflight remains false.

## Formal Amna artifact closure update (2026-10-01)

The supplied PDF is archived unchanged at
`engineering/provenance/URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.pdf` (SHA-256
`39e233e39a8fa9fede9a4dee5ae12f34f0cd79e29147cb4ed2f2c4938b94c3fc`). Its
canonical extraction is `engineering/amna_urdu_equivalence_review.json` (SHA-256
`a8e5dcce0be03b28393ab86af1cacebb6b720e5158e71badd209fec4a0f4951b`). Amna Anwar
Riaz marked the review complete on 30/09/2026. All 120 IDs, 36 Cue-B memberships,
dataset/manifest identifiers, answer keys, and frozen source-row hashes validate;
all 120 final statuses are PASS. Three rows (`11-56`, `7-700`, `13-304`) have a
blank/unselected Meaning-preserved checkbox despite PASS. Because the pre-existing
rules did not permit silently treating a blank required check as affirmative, so
the initial ingestion view was `NEEDS_REVIEWER_CLARIFICATION`; no row was altered,
excluded, replaced, or resampled.

The investigator subsequently recorded Amna's telephone clarification on
2026-10-01 in `engineering/provenance/AMNA_TELEPHONE_CLARIFICATION_2026-10-01.json`
(SHA-256 `b582f6fb686b750a6ea1fc514cf5749f66f3f26c513198e7bc1f5eab065b79ac`).
It is explicitly supplemental provenance linked to the original PDF and contains
no fabricated reviewer signature. Amna confirmed Meaning-preserved = Yes for
`11-56`, `7-700`, and `13-304`. The derived closure view is
`engineering/amna_urdu_equivalence_review_closure.json` (SHA-256
`a3e3d9582188f17276340db71df440d42a0f6044e0d7d2955de90408b1899e81`). The
item-equivalence gate is now PASS: 120 PASS, 36/36 Cue-B PASS, and zero unresolved
required checks. The original PDF and original canonical extraction remain unchanged.

Claude's proposed IndicTrans2 package is recorded for reconciliation only. The
primary/backup identities and direction agree with the repository, while exact
checkpoint/tokenizer revision, backend, reference preprocessing/postprocessing,
beam/max-length decoding, package/runtime versions, artifact hashes, and fallback
activation remain unverified or investigator decisions. No scientific translation
was performed; see `engineering/indictrans2_reconciliation.json`.

## Raw-generation boundary (2026-10-01)

The generation-only hash is
`7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec` and is
recorded in `engineering/workshop_v1_generation_config.json`. It covers the
frozen input manifests, model/config/prompt hashes, D5 Qwen configuration, pilot
exclusion, and 3,312-task workload. IndicTrans2, Falcon judging, human/ORPI/rater
requirements, compliance-floor analysis, and the final whole-study hash are
downstream gates; they do not affect raw generation inputs. The new main output
directory `experiments/_runs/workshop-v1-main` is empty. The main executor remains
fail-closed and no investigator authorization file exists.

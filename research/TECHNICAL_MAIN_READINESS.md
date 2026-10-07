# Workshop-v1 Technical Main Readiness

Status: engineering preparation only. Main generation is fail-closed and has not run.

Latest validation: 670 tests passed, Ruff PASS, mypy PASS, and `git diff --check`
PASS. The original native-thinking pilot and its `FAIL_STOP` remain historical
evidence. The later prospectively frozen D5 Option-B amendment passed and is also
permanently excluded from all main-study paths.

## Architecture map

`engineering/workshop_v1_dataset_summary.json` and the frozen Parquet snapshot are validated by `src/clsm/workshop_v1/frozen_validation.py`; the ID-only manifests are checked before any run. `prompt_contract.py` renders language, condition, question/options, and final-answer instructions. `config.py` loads model/condition/study specifications. `local_runtime.py` and `llamacpp_generation.py` are the pinned llama.cpp adapter path; `output_parsing.py` extracts Qwen/Gemma traces and answers. `runner.py` is an append-only provenance/checkpoint primitive, while `excluded_pilot.py` is the only real-generation executor and is permanently pilot-scoped. `monitoring.py`, `translation.py`, and `judge.py` provide lineage/parser contracts; `judge_plan.py` creates a non-executing 2,808-call plan. `analysis.py`, `tables.py`, and downstream reporting provide aggregation/table contracts. `dry_run.py` exercises only synthetic transport markers. `urdu_review_ingest.py` validates the returned human packet without choosing exclusions. The complete synthetic transport dry run was verified at `/tmp/synthetic-workshop-v1-dry-run`: 24 fixture generations, routing, translation markers, hashes, and manifest were written as synthetic-only with scientific outcomes not run.

## Frozen-input verification

`validate_frozen_inputs` fails closed on manifest hashes, dataset repository/revision, 120 unique main IDs, 36 unique Cue-B IDs, Cue-B containment, pilot separation, local source-row hashes, split bindings, A–D option ordering, valid answer keys, and deterministic selection metadata. Current verification passes for revision `e4186f6ba5c3395c6f5cc99e1efadd7755ed4055`.

## Readiness and gates

Run:

```bash
source .venv/bin/activate
PYTHONPATH=src python3.11 -m clsm.workshop_v1_main_preflight --root /Users/sullah1/clsm-codex
```

The command reports `MAIN_GENERATION_READY: false` while the Amna packet is missing/incomplete or native governance is unresolved. It also checks model artifacts/runtime paths, prompt-contract presence, disk space, output collision risk, and repository state. `main_launcher.assert_main_authorized` calls this guard and cannot bypass it. The current main launch manifest remains `NOT_AUTHORIZED_FOR_EXECUTION`.

## Model/backend audit

Qwen3-1.7B, Gemma-3-4B-it, and Falcon-H1-7B-Instruct specifications identify local artifacts, hashes, llama.cpp build/commit, decoding, context, parser, and boundary policies. The real excluded pilot verified Qwen/Gemma runtime behavior; its outputs remain excluded. `dry_run.py` and synthetic fixtures are mock-only and never evidence real model behavior. The main executor boundary is implemented fail-closed; translator and scientific judge executors remain downstream interfaces. Missing/blocked external requirements are translator authorization/artifact, judge-stage authorization, and human protocol/authorization.

Known architecture boundaries: `monitoring.py` and `translation.py` are contracts/adapters, not schedulers; the translation adapter requires an exact external revision before use. `configs/workshop_v1/monitoring.yaml` intentionally leaves scientific services unresolved. `src/clsm/workshop_v1_preflight.py` is a legacy stage-specific review check that always exits nonzero and is not an execution credential; `workshop_v1_main_preflight.py` is the new integrated fail-closed check. The Metal runtime is not bitwise deterministic, so seed/decoding/config/runtime hashes are recorded while byte-identical outputs are not assumed. No mock path is allowed to satisfy a real model check.

## Human review ingestion

`urdu_review_ingest.py` validates exactly 120 unique expected IDs, no missing/unexpected/duplicate IDs, exact Cue-B membership, reviewer/date fields, and only `PASS`, `MINOR_LANGUAGE_ONLY`, `MATERIAL_MISMATCH`, or `UNCERTAIN`. It preserves notes and flags material/uncertain outcomes for investigator governance. It never automatically excludes, replaces, or resamples an item. The fixed 312-candidate human pool contract and capacity-block order are implemented separately in `human_pool.py` and are not executed.

## Reproducibility and recovery

Planned records carry item/model/language/condition/sample, prompt/cue/study/config hashes, raw output, parsed output, runtime/error/retry metadata, and source lineage. Append-only checkpoint helpers reject duplicate IDs and mixed study hashes. The dry-run planner validates 936 English direct + 936 Urdu direct + 936 translated Urdu = 2,808 judge calls and 936 translations without model/translator execution. Synthetic dry runs write only explicitly marked synthetic artifacts. Resume behavior skips immutable successes, retries only permitted infrastructure failures, and rejects changed hashes.

## Current blockers

- 120-item Urdu equivalence review has not been returned/ingested.
- Any `MATERIAL_MISMATCH` or `UNCERTAIN` result requires a separately frozen, outcome-blind governance decision; no automatic replacement exists.
- The exact IndicTrans2 checkpoint/revision, backend, preprocessing/postprocessing,
  and runtime provenance remain unresolved; no scientific translation can run.
- The scientific main executor remains deliberately disabled; a final executable
  study/config hash and explicit main authorization are still required.
- Human protocol/ORPI/rater authorization remains downstream.
- The judge format contract is hashed and its synthetic format gate passes, but no
  scientific judge execution is authorized or has occurred.

## Session-14 amended pilot and executor boundaries

The session-14 D1 record authorized the native-reviewed amended pilot independently
of the 120-item review. It was executed exactly once as 12 real local llama.cpp
calls under `experiments/_runs/workshop-v1-excluded-feasibility-v2/`. All calls
completed with preserved raw output, separated completion, visible-trace and final
answer parsing, and immutable checkpoints. Gemma met the fixed English/Urdu
language thresholds; Qwen met English but had 0/3 Urdu calls at the required
Urdu-script threshold. The immutable historical technical outcome is `FAIL_STOP` in
`pilot_qc.json`; no second wording attempt or main call is permitted.

`scientific_executor.py` is the fail-closed main executor boundary: it calls the
integrated preflight before any main operation and has no bypass. The translator
boundary is implemented but IndicTrans2 revision/backend remain unresolved in the
frozen configuration, so it cannot execute. The judge boundary delegates to the
frozen Falcon parser/retry contract only when an explicit backend is supplied; no
scientific judge calls have occurred. The synthetic end-to-end rehearsal remains
the only full-pipeline rehearsal and is explicitly labeled non-scientific.

Frozen workload planning remains: 3,312 generation calls (2 models × 2 languages ×
3 conditions × 120 items × 3 samples), 936 Urdu-to-English translation calls, and
2,808 judge calls (936 English direct + 936 Urdu direct + 936 translated Urdu).
The measured pilot wall time was 254.4 s for Qwen and 78.3 s for Gemma across six
calls each; these are operational observations only and are not a scientific result.
The main preflight now also requires a PASS pilot, an enabled scientific executor,
and the returned 120-item packet, in addition to all frozen-input and authorization
checks.

Using a simple serial linear extrapolation from those six-call-per-model samples,
the 1,656 planned calls per model would be approximately 19.5 hours for Qwen and
6.0 hours for Gemma (about 25.5 hours combined). This is a rough operational estimate
from a one-item pilot; thermal throttling, batching, cache behavior, and failures may
change it materially.

## D5 Qwen Option-B repilot status

The dated D5 decision authorized exactly six Qwen-only calls using the same excluded
pilot item. The Codex harness reconciled item `9-74`, source-row hash, hint seed
`20260921`, target letters (Cue A=`D`, Cue B=`A`), Qwen artifact hash
`061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`, embedded chat
template path, output schema, frozen prompted-rationale wording, decoding, and all six
render-only prompt hashes. The original port failure remains preserved unchanged in
`experiments/_runs/workshop-v1-excluded-feasibility-d5/`.

The investigator then executed the same frozen D5 runner once from a normal Terminal:
all six calls completed, all six raw outputs and parsed records were preserved, all
six technical parses succeeded, all three English reasoning spans scored 1.000 Latin
script, and the Urdu spans scored 0.977011, 0.905172, and 0.953917 Urdu script.
The frozen thresholds therefore passed (English 3/3; Urdu 3/3), and the D5 technical
classification is `PASS`. This remains a permanently excluded feasibility artifact;
it does not authorize main generation, translation, judging, or human annotation.
Evidence is immutable under
`experiments/_runs/workshop-v1-excluded-feasibility-d5-rerun/`, with study hash
`d3af8414fa4be82565d04ebf4bdf9323421a2135a762702728e3aaaad002c014`.

## IndicTrans2 translator readiness audit

The pre-existing freeze names `ai4bharat/indictrans2-indic-en-1B` as the primary
translator (AI4Bharat IndicTrans2 family, MIT license) and
`facebook/nllb-200-distilled-600M` as the backup. Urdu-to-English is the frozen
direction with language codes `urd_Arab` → `eng_Latn`. The design requires translating
all Urdu cued traces by hash, recording failures per trace, and auditing translation
artifacts before translated judging.

The exact IndicTrans2 checkpoint/revision, serving backend (Transformers/PyTorch,
CTranslate2, or another compatible backend), tokenizer files, inference decoding
settings, preprocessing, postprocessing, batching policy beyond the adapter default,
and runtime/resource pin are not frozen in the pre-failure records. The repository
adapter therefore rejects the placeholder revision and has no silent fallback. The
current environment has no IndicTrans2, Transformers, PyTorch, or CTranslate2
installation and no local IndicTrans2 artifact. The synthetic adapter path is tested
with an injected backend and validates batch length, Urdu/English codes, and nonempty
Unicode output; it performs no translation inference.

The frozen translation workload is independently verified by the non-executing judge
planner: 2 models × (120 Cue-A + 36 Cue-B) × 3 samples = **936** Urdu cued traces.
Only Urdu Cue-A/Cue-B traces enter this path; Control, English, pilot IDs, and
duplicates are rejected by the planner. Making the executor reproducibly runnable
requires one new investigator decision: select and record the exact IndicTrans2
checkpoint/revision and serving backend, plus preprocessing/postprocessing and
decoding/batching settings, then supply the corresponding local artifact hashes and
runtime provenance. No scientific translation has been performed.

The follow-up D5 port audit found the failure occurred before inference: this
environment denies TCP bind with `EPERM` even for synthetic binds to port 0, matching
llama.cpp's embedded-server allocator. No stale llama process, fixed-port collision,
PID file, or Workshop server state was found. The original D5 failure remains
unchanged; its runner refuses automatic retry. A future approved rerun requires an
environment that permits loopback/ephemeral socket binding and the unchanged D5
protocol. Details are in `research/D5_PORT_FAILURE_FORENSIC_AUDIT.md`.

### Investigator-terminal D5 rerun procedure

The restricted Codex sandbox cannot bind the loopback socket required by the pinned
llama.cpp server. The frozen runner is ready for execution from a normal macOS
Terminal only. It defaults to the new immutable destination
`experiments/_runs/workshop-v1-excluded-feasibility-d5-rerun`, preserving the original
failed evidence. Run the socket check first:

```sh
cd /Users/sullah1/clsm-codex
source .venv/bin/activate
python3.11 - <<'PY'
import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.listen(1)
    print(f"SOCKET_BIND_PASS host=127.0.0.1 port={port}")
except OSError as exc:
    print(f"SOCKET_BIND_FAIL errno={exc.errno} error={exc}", file=sys.stderr)
    raise SystemExit(1)
finally:
    s.close()
PY
```

Then render and validate all six prompts without model execution:

```sh
cd /Users/sullah1/clsm-codex
source .venv/bin/activate
export CLSM_D5_OUTPUT=experiments/_runs/workshop-v1-excluded-feasibility-d5-rerun
PYTHONPATH=src python3.11 -m clsm.workshop_v1.d5_repilot --preflight
```

The expected pre-execution output is JSON containing `D5_PREFLIGHT: PASS`,
`pilot_item_id: 9-74`, `hint_seed: 20260921`, `target_letters: {cue_a: D, cue_b: A}`,
`expected_calls: 6`, `prompt_hash_count: 6`, and `render_only_pass: true`. Stop if
any of those values differ. Only after that check passes may the investigator run:

```sh
cd /Users/sullah1/clsm-codex
source .venv/bin/activate
export CLSM_D5_OUTPUT=experiments/_runs/workshop-v1-excluded-feasibility-d5-rerun
PYTHONPATH=src python3.11 -m clsm.workshop_v1.d5_repilot --execute
```

The runner is hard-limited to six calls, has no main-generation path, writes an
immutable execution manifest and per-call records, and stops on the first runtime
failure. It refuses to run when the output directory already exists and refuses any
retry after a recorded runtime failure, so repeating the command cannot silently
create another D5 run. Do not delete or reuse an existing D5 output directory.

### D5 governance closure

D5 was a prospectively frozen Option-B amendment. Its first attempt produced zero
scientific outputs solely because the restricted environment denied TCP socket
binding; that immutable infrastructure failure and the earlier native-thinking Qwen
Urdu `FAIL_STOP` remain historical records. The investigator then authorized the
unchanged six-call D5 run from an unrestricted environment. All six calls completed,
all P1-P9 checks passed, and the frozen English (3/3) and Urdu (3/3) language criteria
passed. Study hash:
`d3af8414fa4be82565d04ebf4bdf9323421a2135a762702728e3aaaad002c014`.

The authoritative Qwen configuration going forward is D5 prompted/non-thinking:
`enable_thinking=false`, no forced `<think>` prefix, the exact sentence
`Think through the question step by step in your response before giving your final
answer.`, decoding temperature 0.7, top-p 0.8, top-k 20, min-p 0, and the existing
context/output limits with natural EOT. Reasoning is extracted before the frozen
`Final answer:` marker. The amended-pilot gate is **CLOSED/PASSED**; this does not
authorize main generation.

## Comprehensive pre-main engineering sprint

Amna Anwar Riaz's formal 120-item artifact and investigator-recorded telephone
clarification are ingested; the item-equivalence gate is closed.
`urdu_review_ingest.py` now fails closed on the exact 120 IDs, Cue-B membership,
manifest/revision/source-row hashes, reviewer/date metadata, allowed statuses, and
notes for non-PASS statuses. Synthetic fixtures cover missing, duplicate, unexpected,
Cue-B, hash, metadata, and governance-action cases.

The non-executing workload planner (`workload.py`) verifies 3,312 generation tasks,
936 Urdu Cue-A/Cue-B translation tasks, 2,808 judge tasks, and 312 human candidates;
all identifiers are deterministic and text-free. The IndicTrans2 adapter remains
explicitly unresolved: model family and direction are frozen, but exact checkpoint,
backend, tokenizer/procedure, decoding, and runtime provenance require an investigator
decision. The judge planner and format contract are technically ready and no scientific
judge calls have occurred. Human export/import tooling is deterministic and blinded;
no annotation has occurred. The main executor validates expected count, final study
hash, authorization-file hash, new output state, and pilot exclusion before any future
backend call, while the backend remains disabled.

The provisional study-hash mechanism reports `PROVISIONAL_NOT_EXECUTABLE` with hash
`2eb23e6993956c09c3e83ce72a65cedde537444e59c8e8e8301c8156ea3cebfd` until the formal
Urdu review, IndicTrans2 contract, and explicit authorization are bound. See
`engineering/WORKSHOP_V1_PRE_MAIN_CHECKLIST.md` for the current gate ledger.

Session-12 language-control review and Cue A/B native review are recorded as approved by the current governance state; the exact approved wording remains unchanged. The 120-item equivalence review is the active pre-main human gate.

## Eventual launch sequence

After the review and all governance evidence are recorded, rerun frozen-input validation, packet ingestion, model/runtime checks, full tests, and preflight. Only then may a separately authorized main executor consume the sealed 3,312-generation manifest, write immutable QC/provenance artifacts, and proceed through translation, direct/translated judging, human reference, and analysis gates. No command in this sprint launches that run.

## Formal Amna packet received (2026-10-01)

The received PDF is preserved unchanged at
`engineering/provenance/URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.pdf` with SHA-256
`39e233e39a8fa9fede9a4dee5ae12f34f0cd79e29147cb4ed2f2c4938b94c3fc`. The
outcome-blind canonical extraction is
`engineering/amna_urdu_equivalence_review.json` with SHA-256
`a8e5dcce0be03b28393ab86af1cacebb6b720e5158e71badd209fec4a0f4951b`.
Provenance validates against the frozen dataset revision, main/Cue-B hashes,
120 unique IDs, 36-item subset, answer keys, and source-row hashes. The packet
contains 120 PASS final statuses and no other final status. Three PASS rows had
the required Meaning-preserved checkbox blank/unselected in the initial
extraction: `11-56`, `7-700`, and `13-304`. The separately recorded telephone
clarification closed those fields without altering the PDF or canonical extraction.

## Translator reconciliation

The primary `ai4bharat/indictrans2-indic-en-1B`, backup
`facebook/nllb-200-distilled-600M`, direction, and language codes agree with
the prior freeze. Claude's reference Transformers + IndicTransToolkit package,
reference preprocessing/postprocessing, `num_beams=5`, and `max_length=256`
remain candidate values, not frozen values. Exact checkpoint/tokenizer revision,
backend, package/runtime versions, artifact hashes, device behavior, and fallback
activation remain unresolved or require investigator choice. No scientific
translation occurred. See `engineering/indictrans2_reconciliation.json`.

## Telephone clarification closure (2026-10-01)

The investigator recorded Amna's telephone confirmation that Meaning-preserved
is Yes for `11-56`, `7-700`, and `13-304`. This supplemental record is linked to
the unchanged PDF SHA-256 and contains no fabricated reviewer signature:
`engineering/provenance/AMNA_TELEPHONE_CLARIFICATION_2026-10-01.json`.
The derived closure view records 120 PASS, 36/36 Cue-B PASS, and no unresolved
required checks. The item-equivalence gate is PASS. This does not resolve the
translator, executor, final-hash, or authorization gates.

## Generation boundary closure (2026-10-01)

The generation-only configuration is recorded and hashed as
`7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec` in
`engineering/workshop_v1_generation_config.json`. It binds the frozen dataset,
manifests, source-row plan, Qwen D5/Gemma artifacts and configs, prompt/cue hash,
pilot exclusion, and exactly 3,312 tasks. The previous whole-study provisional
hash remains unchanged and non-executable.

IndicTrans2 is a downstream translation-monitoring dependency: it consumes
completed Urdu cued traces and does not affect raw generation inputs. Its exact
revision/backend/procedure remains required before translation, but is no longer
on the raw-generation critical path. Falcon judging, ORPI/rater/compensation,
compliance-floor analysis, and final whole-study closure are also downstream
gates. The main output directory is newly created and empty. The main executor
boundary is implemented fail-closed; no authorization file exists, so no model
call is possible.

## Authorized main-run attempt (2026-10-02)

The exact investigator authorization was recorded for generation hash
`7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec`.
The runner attempted all 3,312 frozen task IDs, but the restricted environment
failed before inference on every call with `failed to get a free port`. There
were zero generated completions, visible traces, parsed answers, or scientific
outputs. Immutable failure records remain in
`experiments/_runs/workshop-v1-main/`; no retry or downstream stage was run.
The run is classified infrastructure `FAIL_STOP` pending an unrestricted
environment and governed handling of the failed checkpoints.

## Attempt-2 persistence failure (2026-10-02)

Attempt 2 persisted 30 successful records, then stopped on Qwen Urdu Control
sample 0 for item `10-220` while hashing runtime output containing a
`surrogateescape` transport surrogate. The subprocess had returned, but the
raw output was not durably recoverable and no partial scientific record was
written. The task-level persistence failure is recorded separately under
`experiments/_runs/workshop-v1-main-attempt-2/`.

The engineering-only fix uses reversible runtime-byte hashing and ASCII JSON
escapes for surrogate-containing output; it drops or replaces no content and
does not change the generation hash, prompts, models, seeds, or task plan.
Successful records remain immutable and resume skips them. See
`research/WORKSHOP_V1_ATTEMPT_2_UNICODE_FAILURE_FORENSICS.md`.

## Post-generation QC and downstream preparation (2026-10-04)

Attempt 2 contains all 3,312 expected task IDs with no duplicates or pilot
contamination and the unchanged generation hash. There are 3,311 runtime
successful records and one persisted runtime failure (Qwen Urdu Cue-A sample 0,
item `9-1065`, a 900-second timeout); its provenance remains in the run directory.
The earlier `10-220` event was a serialization/persistence failure and its final
persisted record is runtime-successful. Final-answer
parsing succeeds for 3,182 records and fails technically for 130; no scientific
interpretation was performed. Canonical QC is recorded in
`experiments/_runs/workshop-v1-main-attempt-2/post_generation_qc.json`.

The exact 936-task translation manifest is prepared but blocked: one Urdu
source trace is not runtime-successful, and the IndicTrans2 checkpoint,
backend, preprocessing/postprocessing, decoding, and fallback contract remain
investigator decisions. Judge planning validates 936 English-direct, 936
Urdu-direct, and 936 translated-Urdu calls (2,808 total); existing synthetic
format fixtures pass, but scientific judging is unauthorized. The blinded
312-trace human packet is prepared without labels or annotation. Staged hashes
and preprint outputs remain provisional/template-only.

## Downstream governance closure (2026-10-04)

Investigator approvals D-PG-1 through D-PG-5 are recorded in
`engineering/provenance/INVESTIGATOR_DOWNSTREAM_APPROVALS_2026-10-04.json`.
Generation is locked at 3,312 structural tasks, 3,311 runtime-successful records,
and one retained missing timeout (`9-1065`); the generation hash is unchanged.
No retry is permitted. The actual eligible translation workload is 935, and the
actual eligible direct/translated judge workloads are 936 English-direct, 935
Urdu-direct, and 935 translated-Urdu (2,806 total), pending their separate
scientific authorizations.

The approved rater parity package is
`experiments/_runs/workshop-v1-human-validation-packet-v2/rater_context.jsonl`:
312 rows (240 Cue-A, 72 Cue-B), exposing the question, ordered options, exact
language-matched suggestion, and trace while withholding model, item, condition,
and sample identity. Annotation remains institutionally unauthorized.

The no-truncation translation rule is approved, but the exact IndicTrans2
checkpoint/tokenizer/backend/package revisions and artifact hashes remain
unresolved. `engineering/indictrans2_final_contract.json` records the contract
and fail-closed decisions. No translation, judging, annotation, or analysis has
been performed.

## Translator and direct-judge launch preparation (2026-10-04)

The official IndicTrans2 model API resolved the primary repository revision to
`ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a`; the model safetensors LFS hash is
`9b030cdd001e669a4043ea70ebb39a59630f5af58e0d0329ac9edc663ce98448`.
IndicTransToolkit was pinned to release `1.1.1`, commit
`3efb8418d0721b4ce267c2b3586899d313191357`; the upstream IndicTrans2 reference
repository was observed at commit `4f08e39cc6bf13cd62e2445dc725f22bff1a9219`.
The gated model files could not be downloaded without access credentials, so
config/tokenizer hashes and installed Transformers/PyTorch/SentencePiece versions
remain unresolved. The translator therefore remains fail-closed.

The approved segmentation utility is `segment_source_chunks`: it preserves source
order/content, records chunk index/token count/boundary level, and fails closed
rather than truncating. The synthetic tests exercise line, sentence, clause,
token, Unicode, reassembly, and deterministic behavior.

Judge V2 direct manifests are prepared independently: 936 English and 935 Urdu
records. Their launcher is fail-closed and has no scientific authorization. No
translation or judging has been performed.

## Translator freeze audit and launch boundaries

Official metadata resolved IndicTrans2 revision `ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a`, model.safetensors SHA-256 `9b030cdd001e669a4043ea70ebb39a59630f5af58e0d0329ac9edc663ce98448`, IndicTransToolkit 1.1.1 commit `3efb8418d0721b4ce267c2b3586899d313191357`, and reference repository commit `4f08e39cc6bf13cd62e2445dc725f22bff1a9219`. The official example documents `num_beams=5` and `max_length=256`; D-PG-5 adds the no-truncation segmentation boundary. The model repository is gated in this environment, so tokenizer/config hashes and installed runtime versions are still missing; translation remains blocked.

`translator_launcher.py --preflight` is fail-closed. `direct_judge_launcher.py --preflight` validates the 936+935 direct manifests and exact Judge V2 prompt hash. Its execution path requires an approved authorization file and writes only to its dedicated output directory. No downstream calls have been made.

# Workshop-v1 engineering plan

2026-09-20. Prospective infrastructure only. **No Workshop-v1 scientific outcome
exists.** This implements the user's engineering brief, not a scientific protocol
freeze. Scope is visible chain-of-thought from tested models/settings only. The
larger six-model/multilingual project and historical Track A/B remain intact.

## Repository audit and reuse

Read `CLAUDE.md` in full before work; audited `README.md`, `RESEARCH_PLAN.md`,
`experiments/EXPERIMENT_SPEC.md`, `research/FINAL_PROTOCOL.md`,
`research/EXECUTION_ROADMAP.md`, `docs/DOWNSTREAM_BLOCKER_MATRIX.md`, configs,
source/tests, and the M1-Mac-Feasibility, M2-Monitor-Validation,
M3-English-Urdu and M4-Confirmatory scaffolds. Historical documents describe their
own tracks; their model selections, approvals, results/status claims, and numeric
design choices are not imported as Workshop-v1 choices. No pilot outcome files
were used to choose this prospective design.

| Existing component | Audit finding and treatment |
| --- | --- |
| `clsm.config` and composed YAML | Reuse sibling-file composition convention. Its English-only config, one model, greedy restriction, and generation defaults are historical scientific choices; do not extend them in place. |
| `clsm.schemas.Condition`, `PromptPair`, `clsm.interventions` | Explicitly binary control/treatment. Keep their identity, hint-target rule and old records untouched. Add Workshop condition enum and frozen language-specific cue specs. |
| `clsm.generation`, `track_a_backend`, `track_a_plan`, `pipeline` | Existing injection/runtime machinery is useful after scientific selection, but assumes one config/model and binary pairs. Do not invoke or retrofit it now. |
| `downstream.contracts` | Directly reuse strict frozen `Contract`, SHA types, canonical JSON hashing, `DataKind`, and label vocabulary. New nested collections use tuples, not mutable dictionaries. |
| `downstream.matching` | Extend `TraceIdentityKey` with model ID and sample index. Directly reuse H/D/T equality validation, preserving original source language. Never downcast before Workshop matching. |
| `downstream.translation` | Directly reuse request/record/spec models and `validate_translation`; add generation/visible-trace binding and exact service-spec checks. |
| `downstream.partitions` | Existing deterministic four-way partition utility remains available. Do not force Workshop pilot/source selection into its training/calibration/heldout/confirmatory partition sizes. |
| `downstream.mcq`, `extraction` | Reusable after task format/parser selection. Source selection accepts frozen serialized task text without silently choosing MMLU, four-choice schema, or extraction rules. |
| `downstream.annotation`, `calibration`, `stage_gates` | Preserve existing human-reference and judge-acceptance contracts. Workshop review bundle follows their hash-bound evidence pattern; old stage approvals cannot authorize a new study. No alternative annotator UI or calibration implementation added. |
| `track_a_preflight` | Reuse `git_integrity` and output-collision check. Do not reuse Track-A authorization tokens, model binaries, or its frozen config hash. |
| `track_a_artifacts` | Directly reuse atomic no-overwrite publication and byte-level artifact hashing for the synthetic-only writer. |
| `downstream.analysis`, `metrics`, M3/M4 analysis plans | Leave untouched. Do not pool new model/cue levels through historical binary estimators. Analysis adaptation requires a reviewed Workshop estimand. |
| Existing synthetic fixtures | Reuse synthetic provenance and translation contracts. New fixture transport does not invent plausible CoT, answers, labels, or scientific summary statistics. |

## New architecture and configuration

`src/clsm/workshop_v1/` is an additive, offline layer. `config.py` holds the strict
draft/frozen schema; `population.py` handles local snapshot selection; `records.py`
handles identities and pairing; `monitoring.py` handles private lineage;
`preflight.py` validates prospective dependencies; `fixtures.py` and `dry_run.py`
exercise transport with synthetic markers. `clsm.workshop_v1_preflight` is a
read-only command. There is no scientific executor.

`configs/workshop_v1/study.yaml` composes `models.yaml`, `conditions.yaml`,
`languages.yaml`, and `monitoring.yaml`. Unknown/duplicate YAML keys, unsafe
includes, numeric coercion, mutable revision aliases and TODOs inside resolved
specifications are rejected. Draft nulls remain inspectable; a frozen generation
design cannot contain unresolved required choices.

Language roles are exactly `en` and `ur`. The model list supports multiple exact
specifications across exactly two active families. Family slots are not invented
model IDs. Model specs require checkpoint/tokenizer content hashes, revision,
runtime/backend and versions, explicit quantization, per-model decoding, parser
version, and selection evidence. No model-specific defaults are inherited.

`planning_target_only: 200` has no execution meaning. Actual `n_source_items`,
population role, selection rule/seed, sample-size rationale, generation seeds,
pairing mode, designation, protocol and decisions are independently unresolved.
No statistically justified N, monitor, translator, native-reference protocol,
scientific prompts, or cue wording is supplied.

## Conditions, population and pairing

The three levels are `control`, `misleading_cue_a`, `misleading_cue_b`. Every level
has an explicit cue ID/version, target rule and en/ur text/hash. Control text must
be empty; A/B must have different text in each language. Hashes cannot prove
scientific distinctness or linguistic equivalence: those need reviewed evidence.
Text/spec changes alter the study hash and invalidate population/generation bindings.

`DatasetSnapshot` records one dataset/revision/split and verifies a canonical
content hash across unique source IDs, both language renderings, category,
optional source-supplied difficulty and equivalence status/evidence. Selected
items preserve a single source ID across languages.

`sha256_source_id_v1` is an available engineering selection rule, **not adopted by
the draft science config**. When explicitly selected, it ranks candidates by
SHA256 over `[selection_seed, dataset_spec_hash, source_item_id]`, with an ID
tie-break. Input order is irrelevant. N must fit the candidate population.
Outcome/accuracy fields are forbidden in selection inputs. Failed selected-item
equivalence stops selection; it does not advance to a replacement. Changing
content/rule/seed/N requires a new study/population binding and prospective review.
Pilot/confirmatory roles are separate; an explicit disjointness checker is
available where the reviewed protocol requires it. No heldout partition sizes
are chosen by this package.

For `pairing: complete`, validate against the entire selected item × model ×
language × condition × sample grid, including entirely missing groups and
duplicate cells. Per-model decoding and each sample's seed remain fixed across
cue levels. `pairing: partial` can be represented without claiming a complete
paired design; a prospective heterogeneous cell-schedule adapter is still TODO
and scientific preflight blocks that case. No missingness imputation or analysis
eligibility policy is invented.

## Identity, provenance and confounds

Canonical source-generation identity extends the existing H/D/T key with:

`(source_item_id, model_id, language, condition, seed, sample_index, generation_id)`.

The generation ID additionally binds the full study/population hashes. A new
model revision, cue version or population cannot silently reuse an old identity.
Every generation schema requires study/designation, dataset/revision/content hash,
item content hash/category, full model/decoding spec, cue spec/rendering hash,
prompt/template hashes, seed/sample, code commit, source-tree/environment hashes,
UTC timestamp, parser version and relative output path/content hash. Synthetic
records carry the exact label **SYNTHETIC — NOT SCIENTIFIC DATA**.

Confound fields cover optional observed base-task correctness, language compliance,
input/output tokens and observation evidence. Their default is null, not a
fabricated negative/zero. Model family/tokenizer/runtime, category/difficulty,
cue, seed/decoding and translation pathway are separately preserved. Scientific
measurement methods and thresholds remain TODO.

Visible trace is a separate extraction artifact bound to its exact raw generation
and parser/evidence. The private monitoring binding distinguishes English baseline,
direct Urdu (`D`), native human (`H`), and translated-to-English (`T`). D/T must use
the same automated-monitor specification and exact original Urdu generation.
T retains source language `ur` and judge-input language `en`; translation provenance
is independent. Human-reference outputs cannot masquerade as automated outputs.
These private mappings must not be sent to a judge, translator or annotator; reuse
existing blinded input contracts when a collection adapter is eventually written.

## Stage gates and safe commands

From repository root, using a Python 3.11 environment with existing core/dev deps:

```sh
PYTHONPATH=src python3.11 -m clsm.workshop_v1_preflight
PYTHONPATH=src python3.11 -m clsm.workshop_v1.dry_run --output /tmp/synthetic-workshop-v1-review
python3.11 -m pytest
python3.11 -m ruff check src/clsm/workshop_v1 src/clsm/workshop_v1_preflight.py tests/workshop_v1
```

Preflight intentionally exits **1**, including when structural checks eventually
pass. `execution_ready` is always false: no authenticated approval verifier or
scientific executor exists. The default draft reports unresolved identities,
population and review requirements and writes nothing. `--help` lists optional
snapshot/population/review/source-manifest inputs; paths resolve from `--root`.

Structural checks require a clean reviewed commit, matching study hash, verified
snapshot and exact selected population, unused output path, and stage review
evidence bound to study/population/commit/output/source manifest. Evidence file
contents must match their hashes. Existing Track-A authorization cannot be reused.

| Requested stage | Additional structural requirements |
| --- | --- |
| Generation | Frozen design, bilingual item equivalence, stage-specific generation authorization evidence |
| Direct monitoring | Exact source manifest, monitor spec, judge criteria/validation and monitoring authorization evidence |
| Native reference | Exact source manifest, human protocol, ethics/rater qualification and human authorization evidence |
| Translation monitoring | Exact source manifest, same monitor plus translator spec, translator selection/audit plan and translation authorization evidence |
| Confirmatory | Explicit confirmatory designation/population, all applicable dependencies, locked native reference, statistical parameters, preregistration and confirmatory authorization evidence |

These are conservative engineering minima, not a scientific approval policy.
Review attestations and evidence hashes do not authenticate a person or prove
the claims in a document. Stage sequencing, population-scoped calibration/reference
evidence, statistical criteria and approval verification need scientific review
and adapters before any executor can be introduced.

The dry run takes **no scientific inputs or config**. It uses two selected toy
items, two fake families, two language roles and three conditions: 24 marker
records and 48 route bindings. Language roles do not claim linguistic competence;
translation text says `NOT TRANSLATED`. No answers, CoT, human labels or monitor
scores are generated. It writes only to a new `synthetic-workshop-v1-*` directory,
rejects `results/` (including case variants/symlink aliases), and never overwrites
or resumes. A final manifest appears only after all fixtures are written.

## Test requirements and intentional limits

Require rejection tests for unresolved choices, duplicate/mismatched IDs,
cue/content/version drift, missing entire pairing groups, synthetic/scientific
relabeling, dataset/selection tampering, population overlap, stale review evidence,
wrong-stage authorization, translation source/language errors, fabricated confound
values without evidence, output collisions and results aliases. Verify offline
fixture determinism and all artifact hashes. Run the full existing suite unchanged.

Intentionally absent: real model/dataset/judge/translator clients, human collection,
model artifact downloads, scientific prompt rendering and cue target selection,
model-specific visible-CoT parser integration, heterogeneous sampling schedules,
metric/estimand redesign, power/N selection, automated approvals, scientific
output writing, retry/resume, publication claims, and changes to frozen history.
No assumption that model versus monitor exhausts alternative explanations is
encoded; the metadata retains other factors for a future reviewed analysis.

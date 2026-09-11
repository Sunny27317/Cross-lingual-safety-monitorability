# Downstream infrastructure: API, safety and reproducibility

**Prospective infrastructure only.** Branch work starts from merged PR #18 main
`cc6e83599e27aafa2daaa456d9be3b95d9ecefb3`, containing PR #18 head
`ac6cdb5f1d594be75484dae92f7f1d9344769f64`. No execution branch or English pilot outcomes
were read to build this package. No Track-A generator or Track-B implementation/config
was changed. No new authorization token, bypass or scientific executor is introduced.

## Safe entry points

With the repository core/dev environment on Python 3.11:

```sh
python3.11 -m clsm.downstream fixture-check
python3.11 -m clsm.downstream annotation-schema
python3.11 -m pytest tests/downstream
```

`fixture-check` takes no file path, fetches no data, invokes no external executable,
and prints only a deterministic, hash-bound synthetic report to stdout. Its fixed Urdu
strings and label/translation fixtures are not human annotations, validated translations
or scientific model output. Synthetic Git/date placeholders are explicitly synthetic;
installed Python/NumPy/Pydantic versions are recorded. Do not commit fixture reports as
scientific results. `annotation-schema` prints the strict JSON Schema, not an annotation.

The package deliberately contains **no judge, translator or Urdu generation runner**.
Model/provider selection and scientific stage approval are unresolved. Its typed APIs
consume records produced later under separately approved procedures. A function call,
valid schema, hash, HMAC, or synthetic fixture grants no scientific authorization.

## API map

| Module | Public responsibilities |
|---|---|
| `contracts` | Strict extra-field rejection, exact identity/provenance, trace manifests, raw label vocabulary, explicit partial policy, judge request/output validation, prospective candidate plan |
| `annotation` | Metadata-blinded packet/private assignment, annotations, locked reference with original source hashes, validation and pairwise inter-rater reporting |
| `calibration` | Registered candidate comparison on calibration or heldout split; disjoint items/text, version/hash/rubric checks; all-candidate common coverage; no winner selection |
| `mcq` | Offline four-choice adaptation with explicit answer mapping, stable IDs/content SHA; primary/exploratory extraction separation |
| `translation` | Provider-independent specs/requests/records; lineage, context/truncation/error checks; human equivalence-audit schema and counts |
| `agreement` | Confusion, discrimination/agreement/prevalence/missingness diagnostics and explicitly requested item-cluster bootstrap |
| `analysis` | `MeasurementBundle`, `analyze_bundle`; native−direct gap, translated−direct detection recovery, separate agreement recovery, language/control separation |
| `power` | Explicit prospective paired-binary power and cluster simulations/sensitivity; no SESOI/N selection |
| `reporting` | `measurement_envelope`, deterministic JSON/hash, atomic exclusive report publication |
| `fixtures` | In-memory synthetic objects for offline validation only |

Python API workflow, **recipe only for future authorized records**:

1. Construct/validate `TraceSet` from an explicitly locked selection record, exact trace
   text and upstream dataset provenance. No filesystem search or outcome selector exists.
2. Export `AnnotationPacket` from `blind_packet`; retain `PrivateAssignment` and HMAC
   key privately. Validate completed annotations, then provenance-linked reference.
3. Lock candidate specs/plan and item-separated calibration/heldout populations before
   candidate outputs. `candidate_comparison` reports all registered candidates and
   checks that reported output timestamps do not predate the prospective plan. Timestamp
   checks are consistency checks, not independent proof against backdating.
4. For later approved translation controls, import records and run `validate_translation`
   against the exact registered spec/request; collect human `EquivalenceAudit` separately.
5. Validate a `MeasurementBundle` via `MeasurementBundle.model_validate_json(...)` and
   call `analyze_bundle`. Every label is paired by ID/hash. `measurement_envelope` binds
   all inputs and optional `ResamplingPlan`. `write_new_report` refuses existing paths,
   including symlinks; it does not create a run directory or overwrite a report.
6. Complete the prewritten report templates under the approved analysis plan. STOP at
   the authorized stage boundary; no function automatically launches another stage.

## Immutable provenance chain

Every downstream record can be traced through the following retained components:

| Identity | Binding |
|---|---|
| Repository and analysis | Full git SHA, analysis version and config hash in `Provenance` |
| Software | Exact installed Python, NumPy and Pydantic versions; additional provider/tokenizer versions in specs/evidence |
| Dataset | Dataset hash in provenance; `DatasetSpec` repo/config/split/revision and evidence; ordered item content hashes |
| Original trace | Root text SHA, trace/item IDs, language, private generator/condition identity and upstream provenance |
| Judge | Full provider/model/version/prompt/decoding/rubric/provenance spec hash; output input hash and raw-response hash |
| Translator | Full spec/settings/provenance hash; request/root/source/output hashes and parent lineage for backtranslation |
| Humans | Rubric version, pseudonymous raw annotation IDs, confidence/uncertainty, round/status/time/provenance; adjudication source hashes and lock |
| Analysis policy/randomness | Explicit label-policy decision hash and resampling/power plan parameters/seeds |
| Report | Bundle/component hashes, provenance, payload hash and envelope artifact hash |

Canonical hashes use UTF-8 JSON, sorted keys, preserved Unicode/text/choice order,
compact separators and no nonfinite numeric values. Item sets and paired analysis are
sorted by stable IDs; rows are never silently aligned by position. Preserve exact input
artifacts, including raw judge responses: a stored response hash alone cannot reconstruct
its bytes. The report references inputs rather than publishing private annotation data.
A scientific provenance record rejects the all-zero synthetic Git placeholder.

Installed version recording complements the existing environment lock/process; this
package adds no mutable model/provider default and no new dependency. Reproduce a report
with the recorded versions and exact source commit. The analysis version alone is not a
substitute for those identities. A hosted service's version evidence still requires human
verification; a string field cannot make an unversioned service reproducible.

## Validation and independence

Downstream tests deny socket connections, subprocesses and known scientific-data paths.
They use in-memory fixtures and temporary report destinations. Adversarial cases cover
unknown labels, metadata leakage, duplicated IDs, wrong versions/hashes, holdout leakage,
missing/abstained labels, failed translations, extraction contamination, payload mutation,
collisions and absent prospective design inputs. The full existing suite is additionally
run from a snapshot of tracked main files plus this package, excluding ignored pilot
artifacts. This avoids accidental readiness-test access to another researcher's outputs.

Run full non-scientific checks in that snapshot: pytest, `make lint`, `make typecheck`,
`make config-validate`, `make track-a-config-validate`, and `git diff --check` on the working
changes. Secret/local-path scanning covers the proposed infrastructure/doc files. The
repository has no dedicated secret-scanner configuration; a bounded pattern scan is
reported honestly as such, not as proof that every possible secret is detectable.

The [blocker matrix](DOWNSTREAM_BLOCKER_MATRIX.md) is canonical for readiness. Engineering
readiness does not imply judge/translator selection, human competence/equivalence,
ethics approval, final N/SESOI, or downstream scientific authorization.

## Validation record — 2026-09-11

Python 3.11 isolated validation checkout: **398 tests passed**, including **99 downstream
synthetic tests**. `make lint`, `make typecheck` (36 source files), both repository config
validation targets, and staged diff whitespace checks passed. The initial archive-only
snapshot lacked Git metadata, causing eight existing mock/provenance tests to fail;
initializing Git in that temporary snapshot resolved them without changing study code.
The snapshot's local commit is test scaffolding, not scientific run provenance.

The bounded secret/personal-path scan found no matches in new files or modified-document
additions; relative links in the new documentation resolve. Track-A generator/config,
shared extraction/metrics and Track-B files remain byte-unchanged from starting main.
No scientific data was downloaded, no scientific model/judge/translation was executed,
no real human labels were created, and no pilot outcomes were inspected by this work.

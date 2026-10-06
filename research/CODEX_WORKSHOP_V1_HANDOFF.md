# Codex Workshop-v1 engineering handoff

2026-09-20. **Prospective engineering only; no Workshop-v1 scientific outcome
exists.** Changes are uncommitted. No commit, push, PR, merge, scientific execution,
dataset/model download, API call, translation or human collection was performed.

1. **Branch:** `engineering/workshop-v1-scaffold`.
2. **HEAD:** `e7640722cb50e0b1e4c0d328eb7d6fca4e59a8a0` (unchanged).
3. **Files changed:** additive only: five `configs/workshop_v1/*.yaml` drafts,
   eight `src/clsm/workshop_v1/*.py` modules plus `workshop_v1_preflight.py`,
   six `tests/workshop_v1/*.py` files, two engineering documents, and this handoff.
   Exact file list/stat appears below. Existing source, tests, configs, README,
   protocols, result directories and the real git index are unchanged.
4. **New engineering architecture:** strict composed draft/frozen config; exact
   two-family/en–ur/three-condition identities; immutable cue/decoding provenance;
   content-hashed local dataset snapshots and deterministic no-replacement source
   selection; complete pairing validation; distinct H/D/T/English monitoring
   contracts; read-only stage preflight; synthetic-only transport exercise.
   Reuses existing strict contracts, H/D/T equality, translation validation,
   git/output guards, atomic no-overwrite writer and artifact hashing.
5. **Tests/checks:** baseline 423 tests passed; final full suite **537 passed**
   (114 new cases), Python 3.11.16 in the existing development environment. No
   dependencies installed. New-code Ruff and targeted strict mypy passed. Default
   preflight exited 1 with `execution_ready: false` as required. Standalone offline
   dry run completed under `/tmp` with 24 synthetic markers, two fake families,
   two language roles, three cues, and 48 routing bindings. No answers/CoT/labels
   or scientific metrics were produced. Diff/whitespace and integrity review passed.
   Repository-wide Ruff retains five pre-existing diagnostics in untouched
   `experiments/M1-Mac-Feasibility/run_feasibility.py` (one unused E402 suppression,
   four long lines). Full mypy retains two environment-dependent diagnostics at
   untouched `src/clsm/data.py:112` (installed untyped `datasets` import and its
   now-unused missing-import suppression). New-code type checking used
   `--follow-imports=silent`; no historical suppressions/tests were changed.
6. **Backward compatibility:** all 423 original tests still pass, historical
   Track-A/B files are unchanged, old binary condition/config hashes are preserved,
   and old approvals are not accepted as Workshop authorization. No historical
   estimator is silently reused to pool the new model/cue levels.
7. **Remaining technical blockers:** no scientific executor or authenticated
   authorization verifier; no heterogeneous frozen cell-schedule adapter; no
   scientific prompt/target/parser adapters or model artifact verification;
   no connected blinded collection/analysis adapter. Full judge/translator
   packages and population-scoped review evidence still need adapter validation.
8. **Remaining scientific blockers:** exact two model families/artifacts/runtime,
   dataset and bilingual equivalence, actual N and sampling justification,
   prompt/cue wording/target rules, seed/decoding/parser policy, shared judge and
   translator selection/validation, native reference/governance/resources,
   estimands/controls/missingness/multiplicity and confirmatory designation,
   protocol freeze and stage-specific human approvals. The 200-item value remains
   explicitly planning-only. No generalized reasoning claim is supported.
9. **Exact diff stat:** below, including all untracked additions against HEAD,
   computed using a temporary alternate git index; the real index is unchanged.
10. **Recommended next engineering task:** after scientific schema review, add an
    offline frozen cell-schedule and adapter-validation layer binding each planned
    prompt/target/parser and downstream evidence package. Retain fail-closed
    execution and avoid enabling model/service calls during that work.

## Review entry points

- `engineering/WORKSHOP_V1_ENGINEERING_PLAN.md`: audit/reuse map, contracts, gates,
  safe commands, threat boundaries and intentionally absent components.
- `engineering/WORKSHOP_V1_IMPLEMENTATION_STATUS.md`: DONE / PARTIAL / BLOCKED /
  HUMAN DECISION REQUIRED.
- `configs/workshop_v1/study.yaml`: unresolved prospective selections; no silent
  model/judge/translator/N defaults.

The scientific lead should reconcile these contracts with the prospective
Workshop-v1 protocol on their branch. Engineering has not amended the historical
scientific decision log or made the unresolved choices on their behalf.

## Exact diff stat (original scaffold, before the audit below)

<!-- DIFFSTAT BEGIN -->
```text
 configs/workshop_v1/conditions.yaml              |  10 ++
 configs/workshop_v1/languages.yaml               |   2 +
 configs/workshop_v1/models.yaml                  |   7 +
 configs/workshop_v1/monitoring.yaml              |   5 +
 configs/workshop_v1/study.yaml                   |  29 ++++
 engineering/WORKSHOP_V1_ENGINEERING_PLAN.md      | 182 +++++++++++++++++++++++
 engineering/WORKSHOP_V1_IMPLEMENTATION_STATUS.md |  73 ++++++++++
 research/CODEX_WORKSHOP_V1_HANDOFF.md            |  99 +++++++++++++
 src/clsm/workshop_v1/__init__.py                 |   1 +
 src/clsm/workshop_v1/config.py                   | 333 +++++++++++++++++++++++++++++++++++++++++++
 src/clsm/workshop_v1/dry_run.py                  | 298 ++++++++++++++++++++++++++++++++++++++
 src/clsm/workshop_v1/fixtures.py                 | 204 ++++++++++++++++++++++++++
 src/clsm/workshop_v1/monitoring.py               | 170 ++++++++++++++++++++++
 src/clsm/workshop_v1/population.py               | 137 ++++++++++++++++++
 src/clsm/workshop_v1/preflight.py                | 235 ++++++++++++++++++++++++++++++
 src/clsm/workshop_v1/records.py                  | 250 ++++++++++++++++++++++++++++++++
 src/clsm/workshop_v1_preflight.py                |  69 +++++++++
 tests/workshop_v1/__init__.py                    |   1 +
 tests/workshop_v1/conftest.py                    |  36 +++++
 tests/workshop_v1/test_config_population.py      | 248 ++++++++++++++++++++++++++++++++
 tests/workshop_v1/test_identity_provenance.py    | 174 ++++++++++++++++++++++
 tests/workshop_v1/test_monitoring.py             | 168 ++++++++++++++++++++++
 tests/workshop_v1/test_preflight_dry_run.py      | 291 +++++++++++++++++++++++++++++++++++++
 23 files changed, 3022 insertions(+)
```
<!-- DIFFSTAT END -->

## Publication-first simplification audit

**Verdict: keep the useful scaffold, stop framework development, and implement
only the selected experiment's missing adapters after scientific decisions.**
The architecture can represent the minimal design, but it cannot currently run
real generation/evaluation or produce the Workshop paired analysis. Passing the
synthetic tests is not execution readiness or evidence of a publishable result.

This section supersedes item 10 above and the earlier suggestion that a generic
heterogeneous cell-schedule layer or an authenticated authorization service is
the next task. Neither is intrinsically necessary for this first paper. Preserve
actual research approvals, recorded decisions, provenance and execution checks;
do not build an approval platform. The prior diff stat and 537-test result are
historical validation of the original scaffold, not a new run in this audit.
This audit reviewed all 23 additions and collected all 114 new test cases without
executing experiments. No clear current correctness/integrity bug requiring a
code change was found. Only this handoff was changed; no files were added.

### 1–2. Essential files versus optional files

"Essential" below means needed to use this scaffold for the proposed study, not
that its particular file organization is a scientific requirement. No new file
is a real generator, judge, translator, annotation collector or analysis runner.
Keep existing files rather than spend publication time deleting/reorganizing them.

- **Operational core (11 files):** all five
  `configs/workshop_v1/{study,models,conditions,languages,monitoring}.yaml` files;
  `src/clsm/workshop_v1/{__init__,config,population,records,monitoring,preflight}.py`.
  The YAML loader requires all five files even when monitoring values are null.
  `monitoring.py` is needed at evaluation time; the essential part of
  `preflight.py` is the input/provenance/output/authorization checking, not its
  entire five-stage evidence-bundle architecture. The initializer is packaging.
- **Validation support (8 files):**
  `src/clsm/workshop_v1/{fixtures,dry_run}.py` and all six
  `tests/workshop_v1/{__init__,conftest,test_config_population,test_identity_provenance,test_monitoring,test_preflight_dry_run}.py`
  files. They are not runtime dependencies of a scientific experiment's
  measurement logic. Retain them for inexpensive regression/synthetic checks;
  no need for a larger test framework or more fixture demonstrations.
- **Optional operational wrapper (1 file):**
  `src/clsm/workshop_v1_preflight.py`. Useful diagnostics, but it always exits 1;
  it cannot serve as a launch command merely by filling YAML fields. The checks
  matter; a separate CLI wrapper is not a publication requirement.
- **Documentation (3 files):**
  `engineering/WORKSHOP_V1_ENGINEERING_PLAN.md`,
  `engineering/WORKSHOP_V1_IMPLEMENTATION_STATUS.md`, and this handoff. Useful
  references, not scientific execution requirements. Use this final section for
  priorities; defer maintaining three expanding engineering narratives.

### 3. What is over-engineered or unnecessarily coupled

- The generic five-stage review bundle and a future signature/authentication
  service exceed the needs of a single investigator's small study. A verifiable,
  dated, explicitly authorized run record bound to the actual design/commit is
  still required; no external approval server, PKI or cloud service is required
  by `CLAUDE.md`. Any future simplified boundary must preserve applicable checks,
  not ignore the current preflight's nonzero exit code.
- Heterogeneous sampling schedules, plugin-style backend registries, generalized
  orchestration, dashboards, distributed workers and framework-level resume/retry
  are unnecessary for a fixed two-model Cartesian design. Basic failure capture
  and protection against accidental reruns are necessary.
- Repeating full model/cue/dataset specifications in every record, source-tree
  hashes alongside reviewed commits, and separate hashes for many evidence
  objects add bookkeeping. They are already implemented: keep them rather than
  refactor now, but do not extend them into an artifact-management platform.
- The full `Study.artifact_hash` includes monitoring selections and planning
  metadata. Changing a judge/translator/reference spec after generation changes
  population and generation bindings, even if generation settings did not change.
  The smallest compatible path is to resolve/freeze those specs before the run.
  If judge selection genuinely depends on a prior calibration stage, use its
  separately declared calibration population and lock the selected spec before
  the target run. A separate generation/evaluation hash design is conditional
  engineering, not a reason to regenerate outcomes or relabel old artifacts.
- `DatasetSnapshot` expects en/ur text for every supplied candidate, not just the
  eventually selected N. Do not translate an entire benchmark for this schema.
  The narrow adapter must preserve prospective source-ID selection evidence and
  supply the intended bounded bilingual population; if selecting from a larger
  untranslated pool, resolve the selection-before-translation interface explicitly.
  Do not use placeholders as real Urdu content or choose replacements by outcomes.
- Current `complete` validation accepts only a complete grid of nonempty generation
  records. Real failures/empty or absent CoT need a separate attempt/failure ledger
  and prospective missingness handling in the runner. Do not manufacture a success
  record or switch to `partial` after observing inconvenient failures.

### 4. Can it support the requested minimal experiment?

**Represent and validate: yes. Execute and analyze end to end today: no.**
Exactly two active model families, en/ur and three cue levels are supported;
one model per family fits directly. N and generation seeds are explicit inputs.
`full_design` provides the fixed Cartesian schedule, so no new general scheduler
is needed. Exact identity checks preserve item/model/language/seed across cue
comparisons and the original Urdu generation across H/D/T. Monitoring contracts
distinguish the English baseline, direct Urdu, native human and translated English.

Missing are the actual runtime call, scientific prompt/target rendering, answer
and visible-CoT extraction, evaluation collection, and the paired analysis adapter.
The old `clsm.metrics` groups by item and binary condition and has historical
thresholds/eligibility rules; feeding two families/three cues into it directly is
not safe. The downstream report also does not automatically provide the required
Workshop model-by-cue contrasts. A small explicit analysis script is sufficient;
preserve model/cue strata and source-item pairing without declaring every repeated
trace an independent item. Freeze estimands/uncertainty/missingness/multiplicity
before outcomes; do not select a statistical method in this engineering audit.

**Planning arithmetic only, not executed counts or a scientific N recommendation:**
with N=200 and one sample per cell, 2 × 2 × 200 × 3 = 2,400 generations, including
1,200 Urdu traces. Evaluating all applicable traces would involve 1,200 English
baseline, 1,200 direct-Urdu and 1,200 translated-English automated judgments, plus
1,200 translations. Full Urdu coverage by two independent raters would mean 2,400
individual judgments before adjudication, not merely 200 annotations. Calibration,
item equivalence work and any selected controls are additional. A smaller human
reference subset requires a prospectively justified selection/coverage design and
appropriately scoped claims; the code does not select it. The new scaffold does
not override the existing native-reference governance requirements.

### 5. Absolute minimum engineering before real generation

1. **One selected-dataset adapter:** load the approved pinned source, preserve
   prospectively fixed source IDs and bilingual equivalence, freeze the selected
   content, and keep correct-answer metadata separate from model-facing text.
   Store the actual misleading target used for each item/cue so answer adoption
   can later be computed. The generic serialized-text schema does not provide
   these task-specific semantics by itself.
2. **One narrow generation path for the selected models:** use one existing local
   runtime for both if their approved artifacts support it, otherwise only the
   two required runtime adapters. Render the frozen language prompts/cues and
   model chat templates; preserve actual rendered prompts, targets, seeds,
   decoding and artifact/runtime identity. Reuse the fixed grid and atomic writer.
   Do not inherit Track-A model defaults or its old execution authorization.
3. **Raw-output/parser/failure handling:** retain raw output, extract final answers
   and visible-CoT with the approved model-specific parser, and distinguish
   missing/malformed/truncated/failed output from negative disclosure. Record
   every attempted cell and failure without outcome-based replacement. Exact
   seeds record reproducibility settings; they do not prove bitwise determinism
   across hardware/backends.
4. **A small explicit launch boundary plus adapter-level synthetic checks:** verify
   frozen inputs, actual local artifacts/runtime versions, reviewed code, unused
   output location and genuine stage-specific user authorization. Test the chosen
   prompt/parser and all three condition paths with synthetic fixtures, including
   failure handling. The existing transport markers do not test real chat templates
   or CoT parsing. A full authentication service is not necessary. Do not change
   the permanent-refusal CLI into a success flag without implementing those checks.

Before these steps, the scientific lead must settle the design and confirm that
the needed native reference and evaluation resources can actually be obtained.
Monitoring/translation calls, simple blinded annotation export/import, and the
paired analysis script are required before their respective stages/paper, but
their entire implementation need not hold up generation once their protocols,
input/output requirements and feasibility are fixed. No downloads or real calls
are authorized by this audit; a reviewed commit and run approval are future work.

### 6. Defer until after the first paper

Defer six-model/multilingual expansion, additional backends, heterogeneous/adaptive
schedules, generic workflow and authorization systems, dashboards/annotation apps,
distributed execution, automatic retries, performance tuning without a measured
bottleneck, large model/judge/translator sweeps, broader simulation infrastructure,
and additional engineering-status documents. Keep existing tests; defer expanding
them to cover hypothetical platforms. Basic storage, failure accounting, blinding
and reproducibility cannot be deferred. Neither can any control or validation
needed for a claim actually made in the first paper; drop unsupported claims
rather than promise to validate them after publication.

### 7–8. Budget, scope and hidden-selection audit

| Possible imposed requirement | Finding |
| --- | --- |
| Expensive cloud compute / paid APIs | Not imposed: no scientific client/provider, device class or paid service is selected. Existing-core imports do not execute historical backends. Local/free execution is representable; feasibility and elapsed time depend on the eventual artifacts and available hardware. No zero-cost completion guarantee. |
| Six models / extra languages | Not imposed: exactly two active families, at least two model specs, exactly en/ur. Use one selected model per family for the requested design. |
| Excessive seeds | Not imposed: one explicitly supplied seed is accepted; no default seed count. The two-seed test verifies identities, not a scientific requirement. |
| Excessive annotation | No annotation count is imposed by new schemas. The synthetic route demo is not a mandate to label every trace. Real native reference, independence, coverage and governance remain required as applicable; lack of genuine raters cannot be repaired by code or invented labels. |
| Unnecessary infrastructure | Some bookkeeping is imposed by current contracts: composed YAML, full-study hash binding, review bundles, complete population manifests and unconditional preflight refusal. This audit explicitly removes generic schedule/authentication development from the first-paper critical path; the existing refusal is not bypassed. |

Verified the actual draft: model specs are null; dataset is null; actual N is null
while only `planning_target_only` is 200; cue specs/prompts are null/empty;
generation seeds are empty; judge, translator and native-reference specs are null.
No numeric statistical threshold or human sample/rater count is selected by these
new files. Synthetic IDs, text, seed 0, temperature 0 and tiny fixture sizes are
confined to the synthetic path; they are not scientific defaults.

There **are explicit design constraints**, so this is not a claim of unrestricted
configurability: en/ur, two families, three conditions, one shared automated monitor,
no outcome-based replacement, common configured seeds across the complete grid,
per-model decoding shared across its languages/cues, and native-Urdu reference role.
Only the `sha256_source_id_v1` selector is implemented; the draft does not choose it.
If another selection rule is scientifically required, adapt that narrow function
instead of pretending the rule was freely configurable. Pilot/confirmatory roles,
the inherited disclosure vocabulary and provisional stage gates are also encoded;
they do not settle the final rubric, statistical analysis or institutional decisions.

### 9. Audit of all 114 new tests

Confirmed by collection only: 35 config/population + 38 identity/provenance +
16 monitoring + 25 preflight/dry-run = **114 parameterized cases**. Read every test
body and parameter list; no tests were added, altered or rerun in this audit.

| Test file | Cases | Study protection and unnecessary-architecture assessment |
| --- | ---: | --- |
| `test_config_population.py` | 35 | Keep unresolved choices, two-family/three-cue/language shape, immutable content, deterministic selection and no replacement. YAML include layout tests are implementation-specific; pilot/confirmatory disjointness is conditional on that design. Exact assertion that the planning target equals 200 must not be treated as a scientific N freeze. |
| `test_identity_provenance.py` | 38 | Keep exact identities, whole-group omissions, cue drift, duplicates and honest observations. `test_partial_design_is_explicit_and_does_not_claim_complete` concerns a deferred feature. The 17 required-field deletion cases mainly test schema enforcement, not new scientific behavior; retain them, do not expand that pattern instead of testing the real adapters. |
| `test_monitoring.py` | 16 | Direct protection of the central comparison: same Urdu generation, same D/T monitor, distinct human reference, translation language/lineage, abstention and frozen source validation. These are high priority. `test_same_text_on_different_generation_does_not_allow_translation_swap` actually uses different transport-marker texts; it verifies cross-generation rejection but is not evidence of a literal equal-text collision test. |
| `test_preflight_dry_run.py` | 25 | Keep refusal for unresolved/scientific misuse, honest synthetic labels, no network, output collision and results-path protections. Several cases defend the chosen review-bundle machinery, not a minimal paper requirement; see below. |

Specifically lower-priority architecture tests: the two partial-design/schedule
tests; six `test_review_cannot_be_replayed_across_bindings` variants; the
missing/duplicate gate-evidence test; evidence-newline/path and approval-timestamp
tests; and five-stage parameterization including a confirmatory stage the eventual
paper may not invoke. Their underlying goals (correct input binding and honest
authorization) remain valid. A small launch boundary needs those properties,
not necessarily this bundle format or all five stages. Do not delete passing tests
for speed: no feature work is needed to leave them in place. The important missing
tests are for the selected prompt/target/parser, failure accounting and paired
analysis adapters, once those few adapters exist. The current suite does not
establish Urdu competence, translation validity, monitor accuracy or statistical
adequacy.

### 10. Final component table

"Before experiment" below means before real generation; later-stage requirements
are called out explicitly. "Before paper" means before relying on that component's
scientific output, not before starting to write a manuscript scaffold.

| Component | Needed before experiment? | Needed before paper? | Defer? | Reason |
| --- | --- | --- | --- | --- |
| Frozen scientific selections and five config files | Yes | Yes | No | Prevent silent model/N/cue/service choices; current loader requires the files. |
| `__init__.py`, `config.py`, `population.py`, `records.py` | Yes | Yes | No | Existing package/core contracts preserve design, population, pairing and provenance. |
| Selected-source/bilingual task adapter | Yes | Yes | No | Real aligned inputs, answer keys and cue targets are not implemented by the generic schema. |
| Selected-model runtime + prompt + parser adapter | Yes | Yes | No | Actual generation and interpretable visible CoT require it. |
| Attempt/failure ledger and no-overwrite storage | Yes | Yes | No | Preserve denominators and failures; never silently replace or discard. |
| Minimal verified-input and explicit-authorization boundary | Yes | Yes | No | A safe scientific run needs genuine permission and exact bindings. |
| Full five-stage bundles / authentication service | No as a new platform | No as a platform | Yes | Retain actual approvals; do not turn administration into the critical path. |
| `workshop_v1_preflight.py` diagnostic CLI | Optional | Optional | Further development | Current unconditional refusal is useful but not a runnable pipeline. |
| `fixtures.py`, `dry_run.py`, test helpers | Synthetic validation needed | Retain evidence | More demos | Existing scaffolding is enough; extend only for selected adapters. |
| Config/identity/monitoring safety tests | Relevant checks yes | Yes | No essential checks | Cheap protection of the actual comparison. |
| `monitoring.py` + shared judge/translation adapters | Protocol/specs fixed; calls later | Yes | Implementation until evaluation | Four paths are represented, not connected to actual tools. |
| Native Urdu reference + simple blinded export/import | Feasibility/protocol first; collection later | Yes for native-validated claims | No required reference | Real human evidence cannot be replaced by automated labels or engineering. |
| Paired model/cue-aware analysis script | Plan first; implementation can follow | Yes | Only until analysis | Old binary metrics are not automatically correct for the new matrix. |
| Heterogeneous cell-schedule framework | No | No | Yes | Existing complete Cartesian plan fits the minimal experiment. |
| Six models, more languages, extra seed/model sweeps | No | No for narrow claims | Yes | Wider replication belongs to later work; do not force scope inflation. |
| New UI/cloud/distributed orchestration | No | No | Yes | Small local files/scripts suffice if selected models fit available resources. |
| More engineering plans/status docs | No | No | Yes | Existing references and this handoff suffice. |

### 11. Minimal execution dependency chain

**SCIENTIFIC DECISIONS**
→ **IMPLEMENT ONLY REQUIRED ADAPTERS**
→ **SYNTHETIC VALIDATION**
→ **REAL GENERATION**
→ **HUMAN/MONITOR EVALUATION**
→ **ANALYSIS**
→ **PAPER**

Freeze the narrow claims, actual N/population, two models, prompts/cues, sampling,
evaluation resources and analysis plan first. Implement the bounded dataset and
generation adapters, verify them synthetically, then obtain explicit authorization
for the real run. Collect genuine blinded reference/monitor/translation evidence
under the approved protocols, compute the predeclared paired analyses, and report
the observed findings and limitations, including null results. This is a dependency
chain, not permission to execute now or a promise of publishability/acceptance.

**READY TO PAUSE CODEX: YES.** Execution is still blocked on decisions and bounded
adapters, but no further framework work or code change is required for this audit.

---

## Implementation-freeze session (2026-09-21)

Picks up exactly where the audit above left off ("implement only the selected
experiment's missing adapters after scientific decisions"): the scientific-lead branch
(`/Users/sullah1/clsm-claude`) has since frozen the exact stack (models, cues, dataset,
judge, translator — see `research/WORKSHOP_V1_SELECTION_RECOMMENDATION.md` and
`research/CLAUDE_WORKSHOP_V1_HANDOFF.md` there, read but not modified from this
worktree). This session implements the adapters that document's own component table
called "essential, needed before experiment": the selected-source/bilingual task
adapter, the selected-model runtime+prompt+parser adapter, and a synthetic validation
exercise of both — plus performs the one remaining execution-only check the scientific
layer explicitly deferred to engineering (Falcon-H1 llama.cpp compatibility).

**No commit, push, PR, merge, scientific execution on real items, judge run on a real
trace, translator call, or human collection was performed.** Two real model artifacts
were downloaded for engineering smoke-testing purposes only (below); every prompt used
against them was a trivial, non-scientific string, never an OpenBookQA/UrduBench item
or the frozen cue text.

### What changed

New files, all additive (nothing in the prior scaffold was edited or removed):

```
src/clsm/workshop_v1/cue_rule.py
src/clsm/workshop_v1/output_parsing.py
src/clsm/workshop_v1/prompt_contract.py
src/clsm/workshop_v1/openbookqa_adapter.py
src/clsm/workshop_v1/llamacpp_generation.py
src/clsm/workshop_v1/synthetic_adapter_e2e.py
tests/workshop_v1/test_cue_rule.py
tests/workshop_v1/test_output_parsing.py
tests/workshop_v1/test_prompt_contract.py
tests/workshop_v1/test_openbookqa_adapter.py
tests/workshop_v1/test_synthetic_adapter_e2e.py
```

Full detail on each module and the exact validation performed:
`engineering/WORKSHOP_V1_IMPLEMENTATION_STATUS.md` (rewritten this session to describe
the current, not the pre-implementation, state).

### Real artifacts (outside the repository, under `/Users/sullah1/models/clsm/`)

- **Falcon-H1-7B-Instruct-Q4_K_M.gguf** — downloaded from the official (non-gated)
  `tiiuae/Falcon-H1-7B-Instruct-GGUF` repository, repo commit
  `058c8c8f08e57da131ba5f070f9ff1280d141c39`, 4,598,344,960 bytes, **SHA-256
  `145def0b4cd36500bf538ed7ac895b5c1851e02e802b2d1c12ffa6afdbaff25d` (computed locally,
  not invented)**.
- **Gemma-3-4B-it — NOT downloaded.** The exact frozen artifact
  (`google/gemma-3-4b-it-qat-q4_0-gguf`) is a **gated** repository; this environment has
  no Hugging Face credential (checked: `HF_TOKEN` and equivalent variables are all
  absent). Per explicit instruction, **no alternate quantization or mirror was
  substituted.** This is reported as a blocker for the scientific layer/investigator to
  resolve (accept the license and supply a token, or explicitly authorize a named
  alternate source as a new, dated decision), not silently worked around.

### Falcon-H1 llama.cpp compatibility — RESOLVED

The prior session's one remaining execution-only blocker is now closed with real
evidence: the pinned `llama-cli` (v0.4.0-dev, build 10809) loads the downloaded
Falcon-H1-7B-Instruct GGUF, answers a trivial prompt, produces a well-formed one-word
structured-classification label for a disclosure-style classification prompt, and
handles an Urdu-language prompt/response with no encoding corruption. **FALCON LOAD
TEST: PASS.** None of the three prompts used is scientific data.

### Tests / checks

52 new tests across 5 new files, all passing. Full repository suite: **589 passed**
(previously 537), Python 3.11.16. New-code Ruff and targeted strict mypy
(`--follow-imports=silent`) both clean. Repository-wide Ruff retains the same 5
pre-existing diagnostics in `experiments/M1-Mac-Feasibility/run_feasibility.py` already
noted by the prior audit — untouched, out of scope. `git diff --check` clean (nothing
staged; everything remains untracked/uncommitted per this session's no-commit
instruction).

### What is still not implemented (unchanged in kind from the prior audit)

No scientific executor exists; the `Study`/`configs/workshop_v1/*.yaml` contracts are
still unpopulated with real frozen values (blocked on Model B's identity, above); the
dataset adapter has not been exercised against a real fetch of the live
`large-traversaal/openbookqa_urdu_final` schema (synthetic-fixture-tested only); no
judge calibration, translation, human annotation, or analysis code has been added or
run. See `engineering/WORKSHOP_V1_IMPLEMENTATION_STATUS.md` for the full DONE/PARTIAL/
BLOCKED/HUMAN-DECISION-REQUIRED breakdown.

**READY FOR TINY FEASIBILITY RUN: NO.**
**BLOCKERS:** (1) Gemma-3-4B-it cannot be downloaded without a Hugging Face credential
accepting Google's Gemma license, or an explicitly authorized named alternate source —
a human decision, not an engineering one; (2) the dataset adapter has not been
validated against a real fetch of the live Urdu dataset schema, only synthetic
fixtures; (3) every scientific-decision blocker already on record in
`engineering/WORKSHOP_V1_IMPLEMENTATION_STATUS.md`'s HUMAN DECISION REQUIRED section
(final N, SESOI/alpha/power, ethics/IRB, judge acceptance thresholds, rater
identities) remains open and unaffected by this session's engineering work.

## Pipeline completion phase (2026-09-21)

The live Hugging Face viewer was inspected read-only. It confirms the aligned schema
(`id`, English and Urdu question stems, ordered four-choice dictionaries, and shared
four-class `answerKey`) and train/validation/test splits. No benchmark text was saved.
The adapter validator reports metadata-only schema counts, duplicate/missing-field
errors, option mismatches, and an ID manifest hash.

Bounded execution-to-paper support now includes deterministic disjoint pilot/main/Cue-B
ID partitioning (main 120, Cue-B 36), synthetic annotation packet exchange, strict
judge-format parsing, an official `ai4bharat/indictrans2-indic-en-1B` Urdu-to-English interface, source-item cluster
bootstrap intervals, table/figure input contracts, append-only checkpoints, and
transparent call-count arithmetic. These contracts have synthetic tests only; no
scientific values were produced.

Gemma is still blocked by Google's gated repository. `gemma_download.py` checks the
exact repository and filename, requires an immutable revision and explicit authorization,
and hashes the downloaded file; it was not invoked. IndicTrans2 remains pending a
human-frozen revision. Falcon remains smoke-tested only. No study generation, real
judge/translation, human labeling, or analysis was run.

After license acceptance and a frozen commit are available, Sana can run the helper
with the private credential already configured in her environment: `.venv/bin/python -c 'from pathlib import Path; from clsm.workshop_v1.gemma_download import download_exact; print(download_exact(revision="<FROZEN_COMMIT>", output_dir=Path.home()/"models/clsm/Gemma-3-4B-it", allow_download=True))'`.

| Stage | Status |
|---|---|
| Live schema inspection | READY; frozen snapshot still required |
| Pilot/main/Cue-B partition | READY; ID-only deterministic helper |
| Gemma exact download | BLOCKED; Google license/authentication required |
| IndicTrans2 adapter | READY as interface; revision HUMAN ACTION REQUIRED |
| Human annotation exchange | READY for synthetic packet validation |
| Judge format runner | READY for synthetic format validation |
| Paired analysis/bootstrap | READY as bounded code; requires verified scientific records |
| Tables/figure data | READY as empty-input contracts; no fabricated results |
| Main runner | PREPARED only; not executed |

## Final pre-feasibility engineering audit

The dataset repository HEAD was recorded as
`e4186f6ba5c3395c6f5cc99e1efadd7755ed4055` using `git ls-remote`. The public viewer
reports 5,957 total rows across train/validation/test and confirms the aligned schema.
Direct row retrieval from this worktree failed because `huggingface.co` could not be
resolved, so split counts, duplicate/missing-ID checks, option-count checks, and Unicode
checks are explicitly marked blocked in
`engineering/workshop_v1_dataset_summary.json`. No benchmark text or fabricated IDs
were committed, and no pilot/main/Cue-B manifest was created.

The non-destructive readiness command is:

```bash
PYTHONPATH=src python3.11 -m clsm.workshop_v1_readiness
```

It reports only the requested component states and never runs a model or downloads a
dataset. Main-record validation now requires all core hashes, rejects synthetic/pilot
records and mixed study hashes, and annotation contracts validate rater disagreements
and adjudicator rows.

IndicTrans2 is pinned to the official model identity
`ai4bharat/indictrans2-indic-en-1B`, MIT, Transformers/PyTorch, `urd_Arab` → `eng_Latn`.
Its exact commit remains unresolved because the model repository requires authenticated
access; no revision was invented.

## Last offline engineering task

The pipeline can now continue from manually supplied authenticated resources without
changing the study. `local_ingest.py` validates a local JSON/JSONL/Parquet export only
when its sidecar identifies the exact dataset repository and pinned revision
`e4186f6ba5c3395c6f5cc99e1efadd7755ed4055`; it computes row/ID/content hashes and never
writes benchmark text. The population freezer emits IDs and hashes only and labels its
output `POPULATION FREEZE — NOT AN EXPERIMENT RUN`.

`local_artifacts.py` verifies the exact Gemma Q4_0 GGUF filename, size, SHA-256,
repository/revision metadata, and local llama.cpp binary presence. It also verifies a
manual IndicTrans2 directory, tokenizer/config file hashes, immutable revision, MIT
model identity, and `urd_Arab` → `eng_Latn`. Neither helper downloads or runs inference.

The proposed smallest permanent feasibility pilot is one pilot ID, one sample, and 12
calls: 2 models × 2 languages × control/Cue-A/Cue-B. It is permanently excluded from
the 120-item main population and is sufficient to exercise prompt/cue rendering,
visible-trace/final-answer parsing, language compliance, and checkpoint/resume. It is
not executed by this task.

After Sana supplies resources, the documented sequence is:

1. validate the local dataset export and freeze ID-only pilot/main/Cue-B manifests;
2. verify Gemma locally and run only the existing non-scientific smoke test;
3. verify IndicTrans2 identity and tokenizer files;
4. run `PYTHONPATH=src python3.11 -m clsm.workshop_v1_readiness`.

The sequence does not launch the scientific experiment. Sana must provide the exact
dataset export plus metadata sidecar, the accepted-license Gemma GGUF and immutable
revision, a compatible llama.cpp binary, and the authenticated/manual IndicTrans2
files with their exact revision.

The dataset verification/freezing command sequence is:

```bash
PYTHONPATH=src python3.11 -c 'from pathlib import Path; from clsm.workshop_v1.local_ingest import ingest_dataset, load_rows, freeze_population_from_rows; p=Path("/path/to/export"); s=ingest_dataset(p); freeze_population_from_rows(load_rows(p), s, selection_seed=20260921, output=Path("engineering/workshop_v1_population_manifest.json"))'
```

The command writes only the ID/hash manifest. Gemma verification is:

```bash
PYTHONPATH=src python3.11 -c 'from pathlib import Path; from clsm.workshop_v1.local_artifacts import verify_gemma_local; print(verify_gemma_local(Path("/Users/sullah1/models/clsm/gemma-3-4b-it-q4_0.gguf"), repo_id="google/gemma-3-4b-it-qat-q4_0-gguf", revision="<FROZEN_GEMMA_COMMIT>", llama_cli=Path("/path/to/llama-cli")))'
```

Final offline status: **LOCAL DATASET INGEST: READY** (pending Sana’s local exact
snapshot), **LOCAL GEMMA INGEST: READY** (pending license/authenticated file), **LOCAL
INDIC TRANS2 INGEST: READY** (pending authenticated files and revision), **POST-ACCESS
WORKFLOW: READY**, and **TINY PILOT CONFIG: READY**. The tiny pilot is exactly 12 calls
using one permanently excluded pilot ID; it is not executed here and its outputs must
be labelled `FEASIBILITY ONLY — EXCLUDED FROM MAIN ANALYSIS`.

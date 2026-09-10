# Track-A final blocker matrix

**PRE-OUTCOME; no scientific run.** Start with `PRE_RUN_FINAL_CHECKLIST.md`; commands are
in `SCIENTIFIC_RUN_PLAN.md`. Historical hardware verification does not clear current preflight.
Stage membership is typed/code-frozen in `RunStage` / `stage_unresolved` (D-066).

| Requirement | Stage | Current Status | Blocks This Stage? | Evidence | Human Action? | Engineering Action? | External Dependency? | Resolution |
|---|---|---|---|---|---|---|---|---|
| Model | generator | Qwen3-1.7B revision frozen | Yes if different | model.yaml, D-034 | Review identity | None beyond preflight | Installed artifact | Use frozen model only |
| GGUF | generator | SHA/size pinned; historical verification | Yes until current check passes | runtime_llamacpp.yaml, D-037 | Supply local path | SHA/size check implemented | Local GGUF | Current preflight |
| llama.cpp | generator | commit/build pinned; historical verification | Yes until current check passes | runtime_llamacpp.yaml, D-036/D-040 | Supply binary path | Fail-closed version probe | Local arm64 binary | Current preflight |
| Config hash / commit | generator | hash frozen; package awaiting review | Yes | pre_run_freeze.json | Review exact final commit/hash | Drift/dirty checks implemented | Human signoff | Bind both in authorization |
| MMLU repository/revision | generator | cais/mmlu, all/test, c30699e8… frozen | Yes if different | dataset.yaml | Approve dataset-only retrieval | Native parquet adapter prepared | Dataset access/layout | Resolve exact commit; no fallback |
| Dataset content pin | generator | NOT CREATED | YES | dataset pin schema/tool; D-056/D-067 | Review IDs/content/order/labels/hash | Fixture-tested; real adapter not exercised | Real source metadata/content | Explicit opt-in retrieval, then validate/review |
| Prompt | generator | Frozen | Yes if changed | pilot.yaml, prompt SHA | Review | Existing builder reused | None | Preserve bytes |
| Cue / experiment ID | generator | Frozen; ID now hashed | Yes if changed | cue.yaml, D-017/D-067 | Review | Existing hint rule reused | None | Fixed experiment ID, separate output directory |
| Seeds | generator | 0..7 | Yes if changed | decoding.yaml | Review | Plan validation | None | 8 distinct paired seeds |
| Samples/condition | generator | 8 | Yes if changed | decoding.yaml | Review | 800-call workload check | None | Fixed 50 × 2 × 8 |
| Parser | generator | D-038 Latin final-answer parser | Yes if changed | extraction.py | Review | Existing parser reused | None | No label guessing |
| Stop reason | generator | Five explicit states | Yes if policy absent | backend.py, D-053 | Review diagnostics | Unit tests incl timeout/LENGTH | Runtime perf output | UNKNOWN retained when signal absent |
| Retry | generator | ZERO | Yes if changed | D-054 | Review interruptions | One attempt/spec | None | No rerolls/resume |
| Output collision policy | generator | Exclusive new directory and artifacts | YES on collision | artifacts.py, execute.py | Choose unused directory | No-overwrite writes | Storage | Never reuse a partial/completed directory |
| Human authorization | generator | NOT PROVIDED by this package | YES | track_a_run.py, checklist | Required JSON/reviewer/time | Sole issuer preserved; full preflight | Human review | Bind stage/commit/config/content/output/ID |
| Judge | judge | Unselected, calibration rules unresolved | YES for judge; NO for generator | judge.yaml, D-047/D-061 | Approve prospective calibration | Later adapter/validation | Candidate/resources | Validated independent judge, no size proxy |
| Human disclosure reference | human_validation, judge | Conceptual protocol only; acceptance rules unresolved | YES for human/judge; NO for generator | MONITOR_VALIDATION_PROTOCOL.md §4 | Approve rubric/recruitment/adjudication | Later blinded labeling workflow | Qualified annotators | Prospective human protocol before use |
| Urdu native validation | urdu | English NOT_APPLICABLE is not a later-stage clearance | YES for Urdu; NO for generator | D-049/D-061 | Approve equivalence/reliability | Later Urdu instrumentation | Native reviewers | Separate Urdu-stage freeze |
| Translator | urdu/translation comparison | Unselected; non-lossy validation unresolved | YES for translation/Urdu package; NO for generator | D-061, monitor protocol §3 | Select and approve acceptance plan | Later translator adapter | System/native review | Preserve reasoning and hint influence |
| Ethics | human_validation, judge, urdu | Institutional determination unresolved | YES before recruitment/annotation; NO for public-benchmark generator | D-049/D-066 | Obtain determination/consent plan | No exemption inferred | Institution/annotators | Approval before human participation |
| Confirmatory N | confirmatory | Not frozen | YES for confirmatory; NO for pilot | D-058, POWER_ANALYSIS.md | Scientific design decision | Later design validation | Scientist | Prospective N; no outcome-driven tuning |
| Confirmatory SESOI | confirmatory | Not frozen | YES for confirmatory; NO for pilot | D-058/D-061 | Scientific design decision | Later design validation | Scientist | Do not select from pilot effects |

## Canonical versus historical material

| Material | Status / audit resolution |
|---|---|
| This matrix + final checklist + scientific run plan | Canonical operational package; avoid creating another checklist |
| configs/track_a_pilot/*.yaml + pre_run_freeze.json | Canonical scientific settings and expected hash |
| PILOT_PROTOCOL.md | Canonical scientific rationale; D-066 staged-readiness amendment supersedes all-stage generator blockers |
| PILOT_PREREGISTRATION.md | Preregistration summary; not a competing command recipe; unresolved later-stage choices remain explicit |
| MONITOR_VALIDATION_PROTOCOL.md | Later-stage conceptual protocol; calibration thresholds remain unresolved |
| PILOT_REPORT_TEMPLATE.md | Frozen descriptive reporting structure; no result values filled |
| READINESS.md, MODEL_SCREEN.md, EXPERIMENT_SPEC.md, runtime.local.example.yaml | Historical hardware/model-screen evidence; no current execution authority |
| run_feasibility.py / feasibility.py | Synthetic feasibility harness; real path refuses; not the scientific entry point |
| clsm.pipeline.run | Shared legacy generator-plus-judge orchestrator; NOT the Track-A pilot entry point; preserved for Track B/tests |
| POWER_ANALYSIS.md and analysis/track_a_power_sim* | Historical prospective sensitivity illustrations, not observed pilot results or frozen confirmatory N |
| RESEARCH_PLAN.md, CLAUDE.md | Governing scientific question/integrity rules; early milestone orientation is historical; no changes to Track B |
| literature/DECISION_LOG.md, CITATION_VERIFICATION.md | Historical scientific record preserved. D-066–D-068 add corrections; no new literature review |

## Audit findings resolved / explicitly retained

- The judge-resolution recipe already required English traces first, but the generic manifest
  blocked their collection on judge/audit/ethics. D-066 supplies stage-specific requirements;
  English generation still requires methodology, content evidence and explicit authorization.
- Stale Track-A README claims that preregistration is an unfrozen scaffold and no real backend
  exists are replaced with links to this package. Historical gate dates/configs remain labeled.
- Dataset TODOs previously described a file with no validator or executable path. The canonical
  bundle now validates content and metadata and is required by the actual authorization issuer.
- Prior output-directory examples confused the path with experiment ID; D-017 uses the ID to
  choose hints. ID is frozen and hashed; timestamp/git suffixes are allowed only on output paths.
- The shared orchestrator automatically judges and computes metrics. The new dedicated runner
  performs only collection/parsing; it never invokes that orchestrator's `run()` function.
- The old `_atomic_write` helper retains idempotent replay for existing helper tests; the future
  runner refuses directory/artifact reuse before generation, and new bundle writes are exclusive.
- Timeout byte output was being discarded; D-068 preserves partial output without changing
  retry, parser, stop-reason or shared metric definitions.
- Relevant `TODO`/`FIXME`: downstream judge/ethics/Urdu/translator/confirmatory choices remain
  unresolved; citations remain evidence-qualified. They are not silently marked complete.
- `for_testing_only` / `for_synthetic_test` matches: historical decision text and negative tests,
  not production authorization. `skip_auth` / `test_mode` / `unsafe`: negative tests or research
  prose only. `extra_args`: removed-field tests, history and frozen empty hash marker only.
- No duplicate current scientific execution command exists: use `clsm.track_a_execute` only.
  Track B GPU commands/configs and shared scientific metric definitions are byte-unchanged.

## Remaining readiness boundary

Ready for final human **review of this package**, not for generator execution now. The real
pin, current runtime/path verification and human authorization are still required. Later-stage
scientific decisions are intentionally not manufactured by engineering. Real dataset adapter
layout/label metadata compatibility must be checked during authorized dataset-only preparation;
if it fails, stop for source review without changing the dataset or revision.

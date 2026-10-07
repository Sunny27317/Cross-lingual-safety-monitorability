# 01 — Scientific design audit (Workshop-v1)

**2026-10-06. Branch `research/workshop-v1-paper-readiness`.**

**Sources:** repository documents, engineering records and code, read as written. No
scientific outputs were read: no judge labels, no translations, no human labels.
Translation is running in a separate process and was not touched.

## 1. Design as currently locked

| Element | Locked value | Source |
|---|---|---|
| Research question | Whether an apparent English–Urdu difference in automated disclosure monitoring reflects the rationale text or the monitor | `paper/WORKSHOP_V1_PREPRINT.md` §1, §3; frozen design table |
| Aims (all descriptive) | RQ1 cue sensitivity by language and cue source. RQ2 (primary) monitor-validity gap G on Urdu. RQ3 apparent language gap AG. RQ4 translation contrast R (descriptive only, D-PG-3) | preprint §3; analysis plan |
| Confirmatory hypotheses | **None.** No hypothesis tests | analysis plan §14; D-PG-6 |
| Models | Qwen3-1.7B (GGUF Q8_0, rev `90862c4b`, SHA `061b54da…`; D5 non-thinking). Gemma-3-4B-it (QAT Q4_0 GGUF, rev `15f73f5e`, SHA `76aed0a8…`) | `configs/workshop_v1/models.yaml` |
| Languages | English, Urdu | `languages.yaml` |
| Dataset | `large-traversaal/openbookqa_urdu_final`, rev `e4186f6b` (UrduBench OpenBookQA translation; licence unstated) | dataset summary; card |
| Items | 120 main (manifest `576a991f…`); Cue-B subset 36 (`e18b48b6…`); pilot item excluded; replacement prohibited | manifests |
| Conditions | Control; Cue A (third-party authority) on 120; Cue B (user assertion) on 36 | `prompt_contract.py` |
| Samples | k = 3, seed = sample index | `models.yaml` |
| Generation | 3,312 planned; 3,311 runtime-successful; 1 retained timeout (`9-1065`, Qwen/ur/Cue A/s0); config `7b00e996…` | generation QC and lock; D-PG-2 |
| Direct judging | Falcon-H1-7B-Instruct Q4_K_M (rev `058c8c8f`); Judge V2 (prompt `050ed492…`, spec `a8cb84c1…`); 1,871 tasks (936 EN, 935 UR); **complete and sealed** `3077fae1…`. Result: 1,863 valid, 5 malformed, 3 no-label | stage hashes; judge records (technical counts only) |
| Judge input | Question and options as in the generation prompt (Urdu for Urdu traces) + suggestion + `parsed.reasoning_span` | `direct_judge_launcher._judge_inputs`; verified 1,871/1,871 |
| Translation | IndicTrans2 1B, rev `ac3daf0e…`, toolkit 1.1.1, beams 5, max_length 256, batch 1, CPU fp32. Base `74b81473…` + D-TR-1–6 `3a054e8b…` → effective `106f366c…`. **In progress** (investigator-reported 884/935 successes, 0 unresolved) | contract; amendment; amended authorization |
| Translated judging | Same Judge V2 spec; 935 tasks; executor implemented; **not authorized** | `translated_judge_launcher.py`; template |
| Human reference | 312 traces (240 Cue A, 72 Cue B); 2 native or near-native raters + 1 adjudicator; inputs identical to the judge's; five labels incl. `abstain`; Cohen's κ, no bands; packet v2 built (`human_export/2`); **annotation not authorized (ORPI pending)** | frozen human summary; packet manifest |
| Analysis | D-PG-6: item-cluster percentile bootstrap, B = 10,000, seed 0, paired within replicate, trace-level, models never pooled, Cue B vs Cue A on the shared 36 only. Code frozen by hash `1671bc3c…` (uncommitted) | D-PG-6 record; analysis freeze |
| Compliance | Covariate only; one exploratory ≥ 0.50 recomputation | D-PG-1 |
| Paraphrase control | Not run. R is descriptive only | D-PG-3 |

## 2. Still requires a decision or human action

| Item | Type | Owner |
|---|---|---|
| ORPI determination | Ethics gate | ORPI → investigator |
| Rater recruitment, compensation, consent; whether the investigator rates | Human | Investigator |
| Translation auditor and audit scope (the R primary subset) | Human / design | Investigator |
| Authorizing translated judging | Gate | Investigator |
| Handling the **6 identity-translation rationales** in translated judging (see C1) | Design | Investigator |
| Archival commit (pre-result) | Provenance | Investigator |
| Note on the 1.84 h generation pause | Provenance | Investigator |
| Author, affiliation, acknowledgment consent, funding, release route | Publication | Investigator |

## 3. Contradictions and unresolved issues (reported, not silently resolved)

| # | Contradiction | Evidence | Severity | Proposed resolution (needs approval where marked) |
|---|---|---|---|---|
| C1 | **Six translated traces equal their source.** D-TR-2 makes them identity translations, but `validate_translated_context` raises when the translated trace equals the direct trace, so the translated-judge executor would abort on them | `translated_context.py`; D-TR-2 counts (6 spans with no Arabic-script letter) | **High** (blocks translated judging) | **Decision:** judge them as is (allow identity, recorded with a flag), or record them as missing for T by reason. Then engineering adjusts the validator |
| C2 | The translated-judge preflight and record loader check only the **base** contract. They do not check the effective config, the amendment binding, or a translation stage seal | `translated_judge_launcher.preflight`, `_translation` | Medium | Engineering: require `translation_stage_seal.json` and `effective_translation_config_hash == 106f366c…` on every record used |
| C3 | Human adjudication code vs the frozen protocol: `annotation_io.disagreements()` triggers only on differing labels (protocol: also when either rater abstains), and `validate_adjudications()` rejects `unresolved` (protocol allows it) | `annotation_io.py`; `ADJUDICATOR_INSTRUCTIONS.md`; frozen human summary | Medium (before annotation) | Engineering: align the code with the frozen protocol. No design change |
| C4 | Packet v2 manifest `blinding` flags are all `false`, including `language`, yet rows contain `language` and omit model, condition, item and sample. The flag semantics are ambiguous | packet v2 manifest vs rows | Low | Rename to `exposed_fields` / `hidden_fields`, or document the semantics in the packet README |
| C5 | Codex's `research/WORKSHOP_V1_TRANSLATION_FAILURE_FORENSICS.md` describes 2 failure records, an hf-hub drift, and says "existing authorization remains valid". All three are superseded | vs `WORKSHOP_V1_TRANSLATION_FORENSIC_REVIEW.md` §§1–7 | Low (documentation) | Add a supersession pointer. Do not rewrite |
| C6 | `engineering/indictrans2_segmentation_validation.json` is not valid JSON (it is a Python dict literal), and it predates the amendment (`model_loaded: false`, 1 chunk). The synthetic validation of the amended path (single, 58-unit, boundary and re-split cases) is reported in the forensic review but **not saved as an artifact** | file contents | Medium (Methods placeholder `[[SEGMENTATION_VALIDATION]]`) | After translation finishes, re-run the synthetic validation of the amended path and save it as JSON with hashes. Do not run it while translation is active (CPU contention) |
| C7 | `engineering/provenance/PRE_RESULT_ARCHIVAL_SNAPSHOT_STATE.json` records only the base translator hash `74b81473…`, not the amendment or effective hash, and predates translation execution | file | Low | Supersede with an updated state record at archival time |
| C8 | D-PG-5 (approved text) described an output-overflow "split once more and retranslate". D-TR-5 (2026-10-05) replaces this with fail-closed. The translation-methods kit §1 still states the old rule | decision pack; methods kit | Low (superseded by a dated amendment) | Kit annotated as superseded; manuscript §4.7 now states D-TR-5 |
| C9 | Older judge governance (Claude-side `JUDGE_GOVERNANCE_RECORD.md`) says the judge sees the "English canonical question/options". The implemented direct judge uses the question/options **as in the generation prompt (Urdu for Urdu traces)**, matching D-PG-4 parity | `_judge_inputs`; Methods §4.6 | Low (already executed; manuscript states the implemented behavior) | Record as an erratum in Appendix J |
| C10 | `paper/main.md` still describes MMLU, a GPT/Claude judge shortlist and a confirmatory test | file | Low | Retire, or mark superseded by `paper/WORKSHOP_V1_PREPRINT.md` |
| C11 | Claude-side nominal session dates (10-05 … 10-15) and `models.yaml` "D5 2026-10-05" conflict with artifact timestamps | governance timeline register; errata JSON | Low (documented) | Use artifact timestamps (already done) |
| C12 | The generation and analysis code were run or frozen from an **uncommitted** working tree; no commit exists after `e764072` | git log; freeze record | Medium | Approve the pre-result archival commit; Methods wording already distinguishes executed code from a later snapshot |

The full design history and earlier audits are in:
- `research/WORKSHOP_V1_POST_GENERATION_SCIENTIFIC_AUDIT.md`
- `research/WORKSHOP_V1_PRE_UNSEAL_AUDIT.md`
- `research/WORKSHOP_V1_TRANSLATION_FORENSIC_REVIEW.md`
- `research/WORKSHOP_V1_GOVERNANCE_TIMELINE.md`

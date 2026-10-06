# Workshop-v1 preprint critical path

## Update: ORPI sent; citations closed (2026-10-04)

- **ORPI request sent** (investigator-reported). Waiting for the reply. Templates for each
  outcome are in `docs/ORPI_RESPONSE_TEMPLATES.md`. Item 8 below is done.
- **Citations:**
  - All 8 HIGH items checked. 7 are verified; the Urdu dataset's licence is unstated
    upstream, so item text is not redistributed.
  - Related Work rewritten from verified sources only.
  - References compiled (28 entries).
  - All inline citation placeholders resolved. Item 13 is done, except for re-checking
    on the upload date.
- **Methods audit:** 6 overstatements corrected (stage-approval wording, Qwen sampling
  provenance, serialization causality, uncommitted generation code, analysis-freeze
  tense, "labels existed" → "labels examined").
- **New:**
  - `research/WORKSHOP_V1_AUTHORSHIP_DECISION_SHEET.md`
  - `research/WORKSHOP_V1_RAPID_FILL.md`
  - `research/PREPRINT_FINAL_DAY_QC.md`

## Current waiting list (2026-10-04, latest)

**Newly complete:**
- Synthetic Urdu training examples: native meaning check complete (verbal). All 16 have
  the same meaning, no corrections, no written form. Record:
  `engineering/provenance/AMNA_TRAINING_EXAMPLES_VERBAL_REVIEW_2026-10-04.json`.
- κ cutoff withdrawn.
- Human-validation Methods final.
- ORPI email final.

**WAITING ON COMPUTATION**
1. Direct Falcon judge run (936 EN + 935 UR) to finish, then its post-QC (technical
   states only; labels sealed).

**WAITING ON TRANSLATOR**
2. Gated IndicTrans2 files and their hashes; pinned runtime (device, dtype, package
   versions); translator contract frozen.
3. Wire `validate_translated_context` into the translated-judge execution path.
4. Translate up to 935 traces → translation QC → authorize and run translated judging
   (up to 935) → translation audit.

**WAITING ON ORPI/HUMANS**
5. ORPI written determination. **The email has not been sent.**
6. Recruit 2 raters + 1 adjudicator; consent; compensation; screener; practice set.
7. Double annotation of all 312 (240 Cue-A, 72 Cue-B) → adjudication → agreement
   statistics.

**WAITING ON INVESTIGATOR INPUT**
8. Send the ORPI email.
9. Approve a commit (executed generation code + frozen analysis code) **before** any
   output is unsealed.
10. Re-hash the rater package (the tutorial and review-form notes changed).
11. Decide compensation; choose the auditor; choose acknowledgment A or B (A needs
    Amna's consent).
12. Author info, funding, release scope; note on the 1.84 h pause.
13. Verify the HIGH citations (H1–H8), including reading arXiv:2603.20172.

**WAITING ON RESULTS**
14. A single analysis run → fill the slots per `research/WORKSHOP_V1_RESULTS_FILL_GUIDE.md`
    → Discussion via the decision tree → claim audit → upload checklist.

**True critical path:** 8 → 5 → 6 → 7 → 14. Everything else fits inside the ORPI and
annotation window.

---

## Status update (2026-10-04, later the same day)

**Resolved since the original version:**
- D-PG-6 approved.
- Human packet order fixed to lexicographic blind ID.
- Rater package re-reconciled.
- Analysis contract audited as a synthetic-only static PASS.

**Still true:**
- No git commit exists after `e764072`, so "analysis code frozen by commit" requires a
  commit, with investigator approval, before unsealing.
- Direct judging is running.
- Translation artifacts are unresolved.
- ORPI has not been sent.

**New materials:**
- `docs/ORPI_DETERMINATION_PACKAGE.md`: short and full email.
- `docs/rater_package/RECRUITMENT_KIT.md`.
- `docs/rater_package/TRAINING_TUTORIAL.md`: Urdu examples were later confirmed verbally (see the waiting list above).
- `research/WORKSHOP_V1_RESULTS_WRITING_MATRIX.md`.
- `research/WORKSHOP_V1_DISCUSSION_DECISION_TREE.md`: the κ cutoff was withdrawn;
  agreement is reported continuously.
- `literature/WORKSHOP_V1_CITATION_AUDIT.md`.
- `research/PREPRINT_SUBMISSION_CHECKLIST.md`.

**Project status (judgment, not measurement):**

| Component | Status | Completion |
|---|---|---|
| Manuscript text outside numerical results | complete except placeholders | ≈ 85–90% |
| Scientific-data pipeline (weighted by work and risk) | generation done; direct judging in progress; translation, translated judging, human reference and analysis not started | ≈ 45–50% |
| Total project | — | ≈ 55–60% |

**True critical path:** ORPI determination → recruit 2 raters + 1 adjudicator → 2 × 312
labels → adjudication. Everything else (translation, translated judging, analysis code
commit, citation verification) fits inside that window.

The two estimates above are judgments, not measurements.

---

**2026-10-04.** State at writing:
- Generation is locked (3,312 records; 3,311 runtime successes; 1 timeout retained).
- D-PG-1..5 are approved.
- Judge V2 is frozen (prompt `050ed492…`, spec `a8cb84c1…`), and direct judging (936 EN +
  935 UR) is authorized and **running**. Its outputs have not been inspected for this
  document.
- Translation is not frozen: gated artifacts and runtime versions are outstanding.
- Translated judging is not authorized.
- ORPI has not been contacted, as far as the repository records.
- No annotation or analysis has happened.

The **critical path is the human reference**: ORPI → recruitment → 2 × 312 labels →
adjudication. Everything automated can finish while that runs, provided outputs stay
sealed from anyone who rates.

## MUST BEFORE PREPRINT

### Governance and provenance
- [ ] Commit the governance set, with approval, so that it is dated before any output is
  inspected: interpretation framework (lock line signed), decision pack, approvals
  record, final claim ledger.
- [ ] Approve D-PG-6 (bootstrap B and seed; paired-replicate rule) **before** unsealing
  any judge output.
- [ ] Record the cause of the 1.84 h pause on 2026-10-03.
- [ ] Archive the executed generation code state (commit, plus implementation hashes) and
  cite it.
- [ ] Add a data-dictionary note on `population_role` and a dated erratum for the
  misdated records (D5 "2026-10-05"; Claude-side session dates).
- [ ] Native sign-offs for the cue and language-instruction wording are attached, or
  Methods uses the "verbal approval" wording (C3b).

### Judging (running)
- [ ] Direct run completes. The technical-state census is recorded by arm × language ×
  model × cue without opening labels for interpretation.
- [ ] Before T judging, verify **D-PG-4 criterion 6** in the translated-arm
  implementation: the question, options and suggestion for T are byte-identical to the
  D_ur input, and only the trace differs.
- [ ] T judging (≤935) is authorized and run after translation, under the same spec hash.

### Translation
- [ ] Obtain the gated IndicTrans2 files, archive their hashes, and pin
  Transformers/PyTorch/sentencepiece versions, device and dtype. Freeze the translator
  contract hash.
- [ ] Validate segmentation on non-study text (including a long synthetic trace).
  Authorize translation, translate ≤935, and record failures by reason.
- [ ] Translation-artifact audit on the translations entering H/D/T triples: name the
  auditor and fix the scope. The auditor must not be a rater, or must audit only after
  completing their rating.

### Human reference
- [ ] **Send the ORPI email** (`docs/ORPI_DETERMINATION_PACKAGE.md`) and save the reply.
- [ ] Recompute `engineering/rater_package_reconciliation.json` hashes. The 2026-10-04
  parity edits changed `RATER_INSTRUCTIONS.md`, `RATER_ONBOARDING.md`,
  `ADJUDICATOR_INSTRUCTIONS.md` and `RATER_QUALIFICATION_TEMPLATE.md`.
- [ ] Confirm the exported packet order is by blind ID or a recorded random permutation.
  Ordering by model or cue would weaken blinding.
- [ ] Recruit 2 raters and 1 adjudicator (`RECRUITMENT_MESSAGE.md`). Record
  qualification, consent and compensation. Run the practice set.
- [ ] Complete double annotation of all 312; lock submissions; adjudicate; compute κ per
  `AGREEMENT_REPORTING.md`. The 12-block capacity contingency is used only with a stop
  date recorded before annotation.

### Analysis
- [ ] Freeze the analysis code (commit) and validate it on synthetic data. Then unseal
  and run the full plan once.
- [ ] All planned comparisons go into tables and the appendix, regardless of direction.

### Manuscript
- [ ] Fill every `[[R-…]]` slot from analysis outputs only. Select Discussion branches by
  framework §3. Delete unselected branches.
- [ ] Claim audit: every abstract, results, discussion and conclusion sentence maps to a
  SUPPORTED ledger row.
- [ ] Fill every `[[PENDING]]` with a verified fact, or remove it.
- [ ] Citations: verify Gemma 3, Falcon-H1, IndicTrans2, OpenBookQA and the dataset
  provenance (UrduBench link), plus a fresh literature check. Mark anything unverifiable
  `TODO — UNVERIFIED` or remove it.
- [ ] `paper/main.md` is retired or reconciled. It still describes MMLU, a closed-model
  judge and a confirmatory test.

### Author checklist (each author confirms in writing)
- [ ] Name, affiliation and email are exact. No Harvard affiliation. No faculty
  supervision unless confirmed by that faculty member.
- [ ] Each author has read the full text and the claim ledger.
- [ ] No result is reported that was not produced by an executed, provenance-bound run.
- [ ] Ethics statement matches the ORPI determination verbatim.
- [ ] Acknowledgments: the native reviewer's and raters' names are included only with
  their consent. Otherwise use pseudonyms or roles.
- [ ] Funding and competing interests are stated: "none" if none.
- [ ] Data and code availability links resolve. Dataset text is not redistributed.
- [ ] LLM-assistance disclosure per the target server's or venue's policy.
- [ ] Preprint server category and licence chosen.

## CAN HAPPEN IN PARALLEL (now)

1. Send ORPI and line up rater candidates (no onboarding before the reply).
2. Obtain the translator artifacts, pin the runtime, validate segmentation.
3. Fix the rater-package hashes and export ordering; build the practice set from non-study
   passages.
4. Finalize the analysis code against the contract, run synthetic validation, freeze it.
5. Build figure and table templates from synthetic data (labelled synthetic; never
   committed into `results/`).
6. Verify citations; write Related Work prose from verified entries.
7. Write the provenance errata, archive the code state, record the pause note.

**Order once inputs exist:**
1. Direct judging finishes (sealed).
2. Translation, then T judging (sealed).
3. ORPI reply, then annotation.
4. Adjudication and κ.
5. Translation audit.
6. Analysis (single unsealing).
7. Fill the slots, choose branches, audit claims.
8. Internal read.
9. Post.

## OPTIONAL FOR LATER VENUE SUBMISSION

- English→English paraphrase control and an English human anchor. Any version specified
  after D/T outputs were seen is labelled exploratory.
- Backup-translator (NLLB) robustness; back-translation diagnostic.
- Additional cue wordings per source; additional models or languages (a new study, not
  an extension of this one's claims).
- Extended related work, venue formatting, camera-ready figures, archival DOI.

## Engineering notes found during this pass (no effect on any running stage)

- `direct_judge_launcher._judge_inputs` uses the final-instruction marker
  `"\n\nअपने جواب کو"`. Its first word is in **Devanagari** script, not Urdu (`اپنے`).
  For cued traces this is harmless, because the item block is split at the cue sentence
  first. For any Control-condition use it would fail closed. Fix it before reusing the
  function outside cued traces. **Do not alter it mid-run.**
- The parity export (`human_pool.parity_export_rows`) emits rows in candidate order
  (model → cue → item) unless the caller shuffles them. See "Human reference" above.

## Manuscript work remaining after numbers arrive

| Task | Share of remaining text work |
|---|---|
| Generate Tables 1–8, S1–S6, Figures 2–4 from frozen code | mostly scripted |
| Fill result slots (§5, abstract, intro summary, conclusion) | ~30% |
| Select and edit Discussion branches; delete the rest | ~25% |
| Claim audit against the ledger | ~15% |
| Ethics, authors, availability, citations, appendix assembly | ~20% |
| Final internal read and consistency pass | ~10% |

Pre-results text is about **75–80% complete** by volume and structure. The remaining
20–25% depends entirely on results. If the outputs exist and pass QC, it is roughly a few
focused working days. That is an engineering estimate, not a commitment. A complicated
result (several branches applying, H–K edge cases) adds editing time but no new
structure.

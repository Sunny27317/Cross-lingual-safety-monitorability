# Workshop-v1 translated judging: definitive pre-authorization checklist

**Status: NOT AUTHORIZED. The independent audit is NOT passed.** Last updated 2026-10-06.
This is the only checklist for authorizing translated judging, and it replaces scattered
partial lists. Each box is ticked only from on-disk evidence. Engineering may tick only
the boxes marked *(eng)*. Boxes marked *(investigator)* or *(independent auditor)* belong
to those people alone.

## A. Engineering fixes (branch `research/workshop-v1-post-translation-pipeline`; uncommitted)

- [x] *(eng)* **Single seal writer.** The seal is written only by `translator_launcher --seal`. The `post_translation_pipeline --seal-translation` path is removed, and a regression test proves no second writer is reachable.
- [x] *(eng)* **Seal v2 schema.** Binds:
  - population 935;
  - the population hash and its recipe;
  - task and artifact manifests;
  - canonical QC and its hash;
  - base, amendment and effective config hashes;
  - operative and historical authorizations;
  - executed launcher `8f7c241a…`, with the current launcher hash recorded separately;
  - the final stage hash.
- [x] *(eng)* **Gate recomputes the seal from disk.** It checks 15 conditions. There are 12 required negative cases plus extras, and each asserts the judge backend is called 0 times (`tests/workshop_v1/test_canonical_seal_gate.py`).
- [x] *(eng)* **Judge outputs persist provenance:** identity, changed, reason, stage hash, effective hash, record SHA-256.
- [x] *(eng)* **G7 fixed:**
  - one row per task;
  - retry merge;
  - deterministic terminal attempt;
  - identity provenance in the analysis table;
  - reproducible `analysis_input_layer_sha256`;
  - superseding addendum `research/WORKSHOP_V1_PRE_RESULT_ANALYSIS_FREEZE_ADDENDUM_V2.json`.
- [x] *(eng)* **C1 identity QC:**
  - hash identity is recomputed from the source span and the translated text;
  - zero Urdu letters;
  - at most 6;
  - deterministic membership;
  - an Urdu-letter identity fails.
- [x] *(eng)* **C6.** Non-model amended-path validation artifact `engineering/indictrans2_amended_path_validation_2026-10-06.json` (`22372034…`): **PASS**, 935/935 replayed, 0 failures. The historical artifact is untouched.
- [x] *(eng)* **C7.** Superseding provenance record `engineering/provenance/TRANSLATION_STAGE_PROVENANCE_2026-10-06.json`. The base hash is no longer presented as the final effective configuration.
- [x] *(eng)* **C9 erratum:** `engineering/provenance/C9_JUDGE_INPUT_ERRATUM_2026-10-06.json`.
- [x] *(eng)* **C10.** `paper/main.md` is marked SUPERSEDED and points to `paper/WORKSHOP_V1_PREPRINT.md`.
- [x] *(eng)* **Human hardening:**
  - immutable atomic rater and adjudication writes;
  - frozen H mapping (primary, S1, S2);
  - the adjudicator's independent first label is required.
- [x] *(eng)* **Checks pass:** full test suite (815 passed), Ruff and mypy on all changed files, `git diff --check`. Pre-existing findings in untouched files are listed in the engineering report.

## B. Stage operations (technical; run in this order; each must exit 0)

- [x] *(eng)* Canonical QC on the real stage, read-only, 2026-10-06:
  - PASS;
  - 935 successes;
  - 0 unresolved failures (6 historical failure records);
  - 6 identity translations;
  - 0 QC errors.
- [ ] *(eng)* `PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --seal`. This writes the immutable canonical seal; it is **not yet run**.
- [ ] *(eng)* `… translator_launcher --verify-seal`, which must print `valid: true`.
- [ ] *(eng)* `… translated_judge_launcher --preflight`, which must print `ready: true` and a `translation_stage_hash`.
- [ ] *(eng)* Record the seal file's SHA-256 and the `translation_stage_hash` in the governance timeline.

## C. Governance (not engineering)

- [ ] *(investigator)* Approve the pre-result archival commit of the branch (code hashes as recorded) **before** authorization. Until then, executed code is identified by content hash only.
- [x] *(investigator)* **Decide C1.** Recorded 2026-10-06, pre-result:
  `engineering/provenance/C1_IDENTITY_TRANSLATION_DECISION_2026-10-06.json`. The six D-TR-2
  identity translations stay in the primary translated arm, are judged as-is, are not
  treated as missing, and keep identity provenance downstream.
- [x] *(investigator)* **Robustness addendum.** Recorded 2026-10-06, pre-result:
  `research/WORKSHOP_V1_PRE_RESULT_IDENTITY_ROBUSTNESS_ADDENDUM.json`. An exclude-six
  analysis is secondary and robustness-only. It does not replace the primary analysis or
  change the estimands or the statistical plan.
- [ ] *(investigator)* Commit both records with the reviewed branch before sealing, so the
  identity decision predates the seal in git history.
- [ ] *(independent auditor)* Independent audit of sections A and B against disk. **Not passed. Engineering does not tick this box.**
- [ ] *(investigator)* Write `engineering/INVESTIGATOR_TRANSLATED_URDU_JUDGE_AUTHORIZATION.json` with:
  - `authorized: true`, `status: APPROVED`;
  - `translated_urdu_tasks: 935`;
  - the Judge V2 `prompt_hash` `050ed492…`;
  - `output_directory: experiments/_runs/workshop-v1-translated-urdu-judge`;
  - `translation_stage_hash` equal to the value printed at B.3.
- [ ] *(eng)* `validate_authorization` returns `valid: true` against the sealed stage.

## D. Explicitly out of scope until C is complete

Translated judging, any model call, human annotation, final analysis and inspection of
any scientific outcome.

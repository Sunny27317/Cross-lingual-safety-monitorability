# Workshop-v1 canonical scientific index (start here; 2026-10-07)

This lists the **current authoritative** document for each topic. Everything else in
`research/` is working material or history. Nothing is deleted. Superseded files stay for
provenance, and the table in §2 points each one to its current source. Engineering
records live in `engineering/` and `engineering/provenance/`.

## 1. Current authoritative sources

| Topic | Authoritative source(s) |
|---|---|
| **Study design (paper text)** | `paper/WORKSHOP_V1_PREPRINT.md` §§3–4 |
| Item population | `engineering/workshop_v1_main_manifest.json` (`576a991f…`), `engineering/workshop_v1_cue_b_manifest.json` (`e18b48b6…`); native item review: the item-equivalence review closure record in `engineering/` (`*_urdu_equivalence_review_closure.json`; gate PASS) |
| Model specifications | `configs/workshop_v1/models.yaml`; generation configuration `engineering/workshop_v1_generation_config.json` (`7b00e996…`) |
| Generation | `experiments/_runs/workshop-v1-main-attempt-2/generation_data_lock.json` (stage `7b00e996…`); timeout rule D-PG-2 |
| Direct judge | `configs/workshop_v1/judge_model.yaml`, `configs/workshop_v1/judge_contract.json`, Judge V2 prompt `engineering/workshop_v1_judge_prompt_v2.json` (`050ed492…`); seal `engineering/workshop_v1_direct_judge_stage_seal_v2.json` (`3077fae1…`) |
| Translation | `engineering/indictrans2_final_contract.json` (base `74b81473…`) + `engineering/indictrans2_contract_amendment_DTR_2026-10-05.json` (D-TR-1–6); effective `106f366c…`; seal stage hash `14175ab5…`; provenance `engineering/provenance/TRANSLATION_STAGE_PROVENANCE_2026-10-06.json`; C6 validation `engineering/indictrans2_amended_path_validation_2026-10-06.json` |
| Identity translations | Record A `engineering/provenance/C1_IDENTITY_TRANSLATION_DECISION_2026-10-06.json`; Record B `research/WORKSHOP_V1_PRE_RESULT_IDENTITY_ROBUSTNESS_ADDENDUM.json` |
| Translated judge | Authorization `engineering/INVESTIGATOR_TRANSLATED_URDU_JUDGE_AUTHORIZATION.json` (`267b6735…`); QC `engineering/workshop_v1_translated_urdu_judge_post_qc.json`; seal `engineering/workshop_v1_translated_urdu_judge_stage_seal.json` (`seal_sha256` `ca85f8d2…`). The QC and seal records are in the main worktree and still to be committed |
| Human annotation | **`research/WORKSHOP_V1_HUMAN_ANNOTATION_CANONICAL_PROTOCOL.md`**; packet: `research/WORKSHOP_V1_RATER_PACKET_FINAL_SPEC.md`; consent template in `…HUMAN_ANNOTATION_FINAL_PACKAGE.md` §6; plus the frozen rater documents in `docs/rater_package/` (hashes in `engineering/rater_package_reconciliation.json`); summary `research/WORKSHOP_V1_HUMAN_STAGE_FROZEN_SUMMARY.md` |
| Ethics / ORPI | `research/WORKSHOP_V1_ORPI_SUBMISSION_PACKET.md`, `research/WORKSHOP_V1_ORPI_CLARIFICATION_RECORD.md`, `research/WORKSHOP_V1_ORPI_RESPONSE_PLAYBOOK.md`; request record `engineering/provenance/ORPI_REQUEST_SENT_2026-10-04.json` |
| **Analysis authority (ordered)** | 1. `research/frozen_sources/ANALYSIS_PLAN_FREEZE.md`; 2. D-PG-1 to D-PG-6 (`engineering/provenance/INVESTIGATOR_DOWNSTREAM_APPROVALS_2026-10-04.json`, `DPG6_APPROVAL_2026-10-04.json`); 3. Records A and B; 4. `docs/rater_package/AGREEMENT_REPORTING.md`; 5. `research/WORKSHOP_V1_INTERPRETATION_FRAMEWORK.md` (locked, `ac28af75…`). Governance: `engineering/provenance/WORKSHOP_V1_ANALYSIS_GOVERNANCE_D-FA_2026-10-06.json`, `…_D-FA-6_2026-10-06.json` |
| Primary estimand and sensitivities (readable guide) | `research/WORKSHOP_V1_CANONICAL_ANALYSIS_SPECIFICATION.md` (derived; no authority of its own); worked example `research/WORKSHOP_V1_G_WORKED_EXAMPLE.md` |
| **Analysis code** | `src/clsm/workshop_v1/final_analysis.py` (`9b1797bc…`), `final_analysis_loader.py`, `final_tables.py`; freeze **V4** `research/WORKSHOP_V1_FINAL_ANALYSIS_FREEZE_V4_2026-10-07.json` and its commit binding (V3 `c35785cd` superseded but retained). The primitives `analysis.py`/`metrics.py` (`1671bc3c…`) are unchanged |
| Data contract | `research/WORKSHOP_V1_FINAL_ANALYSIS_DATA_CONTRACT.md` |
| Unseal procedure | `research/WORKSHOP_V1_RESULT_UNSEAL_PROTOCOL.md` + **Addenda A1 and A2** (`…_ADDENDUM_A1_2026-10-07.md`, `…_ADDENDUM_A2_2026-10-07.md`); checklist `research/WORKSHOP_V1_FINAL_PRE_UNSEAL_CHECKLIST.md` |
| Second judge (prospective; not run) | `research/WORKSHOP_V1_SECOND_JUDGE_ROBUSTNESS_PROTOCOL.md`; recommendation `…SECOND_JUDGE_FINAL_RECOMMENDATION.md` |
| Translation audit (S4) | `research/WORKSHOP_V1_TRANSLATION_AUDIT_CANONICAL_PROTOCOL.md` (`audit_flag` = proposed D-FA-7) |
| Tables and figures | `research/WORKSHOP_V1_FINAL_TABLES_FIGURES_SPEC.md` |
| Final audit / submission | `research/WORKSHOP_V1_FINAL_SCIENTIFIC_AUDIT_2026-10-07.md`; `research/WORKSHOP_V1_SUBMISSION_MASTER_CHECKLIST.md` |
| Paraphrase control (decision memo) | `research/WORKSHOP_V1_PARAPHRASE_CONTROL_DECISION.md` |
| **Paper** | `paper/WORKSHOP_V1_PREPRINT.md` (canonical manuscript). Results scaffold `paper/WORKSHOP_V1_RESULTS_SCAFFOLD.md` |
| Claims | `research/WORKSHOP_V1_CLAIM_LADDER_FINAL.md` (safe / conditional / prohibited); detail `…CLAIM_LEDGER_V2.md`; audit `…FINAL_CLAIM_HARDENING_AUDIT.md` |
| Discussion | Selection: framework §3. Wording: `research/WORKSHOP_V1_DISCUSSION_DECISION_TREE_FINAL.md` |
| Governance timeline | Publication: `research/WORKSHOP_V1_ONE_PAGE_GOVERNANCE_TIMELINE.md`. Full detail (Appendix J): `research/WORKSHOP_V1_GOVERNANCE_TIMELINE.md` |
| Reproducibility | `paper/WORKSHOP_V1_DATA_ETHICS_REPRODUCIBILITY.md`; stage seals listed above |
| Release | `research/WORKSHOP_V1_PREPRINT_RELEASE_GUARD_V2.md` |
| Venue | `research/WORKSHOP_V1_PUBLICATION_POSITIONING.md` |

## 2. Superseded or working documents (kept; do not cite)

| File | Status | Use instead |
|---|---|---|
| `paper/main.md` | SUPERSEDED (banner) | `paper/WORKSHOP_V1_PREPRINT.md` |
| `paper/WORKSHOP_V1_MANUSCRIPT_DRAFT.md` | SUPERSEDED (earlier draft) | the preprint |
| `paper/WORKSHOP_V1_METHODS_FINAL.md`, `…LIMITATIONS_FINAL.md`, `…INTRODUCTION_FINAL.md`, `…OUTCOME_BLIND_DRAFTS.md`, `…DATA_ETHICS_REPRODUCIBILITY.md` | Drafts. Their substance was merged into the preprint by targeted edits on 2026-10-07; the preprint's existing, more detailed text was kept where it was already accurate | the preprint |
| `research/WORKSHOP_V1_DISCUSSION_DECISION_TREE.md` | SUPERSEDED | V2 + `WORKSHOP_V1_DISCUSSION_SCENARIOS.md` |
| `research/WORKSHOP_V1_CLAIM_LEDGER_FINAL.md` | SUPERSEDED | Claim ladder + ledger V2 |
| `research/WORKSHOP_V1_PREPRINT_RELEASE_GUARD.md` | SUPERSEDED (its `may_post` stays false) | Release guard V2 |
| `research/WORKSHOP_V1_PRE_RESULT_ANALYSIS_FREEZE_ADDENDUM.json` | SUPERSEDED | `…_ADDENDUM_V2.json` (analysis-input builder) |
| `research/WORKSHOP_V1_PRE_RESULT_ANALYSIS_IMPLEMENTATION_ADDENDUM.json` | SUPERSEDED (proposal) | Freeze V3 |
| `research/WORKSHOP_V1_FINAL_ANALYSIS_FREEZE_2026-10-06.json`, `…_V2_…json`, `…_V3_2026-10-07.json` (+ V3 binding) | SUPERSEDED | Freeze V4 + commit binding |
| `research/WORKSHOP_V1_DISCUSSION_SCENARIOS.md` | Background | `…DISCUSSION_DECISION_TREE_FINAL.md` |
| `research/WORKSHOP_V1_HUMAN_ANNOTATION_FINAL_PACKAGE.md` | Superseded, except §6 (consent template) and §7 | `…HUMAN_ANNOTATION_CANONICAL_PROTOCOL.md` |
| `engineering/provenance/ANALYSIS_CODE_FREEZE_2026-10-04.json` | Still valid for the primitives only | Freeze V3 for the full implementation |
| `research/WORKSHOP_V1_GOVERNANCE_DECISION_PACK.md`, `WORKSHOP_V1_DPG6_APPROVAL_BLOCK.md` | Proposals; the approvals live in the JSON records | D-PG approval JSONs |
| `research/WORKSHOP_V1_TERMINOLOGY.md` | Current (Appendix A1), extended by | `…TERMINOLOGY_POLICY_V2.md` |
| `research/WORKSHOP_V1_PUBLICATION_STRATEGY.md`, `…SUBMISSION_LADDER.md`, `…VENUE_LADDER_V2.md`, `…PHD_AND_POSITIONING.md` | SUPERSEDED | `…PUBLICATION_POSITIONING.md` |
| `research/WORKSHOP_V1_HUMAN_STAGE_ORPI_READINESS.md`, `…HUMAN_VALIDATION_OPERATIONS.md` | Working | `…HUMAN_ANNOTATION_FINAL_PACKAGE.md`, `…HUMAN_STAGE_FINAL_READINESS.md` |
| `research/WORKSHOP_V1_PRE_RESULT_METHODS_COMPLETION.md`, `…OVERNIGHT_REPORT_2026-10-06.md`, `research/paper_readiness/*`, `…RAPID_FILL.md`, `…PARALLEL_PREPRINT_ACCELERATION.md`, `…DOCUMENT_RECONCILIATION.md`, `…POST_*_RECONCILIATION.md` | Working / historical | this index |
| `literature/DECISION_LOG.md` (three divergent copies) | Not analysis authority (D-FA-1) | §1 |
| Claude-side files in other worktrees (e.g. `HUMAN_VALIDATION_PROTOCOL.md`) | Not in this repository; nominal session dates | §1 |

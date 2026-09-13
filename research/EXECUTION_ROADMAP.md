# Execution roadmap — current state to submission

One list, five categories, in dependency order within each. Cross-references only; full
detail lives in the cited files. Nothing in category 1 requires any item in category 2.

## 1. AUTOMATABLE NOW (no human decision, no real data; engineering — currently Codex's lane)

- **Done as of PR #27 commit `23f0718`:** confirmatory-item-ID English-anchor coverage
  (`research/FINAL_PROTOCOL.md` §1), source/rendered/judge-input language separation
  (§2), the judge-acceptance hard gate, and the ≥2,000-simulation/1,000-replicate ADEMP
  upgrade (§3's minimum standard, met on repetition/replicate counts).
- **Still open (`research/FINAL_PROTOCOL.md` §1a):** the ADEMP report must explicitly
  state whether each null scenario's Monte Carlo interval contains nominal alpha/
  coverage — two of three currently do not, undisclosed in the report text; and
  `StageGateLedger`'s G4 gate needs a population-scoped `subject_hash` so a
  calibration-only reference cannot be mistaken for the confirmatory Urdu reference.
- Any further engineering scaffolding that touches no real dataset, model, judge, or
  translator call — e.g., wiring the `JudgeAcceptanceCriteria` sign-off table (`experiments/
  M2-Monitor-Validation/JUDGE_SELECTION_RECORD_TEMPLATE.md`) into the actual calibration
  CLI so it refuses to run without a completed, hashed sign-off file.

**Scientific/paper/human-package side (this pass, complete):** the canonical protocol
(`research/FINAL_PROTOCOL.md`), the operational rater package (`docs/rater_package/`),
Urdu translator/reviewer package (`docs/TRANSLATOR_INSTRUCTIONS.md`, `docs/
BILINGUAL_REVIEWER_INSTRUCTIONS.md`, `docs/URDU_EQUIVALENCE_DECISION_TREE.md`), judge
rubric package (`experiments/M2-Monitor-Validation/JUDGE_RUBRIC_PACKAGE.md`), ethics
request/consent drafts, reproducibility release plan, result interpretation matrix, and
paper scaffold (`paper/main.md`) are all complete and require no further engineering to
be handed to a supervisor or recruited humans.

## 2. HUMAN-REQUIRED (blocks everything after it; see `research/SUPERVISOR_DECISION_PACKET.md`)

In dependency order:
1. Institutional ethics/IRB determination (packet row 1; submit `docs/
   ETHICS_REVIEW_REQUEST_TEMPLATE.md`, completed).
2. Rater recruitment, qualification (`docs/rater_package/
   RATER_QUALIFICATION_TEMPLATE.md`), compensation, consent (`docs/
   RATER_CONSENT_TEMPLATE.md`, only after institutional review) (packet rows 2–3).
3. Judge calibration numeric acceptance criteria, signed before any candidate output
   (packet row 6; form in `experiments/M2-Monitor-Validation/
   JUDGE_SELECTION_RECORD_TEMPLATE.md`).
4. Translator selection criteria approval (packet row 7).
5. Urdu rubric-language approval (packet row 8).
6. Storage/release governance sign-off (packet row 4).
7. SESOI, alpha, target power, multiplicity (packet rows 9–11).
8. Final go/no-go (packet row 13).

## 3–5. Master after-approval sequence (exact order — no further planning round needed)

Once every category-2 row is signed, this is the entire remaining sequence to
submission, in strict order. Each step names what gates it and what it produces; no
step is started before its listed gate is satisfied. This replaces any need to
re-derive an execution plan later.

1. **Judge calibration run**, both registered candidates, against the locked
   English-calibration human reference (`research/HUMAN_EXECUTION_CHECKLIST.md` steps
   1–6, 8–14 on the calibration population) — gated on packet row 6 (signed criteria)
   and row 5 (candidates named). Produces: `experiments/M2-Monitor-Validation/
   JUDGE_CALIBRATION_REPORT_TEMPLATE.md`'s filled structure.
2. **Judge selection lock** — investigator reads step 1's report and records
   accept/reject per candidate (`finalize_calibration_acceptance`) — gated on step 1.
   Produces: a locked, signed judge specification for `D` and `T`.
3. **Translator selection lock** — investigator selects a translator against the
   criteria in packet row 7 (no calibration data required first, since translator
   adequacy is assessed on a separate held-out set per `experiments/M3-English-Urdu/
   TRANSLATION_PROTOCOL.md`) — gated on packet row 7. Can run in parallel with steps
   1–2. Produces: a locked `TranslatorSpec`.
4. **Urdu item translation, bilingual review, and adjudication** — `docs/
   TRANSLATOR_INSTRUCTIONS.md` → `docs/BILINGUAL_REVIEWER_INSTRUCTIONS.md` → `docs/
   URDU_EQUIVALENCE_DECISION_TREE.md`, one `docs/URDU_ITEM_EQUIVALENCE_FORM.md` per
   item — gated on packet row 8 (rubric-adjacent Urdu wording, if used) and reviewer
   availability. Can run in parallel with steps 1–3. Produces: locked Urdu item set.
5. **Urdu generator run** — a separate, freshly authorized Track-A-style stage; the
   English pilot's authorization does not extend here — gated on step 4 (items must be
   locked before generation) and a fresh, explicit human authorization token, per every
   prior Track-A decision. Produces: the actual Urdu reasoning traces.
6. **Urdu human-reference collection** — `research/HUMAN_EXECUTION_CHECKLIST.md` steps
   7 (already done in step 5, here just the annotation half: 1–4, 6, 8–14) on the Urdu
   population — gated on step 5 (traces must exist) and packet rows 1–3 (ethics,
   recruitment, compensation, already resolved in category 2). Produces: a locked
   `LockedReference` tagged as the Urdu confirmatory-population reference (see
   `research/FINAL_PROTOCOL.md` §1a finding 2 on why the tag is necessary).
7. **Direct judge scoring (`D`)** on the Urdu traces — gated on steps 2 and 5.
8. **Translation diagnostic** (Urdu→English via step 3's locked translator; English
   paraphrase control on the English anchor; native/bilingual equivalence audit) —
   gated on steps 3 and 5. Produces: `T`, `P`, and the audit records.
9. **Confirmatory design freeze** — SESOI/alpha/power/multiplicity already signed
   (packet rows 9–11); N computed via the §3-validated simulation method (gated on
   Codex's two open fixes, `research/FINAL_PROTOCOL.md` §1a, being resolved and
   re-validated) crossed with actual step-6 rater capacity. Produces: a filled,
   locked `experiments/M4-Confirmatory/CONFIRMATORY_PREREG_TEMPLATE.md`, filed
   **before** step 10.
10. **Compute `G`, `R`, and the agreement-recovery diagnostic** on the complete,
    locked confirmatory sample — gated on steps 6, 7, 8 all complete and step 9 filed.
11. **Run the one preregistered confirmatory test/interval**, once, against the frozen
    N — gated on step 9's preregistration being filed before this step, not after.
12. **Run every preregistered sensitivity analysis** (original-rater vs. adjudicated;
    `partial`-label mappings; complete-pair vs. common-triple; equal-item weighting) —
    descriptive, alongside, not instead of, steps 10–11.
13. **Publish** `experiments/M3-English-Urdu/REPORT_TEMPLATE.md`, filled.
14. **Populate `paper/main.md` Results** with steps 10–13's outputs only — no earlier
    draft numbers, ever.
15. **Write Discussion**, matching the actual pattern against `research/
    RESULT_INTERPRETATION_MATRIX.md` — not against an assumed direction.
16. **Write Conclusion**, scoped to exactly what step 14 supports; cross-check every
    sentence against `research/FINAL_CLAIM_AUDIT.md` before finalizing wording.
17. **Populate `paper/tables/` and `paper/figures/`** from the same hash-verified
    artifacts, per their existing READMEs.
18. **Final claim-ledger check** (`paper/main.md` §Claim ledger and `research/
    FINAL_CLAIM_AUDIT.md`) against the actual analysis output — the last check before
    submission.
19. **Select a venue tier** per `research/FINAL_SCIENTIFIC_READINESS.md` §"Publication
    strategy", only once the result's strength is actually known.

Steps 1–4 can run in parallel with each other. Step 5 (generation) blocks step 6
(annotation) — this ordering bug existed in an earlier draft of this roadmap and is
corrected here. Steps 7–8 can run in parallel with each other, both after step 5.
Step 9 can be prepared in parallel with steps 5–8 but must be *filed* before step 10.

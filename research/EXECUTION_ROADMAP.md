# Execution roadmap — current state to submission

One list, five categories, in dependency order within each. Cross-references only; full
detail lives in the cited files. Nothing in category 1 requires any item in category 2.

## 1. AUTOMATABLE NOW (no human decision, no real data)

- Fix PR #27's English-anchor gap exactly as specified in `research/FINAL_PROTOCOL.md` §1;
  add the `judge_input_language` field per §2; add both tests.
- Run the minimum-standard simulation validation (`research/FINAL_PROTOCOL.md` §3) across
  the specified scenario grid at 1,000+ bootstrap replicates / 2,000+ simulations per
  scenario; publish the resulting operating-characteristics report.
- Add the D-074 decision-log entry for this pass (done, this branch).
- Any further engineering scaffolding that touches no real dataset, model, judge, or
  translator call — e.g., wiring the `JudgeAcceptanceCriteria` sign-off table (`experiments/
  M2-Monitor-Validation/JUDGE_SELECTION_RECORD_TEMPLATE.md`) into the actual calibration
  CLI so it refuses to run without a completed, hashed sign-off file.

## 2. HUMAN-REQUIRED (blocks everything after it; see `research/SUPERVISOR_DECISION_PACKET.md`)

In dependency order:
1. Institutional ethics/IRB determination (packet row 1).
2. Rater recruitment, qualification, compensation, consent (packet rows 2–3).
3. Judge calibration numeric acceptance criteria, signed before any candidate output
   (packet row 6; form in `experiments/M2-Monitor-Validation/
   JUDGE_SELECTION_RECORD_TEMPLATE.md`).
4. Translator selection criteria approval (packet row 7).
5. Urdu rubric-language approval (packet row 8).
6. Storage/release governance sign-off (packet row 4).
7. SESOI, alpha, target power, multiplicity (packet rows 9–11).
8. Final go/no-go (packet row 13).

## 3. AUTOMATABLE AFTER HUMAN APPROVAL (each gated on the specific row above)

- Judge calibration run against the two candidates (gated on 2.3), producing the report
  in `experiments/M2-Monitor-Validation/JUDGE_CALIBRATION_REPORT_TEMPLATE.md`'s structure.
- Judge selection lock (gated on the calibration report + packet row 5).
- Urdu item translation + independent bilingual review, using `docs/
  URDU_ITEM_EQUIVALENCE_FORM.md` per item (gated on 2.2 for raters/reviewers and 2.5 for
  rubric wording — translation review needs the same qualified bilingual reviewers).
- Human annotation collection on locked Urdu traces, once traces exist (gated on 2.1–2.2
  and the Urdu generator authorization, which is a **separate** stage authorization from
  English, per every prior Track-A decision).
- Urdu generator run (a **separate**, freshly authorized Track-A-style stage; not covered
  by the English pilot's authorization; requires its own frozen config and human
  authorization token, structurally identical to but independent of the English one).
- Translation diagnostic run (Urdu→English, English paraphrase control, backtranslation
  if used) — gated on 2.4 and on Urdu traces existing.
- Native/bilingual translation-equivalence audit — gated on 2.2.
- Confirmatory N computation — gated on 2.7 and on the §3 simulation validation from
  category 1.

## 4. FINAL ANALYSIS (gated on every item in category 3 being complete)

- Compute `G`, `R`, and the agreement-recovery diagnostic on the locked confirmatory
  sample, per `research/FINAL_PROTOCOL.md` §4.
- Run the one preregistered confirmatory test/interval (per `experiments/M4-Confirmatory/
  CONFIRMATORY_PREREG_TEMPLATE.md`, filled and locked before this step).
- Run all preregistered sensitivity analyses (original-rater vs. adjudicated; partial-label
  mappings; complete-pair vs. common-triple; equal-item weighting) — descriptive, run
  alongside, not instead of, the primary.
- Publish the completed `experiments/M3-English-Urdu/REPORT_TEMPLATE.md`.

## 5. PAPER COMPLETION (gated on category 4)

- Populate `paper/main.md` Results with the category-4 outputs only — no earlier draft.
- Write Discussion against the actual confusion matrices, missingness, and audit findings
  — not against a assumed direction.
- Write Conclusion, scoped to exactly what category 4 supports (see the "WE CAN CLAIM" /
  "WE CANNOT CLAIM" wording already frozen in `research/SCIENTIFIC_LEAD_FINAL_AUDIT.md` §5
  and reaffirmed unchanged by this pass).
- Populate `paper/tables/` and `paper/figures/` from hash-verified category-4 artifacts
  only, per their existing READMEs.
- Final claim-ledger check (`paper/main.md` §"Claim ledger", added by this pass) against
  the actual analysis output before submission.
- Select a venue tier per `research/FINAL_SCIENTIFIC_READINESS.md` §"Publication strategy"
  once the result's strength is known — not before.

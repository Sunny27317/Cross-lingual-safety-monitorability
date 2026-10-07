# Human annotation: final package (outcome-blind; 2026-10-07)

**NOT AUTHORIZED.** The ORPI determination is outstanding. No rater has been contacted and
no annotation has started. This file collects every element of the human stage. Frozen
rater documents are referenced, not edited (their hashes are in
`engineering/rater_package_reconciliation.json`).

## 1. The 312-rationale plan (verified 2026-10-07, structural checks only)

- **Pool:** `human_pool.candidate_pool()` yields **312** units: **240** Cue A and **72** Cue
  B, with two models. Each unit is one sample per (model, item, cue), chosen by
  `sha256(item|model|cue|human_sample) mod 3`. The rule was fixed before generation.
- **Packet v2** (`experiments/_runs/workshop-v1-human-validation-packet-v2/rater_context.jsonl`,
  sha256 `8bccea18…`):
  - 312 rows; 312 unique blind IDs, identical to the pool.
  - Fields: `blind_id`, `language`, `question`, `options`, `suggestion`, `trace` only.
  - No model, condition, item, sample, answer or judge field. This matches judge-input
    parity (D-PG-4).
- **⚠ Blocking finding: presentation order.** The packet rows are in **four model × cue
  blocks**: Qwen Cue A (120), Qwen Cue B (36), Gemma Cue A (120), Gemma Cue B (36). The
  frozen order record (`engineering/workshop_v1_human_packet_order.json`: method
  `lexicographic_blind_id`, order hash `ee0e1b57…`) matches **lexicographic** blind-ID
  order, which interleaves models and cues (221 runs; longest 9). The preprint states the
  sorted order. The block order would let raters infer model or condition from position or
  stylistic shifts.
  - **Fix, before any release to raters:** regenerate the packet with
    `human_pool.packet_order`/`blinded_export_rows` so the rows follow the frozen order.
    Verify that the order hash equals `ee0e1b57…`, record the new packet SHA-256, and
    retain the old packets as superseded.
  - This is engineering work on run outputs (Codex's scope). It changes no content and no
    trace.

## 2. Raters, competence and qualification

**Frozen requirements:**
- 2 independent raters with native or near-native Urdu reading competence and strong
  written English;
- 1 adjudicator who does not rate;
- a qualification screen on synthetic text only;
- conflict-of-interest confirmation.

**Urdu competence criteria.** At least one of the following, recorded on
`docs/rater_package/RATER_QUALIFICATION_TEMPLATE.md`:
- Urdu as a first language;
- formal education in Urdu-medium schooling;
- sustained daily reading of Urdu prose.

In addition, the rater must pass the screener: read synthetic Urdu rationales and answer
the comprehension and boundary questions (`RECRUITMENT_KIT.md` §C). Competence is never
certified from the study rationales.

**Pseudonymous IDs.** The steward assigns an ID (`R1`, `R2`, `ADJ`). All study files use the
ID only.

## 3. Investigator-as-rater (risk and policy)

- **Risk.** The investigator knows the hypotheses, the cue design and the item set. Rating
  could introduce expectation bias and would weaken independence. If the investigator also
  adjudicated, they would decide the contested cases.
- **Recommendation (preferred).** The investigator does **not** serve as either primary rater
  or as adjudicator, provided two independent qualified raters and an adjudicator can be
  recruited.
- **If unavoidable.** The investigator may serve as **one** rater only, under all of these
  conditions:
  - full disclosure in Methods and Limitations;
  - the second rater and the adjudicator are independent;
  - the investigator labels blind, under the same packet and rules, and never sees the
    other rater's labels before locking;
  - the investigator never adjudicates.
- Record the decision before recruitment (pre-unseal checklist U-13).

## 4. Procedures

**Blinded packet generation.** Use the fixed packet in the frozen order (§1). Deliver it with
the submission template. Raters see only the six fields above.

**Calibration (non-study examples only).**
- `docs/rater_package/TRAINING_TUTORIAL.md`: an invented question and 17 constructed
  rationales covering every boundary case, with 16 Urdu sentences.
- Raters complete it before the packet. The steward gives feedback on the practice items
  only.
- No study rationale is ever used for calibration.
- Minutes per item, measured here, set `[HOURS]`.

**Labels.**
- `disclosed`, `not_disclosed`, `partial`, `cannot_tell`, as defined in
  `RATER_INSTRUCTIONS.md`, with the Judge V2 boundaries.
- Plus `abstain`: a personal opt-out, with no penalty.
- `cannot_tell` means the *text* gives nothing usable. `abstain` means the *rater*
  declines. These are distinct and must never be merged.

**Disagreement and adjudication** (frozen; `ADJUDICATOR_INSTRUCTIONS.md`):
- **Trigger:** the raters disagree, or either abstains.
- **First:** the adjudicator records an independent blind label.
- **Then:** the adjudicator sees both labels and notes, and records a final label or
  `unresolved`, with a rationale.
- **Never:** majority vote; returning items to raters.
- Enforced in code: `validate_adjudications` requires `independent_label`.

**Writes.** `annotation_io.persist_rater_labels` and `persist_adjudications` write once,
atomically, with no overwrite. Record each file's SHA-256 in a dated provenance record.

**Agreement.** Raw % and Cohen's κ, five categories with `abstain` as a category (n = 312),
and on the binary subset (with its n). Each has a 95% item-cluster bootstrap CI and the full
contingency table. No bands and no thresholds.

## 5. Privacy, compensation, retention

- **Names and contact details:** used only to administer the task and pay raters; stored
  outside the repository; deleted after payment (confirm with ORPI).
- **Collected:** labels, optional notes, timestamps. **Not collected:** demographics or any
  identifier beyond what payment needs.
- **Compensation:** `[COMPENSATION — INVESTIGATOR DECISION]`. The basis is identical for
  both raters, or the work is stated as unpaid.
- **Retention:** pseudonymous labels are kept as research records. Public release only as
  the ORPI determination and written consent allow.
- **Raters' local copies:** deleted on submission.

## 6. Written consent / acknowledgment template (rater): blank; no signatures exist

```
Workshop-v1 rater consent and acknowledgment            [ORPI-required wording to be inserted]
Pseudonym: ________   Date: ________
[ ] I have read the information sheet and agree to label the rationales as instructed.
[ ] I understand I may skip any item ("abstain") and may withdraw before submitting.
[ ] I understand my submitted labels are stored under my pseudonym and are locked once submitted.
Acknowledgment in publications (choose one):
[ ] Anonymous (default)    [ ] By name: ______________________ (as it should appear)
Release of my pseudonymous labels (if ORPI permits):  [ ] Yes   [ ] No
Signature: ______________________
```

## 7. Native item/cue equivalence sign-off

See `docs/rater_package/NATIVE_REVIEWER_WRITTEN_SIGNOFF_FORM.md`.

## 8. What still blocks collection

1. The ORPI determination, plus any required consent wording.
2. Packet reordering to the frozen lexicographic order (§1).
3. Decisions on compensation, investigator-as-rater and the translation auditor.
4. Removing the native reviewer's name from the rater-facing training documents, through
   a reconciled update.
5. Recruitment of 2 raters and 1 adjudicator.
6. If used, recording the capacity stop date before annotation begins.

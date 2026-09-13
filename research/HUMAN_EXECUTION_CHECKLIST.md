# Human execution checklist — today to first real annotation

Exact chronological steps. Each has an owner, input, output, gate (what must be true
before this step starts), and failure condition (what happens if it can't be
completed). No step here is executed by this repository automatically — every step
requires a real human action.

## 1. Ethics/governance approval

- **Owner:** Investigator + institution.
- **Input:** `docs/ETHICS_REVIEW_REQUEST_TEMPLATE.md`, completed.
- **Output:** A written institutional determination (approval, exemption, or required
  changes).
- **Gate:** None — this is the first step.
- **Failure condition:** Institution requires changes to the protocol itself (e.g., a
  different consent process, item exclusions) → revise `docs/
  ETHICS_REVIEW_REQUEST_TEMPLATE.md` and `docs/RATER_CONSENT_TEMPLATE.md` and resubmit
  before proceeding to step 2.

## 2. Rubric approval

- **Owner:** Investigator + (if Urdu wording is used instead of the English packet) a
  bilingual reviewer.
- **Input:** `docs/rater_package/RATER_INSTRUCTIONS.md`; `research/
  SUPERVISOR_DECISION_PACKET.md` row 8 decision.
- **Output:** A frozen rubric version (English packet as-is, or an approved Urdu
  rendering) with no further wording changes expected.
- **Gate:** Step 1 complete.
- **Failure condition:** Reviewers disagree on wording → escalate to investigator per
  `docs/URDU_EQUIVALENCE_DECISION_TREE.md`'s escalation pattern; do not proceed to
  recruitment with an unresolved rubric.

## 3. Recruit two independent Urdu/English raters

- **Owner:** Investigator/steward.
- **Input:** `research/SUPERVISOR_DECISION_PACKET.md` row 2 decision (recruitment
  channel); `docs/rater_package/RATER_QUALIFICATION_TEMPLATE.md`.
- **Output:** Two completed, signed qualification records.
- **Gate:** Steps 1–2 complete.
- **Failure condition:** Fewer than two qualified candidates found in the chosen
  channel → return to row 2 of the decision packet and choose a different channel; do
  not lower the qualification bar to fill the role.

## 4. Appoint adjudicator

- **Owner:** Investigator/steward.
- **Input:** Same qualification template; additionally confirm no conflict of interest
  with either rater or with the study design.
- **Output:** One completed, signed qualification record for the adjudicator.
- **Gate:** Step 3 complete (so conflict-of-interest can be checked against the actual
  raters).
- **Failure condition:** Only candidate available has a conflict → document the
  conflict and its handling per `docs/rater_package/RATER_QUALIFICATION_TEMPLATE.md`,
  or find another candidate; do not proceed with an undisclosed conflict.

## 5. Compensation decision

- **Owner:** Investigator/institution.
- **Input:** `research/SUPERVISOR_DECISION_PACKET.md` row 3.
- **Output:** A documented compensation basis and amount.
- **Gate:** Can run in parallel with steps 2–4; must complete before consent (step 9).
- **Failure condition:** Budget doesn't support the chosen recruitment channel →
  revisit row 2/row 3 jointly.

## 6. Blind-ID secret setup

- **Owner:** Steward (technical).
- **Input:** `docs/DOWNSTREAM_INFRASTRUCTURE.md`'s `blind_packet` mechanism.
- **Output:** A private HMAC secret generated and stored per `docs/
  ETHICS_AND_DATA_GOVERNANCE_CHECKLIST.md`'s "Blinding key" row (access list, backup,
  rotation policy).
- **Gate:** Step 1 complete (storage/access policy must be approved first).
- **Failure condition:** No approved secure storage location yet → resolve `research/
  SUPERVISOR_DECISION_PACKET.md` row 4 before generating the secret.

## 7. Packet generation

- **Owner:** Steward (technical).
- **Input:** Locked source-item set (English pilot items and/or their Urdu
  equivalents, per whichever population is being annotated first — see `research/
  FINAL_PROTOCOL.md` §11's four-way partition); the blind-ID secret from step 6.
- **Output:** Two independent `AnnotationPacket` objects (one per rater), with
  opaque IDs and independent randomized presentation order, plus the steward-only
  `PrivateAssignment` mapping.
- **Gate:** Steps 1, 2, 6 complete; the relevant source items must already be
  translated and locked if this is the Urdu population (`docs/
  URDU_ITEM_EQUIVALENCE_FORM.md`, all forms signed).
- **Failure condition:** Source items not yet locked → this step cannot start; return
  to the Urdu translation/review chain first.

## 8. Packet hash lock

- **Owner:** Steward (technical).
- **Input:** The generated packets from step 7.
- **Output:** A recorded, timestamped hash of each packet, locked before any rater
  sees it.
- **Gate:** Step 7 complete.
- **Failure condition:** A packet needs correction after this lock (e.g., a
  formatting bug found) → generate a new packet with a new hash; never edit a locked
  packet in place.

## 9. Rater onboarding

- **Owner:** Steward.
- **Input:** `docs/rater_package/RATER_ONBOARDING.md`; signed consent (`docs/
  RATER_CONSENT_TEMPLATE.md`, institution-approved version); compensation terms
  (step 5).
- **Output:** Each rater has read onboarding material and signed consent.
- **Gate:** Steps 1, 3–5 complete.
- **Failure condition:** A candidate declines to consent after seeing the materials →
  they do not proceed; recruit a replacement (return to step 3) if needed.

## 10. Qualification (final check before real material)

- **Owner:** Steward.
- **Input:** A short non-study reading-comprehension exercise (per `docs/
  rater_package/RATER_QUALIFICATION_TEMPLATE.md`).
- **Output:** Confirmed competence on record, distinct from self-report.
- **Gate:** Step 9 complete.
- **Failure condition:** A rater doesn't pass the exercise → do not proceed with them
  as a rater; this is a real possibility, not a formality, and must be handled without
  awkwardness or pressure per the consent terms.

## 11. Annotation (training, then production)

- **Owner:** Raters (independently); steward monitors process only.
- **Input:** `docs/rater_package/RATER_INSTRUCTIONS.md`, `ANNOTATION_DECISION_TREE.md`;
  training set first (independent human-authored/permissioned examples, not real study
  data), then the locked production packet (step 8).
- **Output:** Two independent, complete sets of `Annotation` records.
- **Gate:** Step 10 complete for both raters; training round reviewed and approved
  before production begins.
- **Failure condition:** Training reveals the rubric is unclear in practice → return
  to step 2 (rubric approval) with the specific confusion documented; do not silently
  reinterpret the rubric mid-production.

## 12. Adjudication

- **Owner:** Adjudicator.
- **Input:** `docs/rater_package/ADJUDICATOR_INSTRUCTIONS.md`; both raters' completed,
  locked submissions from step 11.
- **Output:** A final adjudicated label (or explicit "unresolved") for every
  disagreement, with rationale, preserving both original labels unchanged.
- **Gate:** Step 11 complete for both raters.
- **Failure condition:** A case doesn't fit the frozen rubric even after adjudication
  → mark unresolved and escalate to the investigator; do not force a label.

## 13. Human-reference lock

- **Owner:** Steward, with investigator attestation.
- **Input:** All original annotations (step 11) and adjudication records (step 12).
- **Output:** A `LockedReference` binding the packet, protocol decision, steward, and
  timestamp — the human reference used for all subsequent judge calibration and
  measurement.
- **Gate:** Step 12 complete; lineage validated (`validate_reference` passes).
- **Failure condition:** Lineage validation fails (a hash mismatch, a missing source
  record) → do not lock; resolve the specific integrity issue first. Once locked, any
  later correction requires a new lock and a visible deviation note — it never
  silently replaces the original.

## After step 13

Judge calibration may begin (`experiments/M2-Monitor-Validation/
JUDGE_RUBRIC_PACKAGE.md`), gated on the signed acceptance criteria
(`research/SUPERVISOR_DECISION_PACKET.md` row 6) existing independently of and before
this lock. Full continuation: `research/EXECUTION_ROADMAP.md` category 3.

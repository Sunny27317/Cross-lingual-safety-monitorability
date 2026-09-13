# Human execution checklist — today to first real annotation

Exact chronological steps. Each has an owner, input, output, gate (what must be true
before this step starts), and failure condition (what happens if it can't be
completed). No step here is executed by this repository automatically — every step
requires a real human action. **Two populations can be annotated, and they are not
interchangeable:** an English-calibration-partition population (traces already exist,
from the completed English pilot) and the Urdu confirmatory population (traces do not
exist yet and require a separately authorized generation stage — step 7, below). Steps
1–6 and 8–14 apply to either population; step 7 applies only to the Urdu population.

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
- **Gate:** Can run in parallel with steps 2–4; must complete before consent (step 10).
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

## 7. Urdu material lock and model execution — Urdu population only

**Skip this step entirely if the first annotation round uses the existing
English-calibration population (traces already exist from PR #19); it is mandatory
before any Urdu trace can be annotated.**

- **Owner:** Translator, bilingual reviewers, and adjudicator (material lock); then a
  separately authorized Track-A-Urdu execution owner (generation).
- **Input:** Frozen English source items; `docs/TRANSLATOR_INSTRUCTIONS.md`, `docs/
  BILINGUAL_REVIEWER_INSTRUCTIONS.md`, `docs/URDU_EQUIVALENCE_DECISION_TREE.md`, one
  `docs/URDU_ITEM_EQUIVALENCE_FORM.md` per item.
- **Output:** (a) Every Urdu item locked (all equivalence forms signed, content
  hashes fixed); (b) a **separate, freshly issued** Urdu generation-authorization
  artifact, structurally identical to but independent from the English pilot's — the
  English authorization does not extend to Urdu, per every prior Track-A decision;
  (c) the completed Urdu generation run itself, producing the actual reasoning traces
  raters will read, with the same integrity review the English pilot received (planned
  vs. complete vs. missing, parse validity, no reruns of a failed item).
- **Gate:** Steps 1–2 complete (ethics and rubric, since item content and exposure are
  ethics-relevant); translator/reviewer roles filled (may reuse rater/adjudicator
  candidates from steps 3–4 only if the reuse and any resulting role overlap is
  disclosed as a limitation, per `docs/HUMAN_URDU_VALIDATION_PACKAGE.md`).
- **Failure condition:** An item cannot be resolved to a locked equivalence record
  (`docs/URDU_EQUIVALENCE_DECISION_TREE.md` Q4's "exclude" branch) → the item is
  excluded, not force-locked; document the exclusion. If the Urdu generation run itself
  fails partial integrity checks → apply the same zero-retry, preserve-everything
  policy as the English pilot; do not silently drop or rerun a failed item.

## 8. Packet generation

- **Owner:** Steward (technical).
- **Input:** For the English-calibration population: the existing locked English pilot
  traces (PR #19). For the Urdu population: the locked Urdu traces from step 7. The
  blind-ID secret from step 6 either way.
- **Output:** Two independent `AnnotationPacket` objects (one per rater), with
  opaque IDs and independent randomized presentation order, plus the steward-only
  `PrivateAssignment` mapping.
- **Gate:** Steps 1, 2, 6 complete; step 7 complete if this is the Urdu population.
- **Failure condition:** Traces not yet locked for the target population → this step
  cannot start; return to step 7 (Urdu) or confirm the correct English artifact
  (calibration).

## 9. Packet hash lock

- **Owner:** Steward (technical).
- **Input:** The generated packets from step 8.
- **Output:** A recorded, timestamped hash of each packet, locked before any rater
  sees it.
- **Gate:** Step 8 complete.
- **Failure condition:** A packet needs correction after this lock (e.g., a
  formatting bug found) → generate a new packet with a new hash; never edit a locked
  packet in place.

## 10. Rater onboarding

- **Owner:** Steward.
- **Input:** `docs/rater_package/RATER_ONBOARDING.md`; signed consent (`docs/
  RATER_CONSENT_TEMPLATE.md`, institution-approved version); compensation terms
  (step 5).
- **Output:** Each rater has read onboarding material and signed consent.
- **Gate:** Steps 1, 3–5 complete.
- **Failure condition:** A candidate declines to consent after seeing the materials →
  they do not proceed; recruit a replacement (return to step 3) if needed.

## 11. Qualification (final check before real material)

- **Owner:** Steward.
- **Input:** A short non-study reading-comprehension exercise (per `docs/
  rater_package/RATER_QUALIFICATION_TEMPLATE.md`).
- **Output:** Confirmed competence on record, distinct from self-report.
- **Gate:** Step 10 complete.
- **Failure condition:** A rater doesn't pass the exercise → do not proceed with them
  as a rater; this is a real possibility, not a formality, and must be handled without
  awkwardness or pressure per the consent terms.

## 12. Annotation (training, then production)

- **Owner:** Raters (independently); steward monitors process only.
- **Input:** `docs/rater_package/RATER_INSTRUCTIONS.md`, `ANNOTATION_DECISION_TREE.md`;
  training set first (independent human-authored/permissioned examples, not real study
  data), then the locked production packet (step 9).
- **Output:** Two independent, complete sets of `Annotation` records.
- **Gate:** Step 11 complete for both raters; training round reviewed and approved
  before production begins.
- **Failure condition:** Training reveals the rubric is unclear in practice → return
  to step 2 (rubric approval) with the specific confusion documented; do not silently
  reinterpret the rubric mid-production.

## 13. Adjudication

- **Owner:** Adjudicator.
- **Input:** `docs/rater_package/ADJUDICATOR_INSTRUCTIONS.md`; both raters' completed,
  locked submissions from step 12.
- **Output:** A final adjudicated label (or explicit "unresolved") for every
  disagreement, with rationale, preserving both original labels unchanged.
- **Gate:** Step 12 complete for both raters.
- **Failure condition:** A case doesn't fit the frozen rubric even after adjudication
  → mark unresolved and escalate to the investigator; do not force a label.

## 14. Human-reference lock

- **Owner:** Steward, with investigator attestation.
- **Input:** All original annotations (step 12) and adjudication records (step 13).
- **Output:** A `LockedReference` binding the packet, protocol decision, steward, and
  timestamp, **tagged with which population it covers** (English-calibration or Urdu
  confirmatory — see `research/FINAL_PROTOCOL.md` §1a finding 2 on why this tag matters:
  the current stage-gate schema cannot yet distinguish the two automatically, so the
  lock record itself must state it explicitly until that is fixed).
- **Gate:** Step 13 complete; lineage validated (`validate_reference` passes).
- **Failure condition:** Lineage validation fails (a hash mismatch, a missing source
  record) → do not lock; resolve the specific integrity issue first. Once locked, any
  later correction requires a new lock and a visible deviation note — it never
  silently replaces the original.

## After step 14

If this was the **English-calibration population**: judge calibration may begin
(`experiments/M2-Monitor-Validation/JUDGE_RUBRIC_PACKAGE.md`), gated on the signed
acceptance criteria (`research/SUPERVISOR_DECISION_PACKET.md` row 6) existing
independently of and before this lock.

If this was the **Urdu confirmatory population**: the translation diagnostic
(translator selection already resolved, packet row 7) and the measurement analysis
(`research/FINAL_PROTOCOL.md` §4) may begin, gated on judge calibration/selection
already being complete from an earlier English-calibration round.

Full continuation either way: `research/EXECUTION_ROADMAP.md` category 3.

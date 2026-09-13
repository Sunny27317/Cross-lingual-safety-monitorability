# Ethics review request template

**DRAFT — for submission to institutional ethics/IRB review. This document does not
assert any determination, exemption, or approval. Every bracketed field must be
completed and reviewed by the responsible investigator and institution before use.**
See `docs/ETHICS_AND_DATA_GOVERNANCE_CHECKLIST.md` for the full governance checklist
this summarizes into a submittable form.

## 1. Research purpose

This study measures whether an automated system correctly detects, in AI-generated
text, explicit acknowledgment that a hint influenced an answer. Human raters provide an
independent reference judgment against which the automated system is compared. Full
scientific protocol: `research/FINAL_PROTOCOL.md`.

## 2. What raters actually do

Raters read short (typically a few sentences to a few paragraphs) passages of
AI-generated reasoning text and select one of five labels describing whether the text
discloses reliance on a hint. They do not generate content, interact with the AI model
directly, or make any judgment about factual correctness. Full task:
`docs/rater_package/RATER_INSTRUCTIONS.md`.

## 3. Data collected from raters

- A pseudonym assigned by the study steward (not the rater's real name, used in all
  records).
- Their labels, confidence values, uncertainty flags, and optional free-text rationales
  for each passage.
- [IF APPLICABLE] Qualification information used to verify language competence
  (`docs/rater_package/RATER_QUALIFICATION_TEMPLATE.md`) — describe exactly what is
  recorded there (e.g., self-described language background, a short reading exercise
  result) once finalized.
- [IF APPLICABLE] Consent record and compensation record.

## 4. Is identifiable information needed?

[TO BE DETERMINED WITH INSTITUTION.] The study steward will know each rater's real
identity (for recruitment, consent, and payment); study records use pseudonyms only.
State here whether any identifiable information beyond what's needed for consent/payment
is collected or retained, and where the identity-to-pseudonym mapping is stored.

## 5. Expected time burden

[TO BE FILLED once the confirmatory sample size is set — `research/
SUPERVISOR_DECISION_PACKET.md` row 12 — plus training time. Provide a realistic
per-rater time estimate for the actual approved N before recruitment.]

## 6. Compensation

[TO BE FILLED — `research/SUPERVISOR_DECISION_PACKET.md` row 3: basis, amount, and
payment process.]

## 7. Risks

The primary foreseeable risk is exposure to AI-generated text that could occasionally be
confusing, mildly frustrating, or (rarely, given the MMLU-derived academic source
material) touch on a sensitive topic embedded in a source question. Raters are
instructed they may skip any passage using `abstain` with no explanation required and no
penalty (`docs/rater_package/RATER_INSTRUCTIONS.md`). [Institution to assess whether
this warrants additional safeguards, e.g. a specific escalation contact for distress.]

## 8. Privacy

Rater identities are pseudonymized in all study records; the identity mapping is held
separately by the steward with restricted access (`docs/
ETHICS_AND_DATA_GOVERNANCE_CHECKLIST.md`, "Pseudonyms" and "Blinding key" rows). Raters
are told not to include personally identifying information in their free-text
rationales.

## 9. Storage

[TO BE FILLED — `research/SUPERVISOR_DECISION_PACKET.md` row 4: storage location,
access controls, encryption.]

## 10. Retention

[TO BE FILLED — how long raw records, the identity mapping, and de-identified records
are each retained, and what happens at the end of that period.]

## 11. Withdrawal

Raters may withdraw at any point without penalty. [TO BE FILLED — the institution's
policy on what happens to already-submitted labels from a withdrawn rater: are they
retained (de-identified) or deleted? State the default and how a rater can request
either.]

## 12. Publication / release plan

Aggregate statistics (agreement rates, calibration metrics, the estimands `G`/`R`) are
intended for eventual publication. Individual rater identities are never released.
Whether de-identified individual labels/rationales are released, and under what review,
is a governance decision — see `docs/REPRODUCIBILITY_RELEASE_PLAN.md` (tiered
PUBLIC/PUBLIC AFTER REVIEW/PRIVATE/NEVER PUBLIC classification) and `research/
SUPERVISOR_DECISION_PACKET.md` row 4.

## 13. AI-generated material exposure

Raters read AI-generated (not human-authored) reasoning text throughout the task. The
source items are drawn from a public academic benchmark (MMLU); the AI-generated
reasoning is produced by a specific, disclosed model configuration
(`research/FINAL_PROTOCOL.md`; `paper/main.md` §Methods). This should be disclosed to
raters during consent (already done in `docs/rater_package/RATER_ONBOARDING.md`) and to
the reviewing institution here.

## 14. Potentially sensitive content considerations

The source material is academic multiple-choice content (e.g. moral scenarios, foreign
policy, and other MMLU subjects already in the frozen item set —
`research/FINAL_PROTOCOL.md` §0). [Institution/investigator to review the specific
frozen 50-item set, or its Urdu equivalent, for content the institution considers
sensitive, and decide whether any item needs exclusion or a content warning before
rater exposure.]

## 15. Investigator contact

[NAME] — [ROLE] — [INSTITUTIONAL EMAIL] — [PHONE, if required by institution]

## 16. Escalation / urgent contact (if different from above)

[NAME / CONTACT]

---

**This template does not constitute, claim, or imply an ethics determination. It is a
drafting aid for the actual submission the institution requires.**

# Workshop-v1 human stage: ORPI readiness

**Status (2026-10-06):** an ORPI determination was requested on or before 2026-10-04. **None has been received. No approval or exemption is claimed.** No rater has been recruited and no label exists.

This file lists what is ready, and what stays blocked until ORPI's written determination is saved in `engineering/provenance/` with its SHA-256.

## 1. Data shown to raters

Packet v2 (`experiments/_runs/workshop-v1-human-validation-packet-v2/`, packet sha256 `8bccea18…`, 312 rows):

| Shown | Not shown |
|---|---|
| Blind ID | Model or model family |
| Language | Item ID |
| Question and four options (as in the generation prompt) | Sample index |
| The exact suggestion sentence | Condition label (Cue A vs Cue B) |
| The model's visible rationale | Answer key and the model's answer |
| | Any automated or translated label |
| | Compliance values |
| | The other rater's labels |

- **Content:** science-question items and model-written rationales. They contain no personal data about third parties.
- **Exposure risk:** low (non-sensitive content). The rater may skip any item.

## 2. Recruitment criteria (frozen)

- **Raters:** 2, with native or near-native Urdu reading and strong written English.
- **Screen:** passed on synthetic text only (`RECRUITMENT_KIT.md` §C).
- **Conflict of interest:** none; confirmed in writing.
- **Adjudicator:** 1, who is not a rater.
- **Investigator as rater:** recommended NO. If yes, disclose it, and the investigator does not adjudicate.

## 3. Compensation

**`[COMPENSATION — INVESTIGATOR DECISION]`**

- Use the same basis for both raters: either a fixed amount per completed packet, or "unpaid", stated as such.
- Time estimate: `[HOURS]` = 312 × (minutes per item, measured during the practice set) / 60, plus about 1 hour of training.
- Decide before any recruitment message is sent.

## 4. Consent considerations

- **Information sheet:** `RECRUITMENT_KIT.md` §D, given before consent.
- **Consent form:** only as ORPI requires (`[ORPI: consent / information-sheet requirement]`).
- **Voluntary:** participation is voluntary. A rater may withdraw before submitting.
- **After submission:** labels are locked for integrity. Whether a later withdrawal request can remove them is `[ORPI GUIDANCE]`.
- **Disclosure:** no deception. Raters are not told the hypotheses (to avoid demand effects), only the task.

## 5. Privacy and identifiers

- **Names collected?** Yes, for administration and payment only. They are kept **separately** from labels and never stored in the repository.
- **Labels:** stored under an assigned pseudonym (`RATER_QUALIFICATION_TEMPLATE.md`).
- **Acknowledgment:** a rater is named only with explicit consent; the default is anonymous.
- **Open issue:** the native item reviewer's full name is already in public commits without a recorded consent decision (see `research/SCIENTIFIC_COMPLETION_AUDIT.md` R2). Resolve this before any rater-related release.

## 6. Data retention

| Data | Retention |
|---|---|
| Labels and notes, under pseudonym | Retained as research records. Public release only as the determination **and** consent allow (`[ORPI GUIDANCE]`) |
| Names and contact details | Deleted after payment is complete (proposed; confirm with ORPI) |
| Raters' local copies of the packet | Deleted on submission (instructed) |

## 7. Ready now (no ORPI dependency)

- Packet v2 built and hashed.
- Rater instructions, decision tree, FAQ, synthetic training tutorial and 17 practice items.
- Adjudicator instructions.
- Agreement-reporting specification.
- Immutable writers (`annotation_io.persist_rater_labels`, `persist_adjudications`).
- The H mapping.
- The join and κ code (`final_analysis.py`), synthetic-tested.
- Recruitment message templates (placeholders unfilled).

## 8. Blocked until ORPI replies

| Blocked item | Why |
|---|---|
| Sending any recruitment message | Protocol gate |
| Consent or information-sheet wording | `[ORPI]` |
| Whether a consent form, exemption form or nothing is required | `[ORPI]` |
| Release of pseudonymous labels | `[ORPI]` + consent |
| Methods §4.8 and Ethics text | Must quote the determination verbatim |
| Annotation start | Gated |
| If ORPI requires changes to the protocol | Record them as a dated amendment **before** annotation |

## 9. Decisions due before recruitment (investigator)

- Compensation.
- Investigator-as-rater.
- Translation auditor (a non-rater, or one who audits only after finishing their own rating).
- Capacity stop date: only if the 12-block contingency will be used, and recorded **before** annotation begins.
- Rater acknowledgment default.

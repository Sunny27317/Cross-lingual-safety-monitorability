# Workshop-v1 human stage: final go/no-go (2026-10-07)

| Item | Status | Basis |
|---|---|---|
| **ORPI READY** | **YES** (package ready). **The determination itself has NOT been received** | `WORKSHOP_V1_ORPI_SUBMISSION_PACKET.md`, `WORKSHOP_V1_ORPI_RESPONSE_PLAYBOOK.md`; request sent on or before 2026-10-04 |
| **RATER PACKAGE READY** | **YES, with two fixes before release** | Instructions, decision tree, FAQ, synthetic training, adjudicator instructions, agreement specification, immutable writers and qualification template are all present (`WORKSHOP_V1_HUMAN_ANNOTATION_FINAL_PACKAGE.md`). Fixes: (1) remove the native reviewer's name from the rater-facing training documents through a reconciled update; (2) see "Blinding ready" |
| **BLINDING READY** | **NO, until the packet is reordered** | Fields are correct (only blind ID, language, question, options, suggestion and rationale; no model, condition, item or answer). But the current packet files are ordered in **model × cue blocks**, which contradicts the frozen lexicographic order (order hash `ee0e1b57…`). Regenerate in the frozen order, verify the order hash, and record the new packet hash |
| **SIGN-OFF FORM READY** | **YES** (blank) | `docs/rater_package/NATIVE_REVIEWER_WRITTEN_SIGNOFF_FORM.md`; rater consent template in the final package §6. No signature exists or was created |
| **HUMAN DATA COLLECTION AUTHORIZED** | **NO** | No ORPI determination; no recruitment |

## What exactly still blocks human collection

1. **The ORPI written determination.** Save it verbatim with its SHA-256. Apply any required
   consent wording or protocol change as a dated amendment before annotation.
2. **Packet reorder to the frozen lexicographic blind-ID order** (an engineering change to
   run outputs, in Codex's scope). Verify order hash `ee0e1b57…`. No content changes.
3. **Investigator decisions:**
   - compensation;
   - whether the investigator rates (recommended: no);
   - a translation auditor (a non-rater, or after rating);
   - a capacity stop date, only if the 12-block contingency will be used, recorded before
     annotation begins.
4. **Rater-document reconciliation:** remove the reviewer's name, then update the hashes in
   `engineering/rater_package_reconciliation.json`.
5. **Recruitment** of 2 qualified raters and 1 adjudicator, with screener, consent and
   pseudonyms.

**Not blocking, but recommended before collection:** the native reviewer completes the
written sign-off form; the acknowledgment default stays anonymous.

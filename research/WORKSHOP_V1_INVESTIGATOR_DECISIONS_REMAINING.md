# Investigator decisions remaining (ranked; 2026-10-04)

Only decisions that require you. Each has a default and a consequence. Engineering
items belong to Codex and are excluded.

## NOW

| Decision | Recommended default | Consequence |
|---|---|---|
| Approve an **archival commit** of the executed generation code and the frozen analysis code, **before any result is inspected** | Approve. Describe it with the §10 wording in `PRE_UNSEAL_AUDIT.md` (a later snapshot, not the executed commit) | Without it, Methods can only cite hashes. A commit made after inspection is weaker provenance |
| **1.84 h generation-pause note** | One factual sentence (cause, or "cause not recorded") | Closes a provenance gap |
| **Merge the two verbal-review records** | Keep both. Add a one-line cross-reference note | Avoids an apparent duplicate in the appendix |

## BEFORE HUMAN ANNOTATION

| Decision | Recommended default | Consequence |
|---|---|---|
| **Rater compensation** | Fixed amount per completed packet, identical for both raters (or "unpaid", stated) | Needed for recruitment, the ORPI follow-up and the Ethics text |
| **Translation auditor** | A bilingual person who is not a rater, or one who audits only after finishing their own rating | Keeps annotation uncontaminated |
| **Whether you will serve as a rater** | Prefer not to. If you do, disclose it and do not adjudicate | Affects independence and the Methods wording |
| Act on the **ORPI reply** | Follow `docs/ORPI_RESPONSE_TEMPLATES.md` | Gates all recruitment |

## BEFORE PREPRINT

| Decision | Recommended default | Consequence |
|---|---|---|
| **Author name and affiliation** | Name as it should be cited. Affiliation only if formal; otherwise "Independent researcher" | Misstatement is a misrepresentation |
| **Co-author / supervisor** | None unless someone contributed substantively and gives written approval | Co-authors must approve the final PDF |
| **Amna acknowledgment** | Anonymous until her consent is recorded; named with consent | — |
| **Rater acknowledgment** | Anonymous | — |
| **Funding statement** | "No specific funding" (if true) | — |
| **Release route for outputs and labels** | Version 3 (code, hashes, IDs; outputs on request) until the licence is clarified | Avoids redistributing item text |
| **Title** | Choose after results from the top 3 | — |
| **Preprint before review?** | Yes, once every release-guard gate is true and the venue policy allows it | Citable in applications |

## BEFORE SUBMISSION

| Decision | Recommended default | Consequence |
|---|---|---|
| **Target venue** | A non-archival workshop first; then an archival workshop or Findings; the expanded version to a main track or journal | Keeps options open |
| **Anonymization** | Only if the venue is double-blind | — |
| **Licence for released artifacts** | Code MIT; annotations CC BY 4.0 (if released) | — |

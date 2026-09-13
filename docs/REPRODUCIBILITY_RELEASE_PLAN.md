# Reproducibility and open-science release plan

**This document proposes a classification for review, not an institutional decision.**
The actual release tier for any row below is set by the investigator and institution
via `research/SUPERVISOR_DECISION_PACKET.md` row 4 (storage/release governance) and,
where raters are concerned, by their consent terms (`docs/RATER_CONSENT_TEMPLATE.md`).
Nothing here authorizes releasing anything today; no artifact in the rows below yet
exists.

Four tiers:

- **PUBLIC** — releasable alongside or shortly after publication, no additional review
  needed beyond normal pre-publication checks.
- **PUBLIC AFTER REVIEW** — releasable, but only after an explicit de-identification /
  sensitivity review confirms it's safe to release in that form.
- **PRIVATE** — retained for reproducibility/audit purposes, accessible to the research
  team and, on request, to reviewers/replicators under a data-access agreement; not
  publicly posted.
- **NEVER PUBLIC** — never released in any form, including to reviewers, beyond what's
  strictly needed for the institution's own audit trail.

| Artifact | Proposed tier | Why |
|---|---|---|
| Analysis code (`src/clsm/`) | **PUBLIC** | Already the project's own practice; no participant data in code itself |
| Configs (scientific config, decoding, dataset pin) | **PUBLIC** | Needed for reproducibility; contain no personal data |
| Judge prompts and rubric text (`experiments/M2-Monitor-Validation/JUDGE_RUBRIC_PACKAGE.md`) | **PUBLIC** | Needed to interpret and reproduce judge behavior |
| Hashes (config, dataset, judge/translator spec, artifact hashes) | **PUBLIC** | Exactly what they're for — verifying identity without exposing content prematurely |
| Disclosure annotation rubric (English + locked Urdu wording) | **PUBLIC** | Needed to interpret human labels; no personal data |
| Aggregate statistics (`G`, `R`, confusion matrices, calibration metrics, agreement) | **PUBLIC** | The actual scientific contribution; no individual-level data |
| Individual, de-identified rater labels + rationales | **PUBLIC AFTER REVIEW** | Scientifically valuable for replication/audit, but free-text rationales can be re-identifying or reveal something a rater didn't intend to share publicly — review each batch before release |
| Raw model-generated reasoning traces (English pilot and any Urdu traces) | **PUBLIC AFTER REVIEW** | Valuable for replication; must be checked for any inadvertently sensitive content the misleading-hint paradigm might have surfaced, and for license/redistribution terms on the underlying MMLU-derived items |
| Locked Urdu translations of source items | **PUBLIC AFTER REVIEW** | Same considerations as source items; also check translator/provider redistribution terms if a hosted API produced them |
| Same-trace English translations (`T` inputs) | **PUBLIC AFTER REVIEW** | Same as above |
| Rater qualification records (competence basis, not identity) | **PRIVATE** | Useful for audit that competence was real, but may contain enough detail to be identifying in a small rater pool |
| Rater pseudonym-to-identity mapping | **NEVER PUBLIC** | The entire purpose of pseudonymization fails if this is ever released |
| Rater real names, contact info, consent forms, compensation records | **NEVER PUBLIC** | Personal data; retained privately per institutional policy, not part of any research release |
| Raw judge API responses (full, unparsed) | **PRIVATE**, unless the provider's terms explicitly allow redistribution | May contain provider-specific formatting/metadata beyond what redistribution terms permit; the parsed `JudgeOutput` (label, rationale, hashes) is the public-facing form |
| Exclusion records (items excluded during Urdu equivalence review, and why) | **PUBLIC** | Directly relevant to interpreting the final item population; no personal data |
| Adjudication rationales | **PUBLIC AFTER REVIEW** | Same free-text consideration as rater rationales |
| Any content an institution's ethics review flags as sensitive (per `docs/ETHICS_REVIEW_REQUEST_TEMPLATE.md` §14) | **NEVER PUBLIC**, or PUBLIC AFTER REVIEW at the institution's specific direction | Institution-specific; do not default to public without an explicit review outcome |

## What this plan does not decide

- Whether de-identified individual rater labels are released at all (PUBLIC AFTER REVIEW
  vs. PRIVATE) — that's `research/SUPERVISOR_DECISION_PACKET.md` row 4, options (a)
  vs. (b).
- The exact review process and reviewer for any "AFTER REVIEW" row — to be named by the
  investigator/institution.
- Retention duration for PRIVATE and NEVER PUBLIC rows — `docs/
  ETHICS_REVIEW_REQUEST_TEMPLATE.md` §10.
- Whether any provider's terms of service actually permit redistributing raw API
  responses or model outputs at all — verify against the specific provider's current
  terms before any release, separately from this plan's tier assignment.

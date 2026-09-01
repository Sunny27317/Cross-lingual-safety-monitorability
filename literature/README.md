# literature/

Provenance, verified literature evidence, and the novelty audit.

## Contents

| File | What it is | Mutability |
|---|---|---|
| `RUN2_BLUEPRINT.pdf` | The original Run-2 Deep Research report (13 pp). | **Immutable provenance artifact** — never edit or replace. |
| `RUN2_BLUEPRINT_HANDOFF.md` | Structured Markdown extraction of the PDF, tagged `[BLUEPRINT]` / `[PRIOR WORK]` / `[HYPOTHESIS]` / `[PLANNED]` / `[UNRESOLVED]`. | Derived; update only to fix an extraction error (note the fix), never to change the science. |
| `CITATION_VERIFICATION.md` | Independent verification (arXiv / ACL Anthology / model cards) of every citation and number imported from the blueprint. Status: VERIFIED / PARTIALLY VERIFIED / TODO — UNVERIFIED / CONTRADICTED. | Append/update as sources are checked. |
| `COMPETITOR_MATRIX.md` | Per-paper analysis of the closest prior work: RQ, languages, models, datasets, intervention, monitor setup, metrics, findings, limitations, overlap, what we add, threat level. | Update as the literature moves. |
| `DECISION_LOG.md` | Append-only log of major scientific decisions with rationale, evidence, and reversal conditions. | Append-only. |

## Rules

- A citation is factual evidence **only after verification** (title, authors, venue,
  year, and that the paper supports the claim). Unverified → `TODO — UNVERIFIED`.
- Never invent DOI, URL, author, year, or result.
- Do not reconstruct the contents of `RUN2_BLUEPRINT.pdf` from memory — read the PDF.
- New analysis not derived from Run-2 is labelled **NEW INDEPENDENT ANALYSIS — NOT FROM
  RUN-2** (see `CITATION_VERIFICATION.md` §D).
- Novelty is never claimed solely because Urdu is included.

## Status (2026-09-01)

Run-2 blueprint imported and verified. All 12 competitor/foundational citations are real
and correctly identified (three had shorthand titles corrected). The YELLOW verdict
survives (`DECISION_LOG.md` D-007). Standing threats and newer un-cited 2026 work are
tracked in `CITATION_VERIFICATION.md` §D and `COMPETITOR_MATRIX.md`.

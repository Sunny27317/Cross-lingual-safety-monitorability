# Workshop-v1 submission ladder and sealed-to-PDF workflow

Before acting on any step, verify the venue calls, deadlines and preprint/anonymity
policies on the official sites. None are asserted here.

## Recommended ladder

1. **Preprint**, once the human reference, analysis and claim audit are complete. Post
   as a clearly scoped single-language case study. This establishes the record and is
   citable in applications.
2. **First submission: a non-archival workshop** on multilingual/low-resource NLP or AI
   safety, or on reasoning and evaluation. Non-archival keeps the main-track option open.
3. **Fallback: an archival workshop or a Findings-type track**, with the same paper,
   tightened in response to reviews.
4. **Expanded version: a main-track NLP venue or a journal (e.g. TMLR)**. Requirements:
   - at least two more languages, including one in a different script or resource tier;
   - at least one reasoning model with native thinking;
   - a second judge and a second translator;
   - an English human anchor and a paraphrase control;
   - the same governance discipline, with a new preregistration-style freeze.

## Sealed results → PDF (20 steps, in order)

1. **Import result artifacts.** Generation QC, direct-judge and translated-judge post-QC,
   translation QC and audit, locked human labels and adjudication. Record each SHA-256
   in the stage-hash file. The analysis code commit must already exist.
2. **Fill tables.** Run the frozen analysis once and generate Tables 1–8 and S1–S6 from
   its output. No manual edits.
3. **Make figures.** F1–F4 from the same output (see `WORKSHOP_V1_FIGURE_TABLE_PLAN.md`).
4. **Fill Results.** Use `WORKSHOP_V1_RAPID_FILL.md` and `WORKSHOP_V1_RESULT_BRANCHES.md`,
   with interval wording per framework §2.1.
5. **Activate Discussion branches.** Use `WORKSHOP_V1_DISCUSSION_DECISION_TREE_V2.md`.
   Delete inactive paragraphs. Record the activated IDs.
6. **Human-validation section.** Fill κ, raw agreement, adjudication counts and rater
   details (quals, compensation, author-as-rater disclosure).
7. **Limitations audit.** Add any limitation the results reveal, such as high
   `cannot_tell` or concentrated translation failures. Remove none.
8. **Claim ledger audit.** Every claim maps to a SUPPORTED row; exploratory items are
   labelled.
9. **Citations.** Re-check versions and venues; run a fresh closer-work search.
10. **Ethics.** Quote the ORPI determination verbatim; add consent and compensation.
11. **Author contributions** (decision sheet).
12. **Funding** (decision sheet).
13. **Acknowledgments.** Option A or B for the native reviewer; raters per consent.
14. **Reproducibility statement.** All stage hashes, the analysis freeze in past tense,
    and archive links.
15. **Appendix.** A–K complete; Urdu renders correctly.
16. **Anonymization**, only if the target venue is double-blind. Make an anonymized
    copy; follow that venue's rules on concurrent preprints.
17. **PDF build.** Clean compile, embedded Urdu font, no broken references.
18. **Formatting checks.** Page limits, template, figure legibility in greyscale.
19. **Overclaim scan.** The phrase list in `PREPRINT_FINAL_DAY_QC.md` §11, plus the
    banned terms in the claim ledger.
20. **Final submission check.** Investigator reads the PDF end to end, confirms the
    links resolve, and uploads.

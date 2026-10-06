# 08 — Submission readiness checklist

Machine-readable gates are in `research/WORKSHOP_V1_PREPRINT_RELEASE_GUARD.md` (`may_post`).
This list is the human-readable superset, current as of 2026-10-06.

## Experiment completion
- [x] Generation: 3,312 persisted / 3,311 successful; locked
- [x] Direct judging: 1,871 tasks; sealed `3077fae1…`
- [ ] Translation: complete 935; post-QC; seal. The seal records the operative amended
      authorization (in progress; investigator-reported 884/935)
- [ ] Resolve **C1** (six identity translations) and **C2** (translated-judge seal and
      amendment checks); authorize translated judging; run; seal
- [ ] Translation audit on the H/D/T subset (auditor named; scope fixed)
- [ ] ORPI determination saved → recruitment → 2 × 312 labels → adjudication → locked

## Quality control
- [ ] Generation QC table by cell (T1)
- [ ] Judge technical-state table (T2a)
- [ ] Translation failures by reason; no partial translations
- [ ] Human file integrity: 312 IDs, hashes, adjudication via the protocol trigger (after
      the **C3** fix)

## Statistics
- [ ] Analysis code archived (commit), and its hash matches `1671bc3c…`
- [ ] Run the unseal protocol once (`research/WORKSHOP_V1_RESULT_UNSEAL_PROTOCOL.md`)
- [ ] All planned comparisons; S1–S5; exploratory items labelled; no thresholds

## Tables and figures
- [ ] T1–T8, F1–F5, S-F1 generated from the analysis artifact
      (`paper_readiness/04_RESULTS_SHELL.md`)
- [ ] Every caption states denominators, the interval method and "descriptive"

## Manuscript
- [ ] Fill all slots from the slot registry; remove the abstract posting guard
- [ ] Discussion branches via tree V2; claim-ledger audit; tripwire scan
- [ ] `[[SEGMENTATION_VALIDATION]]` filled from a saved artifact (**C6**)
- [ ] Re-verify citations on the upload date

## Reproducibility
- [ ] Pre-result archival commit approved and made; Methods wording per
      `PRE_UNSEAL_AUDIT.md` §10
- [ ] Stage hashes recorded for all stages; errata (C5, C7, C9, C11) in Appendix J
- [ ] Pause note (1.84 h) recorded

## Ethics statement
- [ ] ORPI determination quoted verbatim; consent and compensation statement;
      acknowledgment consent (Amna: named or anonymous)

## Artifacts
- [ ] Release route decided (default: code, hashes and IDs; no item text)
- [ ] No rater identities; no secrets

## Final review
- [ ] Supervisor / co-author review of the full PDF, if applicable (with written
      confirmation)
- [ ] Investigator end-to-end read; flip `may_post`

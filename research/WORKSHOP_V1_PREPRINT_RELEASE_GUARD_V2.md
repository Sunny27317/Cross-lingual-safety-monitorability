# Preprint release guard V2 (hard checklist; 2026-10-06)

This extends `research/WORKSHOP_V1_PREPRINT_RELEASE_GUARD.md`, whose `may_post` stays
`false`. **The preprint is NOT READY until every box below is ticked with an evidence path.**
Only the investigator ticks the boxes.

**Stages**
- [ ] R-1. Translated judging complete, technical QC passed, stage sealed, hash recorded
- [ ] R-2. Analysis frozen and committed; single unseal executed per protocol; result
      artifact hashed
- [ ] R-3. Results filled only from that artifact (zero `{{…}}`, `[[R-…]]` or `[…]`
      result slots)

**Human validation**
- [ ] R-4. Human-validation status resolved. Either H is collected, locked and analysed,
      **or** the paper uses the explicit validation-pending variant (no G, R, A or κ
      claims anywhere, including the abstract and title)
- [ ] R-5. ORPI wording is verbatim from a saved determination, or the "no
      determination received; no annotation conducted" sentence is used

**Privacy and licensing**
- [ ] R-6. Public-repository privacy remediated or explicitly accepted:
      - item-text PDF (`URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.pdf`);
      - reviewer's full name in ~10 committed files;
      - rater-facing documents.
- [ ] R-7. Dataset-licence language final, and consistent with what is actually public
- [ ] R-8. Reviewer identity handled: named only with recorded consent; otherwise
      anonymous everywhere (paper, repository, acknowledgments)

**Text checks**
- [ ] R-9. Placeholder scan passes: zero `[[`, `{{`, TODO, TBD, FIXME and template comments
      in the posted text (`research/WORKSHOP_V1_PLACEHOLDER_STALENESS_AUDIT.md` §3)
- [ ] R-10. Claim-ledger and tripwire scan passes (`WORKSHOP_V1_CLAIM_LEDGER_V2.md`), with
      every "differed/excluded 0" sentence stating its family size
- [ ] R-11. Hashes and provenance final: stage seals, analysis freeze commit, archival
      commit, errata (D-PG-2 2,806; date labels; C9) in Appendix J
- [ ] R-12. Author information complete: names, affiliation only if formal, CRediT,
      funding, conflicts
- [ ] R-13. Citations re-verified on the upload date (Onyame; Doğruöz venue; all arXiv
      versions)

**Final**
- [ ] R-14. Investigator has read the full PDF end to end, then flips `may_post`

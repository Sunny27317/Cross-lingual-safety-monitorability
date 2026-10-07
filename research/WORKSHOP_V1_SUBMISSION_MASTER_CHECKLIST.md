# Workshop-v1 submission master checklist (2026-10-07)

Tick each box only with an evidence path. "(I)" = investigator. "(E)" = engineering (Codex).
"(A)" = analysis.

**Ethics and people**
- [ ] (I) ORPI written determination saved verbatim with its SHA-256; required consent
      wording applied as a dated amendment
- [ ] (I) Compensation decided; investigator-as-rater decided (recommended: not a rater)
- [ ] (I) Translation auditor named (non-rater, or audits after rating)
- [ ] (I) Native reviewer's written sign-off completed (optional but recommended);
      acknowledgment choice recorded (default anonymous)

**Human data**
- [ ] (E) Rater packet regenerated in the frozen order (`ee0e1b57…`); packet and
      assignment hashes recorded (`WORKSHOP_V1_RATER_PACKET_FINAL_SPEC.md`)
- [ ] (E/I) Rater documents reconciled (reviewer name removed); hashes updated
- [ ] (I) 2 raters and 1 adjudicator recruited, qualified, consented, pseudonymized
- [ ] (I) 2 × 312 raw labels locked via `persist_rater_labels`; hashes recorded
- [ ] (I) Adjudication done (independent first label; `unresolved` allowed) via
      `persist_adjudications`; hashes recorded

**Translation audit (S4)**
- [ ] (I) D-FA-7 `audit_flag` rule decided before unseal
- [ ] (I) 312 translations audited with `EquivalenceAudit`; flagged set frozen and hashed
      (or a dated decision: S4 not performed)

**Second judge (optional; secondary)**
- [ ] (I) Decide run or skip. If run: data-policy check, spec and authorization frozen
      **before unseal**; separate seal

**Frozen analysis and unseal**
- [x] (A) Final analysis frozen and committed (V3 `c35785cd`); freeze V4 with binding
- [ ] (E) Translated-judge QC and seal committed; stage-hash file updated
- [ ] (I) Analysis authorization written (binds stage hashes, freeze, human-label hashes,
      B and seed)
- [ ] (I) Single unseal per the protocol and Addenda A1/A2; result artifact hashed

**Results and paper**
- [ ] (A) Tables T1–T7 and figures F1–F7 generated from the artifact only
      (`WORKSHOP_V1_FINAL_TABLES_FIGURES_SPEC.md`)
- [ ] (A) Result slots filled from the artifact; Discussion wording from
      `WORKSHOP_V1_DISCUSSION_DECISION_TREE_FINAL.md`
- [ ] (A) Claim ladder and tripwire scan clean (`WORKSHOP_V1_FINAL_CLAIM_HARDENING_AUDIT.md`)
- [ ] (I) Title chosen (scoped to Urdu)

**Release**
- [ ] (I/E) Public-repository privacy cleanup: item-text PDF and the reviewer's name
- [ ] (I) Data-availability text matches what is actually public; dataset-licence wording
      final
- [ ] (A) Reproducibility statement final: all stage hashes, freeze commit, archival
      commits
- [ ] (A) Placeholder scan: zero `[[`, `{{` and template comments
- [ ] (I) Author information, affiliation only if formal, CRediT, funding, AI-assistance
      statement checked against venue policy
- [ ] (I) Formatting to venue template; page limit
- [ ] (I) Supervisor or co-author review, if applicable (written confirmation)
- [ ] (I) End-to-end read; release guards V1/V2 `may_post` flipped

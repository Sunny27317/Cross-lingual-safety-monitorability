# Human validation: operational readiness audit and final drafts (2026-10-06)

**Status:** NOT AUTHORIZED. No ORPI determination has been received. No rater has been
contacted. No annotation has started.

The rater-package files are hash-recorded in `engineering/rater_package_reconciliation.json`,
so this document **does not edit them**. It audits them and provides drafts. Any change
to a recorded file needs a reconciled update before the package is released to raters.

## 1. Audit

| Component | Where | Finding | Action |
|---|---|---|---|
| Labels | `RATER_INSTRUCTIONS.md` | Five labels (`disclosed`, `not_disclosed`, `partial`, `cannot_tell`, `abstain`) with the Judge V2 boundary rules; `abstain` is optional and carries no penalty | OK |
| Decision tree / FAQ | `ANNOTATION_DECISION_TREE.md`, `RATER_FAQ.md` | Consistent with the D-PG-4 boundaries (per the reconciliation record) | OK |
| Context parity with the judge | packet v2 `rater_context.jsonl` (keys: `blind_id`, `language`, `question`, `options`, `suggestion`, `trace`); D-PG-4 | Matches the judge's non-instruction inputs | OK |
| Blinded identifiers | `blind-<hash>` from the frozen pool rule; lexicographic order (`workshop_v1_human_packet_order.json`) | No model, cue or sample grouping | OK |
| Training | `TRAINING_TUTORIAL.md`: an invented question and **17** practice rationales containing **16** Urdu sentences; verbally confirmed, no written form | Counts are consistent with the manuscript | OK |
| **Reviewer name in rater-facing material** | `TRAINING_TUTORIAL.md` line 7 and `URDU_TRAINING_EXAMPLES_NATIVE_REVIEW.md` name the native reviewer | Raters would see a third party's name; acknowledgment consent is not recorded | **Change before release**: replace the name with "a native Urdu reader" (draft §2.6) and update the reconciliation hashes |
| Adjudication | `ADJUDICATOR_INSTRUCTIONS.md` Step 1 (independent blind first label), then final label or `unresolved` | Enforced in code (`validate_adjudications` requires `independent_label`) | OK |
| Immutable writer | `annotation_io.persist_rater_labels`, `persist_adjudications` (atomic, no-clobber) | Tested | OK |
| Agreement | `AGREEMENT_REPORTING.md`; `final_analysis.human_agreement` (raw %, κ5 with `abstain` as a category, binary κ with n, contingency table) and `human_agreement_intervals` (95% item-cluster bootstrap CIs, D-PG-6 B and seed) | **Gap found and closed tonight**: the CIs that AR specifies were not implemented; now implemented and tested (`test_agreement_intervals_cluster_by_item`), and wired into T7 | OK |
| Five-category reporting | AR; T7 | OK | — |
| Binary subset | AR; `human_agreement.n_binary_subset` | OK | — |

## 2. Final drafts (for investigator review; none is sent)

### 2.1 Onboarding checklist (steward)
1. ORPI determination saved; consent wording per the determination.
2. Qualification screener passed (synthetic text only); conflict of interest confirmed.
3. Pseudonym assigned. Name and contact details stored outside the repository.
4. Compensation recorded on the qualification record.
5. Tutorial and practice set completed; minutes per item measured.
6. Packet v2 delivered (hash `8bccea18…`) with a submission template.
7. The rater confirms they will not discuss items with anyone.
8. Submission written via `persist_rater_labels`; file SHA-256 recorded; the rater
   receives the hash as a receipt.

### 2.2 Disagreement handling
- **Trigger:** the raters disagree, or either abstains. Both rules are frozen.
- **Order of work:** the adjudicator labels independently first, blind to the raters'
  labels. Only then does the adjudicator see both labels and their brief notes, and record
  a final label or `unresolved`, with a rationale referencing the text.
- **Never:** a majority vote; returning items to raters; resolving toward an expected study
  outcome.
- **Unresolved items** are missing in the primary analysis and counted in the cascade.

### 2.3 Version control
- Each submission is a new immutable file: `human/rater_<pseudonym>.jsonl`,
  `human/adjudication.jsonl`.
- SHA-256 hashes are recorded in a dated provenance JSON. Files are never edited.
- Corrections are made only as a new, dated addendum file, explained in Appendix J.
- The package documents are frozen at their recorded hashes when distributed.

### 2.4 Data handling
- **Labels and notes:** stored under pseudonyms in the research record.
- **Names and contact details:** kept separately, outside the repository, and deleted after
  payment (proposed; confirm with ORPI).
- **Raters' copies of the packet:** raters delete them on submission. The packet contains
  rationale text, so it is not posted publicly while the dataset licence is unclear.
- **Release:** labels are released only as ORPI and rater consent allow.

### 2.5 Acknowledgment language
- **Default (anonymous):** "We thank two native Urdu readers and an adjudicator for their
  annotations, and a native Urdu reader for reviewing the item translations and cue
  wordings."
- **Named variant:** only with written consent. Record the consent in
  `engineering/provenance/` before use.

### 2.6 Replacement sentence for rater-facing documents
> "Native meaning review: complete (verbal). A native Urdu reader confirmed to the
> investigator that all 16 Urdu example sentences preserve the intended English meaning."

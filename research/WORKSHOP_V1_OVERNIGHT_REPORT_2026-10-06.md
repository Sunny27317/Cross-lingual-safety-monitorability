# Overnight scientific / manuscript package: completion report (2026-10-06, about 20:40 UTC)

**Result-blind throughout.** No judge label, label frequency, translation meaning, human
label or result was read or computed. The live translated-judge process was not touched.
At 20:35Z the process table showed it no longer running; nothing else about it was
inspected. Nothing is committed.

## Completion estimates

| Part | % | What remains |
|---|---|---|
| Methods | 90 | Translated-judge stage hash; ORPI text; rater qualifications and compensation; analysis freeze commit SHA |
| Introduction | 85 | One results sentence (contribution 3); citation re-check |
| Related work | 85 | Re-verify Onyame and the Doğruöz venue on the upload date; optional verified additions |
| Results scaffold | 95 | Numbers only (fill from the single unseal artifact) |
| Discussion scaffold | 90 | Branch selection after unseal; D-FA-6 decides the cross-model flag wording |
| Limitations | 90 | Final precision sentence (replace design-based widths only if rewritten post-unseal) |
| Human validation package | 85 | ORPI; compensation; investigator-as-rater; translation auditor; reviewer-name removal from rater-facing docs (reconciled update) |
| Reproducibility | 85 | Stage hash for translated judging; freeze commit; archival commit IDs |
| Ethics | 70 | Determination text; consent and acknowledgment decisions |
| Data availability | 60 | **Public item-text PDF and reviewer-name remediation**, or rewrite the text to match reality; release route |
| **Manuscript before results** | **≈ 82** | — |
| **Project before submission** | **≈ 70** | Translated stage unconfirmed and unsealed; human stage (ORPI-gated) is the largest remaining block; unseal and results; release gates |

The project figure is effort-weighted:

| Stage | Share of the total | Credited |
|---|---|---|
| Design, generation, direct judging, translation | 45% | full |
| Translated judging | 10% | half (not confirmed or sealed) |
| Analysis implementation | 10% | 90% |
| Human stage | 20% | 20% |
| Unseal and results | 5% | 0% |
| Manuscript | 10% | 80% |

## Self-review (Task 22)

- **Diff:** only new, untracked files on this branch. No tracked file is modified, so the
  frozen `analysis.py` and `metrics.py`, the framework and the plan imports are unchanged.
- **No real result data read:** the new modules contain no file I/O, except the loader,
  which refuses `experiments/_runs` paths. Tests use temporary synthetic directories.
  `frozen_item_metadata` reads only design data (manifests, generation plan, source answer
  keys).
- **No judge labels loaded.** No live-run file modified (only the live judge's own output
  directory changed tonight). No human annotation started.
- **No outcome-dependent wording.** Every number in the new documents is either a design
  quantity, a technical count already sealed (e.g. 1,863/5/3), a hash, a synthetic oracle
  value, or a labelled hypothetical (precision table).
- **Unresolved choices:**
  - The **zero-sign convention** was being applied silently by the V1 code. It is now
    explicit (`ZERO_SIGN_UNDECIDED` until D-FA-6).
  - The **R_full** paired reading is documented as determined by the locked text, with
    reasoning; countersignature is optional.
  - No other choice was made.
- **Planned-but-missing item found and fixed:** κ / raw-agreement bootstrap CIs required by
  `AGREEMENT_REPORTING.md` (`human_agreement_intervals`).

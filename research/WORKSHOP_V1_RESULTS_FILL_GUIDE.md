# When results are ready: one-pass fill guide

> **Superseded in part (2026-10-04):** slot IDs and table/figure numbers are governed by
> `research/WORKSHOP_V1_SLOT_REGISTRY.md` and `WORKSHOP_V1_TABLE_SHELLS_AND_CAPTIONS.md`;
> abstract slots by `WORKSHOP_V1_ABSTRACT_MASTER.md`. The content definitions here remain valid.


**Preconditions (all must hold before step 1):**
- D-PG-6 analysis code committed and hash recorded;
- direct and translated judge post-QC locked;
- translation QC and audit locked;
- human labels locked and adjudicated.

Then run the frozen analysis **once**. Never type a number by hand. Copy it from the
analysis output, and add a comment with the ledger row ID.

**Interval wording (D-PG-6 95% item-cluster intervals):**
- CI excludes 0: "descriptively higher/lower".
- CI includes 0: "not resolved; compatible with a to b".
- Zero denominator: "UNDEFINED".

**Order:** §5 slots → Tables/Figures → §6 (decision tree) → Abstract → Intro summary →
Conclusion → claim audit.

| Slot(s) | Artifact | Statistic | Denominator | Allowed sentence | Forbidden |
|---|---|---|---|---|---|
| R-QC-1..4 | generation QC + AN | counts and rates | 3,312 planned; 3,311 completed; per cell | "3,311 of 3,312 completed; [n] produced a parseable answer." | "All completed"; hiding differential failure |
| R-COMP-1..3 | AN | `compliant` rate; script bins | traces with a reasoning span, per cell | "[x]% of [model]'s Urdu-requested rationales were predominantly in Urdu script." | "Thinks in Urdu"; any new threshold |
| R-ACC-1..4 | AN | Control accuracy | parsed Control traces per cell | "Control accuracy was [x] (EN), [y] (UR)." | General language-ability claims |
| R-CUEA-1 / R-CUEB-1 | AN | ΔTM, paired CI | Cue A: 120-item cells; Cue B: the 36 items vs Control on the same 36 | "[Cue] increased selection of the suggested option by [d] points (CI)." Only if CI > 0 | "Unfaithful", "deceptive", "sycophantic" |
| R-LANG-B-1 | AN | ΔTM(ur) − ΔTM(en) | as above | resolved / not-resolved wording | "Equivalent"; "the Urdu language causes" |
| R-AB-1 | AN | Cue B − Cue A(36) | shared 36 items | "On the 36 shared items, the user-asserted cue [differed / did not resolvably differ]." | Full-120 comparison; general authority-vs-user claims |
| R-MON-1..2 | direct judge + AN | D_en, D_ur | binary-labelled traces per model × cue | "The judge labelled [x]% EN / [y]% UR as disclosing." | "Models disclosed [x]%" |
| R-MON-3 | AN | AG, paired CI | both arms binary | "Automated rates differed by [d] (CI)." | Interpreting AG in Results |
| R-MON-4 | direct-judge post-QC | partial / cannot_tell / technical-state rates | traces sent (936 EN; 935 UR) | "Non-decisions [x]%, failures [y]%." | Coercing non-decisions to not_disclosed |
| R-HUM-1..4 | human labels + AN | % agreement, κ (5-cat; binary + n), CI; adjudication counts; H | 312; binary subset n | "Raters agreed on [x]% (κ = [k], CI)." | Verbal bands; "reliable"; "ground truth" |
| R-GAP-1..3 | AN | G, confusion matrix, S1–S3, S5 | complete H/D pairs (≤120 Cue A, ≤36 Cue B per model) | "The direct monitor under-/over-labelled disclosure by [d] points (CI)", or "no gap resolved; beyond [a, b] not supported" | "Monitors fail in Urdu"; "model hid reasoning"; English-validity claims |
| R-TR-1..4 | translation, translated judge, audit, AN | R_full, R, agreement diagnostic (exploratory), failures, audit counts | Urdu traces with binary D_ur and T; triples; 935 | "Translating before monitoring changed / did not change the automated rate by [d]." | "Mitigation / recovery / language-specific" |
| R-MOD-1 | AN | consistency flags | parent quantities | "Direction was consistent / differed across configurations." | Pooling; size/family attribution |
| R-SENS-1..3 | AN | S1–S5; exploratory compliance; worst-case bounds | as parent | "Conclusions were [not] sensitive to …"; "(exploratory) …" | Calling bounds CIs; promoting exploratory results |
| R-DISC-* | same artifacts as the parent slot | as named | as parent | the activated paragraph's wording | — |
| R-ABS-1..6, R-INTRO-1, R-CONC-1..3 | the filled §5 slots | — | — | only ledger rows with ABS=YES and supported | anything not already in §5 |

**After filling:**
- Delete inactive Discussion paragraphs.
- Run the tripwire phrase search (ledger).
- Confirm no `[[` remains.
- Run `research/PREPRINT_SUBMISSION_CHECKLIST.md`.

Full per-slot detail: `research/WORKSHOP_V1_RESULTS_WRITING_MATRIX.md`.

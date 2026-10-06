# Workshop-v1 canonical result-slot registry

**Canonical.** Where this file conflicts with slot IDs or table/figure numbers in
`WORKSHOP_V1_RESULTS_WRITING_MATRIX.md`, `WORKSHOP_V1_RAPID_FILL.md`,
`WORKSHOP_V1_RESULTS_FILL_GUIDE.md` or `WORKSHOP_V1_FIGURE_TABLE_PLAN.md`, **this file
wins.** Table and figure numbering follows `WORKSHOP_V1_TABLE_SHELLS_AND_CAPTIONS.md`.
Each slot has exactly one prose destination. Tables and figures are filled from the same
analysis output and are not separate "slots".

| Slot | Prose destination (preprint) | Table / figure | Source artifact | Definition (matrix row) |
|---|---|---|---|---|
| R-QC-2 | §5.1 | T1 | generation QC | parseable final answers, overall |
| R-QC-3 | §5.1 | T1 | generation QC + analysis | parse-failure / trace / truncation by cell (matrix R-QC-3 and R-QC-4 merged) |
| (R-QC-1) | fixed text §5.1 (3,312 / 3,311) | T1 | — | not a slot |
| R-COMP-1, R-COMP-2 | §5.2 | T8, Fig. S1 | analysis | compliant rate, Urdu, per model (matrix R-COMP-3 bins → Fig. S1 only) |
| R-ACC-1..4 | §5.3 | T4 | analysis | Control accuracy |
| R-CUEA-1 | §5.3 | T4, F3 | analysis | ΔTM Cue A (switch rate, matrix R-CUE-SW → T4 supporting column only) |
| R-CUEB-1 | §5.3 | T5 | analysis | ΔTM Cue B on the 36 items |
| R-LANG-B-1 | §5.4 | T3, F3 | analysis | ΔTM(ur) − ΔTM(en) |
| R-AB-1 | §5.5 | T5 | analysis | Cue B − Cue A(36) |
| R-MON-0 | §5.6 | T2a | direct-judge technical QC | cell breakdown of the 5 malformed and 3 no-label outputs (**new; added to the matrix by this registry**) |
| R-MON-1, R-MON-2 | §5.6 | T2, F2 | analysis | D_en, D_ur |
| R-MON-3 | §5.6 | T3, F3 | analysis | AG |
| R-MON-4 | §5.6 | T2 | direct-judge QC + analysis | `partial` / `cannot_tell` rates by arm |
| R-HUM-1..4 | §5.7 | T7a | human + analysis | agreement, κ, adjudication, H distribution |
| R-GAP-1..3 | §5.8 | T7b, F5 | analysis | G, confusion matrix, S1–S3/S5 for G |
| R-TR-1..4 | §5.9 | T6, F4 | translation + translated judge + audit + analysis | R_full, R, agreement diagnostic (exploratory), failures/audit |
| R-MOD-1 | §5.10 | consistency rows in T2, T3, T7 | analysis | cross-model flags |
| R-SENS-1..3 | §5.11 | T8, S1–S13 | analysis | sensitivity, exploratory compliance, bounds |
| R-DISC: * | §6 activated paragraphs only | — | the same values as the parent slot, never recomputed | — |
| `[PRIMARY_LANGUAGE_DIFFERENCE]`, `[MAIN_INTERVAL]` | Abstract | — | = R-MON-3 (AG) and its CI | replaces the former R-ABS-2 |
| `[HUMAN_JUDGE_AGREEMENT]` | Abstract | — | = R-GAP-1 (G) + R-HUM-1 (κ) | replaces the former R-ABS-3/5 |
| `[DIRECT_VS_TRANSLATED_DIFFERENCE]` | Abstract | — | = R-TR-1 / R-TR-2 | replaces the former R-ABS-4 |
| `[IMPLICATION]` | Abstract | — | the activated Discussion branch | replaces the former R-ABS-6 |
| (former R-ABS-1, cue effect) | — | — | — | **Dropped from the abstract.** The cue effect is reported in §5.3 only; the abstract may mention it only if the ledger supports it |
| R-INTRO-1, R-CONC-1..3 | §1 end, §8 | — | copied from filled §5 slots | — |

**Rule.** Abstract, introduction, discussion and conclusion values are copies of §5 slot
values. They are never computed separately.

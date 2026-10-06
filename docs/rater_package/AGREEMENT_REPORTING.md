# Agreement-reporting specification and language (Workshop-v1)

Fixed before annotation begins. Computed only by the frozen analysis code at its recorded
commit. No value is entered by hand.

## What is computed

| Quantity | Population | Notes |
|---|---|---|
| Raw label distribution, per rater | all 312 items | five labels, plus uncertainty-flag counts |
| Rater 1 × Rater 2 contingency table | all 312 | always shown in full (Appendix) |
| Cohen's κ, five-category | all 312 pairs, `abstain` treated as a category | 95% item-cluster bootstrap CI (same B/seed as D-PG-6) |
| Cohen's κ, binary | pairs where both raters chose `disclosed` or `not_disclosed` | 95% CI; state the n of the pair subset |
| Raw percent agreement | same two populations | reported beside κ (κ can be low when one label dominates) |
| Adjudication count and outcome | flagged items (disagreement or any `abstain`) | matched rater 1 / rater 2 / neither / unresolved |
| Final reference `H` distribution | 312, by model × cue | binary `H` = adjudicated `disclosed`/`not_disclosed`; others missing |

The investigator does not inspect agreement statistics until both raters have submitted
and locked their labels.

## Permitted wording

- "Before adjudication, the two raters agreed on [x]% of items (Cohen's κ = [k], 95% CI
  [a, b]; five categories, n = 312). On the [n] items both raters labelled `disclosed` or
  `not_disclosed`, κ = [k] ([a, b])."
- "[n] items ([x]%) were adjudicated; the adjudicator's final label matched rater 1 on
  [n], rater 2 on [n], neither on [n], and [n] were left unresolved."
- "Disagreements were concentrated in [label pair], consistent with the rubric's
  acknowledged boundary between mention and stated influence." Use this only if the
  contingency table shows it.

## Prohibited wording

- Calling post-adjudication agreement "inter-rater reliability" or "agreement".
- Any verbal band or cutoff ("substantial", "moderate", "acceptable", or a numeric κ
  threshold). Agreement is reported and interpreted continuously, together with raw
  agreement and the contingency table (cutoff withdrawn 2026-10-04, before any label
  existed).
- Reporting κ without its CI, or binary κ without its subset n.
- Dropping `abstain`/`unresolved` items without reporting them.
- Describing H as "ground truth". Use "native-reader reference".

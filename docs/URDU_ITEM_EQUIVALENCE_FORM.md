# Urdu item equivalence form — one record per source item

**Fillable per-item record, not prose.** Complete one copy of this form for every
source item before its Urdu material is locked. This form implements the checklist in
`docs/HUMAN_URDU_VALIDATION_PACKAGE.md` §"Urdu material QA checklist" and
`experiments/M3-English-Urdu/URDU_PROTOCOL.md` as a concrete record; it does not change
either. No item is used in collection until its form is complete and signed.

## 1. Source item identity

| Field | Entry |
|---|---|
| Source dataset / revision | e.g. `cais/mmlu`, `c30699e8356da336a370243923dbaf21066bb9fe` |
| Source item ID | |
| Subject | |
| Source question text (verbatim, hashed) | text hash: |
| Source choices A–D (verbatim, in order, hashed) | text hash: |
| Correct answer index | |
| Hint/cue text as used in the treatment condition (verbatim, hashed) | text hash: |
| Partition assignment (rubric-training / calibration / heldout / confirmatory) | from `partitions.assign_source_items`; must not be filled in by hand |

## 2. Forward translation

| Field | Entry |
|---|---|
| Translator (name/role, or system + version if machine-drafted) | |
| Date | |
| Urdu question text | |
| Urdu choices A–D, in the same order as source | |
| Urdu hint/cue text, preserving epistemic force and source attribution | |
| Translation method (human forward translation / machine draft + full native correction) | |
| If machine draft: reviewer who performed the full native correction | |
| Urdu text hash (question + choices + cue, canonical Unicode) | |

## 3. Independent bilingual review (one row per reviewer; minimum two)

| Field | Reviewer 1 | Reviewer 2 |
|---|---|---|
| Reviewer pseudonym | | |
| Date | | |
| Question meaning preserved? (Y/N) | | |
| All four choices preserved, same order, same correctness? (Y/N) | | |
| Distractor plausibility preserved? (Y/N) | | |
| Negation/quantifiers/units/numbers preserved? (Y/N) | | |
| Hint epistemic force/source attribution preserved, no added/removed deference? (Y/N) | | |
| RTL rendering, Unicode normalization, Latin A–D labels intact? (Y/N) | | |
| Culturally loaded or untranslatable element flagged? (Y/N; describe below if Y) | | |
| Free-text notes / flagged issues | | |

## 4. Discrepancy classification (complete one row per flagged issue, if any)

| Issue # | Category (answer-changing / cue-strength-changing / meaning-changing / cultural-ambiguity / format-only) | Description | Reviewer(s) who flagged it |
|---|---|---|---|
| | | | |

**Category definitions:**
- `answer-changing` — the translation makes a different choice correct, removes/adds a
  distinguishing distractor property, or otherwise changes the answer key. **Blocks lock.**
- `cue-strength-changing` — the hint's epistemic force, certainty, or source authority is
  stronger/weaker in Urdu than English. **Blocks lock.**
- `meaning-changing` — any other change to question/choice/cue meaning not covered above.
  **Blocks lock.**
- `cultural-ambiguity` — a reference, idiom, or assumption may not transfer, without
  changing the answer or cue. Does not block lock by itself; flagged for the exclusion/
  sensitivity policy below.
- `format-only` — script, punctuation, spacing, or normalization only. Does not block lock.

## 5. Adjudication (required only if any `answer-changing`, `cue-strength-changing`, or
`meaning-changing` issue was flagged)

| Field | Entry |
|---|---|
| Adjudicator pseudonym | |
| Date | |
| Independent blind read performed before viewing reviewer rationales? (Y/N) | |
| Resolution (repair translation / exclude item / escalate to investigator) | |
| If repaired: new Urdu text hash | |
| Rationale (short) | |

An item with an unresolved `answer-changing`, `cue-strength-changing`, or
`meaning-changing` issue after adjudication is **excluded**, not force-locked. Record the
exclusion and reason; do not substitute an easier item.

## 6. Semantic-equivalence lock

| Field | Entry |
|---|---|
| All flagged non-format issues resolved (repaired or excluded)? (Y/N) | |
| Cultural-ambiguity flags retained as a sensitivity note (not resolved, just disclosed)? (Y/N) | |
| Final locked Urdu text hash (question + choices + cue) | |
| Lock timestamp (UTC) | |
| Steward pseudonym who validated lineage before lock | |
| Lock record hash (`object_hash` of this completed form) | |

**Cultural/lexical ambiguity policy:** an item is not excluded solely for a disclosed
cultural or lexical ambiguity that does not change the answer or cue strength. It is
locked with the ambiguity noted here and carried into the paper's limitations as a
population-level caveat, per `docs/HUMAN_URDU_VALIDATION_PACKAGE.md`: "Do not claim
equal difficulty from a fluency review."

**Token/script issues:** record here any item whose Urdu rendering required a token
budget different from the English original's assumptions (§"Context requirement" in
`research/POST_PILOT_METHODS_DECISIONS.md` §F applies at the judge/translator stage, not
here; this row is only about whether the source Urdu text itself renders correctly and
completely, with no truncation or mis-encoding, at rest).

## 7. Urdu-language suitability (generator-side, separate from translation quality)

This form locks the **item's** Urdu text. It does not certify that the frozen generator
(`Qwen/Qwen3-1.7B`, unchanged) produces usable Urdu reasoning for this item — that is an
observed, post-hoc property of the actual Urdu run, not something a translation review
can pre-certify. Do not use this form to select items expected to produce "better" Urdu
generations.

## 8. Trace provenance and downstream propagation

| Field | Entry |
|---|---|
| This form's own content hash (recompute after any edit) | |
| Every downstream artifact that has already consumed this item's prior hash (list run/report IDs) | |

**Edit-invalidation rule.** Any edit to the locked Urdu text (§6) after lock — including
a later-discovered discrepancy — creates a **new** hash and a **new** version of this
form; it does not overwrite the old one. Every downstream artifact keyed to the old hash
(dataset pin, generation records, judge/translation records, analysis reports) is thereby
stale and must be either regenerated against the new hash or explicitly carried forward
with a recorded deviation note — never silently treated as still valid. If any scientific
output has already been produced from the old hash, record the edit as a dated deviation
in the eventual pilot/measurement report, per the existing "any later correction
invalidates the old lock for a new analysis and requires a visible deviation and
sensitivity report" rule in `experiments/M2-Monitor-Validation/ADJUDICATION_PROTOCOL.md`.

## 9. Sign-off

| Field | Entry |
|---|---|
| Investigator approval | |
| Date | |
| This item is cleared for Urdu collection (Y/N) | |

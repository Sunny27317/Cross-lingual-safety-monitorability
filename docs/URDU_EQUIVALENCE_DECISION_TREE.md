# Urdu equivalence decision tree

Used by the adjudicator once a translated item has one or more flagged discrepancies
(`docs/URDU_ITEM_EQUIVALENCE_FORM.md` §4). Not used by the translator or reviewers
directly — they flag issues; this tree decides what happens next.

```
START: an item has at least one flagged discrepancy.
  |
  v
Q1. Independently re-read the English source and the Urdu draft yourself,
    before looking at the reviewers' rationales. Does the discrepancy
    change the correct answer, or which distractor is most plausible?
  YES -> category: answer-changing -> go to Q4
  NO  -> continue
  |
  v
Q2. Does it change how strongly, or from what source, the hint claims
    the answer is correct (e.g. "suggested" became "confirmed")?
  YES -> category: cue-strength-changing -> go to Q4
  NO  -> continue
  |
  v
Q3. Does it change any other aspect of meaning not covered by Q1/Q2
    (e.g. a technical term mistranslated, a negation dropped)?
  YES -> category: meaning-changing -> go to Q4
  NO  -> continue
  |
  v
Is it a cultural/lexical reference that may not transfer, WITHOUT
changing the answer or hint strength?
  YES -> category: cultural-ambiguity -> go to Q5 (does not block lock)
  NO  -> category: format-only (script/punctuation/spacing) -> go to Q5 (does not block lock)


Q4 (answer-changing / cue-strength-changing / meaning-changing — ALL BLOCK LOCK):
  Can the translation be repaired to remove the issue without changing
  anything else?
    YES -> repair, assign a new Urdu text hash, re-run bilingual review
           on the repaired item before lock.
    NO  -> exclude the item. Record the exclusion and reason
           (`docs/URDU_ITEM_EQUIVALENCE_FORM.md` §5). Do not substitute
           a different, easier item in its place without a separate,
           prospectively documented exclusion/substitution rule.

Q5 (cultural-ambiguity / format-only):
  format-only -> fix directly (e.g. a stray character), no adjudication
                 rationale needed beyond noting the fix.
  cultural-ambiguity -> do NOT exclude solely for this. Lock the item
                 with the ambiguity noted as a permanent sensitivity flag,
                 carried into the paper's Limitations
                 (`paper/main.md` §Limitations) as a population-level
                 caveat, not resolved by pretending it isn't there.
```

## Escalation

If a discrepancy doesn't fit any category cleanly, or you (the adjudicator) are unsure
whether it's `answer-changing` vs. `meaning-changing`, escalate to the investigator
rather than guessing — record the escalation and its resolution in the form. Do not
resolve a translation dispute by which resolution would make the study's expected effect
larger or smaller; you are not told what direction is expected, and should not infer one.

## Version lock

Once an item passes this tree with no unresolved `answer-changing`,
`cue-strength-changing`, or `meaning-changing` issue, lock it
(`docs/URDU_ITEM_EQUIVALENCE_FORM.md` §6) with a hash of the final text. Any later edit —
even a small one, even after data collection has started — creates a new version and
triggers the edit-invalidation propagation rule in that form's §8. It never silently
overwrites the locked version.

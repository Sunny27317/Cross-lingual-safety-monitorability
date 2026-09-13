# Bilingual reviewer instructions

You independently check a translator's Urdu draft against the English source, for every
item. You work independently of the other reviewer (there are at least two of you, per
item) until both of your reviews are recorded — do not compare notes beforehand.
Record your work in `docs/URDU_ITEM_EQUIVALENCE_FORM.md` §3.

## What you are checking, item by item

1. **Question meaning.** Does the Urdu question ask the same thing as the English one?
2. **All four choices, in order.** Same meaning, same order, same correct answer, same
   relative plausibility of distractors.
3. **Numbers, units, negation, quantifiers.** Anything that changes the literal content
   (a number, a "not," a "some" vs. "all") must be checked word by word, not skimmed.
4. **Hint strength and source.** Does the Urdu hint claim the same degree of certainty
   and the same source/authority as the English original? This is the item most likely
   to drift without anyone noticing, because small politeness or certainty shifts feel
   natural in translation but change the experimental manipulation.
5. **Script, formatting, and labels.** Urdu renders correctly right-to-left, the A/B/C/D
   labels are intact and in the Latin script the study parser expects, and there's no
   invisible or stray character.
6. **Cultural or lexical flags the translator raised.** Read their note, and add your
   own assessment — agree, disagree, or flag differently.

## How to record your review

For each item, answer yes/no on each checklist row in the form, and write a free-text
note for anything you're unsure about or want the adjudicator to see. If you find an
issue the translator didn't flag, add it yourself using the same discrepancy categories
(`docs/URDU_ITEM_EQUIVALENCE_FORM.md` §4): `answer-changing`, `cue-strength-changing`,
`meaning-changing`, `cultural-ambiguity`, or `format-only`.

## Independence

Complete your review before discussing the item with the other reviewer or the
translator. Two independent reviews are only informative if they're actually
independent — comparing notes first defeats the purpose, the same way it would for the
disclosure raters (`docs/rater_package/RATER_INSTRUCTIONS.md`, "Independence").

## Disagreement is expected, not a problem

If you and the other reviewer disagree about whether something is
`answer-changing` vs. `cultural-ambiguity`, or whether an issue exists at all, that's
recorded and goes to adjudication (`docs/URDU_EQUIVALENCE_DECISION_TREE.md`) — you don't
need to resolve it yourselves.

## No silent corrections

If you think a translation should be different, don't just fix it yourself. Flag it
with your reasoning; the adjudicator decides whether and how to repair it, and the
change is version-locked and hashed (`docs/URDU_ITEM_EQUIVALENCE_FORM.md` §8).

## What "equivalence" does not mean

Confirming equivalence means the meaning, choices, and hint strength survived
translation. It does not mean the item is equally easy in Urdu, equally natural-sounding,
or free of all translationese — those are separate, real limitations reported elsewhere
(`paper/main.md` §Limitations), not something your review is meant to fix or hide.

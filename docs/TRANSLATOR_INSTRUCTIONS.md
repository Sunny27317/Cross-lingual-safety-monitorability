# Translator instructions

You are producing the forward Urdu translation of the frozen English source items
(question, four answer choices, and the shared hint text). This is source-material
translation for the study design, not the same-trace translation diagnostic done later
on generated model output — that is a separate, automated step
(`experiments/M3-English-Urdu/TRANSLATION_PROTOCOL.md`). No real translation has been
done yet; you are the first human step in that chain.

## Your task

For each source item, produce:
1. The Urdu translation of the question.
2. The Urdu translation of each of the four answer choices, in the same order.
3. The Urdu translation of the shared hint/cue text.

Record your work using `docs/URDU_ITEM_EQUIVALENCE_FORM.md`, §2 ("Forward translation").

## What you must preserve exactly

- **Meaning.** The question must ask the same thing; each choice must mean the same
  thing as its English original.
- **Answer choices and correctness.** The correct answer must still be correct after
  translation, and no distractor may become more or less plausible than in English.
  Do not simplify a choice, add a clarifying word, or fix an ambiguity present in the
  English original — translate what's there, including its rough edges.
- **The hint's strength.** If the English hint says an authority "suggested" an answer,
  the Urdu translation must also say "suggested," not something stronger ("confirmed,"
  "proved") or weaker ("wondered whether"). Do not add extra politeness, deference, or
  certainty that isn't in the English original — this is the single most
  scientifically important thing to get right, because the hint's strength is part of
  the experimental design.
- **Numbers, units, dates, technical terms, and formatting.** Keep numbers and
  mathematical notation exactly as given; translate technical/domain terms accurately
  rather than guessing at a folk equivalent.
- **Choice order and labeling.** Choice A stays first, B second, C third, D fourth —
  never reorder them, even if a different order would read more naturally in Urdu.

## What you must NOT do

- Do not correct an error in the English source (e.g., if a distractor is oddly
  worded, translate it as-is rather than fixing it).
- Do not add an explanation, clarification, or extra context not in the English.
- Do not localize or culturally adapt a reference to make it more familiar — flag it
  instead (see below).
- Do not decide on your own that an item is untranslatable and skip it — flag it for
  review instead.

## Mixed Urdu/English terminology

Many technical/academic terms are commonly used in English even in Urdu speech and
writing (e.g., certain scientific or mathematical terms). Where a term is more
naturally left in English within otherwise-Urdu text, do so — this is normal
code-switching, not an error. Note your choice in the form's free-text field so a
bilingual reviewer can check it, rather than silently picking one convention.

## Transliteration

Where a proper noun or term has no standard Urdu spelling, use a standard, defensible
transliteration and note it in the form. Do not invent an unusual spelling without
flagging it.

## Lexical ambiguity and cultural references

If a word, phrase, or reference doesn't have a clean one-to-one Urdu equivalent, or
carries a cultural assumption that may not transfer, **do not silently pick your best
guess and move on**. Translate as closely as you can, and flag the item in
`docs/URDU_ITEM_EQUIVALENCE_FORM.md` §4 as `cultural-ambiguity` (if it doesn't change
the answer or hint strength) or the appropriate other category (if it might).

## No silent corrections

Every choice you make that isn't a direct, unambiguous translation must be visible to
the bilingual reviewer — either through the form's discrepancy fields or a free-text
note. The reviewer should never have to guess what you decided or why.

## Version and disagreement

Your draft is not final. It goes to independent bilingual review
(`docs/BILINGUAL_REVIEWER_INSTRUCTIONS.md`); disagreements are adjudicated
(`docs/URDU_EQUIVALENCE_DECISION_TREE.md`) before anything is locked. If a reviewer
disagrees with a choice you made, that's expected and normal — it's exactly what the
review step is for.

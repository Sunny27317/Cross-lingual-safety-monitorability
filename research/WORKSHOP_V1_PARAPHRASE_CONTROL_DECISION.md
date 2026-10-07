# Paraphrase-control decision memo (2026-10-07; no new condition executed)

**A. What it would solve.**
R = mean(T − D_ur) changes two things at once:
- the *language* the monitor reads (English instead of Urdu);
- the *text* itself, because machine translation rewrites wording, can drop or add hedges
  and attributions, and splits sentences.

A paraphrase control (P) would hold language fixed and change only the wording: an Urdu →
Urdu paraphrase, judged the same way. Then:
- **T − P** isolates the language-of-reading effect;
- **P − D** isolates the rewriting effect.

Only with P could a difference in R be attributed to language rather than to rewriting.

**B. Why R is descriptive now.** D-PG-3 (approved 2026-10-04) dropped P and fixed R as a
descriptive contrast. The plan's earlier requirement (plan §6) was superseded, and the
paper makes no language-specific or mitigation claim from R.

**C. Cost and delay of adding it now.**
- It needs a paraphraser: a model choice, and a prompt or system to freeze. The paraphraser
  must preserve disclosure meaning, which would itself need native validation. Otherwise P
  is just another unvalidated rewrite.
- It needs 935 new judge calls on paraphrases, a new seal, new governance (an estimand
  amendment, new sensitivity rules) and probably a new native audit.
- Realistically **1–3 weeks** of work and another post-generation design addition, which
  adds multiplicity and governance surface. That is the over-engineering concern raised in
  external review.
- It does not touch the primary estimand G, which needs no paraphrase control: G compares
  the monitor with native readers on the same Urdu text.

**D. Publishable without it?** **Yes**, for a workshop or short paper. The contribution is G
on fixed rationales. R is an honest descriptive secondary result, with its confound stated
in Limitations and in the claim ladder.

**E. Recommendation.** **Keep R descriptive and proceed. Do not add a paraphrase control to
Workshop-v1.** Spend the effort on the human validation, which carries the primary
estimand, and, if anything, on the prospective second-judge robustness check, which
addresses the largest reviewer weakness. Put a paraphrase control (with native validation of
paraphrase fidelity) in the expanded study.

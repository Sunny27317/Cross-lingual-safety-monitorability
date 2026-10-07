# Title and abstract package (outcome-blind; written 2026-10-06; final title not chosen)

## Titles

**Conservative**
1. A Native-Reader Reference for Cross-Lingual Disclosure Monitoring: An Urdu Case Study
2. Same Rationale, Three Readers: Checking an Automated Disclosure Monitor Against Native Urdu Readers
3. Validating an Automated Chain-of-Thought Disclosure Monitor on Urdu Rationales

**Balanced**
4. Monitor or Model? Native-Urdu Validation of Automated Disclosure Monitoring for Multilingual Reasoning Traces *(existing default)*
5. Same Trace, Different Reader: Disclosure Monitoring in English and Urdu
6. Is It the Rationale or the Reader? Separating Monitor Error from Model Disclosure in Urdu
7. Before Reading Monitor Rates as Model Behavior: A Native-Reader Check in Urdu

**Ambitious but defensible** (each must be paired with an abstract that states the scope)
8. When Monitoring Changes Language, Who Changes? Native Readers, Translation and an Automated Monitor on Urdu Rationales
9. Cross-Lingual Monitorability Needs In-Language Validation: Evidence from Urdu *(only if G ≠ 0 and replicates)*
10. Translate, Then Monitor? A Same-Trace Test of Automated Disclosure Monitoring in Urdu

**Notes on the titles:**
- Titles 9 and 10 presuppose a direction or a central role for translation. Use them only
  if the results warrant it.
- Titles 4 and 5 say "multilingual"/"English and Urdu". Pair them with "a case study" in
  the abstract.
- The body uses "rationale". If the title says "reasoning traces", define it in the first
  paragraph.

## Abstract skeletons

All `[…]` are filled only from the unseal artifact. Branch wording follows
`research/WORKSHOP_V1_ABSTRACT_MASTER.md`.

**A. Workshop, conservative (≈150 words)**
> Automated monitors read model rationales for signs that a suggestion influenced an
> answer. When monitoring is applied to another language, a changed detection rate could
> reflect the rationales or the monitor. We test this for Urdu with a same-rationale
> design. Two small open models (Qwen3-1.7B, Gemma-3-4B-it) answered 120 science questions
> in English and Urdu, with and without a misleading suggestion. One automated monitor then
> scored each Urdu rationale directly and after machine translation, and two native readers
> labelled a fixed sample of 312. The monitor–reader gap was [G result with interval, per
> model], and translating before monitoring changed automated labels by [R_full]. [One
> sentence: replicated / not across models.] Results describe these two models, one
> monitor, one translator and one language. They show [whether] automated disclosure rates
> in Urdu need native validation before being read as model behavior.

**B. Findings-style (≈200 words)**
> Chain-of-thought monitoring is increasingly proposed as an oversight tool. Multilingual
> evaluations report that monitoring changes outside English, but there the monitor is
> also the measuring instrument, so a language difference in detection can arise from the
> model or from the monitor. We separate the two by holding the rationale fixed. In
> 3,312 generations from two open models on English and Urdu versions of 120 OpenBookQA
> items, each rationale following a misleading suggestion is scored by Falcon-H1-7B in
> Urdu, by the same monitor after IndicTrans2 translation, and, for a hash-selected 312, by
> two native readers with adjudication. Our primary estimand, the monitor-validity gap G
> (native-reader minus monitor disclosure on the same rationales), was [result, intervals,
> replication]. The apparent automated language gap was [AG]. Translation changed
> automated labels by [R_full]; agreement with readers [exploratory A]. Reader agreement was
> κ = [·]. Analyses were frozen before any label was examined; all intervals are
> descriptive, and sensitivity analyses [summary]. We discuss what this design can and
> cannot attribute to models versus monitors.

**C. General-audience preprint (≈170 words)**
> AI systems are sometimes checked by having another AI read their step-by-step reasoning.
> Does such a checker work as well when the reasoning is written in Urdu instead of
> English? A drop in what the checker finds could mean the AI revealed less, or that the
> checker understood less. We kept the reasoning text fixed and compared three readers of
> it: the automated checker reading Urdu, the same checker reading an English
> translation, and fluent Urdu readers. In this case study with two small open models, the
> checker [agreed with / diverged from] the human readers by [G], and translation [changed
> / did not resolvably change] its judgments [R_full]. The findings are limited to one
> language, one checker and small models. They illustrate why automated monitoring in
> other languages should be checked against native readers before its numbers are trusted.

**Guard:** if posted before native-reader labels exist, no abstract may state any G, R, A
or κ value. Use the "validation pending" variant.

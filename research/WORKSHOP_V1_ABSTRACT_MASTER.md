# Workshop-v1 abstract master template and four branches

**Slots.** Fill only from the frozen analysis output. Wording rules: framework §2.1.

| Slot | Content |
|---|---|
| `[PRIMARY_LANGUAGE_DIFFERENCE]` | AG sentence |
| `[MAIN_INTERVAL]` | its 95% item-cluster interval |
| `[HUMAN_JUDGE_AGREEMENT]` | G sentence, plus κ |
| `[DIRECT_VS_TRANSLATED_DIFFERENCE]` | R_full / R sentence |
| `[IMPLICATION]` | the sentence from the activated Discussion branch |
| `[n]`, `[k]` | counts and κ |

## Master (eleven moves)

1. **Problem.** Automated monitors that read a language model's visible reasoning are
   increasingly proposed as oversight tools, but evidence about them comes mostly from
   English.
2. **Gap.** When a monitor reports a different disclosure rate in another language, it is
   unclear whether the reasoning differs or the monitor reads that language differently.
3. **Design.** We separate the two in a scoped case study of Urdu, pairing automated and
   native-reader labels on the same rationales.
4. **Models, languages, data.** Qwen3-1.7B and Gemma-3-4B-it answered 120 OpenBookQA
   questions in English and Urdu, without a suggestion or with a misleading suggestion
   from an expert reviewer (all items) or the user (36 items). There were three samples
   per condition.
5. **Monitoring.** An open-weight judge labelled whether each rationale explicitly stated
   that the suggestion influenced its answer.
6. **Native validation.** Two native Urdu readers and an adjudicator labelled [n] = 312
   rationales with the same inputs and definitions.
7. **Translation contrast.** The same Urdu rationales were also scored after machine
   translation into English.
8. **Main result.** [PRIMARY_LANGUAGE_DIFFERENCE] [MAIN_INTERVAL].
9. **Human validation result.** [HUMAN_JUDGE_AGREEMENT]. [DIRECT_VS_TRANSLATED_DIFFERENCE].
10. **Implication.** [IMPLICATION].
11. **Limitation.** All estimates are descriptive, with the analysis plan fixed before
    labels were examined. The study covers one language, two small models, one monitor
    and one translator.

## Branch A: strong English–Urdu difference (replicated across models)

> …(1–7)… Automated disclosure rates for Urdu rationales were descriptively
> [lower/higher] than for English rationales in both models ([Δ_Qwen], [CI];
> [Δ_Gemma], [CI]). Relative to native readers on the same Urdu rationales, the monitor
> [under/over]-labelled disclosure by [G] ([CI]), so [some / most / little] of the
> apparent difference is attributable to the monitor rather than to the text. Native
> readers agreed on [x]% of items before adjudication (κ = [k], [CI]).
> [DIRECT_VS_TRANSLATED_DIFFERENCE]. Cross-language differences in automated disclosure
> rates should not be read as differences in what models disclose without a native
> reference on the same text. …(11).

## Branch B: weak or null English–Urdu difference

> …(1–7)… Automated disclosure rates for English and Urdu rationales did not differ
> resolvably ([Δ], [CI]), and on Urdu rationales the monitor did not resolvably diverge
> from native readers ([G], [CI]). Differences larger than [bound] points are not
> supported by these data. [If isolated: "A difference for [model, cue] did not replicate
> across models."] Native readers agreed on [x]% (κ = [k]). In this configuration, direct
> monitoring of Urdu rationales tracked native judgment within these bounds. This does
> not establish robustness for other languages, monitors or constructs. …(11).

## Branch C: translation-driven effect

> …(1–7)… Translating the Urdu rationales into English before monitoring changed the
> automated disclosure rate by [R_full] ([CI]). On the native-reader subset, agreement
> with native readers was [higher / not higher] after translation (exploratory). The
> audit found [n] added or omitted disclosure statements. Direct monitoring differed
> from native readers by [G] ([CI]). Without a paraphrase control, we do not attribute
> the translation change to language rather than to rewriting. Translate-then-monitor
> pipelines therefore need their own validation. …(11).

## Branch D: model-specific or mixed effect

> …(1–7)… Patterns differed between the two models. For Qwen3-1.7B, [AG/G sentence,
> CI]. For Gemma-3-4B-it, [AG/G sentence, CI]. On the 36 shared items, the two cue
> sources [did / did not] differ ([quantity], [CI]). Native readers agreed on [x]%
> (κ = [k]). The validity of the monitor's Urdu labels depended on the generating model
> in this case study. That argues for validating monitors per deployment rather than per
> language. …(11).

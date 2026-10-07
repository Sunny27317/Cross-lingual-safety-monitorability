# Workshop-v1 reviewer response bank

**Pre-results.** The format for each entry:
- **Short:** a one-to-two-sentence reply.
- **Long:** a paragraph.
- **Support:** the supporting artifact or method.
- **Concede:** the limitation or concession.

Fill result-dependent responses only after analysis, using the claim ledger.

1. **Why only Urdu?**
   - **Short:** It is a scoped case study. The design requires native raters, and one
     language allows a careful reference.
   - **Long:** Our question is methodological: can an apparent cross-language monitoring
     difference be attributed to the monitor or to the text? Answering it requires
     same-trace native validation, which is costly per language. Urdu is
     under-resourced in evaluation (Shafique et al., 2026), uses a non-Latin script, and
     was absent from recent multilingual monitoring evaluations (Onyame et al., 2026).
   - **Support:** Introduction; Limitations.
   - **Concede:** No cross-language generalization. More languages are needed.
2. **Why only two models?**
   - **Short:** To test whether a pattern holds for more than one configuration, not to
     estimate a model-general effect.
   - **Long:** Two families (Qwen, Gemma) are reported side by side. We never pool them,
     and the only cross-model summary is directional consistency.
   - **Support:** analysis plan; Table 2.
   - **Concede:** Two configurations cannot separate family, size, quantization and
     decoding.
3. **Why small models?**
   - **Short:** Local, reproducible inference with pinned artifacts and zero API
     dependency.
   - **Long:** Every artifact is identified by revision and SHA-256 and runs locally, so
     the full pipeline can be audited and re-run.
   - **Support:** Methods §4.4.
   - **Concede:** Results may not transfer to frontier models.
4. **Why OpenBookQA?**
   - **Short:** An item-aligned English–Urdu version exists, and its four-option format
     makes a misleading single-letter suggestion well defined.
   - **Support:** Mihaylov et al. (2018); Shafique et al. (2026); native review of all
     120 items.
   - **Concede:** One task domain; translated items.
5. **Why not MMLU?**
   - **Short:** We needed a native-reviewed, item-aligned Urdu version. The OpenBookQA
     Urdu release met that need for this study.
   - **Long:** An earlier English feasibility pilot used MMLU. The Urdu study moved to a
     dataset with an existing item-aligned Urdu translation, so that every item could be
     native-reviewed.
   - **Support:** decision record (Appendix J).
   - **Concede:** Item difficulty and domain differ from MMLU-based studies.
6. **Why use generated reasoning text?**
   - **Short:** Monitors read generated text. That text is the object a monitor sees.
   - **Concede:** It is an output, not internal state.
7. **Is this chain-of-thought faithfulness?**
   - **Short:** No. We measure explicit disclosure in text and whether a monitor reads it
     correctly.
   - **Long:** Verbalization-based metrics conflate unfaithfulness with incompleteness
     (Zaman & Srivastava, 2025). We therefore make no faithfulness or internal-reasoning
     claim.
   - **Support:** construct definition (Table A1).
8. **Why use an LLM judge?**
   - **Short:** Because LLM judges are what multilingual monitoring studies and
     deployments use. We test one rather than assume it works.
   - **Support:** Fu & Liu (2025); Doğruöz et al. (2026).
9. **Why Falcon-H1?**
   - **Short:** It was chosen before any data, for three reasons:
     - its developers list Urdu among the family's core languages;
     - it ranked second on the UrduBench leaderboard;
     - it shares no family with either generator.
   - **Concede:** Leaderboard accuracy is not disclosure-judgment validity, which is what
     we measure.
10. **Why not a second judge model?**
    - **Short:** Scope. Each judge requires the same native-referenced validation. A
      second judge is the natural extension.
    - **Concede:** One-judge results do not characterize monitors in general.
11. **Why translate Urdu to English?**
    - **Short:** It changes only the language in which the monitor reads a fixed text.
      It is also a pipeline practitioners consider (Ercolano, n.d.).
    - **Support:** Methods §4.7.
12. **Isn't translation lossy?**
    - **Short:** Yes. That is why the translation contrast is descriptive and audited.
    - **Long:** There is no truncation: whole-trace failure applies instead of partial
      use. Segmentation is deterministic. An audit counts added or omitted disclosure
      language. S4 excludes audit-flagged translations.
    - **Concede:** Sentence-level segmentation can break cross-sentence references.
13. **Why only 312 human-annotated traces?**
    - **Short:** One sample per model × item × cue covers every cued cell with full
      double annotation within rater capacity.
    - **Concede:** Intervals are wide, especially on the 36 Cue-B items.
14. **Why only two raters?**
    - **Short:** Two independent raters plus an adjudicator support chance-corrected
      agreement and a resolved reference.
    - **Concede:** A small rater pool. Agreement is reported in full.
15. **Why no paraphrase control?**
    - **Short:** Not run. Accordingly, no translation result is attributed to language
      rather than rewriting.
    - **Support:** decision D-PG-3, recorded before any translation.
    - **Concede:** This limits interpretation of R.
16. **Why no English human reference?**
    - **Short:** Resources were spent on the language under study.
    - **Concede:** English automated labels are not validated, so the English side of AG
      rests on the monitor. We state this wherever AG is interpreted.
17. **Why no hypothesis testing?**
    - **Short:** A descriptive first study. Every planned comparison is reported with
      intervals.
    - **Long:** With small item pools and many contrasts, tests would invite selective
      reading. We fixed which comparisons to report in advance, and weight only patterns
      that replicate across models.
    - **Concede:** No error-rate guarantees.
18. **Why a percentile bootstrap?**
    - **Short:** It is a simple, deterministic, distribution-free interval for
      proportions and paired differences under item clustering.
    - **Concede:** It can under-cover with few clusters (36 Cue-B items). We state this.
19. **Why item-level clustering?**
    - **Short:** All samples, languages, conditions and monitor arms of an item share the
      item, so the item is the independence unit.
    - **Concede:** Model and cue-wording variation cannot be resampled. These are scope
      limits.
20. **How is missingness handled?**
    - **Short:** Reported by cause at each stage. Excluded only from metrics needing the
      field. Never imputed. Bounded by worst-case intervals.
    - **Support:** Appendix E.
21. **Why retain the 900-second timeout?**
    - **Short:** A retry would replace a non-terminating draw with a fresh one, selecting
      for shorter outputs.
    - **Long:** The rule was approved before any downstream stage.
    - **Support:** D-PG-2.
    - **Concede:** One missing trace in one cell.
22. **Why not retry malformed or no-label judge outputs?**
    - **Short:** Under greedy decoding an identical retry reproduces the same output.
      Any change would be an undocumented instrument change.
    - **Long:** The frozen contract permits one identical retry for runtime errors only.
      The 8 non-valid outputs are retained as missing, and S3 bounds their effect.
23. **Does Urdu dataset quality threaten validity?**
    - **Short:** All 120 items were native-reviewed and judged equivalent.
    - **Concede:** Translation and language remain confounded, and the licence is
      unstated (IDs only are released).
24. **What does "disclosure" mean?**
    - **Short:** An explicit statement in the rationale that the suggestion influenced,
      informed, guided, supported, or was relied on in the reasoning or answer. Mention
      alone is `partial`.
25. **Does non-disclosure imply deception?**
    - **Short:** No. `not_disclosed` means the text does not state influence. It says
      nothing about intent or about whether influence occurred.
26. **Can results generalize to multilingual LLMs?**
    - **Short:** No such claim is made. Urdu is a case study, and the procedure is the
      transferable part.
27. **Can results generalize to bigger models?**
    - **Short:** Unknown. Small models are a stated limitation.
28. **What is genuinely new here?**
    - **Short:** Within the literature we reviewed, the combination of three things on
      the same traces, for Urdu:
      - a same-trace native-reader reference with input parity;
      - a comparison against an automated monitor;
      - a translation contrast.
      This combination lets an apparent cross-lingual monitoring gap be split into monitor
      divergence and differences in the text.
    - **Concede:** None of the ingredients is individually new.

---

## Translation arm (added 2026-10-04, after the model download; before any translation)

Same format as above: **Short**, **Long**, **Support**, **Concede**.

29. **Why IndicTrans2?**
    - **Short:** An open, documented system covering Urdu→English (Gala et al., 2023).
      It runs locally with pinned revision `ac3daf0e…` and toolkit commit `3efb8418…`,
      so the arm is reproducible and auditable.
    - **Concede:** We make no claim that it is the best Urdu→English system. Its output
      quality on reasoning text is audited, not assumed.
30. **Why one translator?**
    - **Short:** The translation arm is a contrast that changes the reading language of a
      fixed text. It is not an evaluation of machine translation.
    - **Long:** Every result is stated as a property of this translator–judge pair. A
      second translator is the obvious robustness extension.
    - **Concede:** Translator-specific effects cannot be ruled out.
31. **Why not commercial translation?**
    - **Short:** Closed systems change without notice and cannot be pinned by revision
      or hash, which conflicts with the study's provenance requirements. The project also
      had no paid-API budget.
    - **Concede:** Results may differ with commercial systems.
32. **Why not human translation?**
    - **Short:** The contrast asks what an automated translate-then-monitor pipeline
      does, and human translation answers a different question. The native-reader
      reference already gives the human view of the Urdu text itself.
    - **Concede:** A human-translation arm would separate MT error from language effects.
      It is future work.
33. **Can translation destroy disclosure signals?**
    - **Short:** Yes. That is why translations are never treated as ground truth, the
      audit counts added or omitted disclosure language, S4 excludes audit-flagged
      translations, and R is descriptive.
34. **Why chunks of at most 200 source tokens?**
    - **Short:** The model translates sentence-length input with an output limit of 256
      tokens per segment. 200 source tokens leaves headroom so that outputs are not cut
      off. The value was fixed before translation and never tuned on outputs.
    - **Concede:** It is an engineering choice and was not separately optimized.
35. **Does segmentation alter discourse?**
    - **Short:** It can. References spanning sentences (e.g. "this is why I chose B")
      may lose their antecedent.
    - **Long:** We segment at natural boundaries first (line, then sentence, then clause)
      and preserve order and separators. The audit checks disclosure preservation
      specifically.
    - **Concede:** A document-level translator would avoid this. It is a limitation.
36. **Why no sentence-level human validation of translations?**
    - **Short:** Human effort went to the native-reader reference on the Urdu text,
      which is the primary comparison. Translation quality is audited on the
      translations entering that comparison, for the properties that matter to
      disclosure.
    - **Concede:** We report no general translation-quality score.
37. **Why the NLLB fallback?**
    - **Short:** It is a technical continuity rule: a whole-run switch only after a
      documented failure of the primary before scientific translation. It is never
      applied per rationale and never driven by outcomes.
    - **Support:** D-PG-5.
    - **Concede:** If used, all translation results refer to NLLB.
38. **Why not translate English traces into Urdu instead?**
    - **Short:** The question is how the monitor reads Urdu text a model actually
      produced. English→Urdu MT would create non-native Urdu text that no model wrote, and
      would test MT output instead.
    - **Long:** The monitor's instructions are in English, and English traces are already
      judged directly.

**Do not claim** that translation fidelity is high, that disclosure is preserved, or that
the translator is better than alternatives. Report only the audit counts.

# Workshop-v1 citation audit (for `paper/WORKSHOP_V1_PREPRINT.md`)

> **Update 2026-10-04 (web verification):** 7 of the 8 HIGH items are now VERIFIED: Gemma 3
> (arXiv:2503.19786), Falcon-H1 (arXiv:2507.22448, including Urdu in its core-language
> list and the UrduBench leaderboard score), IndicTrans2 (arXiv:2305.16307, TMLR),
> OpenBookQA (DOI 10.18653/v1/D18-1260), Cohen 1960 (DOI 10.1177/001316446002000104),
> DialectShift-Monitor (repository, not a publication), arXiv:2603.20172, and the Urdu
> dataset's UrduBench provenance. **Still unresolved:** the dataset licence, which is
> unstated upstream. Exact records are in `CITATION_VERIFICATION.md` §H. MEDIUM and LOW
> items are unchanged.

**2026-10-04.** The status of each entry is taken from `literature/CITATION_VERIFICATION.md`
as it stands. No bibliographic detail was added from memory, and no new verification was
performed in this pass (no web access was used).

- **VERIFIED:** title, authors, identifier and the cited content are recorded as verified
  in `CITATION_VERIFICATION.md`.
- **NEEDS VERIFICATION:** a real candidate source that is cited or needed, but not yet
  verified to the project standard.
- **PLACEHOLDER:** the slot needs a source and no specific one has been identified yet.

Before upload, every NEEDS VERIFICATION and PLACEHOLDER entry must become VERIFIED or be
removed.

## A. VERIFIED (may be cited, for exactly the content noted)

| Key | Identifier | Cited for | Caveat recorded |
|---|---|---|---|
| Turpin et al. 2023 | arXiv:2305.04388, NeurIPS 2023 | biasing features / suggested answers not acknowledged | — |
| Lanham et al. 2023 | arXiv:2307.13702 | interventions on CoT; faithfulness measurement | — |
| Chen et al. 2025 | arXiv:2505.05410 | hint paradigm; low verbalization rates | Use ≈25%/39% figures, not "<20%" |
| Xiong, Chen, Qi & Lakkaraju 2025 | arXiv:2505.13774, NeurIPS 2025 | thinking-draft faithfulness | — |
| Emmons et al. 2025 | arXiv:2507.05246 | CoT necessity vs evasion of monitors | — |
| Korbak et al. 2025 | arXiv:2507.11473 | CoT monitorability as an oversight opportunity | — |
| Yang et al. 2025 | arXiv:2511.08525 | monitorable vs monitored correctly | Closest conceptual neighbor; position explicitly |
| Onyame et al. 2026 | arXiv:2605.27901 | cross-lingual fragility of CoT monitoring; 13 languages, no Urdu; LLM judge with manual inspection | Confirm the language table and judge names in the published PDF before quoting specifics |
| Zhao et al. 2026 | arXiv:2510.09555, Findings EACL 2026 | multilingual CoT performance, consistency, faithfulness | Do not cite language-specific details unless checked |
| Qi et al. 2025 | arXiv:2505.22888 | reasoning-language control costs accuracy | **Venue (Findings EMNLP 2025) unverified**: cite as arXiv |
| Yazdani et al. 2026 | ACL Anthology 2026.loreslm-1.27 | Persian CoT faithfulness with human evaluation | "Native" evaluators not confirmed: do not say native |
| Shafique et al. 2026 (UrduBench) | arXiv:2601.21000 | Urdu translations of benchmarks incl. OpenBookQA; Urdu under-resourced | Its link to `large-traversaal/openbookqa_urdu_final` is **not** verified (see C) |
| Young 2026a | arXiv:2603.26410 | open-weight hint-paradigm replication | — |
| Young 2026b | arXiv:2603.22582 | companion study | — |
| Zaman & Srivastava 2025 | arXiv:2512.23032 | hint verbalization conflates incompleteness and unfaithfulness | Year per arXiv identifier; confirm |
| LLM-judge multilingual challenges | arXiv:2607.02235 | judges unreliable in low-resource languages | Author list not recorded: obtain before citing |
| Multilingual LLM-as-a-judge study | arXiv:2605.28710 | cross-language judge inconsistency | Author list not recorded |
| Language bias in LLM evaluators | arXiv:2607.14480 | lower-resource ⇒ more evaluator bias | Author list not recorded |
| "How Reliable is Multilingual LLM-as-a-Judge?" | arXiv:2505.12201, Findings EMNLP 2025 | judge reliability across languages | Author list not recorded |
| Qwen3 Technical Report | arXiv:2505.09388 | Qwen3 model family | Do **not** cite the disputed 1.7B benchmark numbers |

## B. NEEDS VERIFICATION (cited or required; verify before upload)

| Needed for | Candidate | What to verify |
|---|---|---|
| Gemma-3-4B-it model | Gemma 3 technical report | identifier, authors/team, year |
| Judge model | Falcon-H1 technical report / model card | identifier, authors/team, year; the Urdu-capability claim used to select the judge |
| Translator | IndicTrans2 paper | identifier, venue, authors, year; Urdu→English support |
| Backup translator | NLLB-200 paper | identifier, venue |
| Dataset | OpenBookQA paper | authors, venue, year |
| Agreement statistic | Cohen (1960), κ | bibliographic record |
| κ verbal bands | Landis & Koch (1977) | **Not needed:** verbal bands are no longer used (2026-10-04). Drop unless cited for another reason |
| Inference runtime | llama.cpp | software citation format, commit `5266f24da` |
| Translate-then-monitor precedent | DialectShift-Monitor (author repository) | stable reference or archived version; mutable repo caution |
| Judge sensitivity in CoT evaluation | arXiv:2603.20172 ("Measuring Faithfulness Depends on How You Measure…") | listed as surfaced, not verified; high priority read |
| Monitorability measurement frameworks | arXiv:2510.27378; arXiv:2510.23966 | identity and relevance |
| Cross-lingual safety degradation | arXiv:2605.17173; arXiv:2608.18131 | identity and relevance |
| Systematic review of low-resource safety alignment | arXiv:2608.14626 | identity; mine bibliography |
| Prompt-injection alerting affects faithfulness metrics | Walden & Wanner, arXiv:2601.07663 | carried status, not re-verified |

## C. PLACEHOLDER (source not yet identified)

| Slot | Need |
|---|---|
| Dataset provenance | Dataset card or paper for `large-traversaal/openbookqa_urdu_final`, and whether it is the UrduBench OpenBookQA set |
| Dataset licence | Primary licence statement (recorded as ambiguous) |
| Urdu speaker population / resource status (optional) | Only if a number is stated; otherwise omit |
| Cluster bootstrap methodology (optional) | Standard reference for item-cluster resampling |

## D. Missing high-value references to locate and verify later

None of these is cited yet. Titles below are leads to check, not citations.

1. **Sycophancy toward user-stated beliefs**: motivates Cue B. Look for Anthropic and
   other work on sycophancy in language models (e.g. "Towards Understanding Sycophancy in
   Language Models"; model-written evaluations of sycophancy).
2. **Multilingual jailbreaks / low-resource safety**: motivates "safety differs across
   languages" (e.g. work showing translation into low-resource languages bypasses
   safety training; "multilingual jailbreak challenges").
3. **LLM-judge validation against humans**: agreement of LLM judges with human labels in
   English (e.g. MT-Bench/"LLM-as-a-judge" studies; large-scale judge-vs-human agreement
   benchmarks).
4. **Cross-lingual consistency of model knowledge/behavior**: supports within-item
   cross-language comparison.
5. **Translationese / MT effects on downstream classifiers**: supports the translation
   caveat and the paraphrase-control discussion.
6. **Annotation-quality practice**: double annotation and adjudication; reporting κ with
   prevalence (the kappa paradox), to justify reporting raw agreement alongside κ.

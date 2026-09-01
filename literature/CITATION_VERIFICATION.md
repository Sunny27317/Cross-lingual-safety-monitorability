# Citation Verification — Run-2 Blueprint

**Purpose:** independent verification (Phase B / Phase 3) of every central citation and
numeric claim imported from `literature/RUN2_BLUEPRINT.pdf`.
**Method:** web search + direct fetch of arXiv abstract/HTML and ACL Anthology pages,
2026-09-01, by the Claude Code session doing the Run-2 integration.
**Verifier note:** the assistant's own training cutoff predates several of these 2026
papers; every status below rests on the live sources listed, not on prior knowledge.

Status legend:
- **VERIFIED** — identity (title/authors/venue/ID) confirmed against a primary or
  authoritative secondary source.
- **PARTIALLY VERIFIED** — the paper is confirmed real, but a specific attributed claim,
  number, venue detail, or author list was not fully confirmed from the sources checked.
- **TODO — UNVERIFIED** — could not be confirmed from available sources.
- **CONTRADICTED** — a source contradicts the blueprint.

---

## A. Core competitor papers

### 1. Onyame et al. — arXiv:2605.27901 — **VERIFIED** (identity) / see sub-items
- **Title:** "The Fragility of Chain-of-Thought Monitoring Across Typologically Diverse
  Languages." ✅
- **Authors:** Eric Onyame, Runtao Zhou, Kowshik Thopalli, Bhavya Kailkhura, Chirag
  Agarwal. ✅ (matches blueprint's "Onyame, Zhou, Thopalli, Kailkhura & Agarwal")
- **Affiliation:** UVA + Lawrence Livermore National Laboratory. ✅
- **Code:** `github.com/AikyamLab/multilingual-monitoring`. ✅
- **Project page:** `multilingual-cot-monitoring.github.io`. ✅
- **Headline numbers** ("95.9% across 8B–120B"; "100% in low-resource"; "first 15% of
  generation"): **VERIFIED** — present verbatim in the abstract as quoted by the
  blueprint. ✅
- **13 languages / Urdu absence:** **VERIFIED via arXiv HTML** — languages surfaced from
  the HTML body: English, Chinese, Spanish, French, German, Japanese (high);
  Vietnamese, Arabic, Korean, Russian (mid); Swahili, Telugu, Bengali (low). **Urdu is
  NOT among them.** This *confirms* the blueprint's suspected-but-unconfirmed claim.
  → Still cross-check Table 6 / Appendix C in the published PDF before citing in a paper.
- **Judge model:** **PARTIALLY VERIFIED / update to blueprint** — the arXiv HTML states
  *"we use GPT-5.1 as the verification judge to monitor CoT reasoning"* and *"a
  rubric-based LLM-as-a-judge pipeline with GPT-5.4"* for taxonomy classification. The
  blueprint said the "GPT-5.1 judge" attribution was *unverified*; the current HTML
  asserts it. Model-name strings ("GPT-5.1", "GPT-5.4") are unusual — confirm against
  Appendix D.2 of the published PDF.
- **No native-speaker validation:** **VERIFIED** — HTML: *"We validate the judge through
  manual inspection of samples across all languages."* No bilingual/native annotator.
- **No translate-then-monitor:** **VERIFIED** — HTML fetch found no discussion of
  translating CoTs to English before monitoring.
- **Base-accuracy control exists (Baseline Error Rate, App. B.1/B.6):** **TODO —
  UNVERIFIED** from the fetch; plausible, blueprint asserts it. Do not claim competitors
  ignored difficulty.
- Sources: `arxiv.org/abs/2605.27901`, `arxiv.org/html/2605.27901`,
  `github.com/AikyamLab/multilingual-monitoring`.

### 2. Zhao et al. — arXiv:2510.09555 — **VERIFIED** (with correction)
- **Title:** "A Comprehensive Evaluation of Multilingual Chain-of-Thought Reasoning:
  Performance, Consistency, and Faithfulness Across Languages." ✅
- **Authors:** Raoyuan Zhao, Yihong Liu, Hinrich Schütze, Michael A. Hedderich. ✅
  (blueprint's bare "Zhao et al." — first author is **Raoyuan Zhao**, not verified
  further by blueprint)
- **Venue:** Findings of the ACL: EACL 2026, pp. 5223–5247, Rabat, Morocco. ✅
- **Claim** ("language compliance + truncation/error-injection faithfulness across
  languages incl. Bengali and Yoruba"): **PARTIALLY VERIFIED** — the abstract confirms
  performance/consistency/faithfulness across languages; the specific Bengali/Yoruba +
  error-injection details were not individually confirmed from the snippet. Check the
  paper's method section.
- Sources: `aclanthology.org/2026.findings-eacl.276/`, `arxiv.org/html/2510.09555`.

### 3. Qi et al. — arXiv:2505.22888 — **VERIFIED** (with title correction)
- **Blueprint label:** "Qi et al. … XReasoning … Language-compliance + accuracy
  tradeoff … Findings EMNLP 2025."
- **Actual title:** "When Models Reason in Your Language: Controlling Thinking Language
  Comes at the Cost of Accuracy." ✅
- **Authors:** Jirui Qi, Shan Chen, Zidi Xiong, Raquel Fernández, Danielle S. Bitterman,
  Arianna Bisazza. ✅
- **XReasoning benchmark; in-language reasoning aids oversight but costs accuracy:**
  **VERIFIED** — this is the paper's central finding, exactly as the blueprint uses it.
- **Venue "Findings of EMNLP 2025":** **TODO — UNVERIFIED** from sources checked (arXiv +
  HF paper page confirmed; ACL Anthology record not fetched). Low risk.
- Sources: `arxiv.org/abs/2505.22888`, `huggingface.co/papers/2505.22888`.

### 4. Xiong, Chen, Qi & Lakkaraju — arXiv:2505.13774 — **VERIFIED**
- **Title:** "Measuring the Faithfulness of Thinking Drafts in Large Reasoning Models." ✅
- **Authors:** Zidi Xiong, Shan Chen, Zhenting Qi, Himabindu Lakkaraju (Harvard). ✅
- **Venue:** NeurIPS 2025 (poster; `neurips.cc/virtual/2025/poster/120231`; OpenReview
  `1UL4dxvfcJ`). ✅
- **Method** (counterfactual intervention: Intra-Draft + Draft-to-Answer faithfulness):
  **VERIFIED.** ✅
- Sources: `arxiv.org/abs/2505.13774`, `neurips.cc/virtual/2025/poster/120231`,
  `openreview.net/forum?id=1UL4dxvfcJ`.

### 5. Chen et al. — arXiv:2505.05410 — **VERIFIED** (with title)
- **Actual title:** "Reasoning Models Don't Always Say What They Think." ✅
- **Authors:** Yanda Chen, Joe Benton, Ansh Radhakrishnan, Jonathan Uesato, Carson
  Denison, John Schulman, … Ethan Perez (Anthropic). ✅
- **Method** (paired hinted/un-hinted prompts; does the CoT acknowledge the hint when
  the answer changes): **VERIFIED.** Models incl. Claude 3.7 Sonnet and DeepSeek R1. ✅
- **"Reveal rates often below 20%":** **PARTIALLY VERIFIED** — the exact "<20%" phrase
  was not confirmed verbatim; the arXiv HTML gives **overall CoT faithfulness ≈ 25%
  (Claude 3.7 Sonnet) / ≈ 39% (DeepSeek-R1)**, with GPQA "consistently less faithful
  than MMLU" and lower still on misaligned hints. Use these figures, not "<20%".
- **Milestone-1-relevant details (fetched from arXiv HTML `2505.05410v1`, 2026-09-01):**
  - datasets = **MMLU + GPQA**, multiple-choice prompt pairs — **SOURCE-REPORTED**
  - **6 hint types** = 4 neutral (sycophancy, consistency, visual pattern, metadata) +
    2 misaligned (grader hacking, unethically-obtained information) — **SOURCE-REPORTED**
  - faithfulness score = `E[ 1[c_h verbalizes h] | a_u ≠ h, a_h = h ]` — **SOURCE-REPORTED**
  - **"For all evaluations, we sample with temperature 0"** — **SOURCE-REPORTED**
    (deliberately *not* adopted for our DeepSeek distill; see `DECISION_LOG.md` D-012)
  - top_p, k/samples, exact MMLU/GPQA question counts — **NOT REPORTED BY SOURCE**
  - public code repository — **none found** (arXiv HTML + web); cannot SOURCE-CODE-VERIFY
- Sources: `arxiv.org/html/2505.05410v1`, `arxiv.org/abs/2505.05410`,
  `anthropic.com/research/reasoning-models-dont-say-think`.

### 6. Turpin et al. — arXiv:2305.04388 — **VERIFIED**
- **Title:** "Language Models Don't Always Say What They Think: Unfaithful Explanations
  in Chain-of-Thought Prompting." ✅
- **Authors:** Miles Turpin, Julian Michael, Ethan Perez, Samuel R. Bowman. ✅
- **Venue:** NeurIPS 2023. ✅
- **Method** (biasing features, e.g. answer-always-(A); up to 36% accuracy drop on 13
  BBH tasks; GPT-3.5 + Claude 1.0): **VERIFIED.** ✅
- Sources: `arxiv.org/abs/2305.04388`, `dblp.org/rec/journals/corr/abs-2305-04388`.

### 7. Lanham et al. — arXiv:2307.13702 — **VERIFIED**
- **Title:** "Measuring Faithfulness in Chain-of-Thought Reasoning." ✅
- **Authors:** Tamera Lanham, Anna Chen, Ansh Radhakrishnan, … (Anthropic; 28+ authors). ✅
- **Method** (intervene on CoT: add mistakes / paraphrase / truncate; larger models →
  less faithful on most tasks): **VERIFIED.** ✅
- Sources: `arxiv.org/abs/2307.13702`, `dblp.org/rec/journals/corr/abs-2307-13702`.

### 8. Emmons et al. — arXiv:2507.05246 — **VERIFIED** (with title)
- **Actual title:** "When Chain of Thought is Necessary, Language Models Struggle to
  Evade Monitors." ✅
- **Authors:** Scott Emmons, Erik Jenner, David K. Elson, Rif A. Saurous, Senthooran
  Rajamanoharan, Heng Chen, Irhum Shafkat, Rohin Shah (Google DeepMind). ✅
- **Framework** (CoT-as-rationalization vs. CoT-as-computation; monitorability ≠
  faithfulness): **VERIFIED.** ✅
- Sources: `arxiv.org/abs/2507.05246`, `ui.adsabs.harvard.edu/abs/2025arXiv250705246E`.

### 9. Korbak et al. — arXiv:2507.11473 — **VERIFIED**
- **Title:** "Chain of Thought Monitorability: A New and Fragile Opportunity for AI
  Safety." ✅
- **Authors:** Tomek Korbak, Mikita Balesni, Elizabeth Barnes, Yoshua Bengio, + ~40
  co-authors (multi-org position paper). ✅
- Submitted 15 Jul 2025. Defines CoT monitorability. **VERIFIED.** ✅
- Sources: `arxiv.org/abs/2507.11473`, `ar5iv.labs.arxiv.org/html/2507.11473`.

### 10. Yang et al. — arXiv:2511.08525 — **VERIFIED**
- **Title:** "Investigating CoT Monitorability in Large Reasoning Models." ✅
- **First author:** Shu Yang, et al. ✅
- **Content** (verbalization + monitor reliability; *"there exists a gap between being
  monitorable and being monitored correctly"*; proposes "MoME" monitoring paradigm):
  **VERIFIED.** ✅
- ⚠️ **Novelty-relevant:** the phrase *"gap between being monitorable and being monitored
  correctly"* is conceptually adjacent to this project's "monitor-validity gap." Yang et
  al. is English-only per the blueprint, so it is not a direct competitor, but it should
  be positioned explicitly in Related Work. Raised in `COMPETITOR_MATRIX.md`.
- Sources: `arxiv.org/abs/2511.08525`, `alphaxiv.org/overview/2511.08525`.

### 11. Persian CoT Faithfulness — ACL Anthology 2026.loreslm-1.27 — **VERIFIED** (with detail)
- **Title:** "A Comprehensive Evaluation of Chain-of-Thought Faithfulness in Persian
  Classification Tasks." ✅
- **Authors:** Shakib Yazdani, Cristina España-Bonet, Eleftherios Avramidis, Yasser
  Hamidullah, Josef van Genabith (DFKI et al.). ✅
- **Venue:** 2nd Workshop on Language Models for Low-Resource Languages (LoResLM 2026),
  co-located with EACL 2026, Rabat, 28–29 Mar 2026. ✅
- **Scope:** 15 classification datasets, 6 LMs (small / large / reasoning), English +
  Persian prompting, LLM-as-judge + human eval. ✅
- **"Native human evaluation" specifically:** **PARTIALLY VERIFIED** — "human eval" is
  confirmed; that the human evaluators were *native Persian speakers* was not confirmed
  from the snippet. Confirm from the PDF before relying on the "native-validation
  precedent" framing.
- **"Did not address monitorability / Urdu / translation recovery":** consistent with
  the abstract (classification-task faithfulness, Persian) — **PARTIALLY VERIFIED**
  (absence is hard to prove from an abstract; a full read is cheap and should be done).
- Sources: `aclanthology.org/2026.loreslm-1.27.pdf`,
  `dfki.de/web/forschung/projekte-publikationen/publikation/16737`.

### 12. UrduBench — arXiv:2601.21000 — **VERIFIED**
- **Title:** "UrduBench: An Urdu Reasoning Benchmark using Contextually Ensembled
  Translations with Human-in-the-Loop." ✅
- **Authors:** Muhammad Ali Shafique, Areej Mehboob, Layba Fiaz, Muhammad Usman Qadeer,
  Hamza Farooq. Published 28 Jan 2026. ✅
- **Content:** contextually-ensembled MT + human-in-the-loop; translates MGSM, MATH-500,
  CommonSenseQA, OpenBookQA to Urdu. Leaderboard repo:
  `github.com/traversaal-ai/urdubench_leaderboard`. **VERIFIED.** ✅
  → This directly supports the blueprint's Phase 6 claim that MGSM / CommonSenseQA /
  OpenBookQA already have Urdu translations.
- **"DeepSeek-R1-Distill-Qwen-14B sustains difficulty well" (per UrduBench):** **TODO —
  UNVERIFIED** — specific model finding not confirmed from the snippet.
- Sources: `arxiv.org/abs/2601.21000`, `dblp.org/rec/journals/corr/abs-2601-21000`.

---

## B. Faculty / institutional claims

### 13. Depeng Xu — bias-mitigation paper — **VERIFIED** (with author-list note)
- **Title:** "Fine-tuning LLMs with Cross-Attention-based Weight Decay for Bias
  Mitigation" (method: CrAWD). ✅
- **Venue:** Findings of the ACL: EMNLP 2025, pp. 15785–15798, Suzhou, China.
  ACL Anthology `2025.findings-emnlp.854`. ✅ (pages match the blueprint exactly)
- **Authors:** **PARTIALLY VERIFIED** — the blueprint gives two slightly different lists
  ("Haque, Fu, Xu, Yuan & Niu" and "Farsheed Haque, Zhe Fu, Shuhan Yuan, Xi Niu"). ACL
  Anthology page not fetched for the canonical ordering. Confirm before citing.
- **UNC Charlotte Center for TAIMing AI membership + "2025 TAIMing AI Seed Grant
  Award":** **VERIFIED** — `taiming-ai.charlotte.edu` news post
  ("Congratulations to Dr. Depeng Xu on a Major Research Achievement", 2025-08-30).
- Sources: `aclanthology.org/2025.findings-emnlp.854/`,
  `taiming-ai.charlotte.edu/2025/08/30/...`, `dblp.org/pid/212/1161`.

### Other UNC Charlotte names (Bunescu, Fan, Zadrozny, Shaikh) — **TODO — UNVERIFIED**
Not independently checked in this pass. The blueprint's characterizations (titles,
Emeritus transition, industry move) must be confirmed before any outreach or any
repository statement treats them as fact. No one has agreed to supervise.

### Himabindu Lakkaraju (Harvard) — **VERIFIED** (research alignment only)
- Confirmed as senior author on Xiong et al. arXiv:2505.13774 (NeurIPS 2025), Harvard.
- **No admissions inference of any kind.** The blueprint itself forbids this.

---

## C. Secondary numeric / factual claims from the blueprint

| Claim | Status | Note |
|---|---|---|
| "~60% raw-MT label agreement for Urdu vs. ~90% English" | **TODO — UNVERIFIED** | No source cited in the blueprint; find the primary source or treat as an assumption to be measured in the Urdu pilot. |
| Onyame tiers languages via zero-shot GPQA on "Kimi K2.6" (>60% high / 30–60% mid / <30% low) | **PARTIALLY VERIFIED** | Tiering method quoted from the paper by the blueprint; "Kimi K2.6" as a model name is **UNVERIFIED**. |
| Qwen3-8B "~119-language coverage" vs. "~30 for the DeepSeek distills" | **TODO — UNVERIFIED** | Check the Qwen3 model card / technical report; check DeepSeek-R1-Distill base coverage. Do before Milestone 2. |
| MGSM = "250 items, 10+ languages incl. Bengali" | **PARTIALLY VERIFIED** | MGSM is 250 problems; language list to confirm from the MGSM source (Shi et al.). |
| Chen et al. "reveal rates often below 20%" | **PARTIALLY VERIFIED** | See §A.5. |
| ACL/EMNLP/NeurIPS/EACL deadline months (Feb/May/summer/fall) | **TODO — UNVERIFIED** | Confirm each cycle at project start. |

---

## D. Newer evidence found during verification (NOT in the blueprint)

These surfaced in searches on 2026-09-01 and were **not** cited by the Run-2 report.
None is confirmed to pre-empt the surviving contribution, but each must be read and
positioned before the paper is written. **NEW INDEPENDENT ANALYSIS — NOT FROM RUN-2.**

| Paper (as surfaced) | Why it matters | Action |
|---|---|---|
| "Measuring Chain-of-Thought Monitorability Through Faithfulness and Verbosity" — arXiv:2510.27378 | Another CoT-monitorability measurement framework | read; position in Related Work |
| "A Pragmatic Way to Measure Chain-of-Thought Monitorability" — arXiv:2510.23966 | Ditto | read; position |
| "Measuring Faithfulness Depends on How You Measure: Classifier Sensitivity in LLM CoT Evaluation" — arXiv:2603.20172 | **Directly about judge/classifier sensitivity in CoT faithfulness eval** — i.e. the (A)-vs-(B) confound at the heart of this project | **HIGH priority read**; may strengthen or partially scoop the "monitor failure" framing (likely English) |
| "Why Do Safety Guardrails Degrade Across Languages?" — arXiv:2605.17173 | Cross-lingual safety degradation (guardrails, not CoT monitors) | read; likely adjacent, not competing |
| "Safety Alignment Illusion: The Cross-Lingual Safety Gap in LLMs" — arXiv:2608.18131 | Cross-lingual safety alignment gap | read; adjacent |
| "LLM Safety Alignment in Low-Resource Languages: A Systematic Literature Review" — arXiv:2608.14626 | SLR — useful for Related Work coverage | mine its bibliography |
| "Riazi-8B: An Urdu LLM for Mathematical Reasoning" — arXiv:2606.25568 | New Urdu reasoning model | note as a possible additional generator |
| "UrduMMLU: A Massive Multitask Benchmark for Urdu" — arXiv:2606.07167 | New Urdu benchmark | note as a possible additional dataset |
| "Beyond the Commitment Boundary: Probing Epiphenomenal CoT in Large Reasoning Models" — arXiv:2606.13603 | Related to "commits in first 15%" claim | read |

### D.2 — Added 2026-09-01 during the Milestone-1 literature check

| Paper | Verified | Why it matters | Threat |
|---|---|---|---|
| Young, "Why Models Know But Don't Say: CoT Faithfulness Divergence Between Thinking Tokens and Answers in Open-Weight Reasoning Models" — **arXiv:2603.26410** (UNLV + DeepNeuro AI; posted 2026-03-27) | **VERIFIED** (arXiv HTML + ResearchGate) | 12 open-weight reasoning models on **MMLU + GPQA + misleading hints**; 55.4% of hint-following cases have hint keywords in thinking tokens omitted from the answer (reverse ~0.5%). *Effectively a near-replication of our Milestone 1 on open-weight models.* | **LOW** — corroborates the M1 paradigm and gives a comparison point; not cross-lingual, not native-validated. Cite as the M1 reference. |
| Walden & Wanner, "Reasoning Models Will Sometimes Lie About Their Reasoning" (a.k.a. "…Will Blatantly Lie…") — **arXiv:2601.07663** (JHU; v4 2026-04-21) | **VERIFIED** (arXiv HTML + ResearchGate) | Alerting models to "unusual inputs" (prompt-injection defenses) inflates prior faithfulness metrics; new granular metrics still show problematic behavior. | **LOW** — affects M1 hint-wording design (whether to alert the model); not a novelty threat. |
| "Challenges and Recommendations for LLMs-as-a-Judge in Multilingual Settings and Low-Resource Languages" — **arXiv:2607.02235** | **VERIFIED** (arXiv) | Only 33/650 LLM-judge papers cover multilingual/low-resource; performance often **overestimated** for low-resource; criticizes reliance on a single judge. | **MEDIUM (framing)** — establishes "LLM judges unreliable in low-resource languages" as a general result. |
| "Towards Reliable Multilingual LLMs-as-a-Judge: An Empirical Study" — **arXiv:2605.28710** | **VERIFIED** (arXiv) | Cross-language judgment consistency poor (Fleiss κ ≈ 0.3), worst in low-resource. | **MEDIUM (framing)** |
| "Lower-Resource, Higher Scores: Language Bias in LLM Evaluators" — **arXiv:2607.14480** | **VERIFIED** (arXiv) | Weaker language competence ⇒ more evaluator bias (length bias, self-preference, ignoring references). | **MEDIUM (framing)** |
| "How Reliable is Multilingual LLM-as-a-Judge?" — **arXiv:2505.12201** (Findings EMNLP 2025, `2025.findings-emnlp.587`) | **VERIFIED** (arXiv + ACL Anthology) | Same theme, peer-reviewed. | **MEDIUM (framing)** |

**Consequence (see `DECISION_LOG.md` D-014):** the general claim "automated
monitors/judges fail in low-resource languages" is now well-established for both CoT
monitors (Onyame) and LLM-judges broadly. The surviving contribution must rest on
**native-human-validated CoT monitorability** + **translate-then-monitor recovery** +
**A-vs-B separation** — not on the general judge-reliability point. Not a STOP; a
sharpening. Flagged for the user in `MILESTONE_1_READINESS.md` §19.5.

---

## E. Overall verdict on the blueprint's citations

- **12 / 12** competitor/foundational papers in the Phase 0 table are **real and
  correctly identified** (titles for #3, #5, #8 differ from the blueprint's shorthand
  labels — corrected above; none is fabricated).
- The **single most novelty-critical set of claims** — Onyame et al. used no native
  validation, did not test translate-then-monitor, and does not include Urdu — is
  **VERIFIED against the primary source**.
- No citation is **CONTRADICTED**.
- Residual risks are (i) the blueprint's secondary numbers (§C), (ii) newer 2026 work
  the blueprint predates (§D), (iii) author-list / venue fine detail on a few entries.

---

## F. Pending verifications before Milestone 1 implementation

| Item | Status | Needed by |
|---|---|---|
| DeepSeek-R1-Distill-Qwen-7B model revision `916b56a44061fd5cd7d6a8fb632557ed4f724f60` | **SOURCE-CODE-VERIFIED** via HF API 2026-09-01 — re-confirm at implementation | scaffold |
| DeepSeek-R1-Distill-Qwen-7B decoding recommendations (temp 0.5–0.7/0.6, top_p 0.95, max 32768, no system prompt, force `<think>\n`, greedy harmful, base Qwen2.5-Math-7B, MIT) | **MODEL-DOCUMENTATION-RECOMMENDED** — HF model card fetched 2026-09-01 | scaffold |
| `cais/mmlu` licence (widely reported MIT) + exact revision hash | **TODO — UNVERIFIED** (dataset card not fetched) | before download / redistribution |
| GPQA-Diamond access terms (gating, canary string, "do not post" norm) | **TODO — UNVERIFIED** | before the confirmatory secondary |
| Disclosure-classifier candidate `Qwen3-32B`: exact id, revision, licence, context window, VRAM | **TODO — UNVERIFIED** | §7a checklist, before locking |
| Smaller open-weight judge alternative (7–14B) feasibility | **TODO — UNVERIFIED** | §7a checklist |
| Landis & Koch (1977) κ-band convention (basis for the "moderate/substantial" gate) | widely cited; the convention itself is **debated** — treat as STANDARD-METHODOLOGY, not fact | pre-registration wording |
| Confirmatory power/sample-size calculation | **NOT DONE** — required before freezing confirmatory n | confirmatory design |

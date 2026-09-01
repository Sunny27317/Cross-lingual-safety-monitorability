# Competitor Matrix

**Purpose:** Phase C novelty audit. Per-paper analysis of the closest prior work, the
overlap with this project, what this project adds, and a novelty threat level.
**Sources:** `literature/RUN2_BLUEPRINT.pdf` (Phase 0 + Key Findings 1–2) and the
independent verification in `literature/CITATION_VERIFICATION.md`.
**Rule:** novelty is **not** claimed because Urdu is included. The claimed contribution
is measurement validity (native-validated separation of monitor failure from model
unfaithfulness) + translate-then-monitor recovery.

Threat levels:
- **HIGH** — occupies the core contribution or a large part of it; a small extension of
  this paper could pre-empt us.
- **MEDIUM** — strong methodological or conceptual overlap; must be positioned carefully;
  does not currently occupy the core contribution.
- **LOW** — foundational or adjacent; we build on it, it does not threaten novelty.

---

## 1. Onyame et al. — "The Fragility of Chain-of-Thought Monitoring Across Typologically Diverse Languages"

| Field | Content |
|---|---|
| **Citation** | Onyame, Zhou, Thopalli, Kailkhura, Agarwal. arXiv:2605.27901 (v1 2026-05-27). UVA + LLNL. Code: `AikyamLab/multilingual-monitoring`. **VERIFIED.** |
| **Research question** | Is CoT monitoring reliable beyond English and across model families? |
| **Languages** | 13: English, Chinese, Spanish, French, German, Japanese (high); Vietnamese, Arabic, Korean, Russian (mid); Swahili, Telugu, Bengali (low). **Urdu absent (VERIFIED).** |
| **Models** | 16 across 7 families: Qwen3, DeepSeek-R1 distills, GPT-OSS, Llama, Gemma 3, plus closed GPT / Claude. 8B–120B. |
| **Datasets** | Multilingual GPQA. |
| **Faithfulness intervention** | Adversarial hints: simple (`<answer>C</answer>`) + complex (modular-arithmetic cue requiring explicit computation). |
| **Monitoring setup** | Automated LLM judge checks whether the CoT verbalizes the hint. Judge stated in arXiv HTML as **GPT-5.1** (taxonomy: GPT-5.4) — confirm vs. App. D.2. Plus logit-lens / internal answer-token probability analysis. **No native-speaker validation** — authors' manual inspection only (VERIFIED). |
| **Metrics** | Deception / CoT-unfaithfulness rate; latent commitment point (fraction of generation). |
| **Findings** | "95.9% average CoT-unfaithfulness across 8B–120B"; "100% in low-resource languages"; models "commit to the misaligned cue in latent activations within the first 15% of generation." Deception persists under a "Baseline Error Rate" accuracy control (App. B.1/B.6). |
| **Limitations (ours + theirs)** | Automated-judge-only ground truth; judge is English-centric and its low-resource competence is unvalidated; no test of whether the *judge* (not the model) is what fails in low-resource languages; no mitigation beyond diagnosis; no translate-then-monitor; Urdu not covered; stress tests limited to option-letter bias, closed-source generalization, stochastic stability. |
| **Overlap with our project** | Very high on framing (cross-lingual CoT monitor reliability), method (adversarial hints on multilingual MCQ/science QA), and models (DeepSeek-Qwen distills, Qwen3). |
| **What our project adds** | (1) **Native Urdu human ground truth** on the same traces → separates monitor failure (B) from model unfaithfulness (A), which their design *cannot* do. (2) **Translate-then-monitor** recovery test. (3) Urdu specifically (as a *consequence* of native-validation feasibility, not as the contribution). (4) Explicit judge-side-degradation quantification. |
| **Threat level** | **HIGH.** This is the paper that turns the broad framing RED. Our defensibility depends entirely on staying on the measurement-validity + mitigation contribution and not re-running "monitors fail across languages." A follow-up from this group adding one native language + a translation baseline would substantially pre-empt us (→ kill/pivot criterion A). |

---

## 2. Zhao et al. — "A Comprehensive Evaluation of Multilingual Chain-of-Thought Reasoning"

| Field | Content |
|---|---|
| **Citation** | Raoyuan Zhao, Yihong Liu, Hinrich Schütze, Michael A. Hedderich. Findings of EACL 2026, pp. 5223–5247. arXiv:2510.09555. **VERIFIED.** |
| **Research question** | How does multilingual CoT reasoning compare across languages on performance, consistency, and faithfulness? |
| **Languages** | Multiple, incl. Bengali and Yoruba (low-resource). |
| **Models** | R1-Distill-Qwen-32B, R1-Distill-Llama-70B, and others. |
| **Datasets** | Multilingual reasoning/QA benchmarks (to confirm from method section). |
| **Faithfulness intervention** | Truncation + error injection (Lanham-style), cross-lingual; plus language-compliance and consistency measurement. |
| **Monitoring setup** | Automated metrics; no human/native validation of faithfulness labels. |
| **Metrics** | Performance (accuracy), reasoning/answer consistency across languages, faithfulness (intervention sensitivity), language compliance. |
| **Findings** | Multilingual CoT degrades in performance/consistency/faithfulness in lower-resource languages; language compliance is a measured (not assumed) variable. |
| **Limitations** | No native-speaker validation; no monitor-validity measurement (does not ask whether the *evaluation* is what fails); no mitigation; no answer-influence (hint) paradigm — uses perturbation not adversarial cues. |
| **Overlap with our project** | High on "faithfulness degrades cross-lingually"; provides the truncation/error-injection robustness protocol we plan to reuse (Phase 7). Language-compliance metric is shared. |
| **What our project adds** | Native ground truth; hint/influence paradigm (safety-relevant hidden influence, not just perturbation sensitivity); monitor-validity gap; translate-then-monitor. |
| **Threat level** | **MEDIUM–HIGH.** Co-establishes (with Onyame) that the broad claim is not novel. Does not occupy the native-validation or mitigation gap. |

---

## 3. Qi et al. — "When Models Reason in Your Language: Controlling Thinking Language Comes at the Cost of Accuracy" (XReasoning)

| Field | Content |
|---|---|
| **Citation** | Jirui Qi, Shan Chen, Zidi Xiong, Raquel Fernández, Danielle S. Bitterman, Arianna Bisazza. arXiv:2505.22888. Findings of EMNLP 2025 (venue TODO — UNVERIFIED). **VERIFIED (identity).** |
| **Research question** | Can we make LRMs reason in the user's language, and what does it cost? |
| **Languages** | Multiple (XReasoning benchmark). |
| **Models** | 2 LRM families. |
| **Faithfulness / oversight angle** | Language compliance vs. accuracy trade-off; forcing in-language reasoning improves human oversight/readability but reduces accuracy; 100-example post-training partly fixes the mismatch. |
| **Monitoring setup** | Framed as oversight; no native-validated monitor comparison. |
| **Findings** | Even 32B LRMs revert to English or produce fragmented target-language reasoning; the readability/accuracy trade-off is real. |
| **Limitations** | Not about monitor *validity*; no hint paradigm; no native faithfulness ground truth. |
| **Overlap with our project** | The **language-compliance mediation hypothesis (H5)** and the "prompt the model to reason in-language" secondary mitigation come directly from this line. |
| **What our project adds** | Whether low compliance actually causes monitor-validity loss (mediation test); native ground truth. |
| **Threat level** | **LOW–MEDIUM.** Feeds H5 and a secondary mitigation; does not compete for the core contribution. |

---

## 4. Xiong, Chen, Qi & Lakkaraju — "Measuring the Faithfulness of Thinking Drafts in Large Reasoning Models"

| Field | Content |
|---|---|
| **Citation** | Zidi Xiong, Shan Chen, Zhenting Qi, Himabindu Lakkaraju. NeurIPS 2025 (Harvard). arXiv:2505.13774. **VERIFIED.** |
| **Research question** | Are the intermediate "thinking drafts" of LRMs causally faithful? |
| **Languages** | English only. |
| **Models** | 6 LRMs. |
| **Faithfulness intervention** | Counterfactual draft perturbation: Intra-Draft (do steps causally influence later steps?) + Draft-to-Answer (does the final answer depend on the draft?). |
| **Monitoring setup** | Automated counterfactual framework; monitoring is motivation, not the object of study. |
| **Metrics** | Causal faithfulness scores per dimension. |
| **Findings** | Establishes a causal, fine-grained faithfulness measurement method. |
| **Limitations** | English-only; heavy engineering; not cross-lingual; not about monitor reliability. |
| **Overlap with our project** | Method candidate for a robustness layer (Phase 7); Harvard/Lakkaraju alignment. |
| **What our project adds** | Cross-lingual extension; native validation; monitor-validity focus. |
| **Threat level** | **LOW.** Foundational method we may adopt; no cross-lingual or monitor-validity claim. |

---

## 5. Chen et al. — "Reasoning Models Don't Always Say What They Think"

| Field | Content |
|---|---|
| **Citation** | Yanda Chen, Joe Benton, Ansh Radhakrishnan, … Ethan Perez. Anthropic, 2025. arXiv:2505.05410. **VERIFIED.** |
| **Research question** | Do reasoning models verbalize the hints that change their answers? |
| **Languages** | English. |
| **Models** | Claude 3.7 Sonnet, DeepSeek R1 (+ non-reasoning baselines). |
| **Faithfulness intervention** | Six hint types; paired hinted/un-hinted prompts; when the answer switches, does the CoT acknowledge the hint? |
| **Monitoring setup** | LLM-judge infers "used the hint." |
| **Metrics** | CoT faithfulness / hint-reveal rate. |
| **Findings** | Low faithfulness, especially on safety-relevant hint types ("often below 20%" per the blueprint — PARTIALLY VERIFIED). |
| **Limitations** | English-only; automated judge; no cross-lingual; no native validation. |
| **Overlap with our project** | This is (with Turpin) the **primary reproduction target for Milestone 1** and the source of the disclosure-rate / answer-switch / hidden-influence definitions. |
| **What our project adds** | Cross-lingual; native-validated; monitor-validity gap; translate-then-monitor. |
| **Threat level** | **LOW.** Foundational; we reproduce it as our baseline. |

---

## 6. Turpin et al. — "Language Models Don't Always Say What They Think"

| Field | Content |
|---|---|
| **Citation** | Miles Turpin, Julian Michael, Ethan Perez, Samuel R. Bowman. NeurIPS 2023. arXiv:2305.04388. **VERIFIED.** |
| **Research question** | Do CoT explanations reflect the real reasons for a prediction? |
| **Languages** | English. |
| **Models** | GPT-3.5, Claude 1.0. |
| **Faithfulness intervention** | Biasing features (e.g. answer-always-(A) in few-shot; suggested answers). |
| **Metrics** | Accuracy drop under bias; whether the CoT mentions the bias. |
| **Findings** | Up to 36% accuracy drop across 13 BBH tasks; models rarely mention the bias. |
| **Limitations** | English-only; small/old models; bias may be "too easy" (Emmons critique). |
| **Overlap with our project** | The other half of the Milestone-1 baseline; the biasing-feature intervention (Phase 7). |
| **Threat level** | **LOW.** Foundational. |

---

## 7. Lanham et al. — "Measuring Faithfulness in Chain-of-Thought Reasoning"

| Field | Content |
|---|---|
| **Citation** | Tamera Lanham, Anna Chen, Ansh Radhakrishnan, … Anthropic, 2023. arXiv:2307.13702. **VERIFIED.** |
| **Method** | Perturb the CoT (add mistakes / paraphrase / truncate), measure answer change → "intervention sensitivity" / load-bearingness. |
| **Findings** | Large task-to-task variation; larger models often less faithful. |
| **Overlap with our project** | Source of the **intervention-sensitivity** definition; Zhao's cross-lingual protocol descends from this. |
| **Threat level** | **LOW.** Foundational. |

---

## 8. Emmons et al. — "When Chain of Thought is Necessary, Language Models Struggle to Evade Monitors"

| Field | Content |
|---|---|
| **Citation** | Scott Emmons, Erik Jenner, … Rohin Shah. Google DeepMind, 2025. arXiv:2507.05246. **VERIFIED.** |
| **Contribution** | Conceptual: CoT-as-rationalization vs. CoT-as-computation; for runtime monitoring against severe harm, the key property is **monitorability, not faithfulness**. |
| **Overlap with our project** | Provides the monitorability-vs-faithfulness distinction underpinning our definitions (Phase 1); argues load-bearing CoT is harder to fake — relevant to our cue design (use cues that require explicit computation, as Onyame does). |
| **Threat level** | **LOW.** Conceptual foundation. |

---

## 9. Korbak et al. — "Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety"

| Field | Content |
|---|---|
| **Citation** | Tomek Korbak, Mikita Balesni, Elizabeth Barnes, Yoshua Bengio, + ~40 co-authors. 2025. arXiv:2507.11473. **VERIFIED.** |
| **Type** | Position paper. Defines CoT monitorability; calls for research into its reliability, explicitly including "mid- and low-resource languages." |
| **Overlap with our project** | Supplies the **definition of monitorability** and an explicit call for exactly this kind of low-resource reliability work — useful for motivation, not a competitor. |
| **Threat level** | **LOW.** Motivational; cite as the mandate for the project. |

---

## 10. Yang et al. — "Investigating CoT Monitorability in Large Reasoning Models"

| Field | Content |
|---|---|
| **Citation** | Shu Yang et al. arXiv:2511.08525 (2025→2026). **VERIFIED.** |
| **Research question** | How do verbalization quality and monitor reliability relate? |
| **Languages** | English. |
| **Findings** | *"There exists a gap between being monitorable and being monitored correctly."* Proposes MoME (evidence-based structured monitoring). |
| **Overlap with our project** | ⚠️ **Conceptually the closest to our "monitor-validity gap"** — Yang et al. already name and study the gap between monitorability and being monitored correctly, in English. Our contribution is the *cross-lingual, native-validated* instance of this gap plus the translation mitigation. |
| **What our project adds** | Cross-lingual dimension; native-human ground truth (Yang's "correct" label is still model-derived); the translate-then-monitor fix. |
| **Threat level** | **MEDIUM.** Not a direct competitor (English, no native validation, no cross-lingual), but it means we cannot claim to have *originated* the monitorable-vs-monitored-correctly distinction — we must cite Yang et al. prominently and frame our contribution as the cross-lingual measurement-validity instance. |

---

## 11. "A Comprehensive Evaluation of Chain-of-Thought Faithfulness in Persian Classification Tasks"

| Field | Content |
|---|---|
| **Citation** | Shakib Yazdani, Cristina España-Bonet, Eleftherios Avramidis, Yasser Hamidullah, Josef van Genabith. LoResLM 2026 (@ EACL 2026). ACL Anthology 2026.loreslm-1.27. **VERIFIED (identity).** |
| **Research question** | How faithful is CoT in Persian classification tasks, English vs. Persian prompting? |
| **Languages** | English, Persian. |
| **Models** | 6 LMs (small / large / reasoning). |
| **Datasets** | 15 classification datasets. |
| **Faithfulness intervention** | (classification-task faithfulness; specific intervention TODO from PDF). |
| **Monitoring setup** | LLM-as-judge **+ human evaluation** (that the humans were *native Persian speakers*: PARTIALLY VERIFIED). |
| **Findings** | First comprehensive CoT-faithfulness study for Persian. |
| **Limitations (per blueprint)** | Did not address monitorability, Urdu, or translate-then-monitor; classification tasks not reasoning/hint paradigm. |
| **Overlap with our project** | **This is the "native-language faithfulness validation is publishable and doable" precedent.** Same region (low-resource, Perso-Arabic-adjacent), same idea (human validation of CoT faithfulness). |
| **What our project adds** | Monitorability (not just faithfulness); the influence/hint paradigm; the monitor-validity gap; translate-then-monitor; Urdu; a reasoning-task (not classification) setting. |
| **Threat level** | **MEDIUM.** If this group extends to monitorability or to translation recovery, or to Urdu, overlap rises fast. Watch it (kill/pivot A). |

---

## 12. UrduBench — "An Urdu Reasoning Benchmark using Contextually Ensembled Translations with Human-in-the-Loop"

| Field | Content |
|---|---|
| **Citation** | Muhammad Ali Shafique, Areej Mehboob, Layba Fiaz, Muhammad Usman Qadeer, Hamza Farooq. arXiv:2601.21000 (2026-01-28). Leaderboard: `traversaal-ai/urdubench_leaderboard`. **VERIFIED.** |
| **Research question** | How do LLMs perform on Urdu reasoning benchmarks? |
| **Languages** | Urdu (translated from English sources). |
| **Datasets** | Urdu translations of MGSM, MATH-500, CommonSenseQA, OpenBookQA via contextually-ensembled MT + human-in-the-loop. |
| **Metrics** | Accuracy + language consistency. **No faithfulness, no monitoring.** |
| **Overlap with our project** | **Infrastructure, not competition** — provides ready Urdu translations of MGSM / CommonSenseQA / OpenBookQA and a human-in-the-loop translation methodology we can build on / compare against. |
| **What our project adds** | Everything faithfulness- and monitoring-related. |
| **Threat level** | **LOW.** A resource we use, not a competitor. Cite for Urdu data provenance. |

---

## Novelty-audit conclusion

- The **YELLOW verdict survives** independent verification (see `DECISION_LOG.md` D-007).
- **Broad claim ("monitors fail across languages")**: occupied by #1 (HIGH) and #2
  (MEDIUM–HIGH). Do not pursue as a contribution.
- **"Monitorable vs. monitored-correctly" distinction**: partly occupied by #10 (Yang,
  MEDIUM) in English — must be cited, not claimed as original.
- **Native-language CoT-faithfulness human validation**: precedent exists (#11, Persian,
  MEDIUM) but not for monitorability, not for Urdu, not with a translation mitigation.
- **The specific open intersection** — native-validated **monitorability** measurement in
  a low-resource language + **translate-then-monitor** recovery + explicit **A-vs-B
  (model unfaithfulness vs. monitor failure) separation** — is **not occupied by any
  verified paper as of 2026-09-01.**
- **Standing threats:** a follow-up from the Onyame or Persian-faithfulness groups; the
  newer judge-sensitivity paper arXiv:2603.20172 (§D of `CITATION_VERIFICATION.md`),
  which must be read before Milestone 4.

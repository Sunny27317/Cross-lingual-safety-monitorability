# RUN-2 BLUEPRINT — CLAUDE CODE SCIENTIFIC HANDOFF

**Document type:** Run-2 Deep Research → Claude Code scientific handoff
**Source:** `literature/RUN2_BLUEPRINT.pdf` (13 pages; internal title "Do Safety Monitors
Fail Across Languages? — Validation & Execution Blueprint for Sana Ullah"; PDF header
dated 9/1/26)
**Project status:** Pre-experiment
**Evidence status:** Literature/planning only — NO PROJECT EXPERIMENTAL RESULTS YET
**Research verdict:** YELLOW — proceed only with the narrowed measurement-validity +
mitigation contribution (reproduced verbatim from the source; see §1)
**Generated purpose:** structured extraction of `RUN2_BLUEPRINT.pdf` for repository
implementation

---

## How to read this document

- This is a **derived** artifact. `literature/RUN2_BLUEPRINT.pdf` remains the original,
  immutable provenance artifact. If the two ever disagree, the PDF wins.
- Text was extracted from the PDF's content streams (the PDF has no OCR/text layer issues
  for the prose; the comparison table in the PDF is laid out cell-by-cell and has been
  reassembled here — reassembly is flagged where ambiguous).
- Attribution tags used throughout:
  - **[BLUEPRINT]** — a claim, recommendation, or design choice made by the Run-2 report.
  - **[PRIOR WORK]** — a finding attributed by the blueprint to an external paper.
  - **[HYPOTHESIS]** — a proposed, not-yet-tested hypothesis.
  - **[PLANNED]** — a planned experiment / parameter / value (never an observed result).
  - **[UNRESOLVED]** — the blueprint explicitly leaves this open.
- Independent citation verification is **not** in this file. It is in
  `literature/CITATION_VERIFICATION.md`. Every paper named here is cross-referenced there.
- Nothing in this document is an experimental result of this project. No number here was
  produced by us.

---

## 1. Research verdict (reproduced from source)

> **[BLUEPRINT]** "Verdict: YELLOW (proceed, but only with a sharply narrowed
> contribution). The broad question 'does CoT safety monitoring fail across languages?'
> was largely answered before Sana could start it — most decisively by Onyame et al. …
> A generic 'we added Urdu' study is now RED. But three genuine, verifiable gaps
> survive: (1) native-speaker validation that automated multilingual monitors are
> actually trustworthy in a low-resource language, (2) translate-the-CoT-then-monitor as
> a recovery mitigation, and (3) disentangling monitor/judge degradation from model
> unfaithfulness — none of which the competing papers did."

> **[BLUEPRINT]** "The defensible contribution is a measurement-validity result, not a
> 'more languages' result: demonstrate, with native Urdu ground truth, whether the
> field's standard automated CoT monitor is measuring genuine unfaithfulness or is
> itself failing in low-resource languages — and whether cheap post-hoc translation
> recovers the lost safety signal."

**Distinction the blueprint insists on:**
- **(A)** "Multilingual CoT faithfulness differs across languages" — **[PRIOR WORK], now
  RED for us**: substantially answered by Onyame et al. 2026 and Zhao et al. 2026.
- **(B)** "The validity/reliability of reasoning-based monitoring itself may change
  across languages" — **[BLUEPRINT], the actual target**: open, because no competitor
  used native-speaker ground truth to separate monitor failure from model
  unfaithfulness, and none tested translate-then-monitor.

---

## 2. Novelty assessment (reproduced from source)

### 2.1 What moved against the original framing
**[BLUEPRINT]** "between the Run-1 recommendation and now (September 2026), the
'monitorability across languages' space filled in." Nearest/most threatening paper:
**Onyame et al., "The Fragility of Chain-of-Thought Monitoring Across Typologically
Diverse Languages"** (arXiv:2605.27901, v1 27 May 2026; University of Virginia +
Lawrence Livermore National Laboratory).

**[PRIOR WORK]** Onyame et al. is reported to deliver:
- 13 typologically diverse languages spanning high/mid/low-resource tiers; 16 models
  across 7 families (Qwen3, DeepSeek-R1 distills, GPT-OSS, Llama, Gemma 3, plus closed
  GPT/Claude).
- Adversarial hint methodology (simple `<answer>C</answer>` cue + complex
  modular-arithmetic cue) on multilingual GPQA.
- An automated LLM judge monitoring whether the CoT verbalizes the hint.
- Verbatim abstract numbers quoted by the blueprint: *"we consistently find CoT
  unfaithfulness across languages and hint types, with an average rate of 95.9% across
  8B–120B parameter models"*; *"these deceptive patterns remain 100% in low-resource
  languages"*; *"frontier models often commit to the misaligned cue in their latent
  activations within the first 15% of generation, even when the CoT appears faithful."*
- Resource tiers defined empirically: prompt "Kimi K2.6 … a strong open-source
  multilingual model" to solve GPQA zero-shot, then tier by accuracy — *"above 60% for
  high-resource, between 30% and 60% for mid-resource, and below 30% for low-resource."*

**[PRIOR WORK]** Combined with **Zhao et al.** (Findings of EACL 2026, arXiv:2510.09555)
— multilingual CoT performance, consistency, and faithfulness (language compliance and
truncation/error-injection faithfulness across languages including Bengali and Yoruba) —
**[BLUEPRINT]** "the plain statement 'monitorability degrades in lower-resource
languages' is no longer novel."

### 2.2 Gaps the competitors left (the surviving contribution)
**[BLUEPRINT]** "Verified against the Onyame et al. text and repository, the closest
competitor did **not**:"
- **(a)** Use any native-speaker human validation. *"we use [the judge model] as the
  verification judge"; "We validate the judge through manual inspection of samples
  across all languages."* No bilingual/native annotator involved.
- **(b)** Test translate-the-CoT-back-to-English-then-monitor as a recovery mitigation.
  Their stress tests cover option-letter bias, closed-source generalization, and
  stochastic stability only.
- **(c)** Separately quantify whether the monitor/judge itself degrades in low-resource
  languages, as distinct from the model's own unfaithfulness. *"A monolingual-English-
  optimized judge reading Urdu CoT could be the thing failing — a confound that directly
  threatens the '100% in low-resource' claim."*
- **(d)** Include Urdu among its named low-resource languages (its low-resource
  exemplars are Swahili, Telugu, Yoruba).

**[BLUEPRINT] important caveat:** "It **did** partially control for base accuracy (a
'Baseline Error Rate' analysis in Appendices B.1/B.6 showing deception persists even when
accuracy is comparable) — so Sana must **not** claim competitors ignored task difficulty.
The residual gap is judge-side degradation, not accuracy control."

**[BLUEPRINT]** "Crucially, no 2025–2026 paper combines native-speaker low-resource
CoT-monitorability validation with a post-hoc CoT-translation recovery method. That
intersection is genuinely open." Nearest native-validation precedent: the Persian
LoResLM 2026 study — *"used native human evaluation of faithfulness but did not address
monitorability, Urdu, or translation recovery."*

### 2.3 On the title
**[BLUEPRINT]** "'Do Safety Monitors Fail Across Languages?' is a better frame … because
it names a falsifiable safety claim. But as a project scope it is now too broad and
collides head-on with Onyame et al. The winning move is to reframe from 'do monitors
fail?' (answered) to 'when monitors appear to fail in a low-resource language, is that
real model unfaithfulness or measurement artifact — and can we fix it?' (open)."

---

## 3. Closest competing papers (blueprint's Phase 0 comparison table, reassembled)

The PDF states: *"The comparison table (all papers verified real, with arXiv/ACL
identifiers)."* Columns: Paper · Year/Venue · Languages · Models · Faithfulness method ·
Safety/monitor focus. Reassembled from the PDF's cell-by-cell layout:

| Paper | Year/Venue | Languages | Models | Faithfulness method | Safety/monitor focus? |
|---|---|---|---|---|---|
| Onyame et al. (arXiv:2605.27901) | 2026 preprint (UVA+LLNL) | 13 typologically diverse (Swahili, Telugu, Yoruba as low-res) | 16 (Qwen3, R1-distills, GPT-OSS, Llama, Gemma 3, GPT, Claude) | Adversarial hints (simple+complex) + logit lens | Yes (core) |
| Zhao et al. (arXiv:2510.09555) | Findings EACL 2026 | Multiple incl. Bengali, Yoruba | R1-Qwen-32B, R1-Llama-70B, etc. | Truncation + error injection; consistency; language compliance | Partial |
| Qi et al. (arXiv:2505.22888) | Findings EMNLP 2025 | Multiple | 2 LRM families (XReasoning) | Language-compliance + accuracy tradeoff | Oversight framing |
| Xiong, Chen, Qi & Lakkaraju (arXiv:2505.13774) | NeurIPS 2025 (Harvard) | English | 6 LRMs | Counterfactual draft perturbation | Monitoring motivation |
| Chen et al. (arXiv:2505.05410) | 2025 (Anthropic) | English | Claude 3.7, R1 | Hint-verbalization reveal rate | Yes |
| Turpin et al. (arXiv:2305.04388) | NeurIPS 2023 | English | GPT-3.5, Claude 1 | Biasing features (answer-always-A) | Foundational |
| Lanham et al. (arXiv:2307.13702) | 2023 (Anthropic) | English | Claude family | Perturb CoT (mistakes/paraphrase/truncation) | Foundational |
| Emmons et al. (arXiv:2507.05246) | 2025 (Google DeepMind) | English | Gemini family | CoT-as-computation vs rationalization | Yes |
| Korbak et al. (arXiv:2507.11473) | 2025 (multi-org) | English | — | Position paper | Yes (defines monitorability) |
| Yang et al. (arXiv:2511.08525) | 2025→2026 | English | LRMs | Verbalization + monitor reliability | Yes |
| "Persian CoT Faithfulness" (aclanthology 2026.loreslm-1.27) | 2026 LoResLM | English, Persian | 6 LMs | LLM-as-judge + human eval | Faithfulness |
| UrduBench (arXiv:2601.21000) | 2026 | Urdu | Reasoning + instruct LLMs | Accuracy + language consistency (not faithfulness) | No |

Independent verification of every row → `literature/CITATION_VERIFICATION.md`.
Full per-paper competitor analysis (RQ, datasets, findings, limitations, overlap, threat
level) → `literature/COMPETITOR_MATRIX.md`.

---

## 4. Surviving research gaps (blueprint's Phase 3 — "the unique, peer-review-defensible contribution")

**[BLUEPRINT]** "A native-validated measurement-validity study of cross-lingual CoT
monitorability, plus a translate-then-monitor recovery test. Three deliverables:"
1. "Native Urdu ground-truth for whether traces are genuinely unfaithful — the first
   such validation for monitorability in Urdu, isolating the monitor-validity gap the
   competing papers could not measure."
2. "Evidence on whether post-hoc CoT translation recovers safety signal — a cheap,
   deployable mitigation nobody has tested."
3. "A reproducible protocol/benchmark separating three often-conflated quantities:
   answer correctness, CoT faithfulness, and monitor detectability. Explicitly not
   'Zhao/Onyame + Urdu.'"

---

## 5. Research questions (blueprint's Phase 2)

**Primary RQ [BLUEPRINT]:** "When an automated CoT safety monitor reports degraded
monitorability in a low-resource language (Urdu), how much is genuine model
unfaithfulness versus monitor/judge measurement failure — and does translating the CoT
to English before monitoring recover the lost safety signal?"

The blueprint does not enumerate separately-numbered secondary RQs; the secondary
questions are embedded in H2–H5 (§6) and the mitigation phase (§14). See
`RESEARCH_PLAN.md` for the frozen RQ set derived from this.

---

## 6. Falsifiable hypotheses (blueprint's Phase 2, reproduced verbatim in substance)

| ID | Hypothesis [HYPOTHESIS] | Falsification condition [BLUEPRINT] |
|---|---|---|
| **H1 (model effect)** | Hidden-influence rate is higher in Urdu than English **even under native-human monitoring**. | If native humans detect influence equally well across languages, the "low-resource fragility" claim is partly a measurement artifact. (Blueprint: "Null still publishable.") |
| **H2 (monitor-validity gap)** | The automated English-centric monitor's detection rate drops more than native-human detection in Urdu (**gap > 0**). | gap ≈ 0 → automated monitors are trustworthy in Urdu. |
| **H3 (recovery)** | Translating the Urdu CoT to English before monitoring raises automated detection **toward the English baseline**. | No recovery → safety-relevant information is lost at generation, not at monitoring. |
| **H4 (dose-response)** | Monitor-validity gap increases monotonically with decreasing resource level **after controlling for base accuracy**. | Effect vanishes after accuracy control → monitorability tracks competence, not language per se (this is **kill trigger D**). |
| **H5 (compliance mediation)** | Degraded monitorability is **mediated by low language compliance** (mid-trace reversion to English). | (Blueprint gives no explicit falsifier; implied: no mediation effect.) |

---

## 7. Operational definitions (blueprint's Phase 1)

**[BLUEPRINT]** "Adapting Turpin 2023, Lanham 2023, Chen 2025, Xiong/Lakkaraju 2025,
Zhao 2026, Korbak 2025:"

- **Faithfulness (verbalization/disclosure):** `disclosure rate = P(CoT explicitly
  mentions dependence on cue h | model reached the hinted answer)`.
- **Intervention sensitivity (Lanham):** Δ in answer distribution when the CoT is
  truncated/corrupted/paraphrased. High sensitivity ⇒ CoT is load-bearing
  (CoT-as-computation).
- **Answer-switch rate (Turpin/Chen):** `P(answer changes from no-hint baseline to
  hinted answer)` — the influence signal.
- **Monitor detection rate / monitor AUROC:** the monitor's ability, given the CoT, to
  correctly flag "this trace was influenced by a cue," scored against ground-truth
  influence labels; report precision/recall/F1 and AUROC.
- **Hidden influence:** answer-switch = yes but disclosure = no — "the safety-critical
  quantity."
- **Language compliance (Zhao/Qi):** fraction of the CoT actually generated in the
  requested language (measured, not assumed).
- **Reasoning consistency / answer consistency:** cross-language agreement of reasoning
  content and of final answers.
- **Calibration:** correspondence between stated confidence and correctness — secondary,
  "only if time allows."
- **Monitorability (composite, Korbak/Emmons):** degree to which reading the CoT lets an
  external monitor identify safety-relevant influence ≈ disclosure rate × monitor
  detection rate × language compliance. *(The PDF renders the operator as `×`; treat the
  exact functional form as **[UNRESOLVED]** — see `RESEARCH_PLAN.md`.)*
- **Monitor-validity gap (the project's novel measured quantity):**
  `(native-human monitor detection) − (automated monitor detection)`, per language.

---

## 8. Language ladder (blueprint's Phase 4)

**[BLUEPRINT]** "Principled language ladder":

| Language | Role | Resource | Script | Rationale (blueprint) |
|---|---|---|---|---|
| English (en) | high-resource anchor | high | Latin | anchor |
| German (de) **or** Spanish (es) | high-resource control | high | Latin | "isolates 'not-English' from 'low-resource'" |
| Arabic (ar) | script control | mid/high | Perso-Arabic | "isolates script from resource level vs. Urdu" |
| Hindi (hi) | linguistic-content control | higher than Urdu | Devanagari | "Hindustani sibling … isolates script from linguistic content" |
| **Urdu (ur)** | **target low-resource** | low | Perso-Arabic | "native validation available" |
| Bengali (bn) **or** Yoruba (yo) | very-low-resource lower anchor | very low | Bengali / Latin | "matches competitors' tiers" |

**[UNRESOLVED]** de-vs-es and bn-vs-yo are not decided by the blueprint.

**[BLUEPRINT]** Operationalizing "resource level" — composite of: (i) estimated
pretraining token share, (ii) benchmark availability, (iii) tokenizer fertility
(tokens-per-word), (iv) base-model accuracy (Onyame's method — zero-shot GPQA accuracy
on a strong multilingual model), (v) linguistic distance from English, (vi) script.

**[BLUEPRINT]** Confound separation designed into the ladder:
- Hindi–Urdu pair: holds language ~constant, varies script/resource.
- Arabic–Urdu pair: holds script family ~constant, varies language.
- German/Spanish: holds resource high, varies "Englishness."

---

## 9. Models (blueprint's Phase 5 — "open-weight, inspectable traces, feasible Sept 2026")

| Model | Params | Role [BLUEPRINT] | Notes from blueprint |
|---|---|---|---|
| **DeepSeek-R1-Distill-Qwen-7B** | 7B | **Primary Tier-A workhorse; English-baseline replication target** | "strong math reasoning; Qwen multilingual base; open; full `<think>` trace; single 16GB GPU / Colab." "Onyame et al. use the DeepSeek-Qwen distills, enabling direct comparison." |
| DeepSeek-R1-Distill-Qwen-14B | 14B | Tier-B/C main model | "UrduBench found it sustains difficulty well; needs ~24–40GB or quantization." **[PARTIALLY VERIFIED claim]** |
| **Qwen3-8B (thinking mode)** | 8B | **Primary for the multilingual arm** | "~119-language coverage (vs. ~30 for the DeepSeek distills) — best multilingual reasoner in the accessible class; open; single-GPU." |
| Qwen3-32B | 32B | Tier-C | "stronger" |
| DeepSeek-R1-Distill-Llama-8B | 8B | family-generalization control | "different family for generalization; open; single-GPU" |
| GPT-OSS-20B | 20B | family/scale generalization | "open-weight, different family/scale; Tier-B/C" |
| **Monitor/judge models** | — | the scientific comparison variable | "an open judge (e.g., Qwen3-32B or a Llama-70B-class model), plus optionally one API judge for calibration — but the scientific comparison is automated judge vs. native human." "Avoid designing around closed models (GPT-5.x, Claude) whose full traces aren't inspectable, except optionally as an extra external judge." |

**[UNRESOLVED]** exact monitor/judge model(s) and versions; exact model revisions/hashes.

---

## 10. Datasets / tasks (blueprint's Phase 6)

| Dataset | Task | Blueprint notes |
|---|---|---|
| **MGSM** | math, multi-step | "250 items, 10+ languages incl. Bengali; already Urdu-translated in UrduBench. Clean for hint injection. Contamination: moderate — mitigate with paraphrase checks." |
| **GPQA / GPQA-Diamond** | hard science MCQ | "the competitors' dataset; enables direct comparison; needs Urdu translation + native correction; low contamination." |
| CommonSenseQA / OpenBookQA | commonsense / factual MCQ | "in UrduBench; MCQ ideal for cue injection." |
| BBH / BBQ-style items | bias/hint-sensitive | "for the biasing-feature intervention; BBQ needs cultural adaptation." |
| Small safety-relevant decision set | ~50 items | "a cue nudges toward an unsafe/wrong recommendation (ethically bounded, no operational-harm content)." **[PLANNED, to be constructed]** |

**[BLUEPRINT] Native Urdu subset construction (required):**
- "~150–250 MCQ items stratified across math/commonsense/science."
- Pipeline: (1) machine-translate; (2) native-speaker (the researcher) correction for
  fluency/terminology/answer-preservation; (3) back-translation check + second-native-
  reviewer adjudication on a 50-item audit; (4) validation criterion **≥90% native
  agreement** that meaning and correct answer are preserved.
- Benchmark: "the documented ~60% raw-MT label agreement for Urdu (vs. ~90% English),
  which is precisely why native correction is scientifically necessary."
  **[PRIOR WORK / UNVERIFIED source]**
- Target: **n ≈ 200 items × ~5 seeds per condition**. **[PLANNED]**

**[BLUEPRINT] question provenance:** items are machine-translated then native-corrected
(not naturally multilingual, not professionally translated, not native-authored).
GPQA additionally needs new Urdu translation + native correction.

---

## 11. Faithfulness / intervention protocols (blueprint's Phase 7)

| Protocol | What it does | Blueprint's assessment |
|---|---|---|
| **Turpin (biasing features)** | reorder options / suggested answer; influence = accuracy drop; disclosure = CoT mentions bias | "Simple, strong effect; but bias may be too easy (Emmons critique); option-letter bias interacts with script/RTL." |
| **Lanham (CoT perturbation)** | truncate / insert-mistake / paraphrase, measure answer change | "Measures load-bearingness; needs controlled decoding; truncation points differ by tokenization." |
| **Chen 2025 (hint reveal rate)** | six hint types; "used the hint" is judge-inferred | "the current standard, directly comparable." |
| **Xiong/Lakkaraju 2025 (counterfactual draft perturbation)** | intra-draft + draft-to-answer | "causal, fine-grained; heavier engineering; English-only so far." |
| **Zhao 2026 (multilingual truncation + error injection)** | already cross-lingual | "reusable; no native validation, no monitor-validity measurement." |

**[BLUEPRINT] recommendation:** "reproduce the Turpin/Chen hint-based method first
(simplest, matches Onyame's setup for direct comparison), then layer Zhao's multilingual
truncation as a robustness check."

**[BLUEPRINT] cue types used in the centerpiece (Phase 8):** incorrect-answer
suggestion, biasing evidence, shortcut feature.

---

## 12. Centerpiece "four-monitor" experiment (blueprint's Phase 8)

**[BLUEPRINT] Design:** "hidden influence → model reasoning → answer; then CoT →
independent monitor → detect influence?; across the ladder; with the native-human
monitor as ground truth." Tests **H2** (gap > 0 in Urdu) + **H3** (translation recovers).

**Independent variables:**
- **language** (the ladder, §8)
- **cue type** (incorrect-answer suggestion / biasing evidence / shortcut feature)
- **monitor type — the four monitors:**
  1. automated **English** judge
  2. automated **in-language** judge
  3. **native human** (ground truth)
  4. **translate-then-English** judge (Urdu CoT → English → same automated judge)

**Dependent variables:** answer-switch rate, disclosure rate, hidden-influence rate,
monitor detection rate / AUROC, language compliance.

**Controls:** no-hint baseline; base-accuracy covariate; option-letter-bias control; ≥5 seeds.

**Sample-size plan [PLANNED]:** "~200 items × 6 languages × 3 cue types × 5 seeds (power
to detect a 10-point detection-rate gap at α = .05, power .8 — smaller than the
tens-of-points effects typical in this literature)."

**Test [PLANNED]:** mixed-effects logistic regression (item + model random effects),
language fixed, base-accuracy covariate; AUROC via DeLong.

**[BLUEPRINT] expected result (a prediction, not a finding):** "automated detection
drops in Urdu; native detection drops far less; translation partially recovers automated
detection."

**[BLUEPRINT] interpretation key:**
- native ≈ automated → "validates competitors' automated-only method (useful confirmation)"
- native ≫ automated → "the '100% low-resource deception' literature partly reflects
  monitor failure (high-impact corrective)"

**How this separates (A) from (B):** the native-human monitor supplies a
language-independent ground-truth label for whether a trace is genuinely unfaithful. If
a trace that native humans read as *disclosed* is flagged *hidden* by the automated
monitor, that is monitor failure (B), not model unfaithfulness (A). The four-monitor
contrast localizes where signal is lost (generation vs. in-language judging vs. English
judging vs. translation).

---

## 13. Control experiments (blueprint's Phase 9)

Translation quality (native validation); task-difficulty matching (item-matched subsets
+ covariate); base-accuracy control (analyze only items solved without hint, or covary
accuracy); language compliance (measure % Urdu, flag reverts); script vs. language
(Hindi/Arabic/Urdu triad); prompt-template sensitivity (≥3 templates); model-family
generalization (Qwen + Llama + GPT-OSS); model-size scaling (7B/14B/32B); repeated
generations (≥5 seeds, temperature reported); contamination/memorization checks
(paraphrase items).

---

## 14. Mitigation (blueprint's Phase 11)

- **Primary:** translate-the-CoT-to-English-then-monitor ("verified not done by
  competitors").
- **Secondary (only if focus permits):** in-language vs. English monitor; ensemble
  monitoring; language-aware calibration thresholds; prompting the model to reason
  in-language ("Qi et al. show this aids oversight but costs accuracy — cite the
  tradeoff").
- **[BLUEPRINT] sequencing:** "Pursue mitigation only after the core measurement result
  is locked."

**[BLUEPRINT] outcome-pattern interpretations (Phase 8/11):**
- native monitor fails + translated monitor succeeds → signal is present but the
  in-language/English judge could not read it; translation is a real fix.
- both fail → signal lost at generation (favors A / H3 falsified).
- both succeed → no monitor-validity problem in Urdu (H2 falsified).
- translation *damages* detection → translation introduces artifacts (kill/pivot E).

---

## 15. Statistical analysis plan (blueprint's Phase 10)

- **Metrics (all with bootstrap 95% CIs):** disclosure rate, hidden-influence rate,
  monitor AUROC + P/R/F1, answer-switch rate, language-compliance rate, monitor-validity
  gap (native − automated).
- **Tests:** mixed-effects logistic regression; DeLong for AUROC; McNemar for paired
  human-vs-automated on identical traces; Cohen's κ for native inter-annotator agreement.
- **Multiple comparisons:** Benjamini–Hochberg FDR across language × cue cells.
- **Meaningful effect size [BLUEPRINT]:** "given disclosure effects often <20% and Urdu
  vs. English label-agreement gaps of ~30 points, treat a ≥10-point monitor-validity gap
  as scientifically meaningful."
- **Unit of analysis:** not explicitly stated beyond "item + model random effects";
  treat as **[UNRESOLVED]** (item-level, per condition).
- **Power / N:** the ~200 × 6 × 3 × 5 design is asserted to give power .8 for a
  10-point gap at α = .05; the power calculation itself is not shown. **[UNRESOLVED —
  reproduce the calculation before Milestone 4.]**

---

## 16. Confounds (consolidated from Phases 4, 8, 9, 18)

base-model accuracy / task difficulty; language resource level; tokenizer fertility;
script (RTL / Perso-Arabic vs. Devanagari vs. Latin); translation quality &
translation-introduced artifacts; model multilingual competence / language compliance;
prompt-template formatting; option-letter (positional) bias interacting with RTL;
CoT length; dataset contamination / memorization; semantic & answer equivalence across
languages; monitor/judge competence in-language; cultural adaptation of bias items;
model-family effects; multiple comparisons.

---

## 17. Ablations (from Phase 9; blueprint has no separate "ablations" section)

The blueprint folds ablations into Phase 9 controls. Explicitly listed variations that
function as ablations: monitor type (4 levels); cue type (3 levels); model family (3);
model size (7B/14B/32B); prompt template (≥3); with/without base-accuracy restriction;
in-language vs. translated vs. English judge; hint-based vs. Zhao truncation protocol.

---

## 18. Compute plan (blueprint's Phase 13) — ESTIMATES, not verified costs

| Tier | Hardware | Scope | GPU-hours | Cost | Storage |
|---|---|---|---|---|---|
| **A (free — start now)** | laptop + Colab free (T4 16GB) | DeepSeek-R1-Distill-Qwen-7B / Qwen3-8B via vLLM or 4-bit; English baseline + Urdu pilot ~50 items | "tens" | **$0** | <20GB |
| **B (realistic)** | Colab Pro / rented A100 40GB (~$1–2/hr) | full ladder × 7B/14B × 5 seeds | ~100–300 | **~$150–600** (+ "tens of dollars" optional API judge) | ~100GB |
| **C (expanded)** | university lab GPUs (via TAIMing AI / advisor) | 32B models, full replication, family generalization | ~500–1000 | "marginal cash cost" | — |

**[BLUEPRINT]** "This week on Tier-A: reproduce Turpin/Chen English hint-faithfulness on
7B; stand up the repo; translate+native-correct a 50-item Urdu pilot."

All figures are the blueprint's **estimates**. None is a quoted vendor price.

---

## 19. Reproducibility requirements (blueprint's Phase 12)

**[BLUEPRINT]** "Environment: uv/conda + pinned `requirements.txt`; vLLM for inference;
global seed control; Hydra/OmegaConf config management; structured JSONL logging (model,
lang, seed, prompt hash); W&B or CSV logging; deterministic decoding option; a
`make reproduce` target."

**[BLUEPRINT] repository structure (Phase 12) — differs from the current repo:**
```
xling-monitor/
  data/          # raw, translated, native-corrected, splits (DVC or git-lfs)
  src/           # generation, hint-injection, monitors, translation
  models/        # model configs, loaders (vLLM)
  experiments/   # one config-driven script per experiment
  configs/       # YAML: model, language, cue, seed
  notebooks/     # exploratory only
  evaluation/    # metrics: disclosure, AUROC, compliance
  statistics/    # mixed-effects, DeLong, FDR
  results/       # versioned JSONL outputs
  figures/
  paper/
  tests/
```
Reconciliation with the Milestone-0 structure → `REPRODUCIBILITY.md` §"Directory layout".

---

## 20. GO / PIVOT / KILL criteria (blueprint's Phase 18, verbatim in substance)

| ID | Condition | Blueprint's mapped consequence |
|---|---|---|
| **A** | A new paper does essentially this exact study (native Urdu validation + translate-then-monitor). | Pivot to a different mitigation (in-language monitors / ensembles) **or** a different low-resource language pair. |
| **B** | English baseline faithfulness effect won't reproduce. | Debug harness; if truly absent, pivot to a multilingual language-compliance / consistency study. |
| **C** | Models can't reliably reason in Urdu (compliance too low). | Pivot to the compliance-as-oversight-bottleneck angle (builds on Qi et al.). |
| **D** | Language differences vanish after base-accuracy control. | Report the null as a corrective (still publishable); shift emphasis to measurement methodology. |
| **E** | The metric mostly measures translation quality. | "That is the finding" — reframe the paper around measurement validity. |

**[BLUEPRINT] quantitative trigger:** "native-vs-automated gap <10 points → pivot to
mitigation/compliance framing (kill D/E); a competing native+translation paper appears →
pivot language pair or mitigation (kill A)."

**[BLUEPRINT]** "Do not optimize the project merely to obtain a positive result.
Negative and null findings must be preserved."

---

## 21. Publication strategy (blueprint's Phase 16) — no acceptance implied

- **Realistic:** ACL/EMNLP/NAACL/EACL **Findings**, or a workshop with proceedings —
  LoResLM, BlackboxNLP, TrustNLP, or a NeurIPS/ICLR safety/SoLaR workshop.
- **Stretch:** main-conference short paper at ACL/EMNLP, or a FAccT paper "if the
  oversight/fairness framing is strong."
- **Fallback:** arXiv preprint + non-archival workshop talk. "Avoid predatory venues."
- **Contribution threshold [BLUEPRINT]:** "workshop = one clean native-validated result;
  Findings = full ladder + mitigation."
- **Likely deadlines named:** ACL cycle (Feb), EMNLP (May), NeurIPS workshops (summer),
  EACL/LoResLM (fall). **[UNVERIFIED — confirm each cycle's dates at project start.]**

---

## 22. Faculty recommendations (blueprint's Phase 14) — NO ONE HAS AGREED TO SUPERVISE

**[BLUEPRINT] ranked, "verified September 2026":**
1. **Depeng Xu** — Assistant Professor, Software & Information Systems + School of Data
   Science; core member, UNC Charlotte Center for Trustworthy AI through Model Risk
   Management (TAIMing AI). Published "Fine-tuning LLMs with Cross-Attention-based Weight
   Decay for Bias Mitigation" (with Farsheed Haque, Zhe Fu, Shuhan Yuan, Xi Niu),
   Findings of EMNLP 2025, pp. 15785–15798; work "received a 2025 TAIMing AI Seed Grant
   Award." "Best current fit and #1 target."
2. **Razvan Bunescu** — Associate Professor, CS; 2025 work on LLM reasoning trajectories
   (Socratic debugging; EMNLP 2025 recommender paper). "#2."
3. **Liyue Fan** — trustworthy/privacy AI; "adjacent, not reasoning-focused."
4. **Wlodek Zadrozny** — Professor, NLP; "transitioning to Emeritus status in 2026 —
   availability risk, deprioritize as primary."
5. **Samira Shaikh** — retains a UNC Charlotte appointment but "now Director of Data
   Science at Ally (industry)"; "only as informal advisor."

**[BLUEPRINT] outreach email to Xu** (reproduced for provenance; **contains claims that
must be true before sending** — GPA/class-year are the researcher's to confirm, and the
email as drafted asserts pilot results that DO NOT EXIST YET):

> Subject: Undergraduate research — validating cross-lingual CoT safety monitors
> (reproduced a baseline)
>
> Dear Dr. Xu, I'm a CS undergraduate (GPA 3.78, Class of '27) and a native Urdu
> speaker. I've been studying chain-of-thought safety monitoring and noticed that recent
> multilingual results (Onyame et al. 2026; Zhao et al., EACL 2026) rely entirely on
> automated, English-centric LLM judges — with no native-speaker validation and no test
> of whether translating the reasoning trace back to English recovers the safety signal.
> I reproduced the English hint-faithfulness baseline (Turpin/Chen) on
> DeepSeek-R1-Distill-Qwen-7B and ran a small Urdu pilot; my early results suggest the
> automated monitor may itself be failing in Urdu, rather than the model being more
> deceptive. I'd value 20 minutes of your guidance on whether this "monitor-validity
> gap" framing is sound and worth developing, given your work on trustworthy LLM
> evaluation (e.g., your Findings of EMNLP 2025 bias-mitigation paper). A one-page design
> and repo are attached.

> ⚠️ **INTEGRITY NOTE (not from the blueprint):** this email may only be sent *after*
> Milestone 1 + the Urdu pilot have actually run and produced the stated evidence. Until
> then it describes results that do not exist. The GPA and class-year claims are the
> researcher's to verify. Do not send from an automated process.

---

## 23. Harvard alignment (blueprint's Phase 15) — NO ADMISSIONS CLAIM

**[BLUEPRINT]** "Himabindu Lakkaraju — strong on faithfulness/trustworthy AI
(thinking-draft faithfulness, NeurIPS 2025); moderate on multilingual. Her frequent
collaborators (Chen, Qi, Xiong) work directly on CoT faithfulness/monitorability — the
exact neighborhood of this project. **Treat as research alignment only; make no
admissions claim.**"

**[BLUEPRINT]** (TL;DR + Caveats) "No public evidence about current admissions should be
treated as a promise." "No statement here implies any Harvard (or other) admission
outcome; PhD admission is not predictable from a single project."

---

## 24. Roadmap (blueprint's Phase 19)

- **Weeks 1–8:** W1 literature mastery + reproduce English hint baseline on 7B; W2 repo
  + config harness + metric unit tests; W3 Urdu 50-item pilot (translate + native-
  correct); W4 run pilot ladder (en/hi/ur), inspect monitor-validity gap; W5 email Xu
  with pilot evidence; W6 expand to full native subset (~200 items) + add
  Arabic/Bengali; W7 add second model family + seeds; W8 first-pass statistics +
  go/no-go against kill criteria.
- **Months 3–6:** full ladder × models × cues; native inter-annotator study;
  translate-then-monitor mitigation; secure supervision + lab GPU (Tier C).
- **Months 6–9:** analysis, robustness/controls, draft workshop paper; post preprint.
- **Months 9–12:** submit workshop/Findings; iterate.
- **Months 12–18:** camera-ready/second study; recommendation-letter timing aligned to
  fall PhD deadlines; PhD applications with preprint + letter in hand.

---

## 25. First 72 hours (blueprint's Phase 20)

- **Day 1 (read):** Onyame et al. 2605.27901 (§3 setup, §7 stress tests, App. B–C incl.
  Table 6 to confirm whether Urdu is included, App. D.2 to confirm the judge model);
  Chen et al. 2505.05410 (hint method); Turpin 2305.04388 (method); Zhao 2510.09555
  (multilingual faithfulness metrics). Write a one-paragraph statement of the
  monitor-validity gap.
  → *Partly done in this integration: Urdu confirmed **absent** and judge stated as
  GPT-5.1 in the arXiv HTML — see `CITATION_VERIFICATION.md`.*
- **Day 2 (build):** create the repo per Phase 12; `pip install vllm transformers`; load
  DeepSeek-R1-Distill-Qwen-7B on Colab; implement `inject_hint(item, cue)` and a
  keyword+LLM disclosure checker; unit-test on 5 items. → **Milestone 1 work — NOT YET
  AUTHORIZED.**
- **Day 3 (baseline target):** reproduce the English hint effect — measure answer-switch
  and disclosure rate on ~50 MGSM items with/without the incorrect-answer cue; target:
  observe answer-switching with disclosure well below switching (the Turpin/Chen
  signature; "Chen et al. report reveal rates often below 20%"). If reproduced,
  translate 10 items to Urdu (native-correct) and check whether the automated judge
  still reads them. → **Milestone 1 work — NOT YET AUTHORIZED.**

---

## 26. Limitations & caveats (blueprint's Caveats section, verbatim in substance)

- "The specific automated-judge model used by Onyame et al. and the full 13-language
  list are stated in the paper's appendices … but were not confirmable from public
  secondary materials; a common 'GPT-5.1 judge' attribution is unverified and Urdu's
  absence is likely but not confirmed — Sana must check both directly in the PDF before
  citing." → **This integration checked the arXiv HTML: Urdu absent; judge stated as
  GPT-5.1. Still confirm against the published PDF appendices.**
- "Many cited works (including the competitor and several 2026 titles) are arXiv
  preprints, some not yet peer-reviewed; numbers may change on revision, and
  future-dated IDs should be re-verified at project start."
- "No statement here implies any Harvard (or other) admission outcome."
- "Ethical scope: use only benign, controlled cues; do not construct operational-harm
  content; credit native annotators (including Sana) explicitly in any publication."

---

## 27. Unresolved decisions (blueprint did NOT settle these)

| # | Decision | Blocking? |
|---|---|---|
| U1 | German vs. Spanish for the high-resource control | before Milestone 2 |
| U2 | Bengali vs. Yoruba for the very-low-resource anchor | before Milestone 2 |
| U3 | Exact monitor/judge model(s) + versions (open judge; optional API judge) | before Milestone 4 |
| U4 | Exact generator model revisions / commit hashes | before Milestone 1 |
| U5 | Which English hint-faithfulness paper is the *primary* reproduction target — Turpin (2305.04388) or Chen (2505.05410) — and the exact protocol/metric to match | before Milestone 1 (BLOCKING) |
| U6 | Milestone-1 dataset: MGSM vs. GPQA vs. CommonSenseQA for the first ~50 items | before Milestone 1 (BLOCKING) |
| U7 | Exact functional form of the composite "monitorability" metric (product? weighted?) | before Milestone 4 |
| U8 | Number of native Urdu annotators beyond the researcher; recruitment; blinding; κ threshold | before Milestone 3 (BLOCKING for that milestone) |
| U9 | Translation system/model for translate-then-monitor, and whether its output is itself native-validated | before Milestone 4 |
| U10 | Decoding config: temperature, top-p, max tokens, n-samples, seed list | before Milestone 1 (BLOCKING) |
| U11 | Cue taxonomy final list (blueprint names 3 for the centerpiece, Chen has 6) | before Milestone 4 |
| U12 | Milestone-1 quantitative success band (what counts as "reproduced") | before Milestone 1 (BLOCKING) |
| U13 | Power calculation actually reproduced (not just asserted) | before Milestone 4 |
| U14 | Unit of analysis + exact random-effects structure for the mixed-effects model | before Milestone 5 |
| U15 | Ethics/IRB status for human annotation; consent; compensation | before Milestone 3 |
| U16 | Data-release plan for traces + annotations | before Milestone 6 |
| U17 | Safety-relevant decision set (~50 items): source, construction, ethics review | before it is used |

---

## 28. Bibliography as cited by the blueprint

Full identifiers + independent verification status → `literature/CITATION_VERIFICATION.md`.

1. Onyame, Zhou, Thopalli, Kailkhura & Agarwal — "The Fragility of Chain-of-Thought
   Monitoring Across Typologically Diverse Languages." arXiv:2605.27901 (v1 27 May 2026).
   UVA + LLNL.
2. Zhao et al. — multilingual CoT reasoning (performance, consistency, faithfulness).
   Findings of EACL 2026. arXiv:2510.09555.
3. Qi et al. — XReasoning; language-compliance vs. accuracy tradeoff. Findings of EMNLP
   2025. arXiv:2505.22888.
4. Xiong, Chen, Qi & Lakkaraju — "Measuring the Faithfulness of Thinking Drafts in Large
   Reasoning Models." NeurIPS 2025 (Harvard). arXiv:2505.13774.
5. Chen et al. — hint-verbalization reveal rate. Anthropic, 2025. arXiv:2505.05410.
6. Turpin et al. — biasing features / unfaithful CoT. NeurIPS 2023. arXiv:2305.04388.
7. Lanham et al. — CoT perturbation faithfulness. Anthropic, 2023. arXiv:2307.13702.
8. Emmons et al. — CoT-as-computation vs. rationalization. Google DeepMind, 2025.
   arXiv:2507.05246.
9. Korbak et al. — "Chain of Thought Monitorability" position paper. 2025.
   arXiv:2507.11473.
10. Yang et al. — verbalization + monitor reliability. 2025→2026. arXiv:2511.08525.
11. "A Comprehensive Evaluation of Chain-of-Thought Faithfulness in Persian
    Classification Tasks." LoResLM 2026. ACL Anthology 2026.loreslm-1.27.
12. UrduBench — Urdu reasoning benchmark. 2026. arXiv:2601.21000.
13. Depeng Xu et al. — "Fine-tuning LLMs with Cross-Attention-based Weight Decay for Bias
    Mitigation." Findings of EMNLP 2025, pp. 15785–15798.
14. (referenced, not in the table) "Kimi K2.6" — the strong multilingual model Onyame et
    al. use to tier languages by zero-shot GPQA accuracy. **[UNVERIFIED]**

# Experiment Specification

**Status:** PLANNING ONLY. Nothing here has been run. No model or dataset has been
downloaded. Every number is a **plan**, never an observation.
**Source:** `literature/RUN2_BLUEPRINT.pdf` Phases 4–13, via
`literature/RUN2_BLUEPRINT_HANDOFF.md`; verification in
`literature/CITATION_VERIFICATION.md`.
**Rule:** where the blueprint does not fix a value, it is marked `TODO — DECISION
REQUIRED` (with alternatives + a recommendation) or `TODO — IMPORT/VERIFY`. Do not guess.

---

## 0. Design overview

Two experimental arms, milestone-gated:

- **Baseline arm (Milestone 1):** reproduce the English hint-faithfulness signature on
  one model. No cross-lingual comparison.
- **Cross-lingual monitorability arm (Milestones 2–5):** the four-monitor centerpiece
  across the language ladder, with native Urdu ground truth and the translate-then-
  monitor condition, plus controls/ablations/statistics.

The design separates three quantities that prior work conflates:
**answer correctness** vs. **CoT faithfulness (disclosure)** vs. **monitor detectability**.

---

## 1. Experimental matrix (cross-lingual arm)

**Model × Language × Dataset × Intervention(cue) × Monitor × Seed**

| Dimension | Planned levels | Status |
|---|---|---|
| **Model (generator)** | DeepSeek-R1-Distill-Qwen-7B (primary, Tier-A); Qwen3-8B thinking (primary multilingual); DeepSeek-R1-Distill-Qwen-14B; DeepSeek-R1-Distill-Llama-8B (family control); Qwen3-32B (Tier-C); GPT-OSS-20B (family/scale) | models named by blueprint; **exact revisions `TODO — IMPORT/VERIFY` (U4)** |
| **Language ladder** | en; {de OR es}; ar; hi; **ur (target)**; {bn OR yo} | 6 slots; **de/es and bn/yo `TODO — DECISION REQUIRED` (U1, U2)** |
| **Dataset** | MGSM (math); GPQA / GPQA-Diamond (science MCQ); CommonSenseQA / OpenBookQA (commonsense MCQ); BBH/BBQ-style (bias); ~50-item safety-relevant decision set | which subset per milestone `TODO — DECISION REQUIRED` (U6); safety set construction `TODO` (U17) |
| **Intervention / cue type** | incorrect-answer suggestion; biasing evidence; shortcut feature (Phase 8 centerpiece uses these 3). Chen has 6 hint types; Turpin biasing features; Lanham perturbations; Zhao truncation+error-injection as robustness | 3 for centerpiece; full taxonomy `TODO — DECISION REQUIRED` (U11) |
| **Monitor type (the four monitors)** | (1) automated English judge; (2) automated in-language judge; (3) native human; (4) translate-then-English judge | fixed by blueprint; judge model(s) `TODO — DECISION REQUIRED` (U3) |
| **Seed** | ≥5 per condition; temperature reported | seed list `TODO — DECISION REQUIRED` (U10) |
| **Control conditions** | no-hint baseline (required for every cell); base-accuracy-restricted subset; option-letter-bias control | fixed by blueprint |

**Planned scale (blueprint Phase 8):** ~200 items × 6 languages × 3 cue types × 5 seeds.
Asserted power: 0.8 to detect a 10-point detection-rate gap at α = .05. **The power
calculation itself is `TODO — reproduce before Milestone 4` (U13).**

---

## 2. Target vs. baseline vs. control models

| Model | Role | Why (blueprint) | HF identifier | Revision |
|---|---|---|---|---|
| DeepSeek-R1-Distill-Qwen-7B | **primary generator / baseline-reproduction target** | fits free compute; full `<think>` trace; Onyame uses the DeepSeek-Qwen distills → direct comparison | `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` *(verify)* | `TODO — IMPORT/VERIFY` |
| Qwen3-8B (thinking) | **primary generator, multilingual arm** | broad language coverage; single-GPU | `Qwen/Qwen3-8B` *(verify)* | `TODO` |
| DeepSeek-R1-Distill-Qwen-14B | scale control | UrduBench: "sustains difficulty well" (**PARTIALLY VERIFIED**) | *(verify)* | `TODO` |
| DeepSeek-R1-Distill-Llama-8B | model-family control | different family, same scale | *(verify)* | `TODO` |
| Qwen3-32B | Tier-C scale control | stronger | *(verify)* | `TODO` |
| GPT-OSS-20B | family/scale control | open-weight, distinct family | *(verify)* | `TODO` |
| open judge (Qwen3-32B or Llama-70B-class) | **monitor** | inspectable; the scientific comparison is judge vs. native human | `TODO — DECISION REQUIRED` (U3) | `TODO` |
| optional API judge | monitor calibration only | not load-bearing for the claim | `TODO` | n/a |

Closed models (GPT-5.x, Claude) are excluded as generators (traces not inspectable);
allowed only as an optional extra external judge.

**Claims to verify before use (`CITATION_VERIFICATION.md` §C):** Qwen3-8B "~119
languages" vs. DeepSeek distill "~30"; the 14B UrduBench finding.

---

## 3. Language ladder — detail

See `RESEARCH_PLAN.md` §"Language ladder" and `RUN2_BLUEPRINT_HANDOFF.md` §8.
Resource level = composite of (i) pretraining token share (est.), (ii) benchmark
availability, (iii) tokenizer fertility (computable), (iv) zero-shot base accuracy
(Onyame's method), (v) linguistic distance from English, (vi) script.

**Confound-separation pairs built into the ladder:**
- Hindi ↔ Urdu: language ~constant, script/resource varies.
- Arabic ↔ Urdu: script family ~constant, language varies.
- German/Spanish ↔ English: resource high, "Englishness" varies.

`TODO — DECISION REQUIRED`: de vs. es (U1); bn vs. yo (U2). Recommendation: **es** (more
training data, more native annotators available if needed) and **bn** (matches Onyame's
low-resource tier and has MGSM coverage) — but this is not settled.

---

## 4. Datasets — detail

| Dataset | Task | Urdu availability | License | Contamination | Role |
|---|---|---|---|---|---|
| MGSM | grade-school math, multi-step | Urdu translation in UrduBench (**VERIFIED** UrduBench translates MGSM) | check (MGSM: CC BY-SA 4.0 — verify) | moderate; mitigate w/ paraphrase | Milestone 1 baseline candidate; core math items |
| GPQA / GPQA-Diamond | hard science MCQ | none — needs new Urdu translation + native correction | check (GPQA license — verify; has usage restrictions) | low | direct Onyame comparison |
| CommonSenseQA / OpenBookQA | commonsense MCQ | in UrduBench (**VERIFIED** for CommonSenseQA, OpenBookQA) | check | moderate | cue-injection items |
| BBH / BBQ-style | bias/hint-sensitive | none; BBQ needs cultural adaptation | check | moderate | biasing-feature intervention |
| Safety-relevant decision set (~50) | unsafe-recommendation nudge | to be authored | n/a — new | n/a | safety-relevant cue arm |

**Cross-language equivalence control (blueprint Phase 6, 9):**
1. machine-translate → 2. native correction (fluency/terminology/answer preservation) →
3. back-translation check + 2nd-native-reviewer adjudication on a 50-item audit →
4. acceptance criterion **≥90% native agreement** that meaning + correct answer preserved.
Benchmark: "~60% raw-MT vs. ~90% English label agreement" (**`TODO — UNVERIFIED` source**;
treat as a quantity to measure, not a citable fact).

`TODO — DECISION REQUIRED` (U6): which single dataset/subset for the first ~50 Milestone-1
items. Recommendation: **MGSM** (multi-step, forces load-bearing CoT per Emmons; already
Urdu-translated; used in the blueprint's Day-3 plan).

---

## 5. Interventions (cue design)

| Cue | Purpose | Treatment | Control | Influence measure | Disclosure measure | Monitor-detection measure |
|---|---|---|---|---|---|---|
| Incorrect-answer suggestion | primary hidden-influence signal | prompt embeds a wrong suggested answer | same prompt, no suggestion | answer-switch rate vs. no-hint baseline | judge/human: does CoT mention the suggestion? | judge/human: "was this trace influenced by a cue?" scored vs. ground-truth influence label |
| Biasing evidence | Turpin-style | prompt embeds misleading supporting info | neutral info | accuracy drop / switch rate | CoT mentions the biasing info? | same |
| Shortcut feature | tests procedural exploitation | a spurious cue that allows skipping reasoning | no shortcut | switch to shortcut answer | CoT mentions the shortcut? | same |
| (robustness) Zhao truncation + error injection | intervention-sensitivity / load-bearingness | truncate/insert error into CoT | unperturbed | Δ answer distribution | n/a | n/a |

**Ground-truth influence label:** an item is "influenced" if the model's answer switched
from the no-hint baseline to the cued answer for that (item, seed). This label is
**independent of any monitor** — that independence is what makes the monitor-validity gap
measurable. `TODO — DECISION REQUIRED`: exact operationalization for multi-sample seeds
(majority? any? per-sample) (part of U10/U14).

`TODO`: interventions NOT adopted and why — truncation-as-primary (tokenization differs
by language, hard to equate); Xiong/Lakkaraju counterfactual draft perturbation (English
tooling only, heavy) — kept as optional robustness only.

---

## 6. The four-monitor centerpiece (Milestone 4)

Pipeline per (model, language, item, cue, seed):
```
item + cue  ─►  generator  ─►  (answer, CoT)
                                  │
        ┌─────────────────────────┼─────────────────────────┬───────────────────────────┐
        ▼                         ▼                         ▼                           ▼
  M1 automated             M2 automated              M3 native human            M4 translate-then-
  ENGLISH judge            IN-LANGUAGE judge         (ground truth)             ENGLISH judge
  (CoT as-is)              (CoT as-is)               (CoT as-is)                (CoT→EN→judge)
        │                         │                         │                           │
        └───────────►  each emits: influence-detected? (+ rationale)  ◄──────────────────┘
```
- **Scoring:** each monitor's detection is scored against the ground-truth influence
  label → detection rate, precision/recall/F1, AUROC (where a score/prob is available).
- **Key comparisons:**
  - M3 − M1 = **monitor-validity gap** (per language). H2.
  - M4 − M1 = **translate-then-monitor recovery**. H3.
  - M4 vs. M3 = how close translation gets automated detection to native.
  - M2 vs. M1 = does an in-language judge already help without translation?
- **Paired test:** McNemar on M1 vs. M3 over identical traces.
- `TODO — DECISION REQUIRED`: whether M3 (native human) scores *all* conditions or a
  powered stratified sample (cost); κ threshold and annotator count (U8).
- `TODO — DECISION REQUIRED`: translation system for M4, and whether its output is
  itself native-validated (U9).

---

## 7. Measurements

| Metric | Definition | What it establishes | What it cannot establish |
|---|---|---|---|
| Task accuracy | P(correct) with/without hint | base competence; difficulty matching | anything about faithfulness |
| Answer-switch rate | P(answer → cued answer vs. no-hint baseline) | that the cue influenced the model | whether the model disclosed it |
| Disclosure rate | P(CoT mentions dependence on cue \| reached hinted answer) | verbalized faithfulness | whether influence occurred without a switch |
| Hidden-influence rate | P(switch = yes ∧ disclosure = no) | the safety-critical quantity | *who* fails (needs the monitor contrast) |
| Monitor detection rate / P / R / F1 | monitor's accuracy vs. ground-truth influence label | how good a given monitor is | why it fails without the 4-monitor contrast |
| Monitor AUROC (DeLong) | threshold-free monitor discrimination | monitor quality independent of threshold | requires a monitor score, not just a label |
| Language compliance | fraction of CoT in requested language | mediator for H5; data-quality flag | causal direction alone |
| **Monitor-validity gap** | native detection − automated detection, per language | (A) vs. (B) separation — the core result | absolute unfaithfulness level |
| Translation recovery | M4 − M1 (toward M3) | whether the cheap mitigation works | whether in-language judges would also work (need M2) |
| Calibration | stated confidence vs. correctness | secondary | — (only "if time allows") |

All point estimates reported with **bootstrap 95% CIs**.

---

## 8. Statistical tests (blueprint Phase 10)

| Purpose | Test | Status |
|---|---|---|
| Rates across language/cue/monitor | mixed-effects logistic regression; item + model random effects; language fixed; base-accuracy covariate | planned; random-effects structure `TODO` (U14) |
| AUROC comparison | DeLong | planned |
| Paired human vs. automated on identical traces | McNemar | planned |
| Native inter-annotator agreement | Cohen's κ | planned; threshold `TODO` (U8) |
| Multiple comparisons | Benjamini–Hochberg FDR across language × cue cells | planned |
| Effect sizes | rate differences + CIs; odds ratios from the GLMM | planned |
| Significance threshold | α = .05 (pre-FDR) | planned |
| Meaningful effect | **≥10-point monitor-validity gap** | fixed by blueprint |
| Power / sample size | ~200 × 6 × 3 × 5 asserted to give power .8 for a 10-pt gap | **calculation `TODO — reproduce` (U13)** |
| Unit of analysis | per (item, condition); seeds aggregated | `TODO — confirm` (U14) |

Confirmatory vs. exploratory: H1–H5 and the four-monitor comparisons are
**confirmatory** and must be pre-registered in the experiment's own README before data
are seen. Anything added after looking at data is labelled **exploratory / post-hoc**.

---

## 9. Confound controls (blueprint Phase 9)

| Confound | Control |
|---|---|
| base-model accuracy / task difficulty | analyze only items solved without hint, and/or base-accuracy covariate; item-matched subsets across languages |
| task difficulty per se | stratified sampling across math/commonsense/science; difficulty covariate |
| translation quality | native correction + ≥90% agreement criterion + back-translation audit |
| translation-introduced signal | human-translated control subset; native validation of M4 translations |
| script (RTL / Perso-Arabic) | Hindi/Arabic/Urdu triad; option-letter-bias control |
| language resource level | composite operationalization; dose-response analysis (H4) |
| tokenizer fertility | measure tokens-per-word per language/model; report; covary if needed |
| model multilingual competence | language-compliance measurement; capability floor before faithfulness claims |
| prompt formatting | ≥3 prompt templates; template as a random effect / sensitivity analysis |
| response / CoT length | measure; covary |
| dataset contamination | paraphrase items; contamination check |
| semantic & answer equivalence | native audit; back-translation |
| monitor competence in-language | the M2 (in-language judge) condition is itself the probe |
| cultural differences (bias items) | cultural adaptation of BBQ-style items; native review |
| model-family effects | ≥3 families (Qwen, Llama, GPT-OSS) |
| multiple comparisons | BH-FDR |

---

## 10. Ablations (blueprint folds these into Phase 9)

monitor type (4 levels) · cue type (3) · model family (3) · model size (7B/14B/32B) ·
prompt template (≥3) · with/without base-accuracy restriction · in-language vs.
translated vs. English judge · hint protocol vs. Zhao truncation protocol · seeds
(≥5, temperature reported).

Purpose of each: see `RESEARCH_PLAN.md` §"Ablations".

---

## 11. What is NOT specified by the blueprint (do not invent)

All items in `RUN2_BLUEPRINT_HANDOFF.md` §27 (U1–U17). BLOCKING for Milestone 1:
U5 (primary reproduction paper), U6 (dataset), U10 (decoding config), U12 (success band).
BLOCKING for Milestone 3: U8 (annotators, blinding, κ), U15 (ethics/consent).
BLOCKING for Milestone 4: U3 (judge models), U9 (translation system), U13 (power calc).

---

## 12. Directory / config plan (no code yet)

Planned `configs/` (Hydra/OmegaConf) groups — schemas only, to be written at Milestone 1:
`model/`, `language/`, `dataset/`, `cue/`, `monitor/`, `decoding/`, `experiment/`.
Planned `src/` packages: `generation/`, `hint_injection/`, `monitors/`, `translation/`,
`evaluation/` (disclosure, AUROC, compliance), `statistics/` (GLMM, DeLong, FDR,
bootstrap). Planned `experiments/<id>/`: one config-driven entrypoint + a pre-registered
README + provenance record. See `REPRODUCIBILITY.md`.

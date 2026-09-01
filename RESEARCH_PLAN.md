# RESEARCH_PLAN.md

> **Derived document.** The immutable provenance artifacts are
> `literature/RUN2_BLUEPRINT.pdf` and its structured extraction
> `literature/RUN2_BLUEPRINT_HANDOFF.md`. Citation checks: `literature/CITATION_VERIFICATION.md`.
> Novelty audit: `literature/COMPETITOR_MATRIX.md`. Decisions: `literature/DECISION_LOG.md`.
> Experiment matrix: `experiments/EXPERIMENT_SPEC.md`. Reproducibility: `REPRODUCIBILITY.md`.
>
> This plan is frozen at the level of research questions, hypotheses, definitions, and
> milestone gates (Run-2 integration, 2026-09-01). Values the Run-2 blueprint did not
> settle are marked `TODO — DECISION REQUIRED` or `TODO — IMPORT/VERIFY`. **Nothing here
> is an experimental result. No experiment has been run.**

---

## 1. Project title

Cross-lingual safety monitorability: a native-validated measurement-validity study of
whether apparent failure of automated CoT safety monitoring on Urdu reasoning traces is
genuine model unfaithfulness or monitor failure — with a translate-then-monitor recovery
test.

Working paper title (from the blueprint, to be narrowed in the manuscript): *"Do Safety
Monitors Fail Across Languages?"* — but the **scope** is measurement validity, not "do
monitors fail" (already answered; see §4).

## 2. Status / verdict

**YELLOW — proceed only with the narrowed measurement-validity + mitigation
contribution.** Re-affirmed after independent citation verification on 2026-09-01
(`DECISION_LOG.md` D-007). Current milestone: **Milestone 0 (governance + validated
design)** — completing the Run-2 integration. No experiments, downloads, or compute.

## 3. Background

Reasoning-based oversight — monitoring a model's visible chain-of-thought (CoT) for
signs of unsafe intent, deception, or hidden influence — is a leading scalable-oversight
proposal (Korbak et al. 2025, arXiv:2507.11473; Emmons et al. 2025, arXiv:2507.05246).
Its validity depends on the monitor being able to *read and correctly judge* the
reasoning it is given.

By September 2026 the broad cross-lingual question was substantially answered:
- **Onyame et al. 2026 (arXiv:2605.27901)** — 13 languages, 16 models: 95.9% average
  CoT-unfaithfulness across 8B–120B models, "100% in low-resource languages", using an
  automated English-centric LLM judge. **VERIFIED**, incl. that they used no native
  validation, did not test translate-then-monitor, and did not include Urdu.
- **Zhao et al. 2026 (Findings EACL 2026, arXiv:2510.09555)** — multilingual CoT
  performance/consistency/faithfulness, language compliance, truncation + error
  injection. **VERIFIED.**

## 4. Broad question that is NOT our contribution

> "Do safety monitors fail across languages / does CoT monitorability degrade in
> lower-resource languages?"

Treated as **settled prior work** (Onyame 2026, Zhao 2026). The repository must never
present this, or "we added Urdu", as novel (`CLAUDE.md` §2.6, §5; `DECISION_LOG.md`
D-001, D-003).

## 5. Narrowed contribution

A **native-validated measurement-validity study of cross-lingual CoT monitorability, plus
a translate-then-monitor recovery test** (blueprint Phase 3). Three deliverables:
1. Native Urdu human ground truth for whether traces are genuinely unfaithful —
   isolating the **monitor-validity gap** that automated-only studies cannot measure.
2. Evidence on whether post-hoc CoT translation recovers the safety signal — a cheap,
   deployable mitigation not yet tested by anyone.
3. A reproducible protocol separating three conflated quantities: **answer correctness**,
   **CoT faithfulness (disclosure)**, and **monitor detectability**.

Urdu's scientific role: the low-resource instance where trustworthy native ground truth
is obtainable (researcher is a native speaker; ≥1 further annotator planned) and which
Onyame omits. Not the contribution itself.

**Canonical novelty statement (user-approved 2026-09-01; `DECISION_LOG.md` D-014/D-015).**
No novelty is claimed from "monitors/judges perform worse in low-resource languages"
(substantial prior work — Onyame 2026 for CoT monitors; arXiv:2607.02235 / 2605.28710 /
2607.14480 / 2505.12201 for LLM-as-judge generally) or from including Urdu. The
contribution is the **surviving intersection**: (1) native-human-validated low-resource
CoT **monitorability**; (2) **translate-then-monitor** as a measurable recovery
mechanism; (3) explicit **A (model unfaithfulness) vs. B (monitor/judge failure)**
separation; (4) controlled **cross-lingual measurement validity**; (5) **Urdu as a
native-validated test environment**, not as the claim. If a paper occupies this
intersection ⇒ kill/pivot A, flagged immediately.

## 6. Primary research question (frozen)

**When an automated CoT safety monitor reports degraded monitorability on a low-resource
language (Urdu), how much of that degradation is genuine model unfaithfulness versus
monitor/judge measurement failure — and does translating the CoT to English before
monitoring recover the lost safety signal?**

## 7. Secondary research questions (frozen)

- **SQ1.** Does an automated in-language judge (no translation) close any of the gap
  relative to an automated English judge?
- **SQ2.** Is any monitor-validity gap mediated by language compliance (mid-trace
  reversion to English)?
- **SQ3.** Does the monitor-validity gap scale with decreasing resource level after
  controlling for base task accuracy (dose–response)?
- **SQ4.** Is degraded *monitoring* separable from degraded *generation* — i.e. is the
  safety signal present in the trace but unread, or absent from the trace?
- **SQ5.** Does translation *introduce or remove* disclosure signal (translation
  artifact), rather than faithfully relaying it?

## 8. Falsifiable hypotheses (frozen — from blueprint Phase 2)

| ID | Hypothesis | Independent var(s) | Dependent var(s) | Expected direction | Prior-lit basis | Falsification condition |
|---|---|---|---|---|---|---|
| **H1** (model effect) | Hidden-influence rate is higher in Urdu than English **even under native-human monitoring**. | language | hidden-influence rate (native-scored) | Urdu > English | Onyame/Zhao report cross-lingual faithfulness drops | Native humans detect influence equally across languages ⇒ the "low-resource fragility" claim is partly a measurement artifact. (Null still publishable.) |
| **H2** (monitor-validity gap) | The automated English-centric monitor's detection rate drops **more** than native-human detection in Urdu (gap > 0). | language, monitor type | monitor detection rate; monitor-validity gap = native − automated | gap > 0, larger in Urdu | Onyame's judge is English-centric and unvalidated in low-resource | gap ≈ 0 ⇒ automated monitors are trustworthy in Urdu. |
| **H3** (recovery) | Translating the Urdu CoT to English before monitoring raises automated detection **toward the English baseline**. | monitor type (translate-then-monitor vs. English-direct) | automated detection rate on Urdu traces | M4 → M1(en) baseline | translation improves multilingual task performance (Qi et al.) | No recovery ⇒ safety-relevant information is lost at generation, not at monitoring. |
| **H4** (dose–response) | The monitor-validity gap increases monotonically with decreasing resource level **after controlling for base accuracy**. | resource level (ladder), base accuracy (covariate) | monitor-validity gap | monotone increase | Onyame's tiered degradation | Effect vanishes after accuracy control ⇒ monitorability tracks competence, not language per se (**= kill/pivot D**). |
| **H5** (compliance mediation) | Degraded monitorability is **mediated by low language compliance**. | language compliance | monitor detection rate; mediation coefficient | partial/full mediation | Zhao/Qi: compliance is a measured cross-lingual weakness | No mediation effect ⇒ compliance is not the mechanism. |

H1–H5 and the four-monitor comparisons are **confirmatory**; they must be pre-registered
in each experiment's README before data are seen. Post-hoc analyses are labelled
exploratory.

## 9. Operational definitions (frozen — blueprint Phase 1)

- **CoT faithfulness / disclosure rate:**
  `disclosure_rate = P(CoT explicitly mentions dependence on cue h | model reached the hinted answer)`.
- **Answer-switch rate:** `P(answer changes from the no-hint baseline to the hinted answer)` — the influence signal.
- **Hidden influence:** `answer-switch = yes ∧ disclosure = no` — the safety-critical quantity.
- **Detection (monitor):** a monitor, given the CoT, outputs whether "this trace was
  influenced by a cue"; scored against the **ground-truth influence label** (the
  answer-switch fact for that item/seed, which does not depend on any monitor).
  Reported as detection rate, precision/recall/F1, and AUROC (DeLong) where a score exists.
- **Intervention sensitivity (Lanham):** Δ in the answer distribution when the CoT is
  truncated / corrupted / paraphrased. High sensitivity ⇒ the CoT is load-bearing
  (CoT-as-computation, Emmons).
- **Language compliance:** measured fraction of the CoT actually generated in the
  requested language.
- **Monitorability (composite, Korbak/Emmons):** the degree to which reading the CoT
  lets an external monitor identify safety-relevant influence. The blueprint writes this
  as ≈ `disclosure_rate × monitor_detection_rate × language_compliance`. **The exact
  functional form is `TODO — DECISION REQUIRED` (U7)** — adopt the product only if
  justified; otherwise report the components separately.
- **Monitor-validity gap (the project's novel measured quantity):**
  `gap_L = native_human_detection_L − automated_monitor_detection_L`, per language L.
- **Translation recovery:** `M4_detection − M1_detection` (Urdu traces), assessed
  relative to the English baseline and to native detection (M3).

## 10. The central distinction: model unfaithfulness (A) vs. monitor failure (B)

This is the project's core scientific claim and must not be dropped or blurred anywhere
in the repository.

| | **(A) Model unfaithfulness** | **(B) Monitor / judge failure** |
|---|---|---|
| What is true | The visible CoT genuinely fails to disclose what influenced the answer. | The CoT *does* contain the evidence; the monitor fails to recognize it — because of language, script, translation, representation, or judge-competence limits. |
| Where the signal is lost | at **generation** | at **monitoring / evaluation** |
| What a naive "monitor success rate" shows | low | low — *indistinguishable from (A)* |
| How we separate them | The **native-human monitor** supplies a language-independent ground-truth reading of the trace. If native readers judge a trace *disclosed* while the automated monitor flags it *hidden*, that is (B). The four-monitor contrast (English judge / in-language judge / native human / translate-then-English) localizes the loss. | |
| Why "does the monitor succeed?" is insufficient | Onyame's "100% low-resource deception" is measured by an English-centric automated judge with no native check. If that judge cannot read Urdu CoT, the number reflects (B) and is **not** evidence about (A). | |

Prior art on the general idea: Yang et al. 2025 (arXiv:2511.08525) already names a gap
"between being monitorable and being monitored correctly" in **English**. We cite this;
our contribution is the **cross-lingual, native-validated** instance + the translation
mitigation (`COMPETITOR_MATRIX.md` #10; `DECISION_LOG.md` D-005).

## 11. Language ladder (frozen structure; two slots undecided)

| Slot | Language | Role | Script | Notes |
|---|---|---|---|---|
| 1 | English (en) | high-resource anchor | Latin | baseline reference |
| 2 | German (de) **or** Spanish (es) | high-resource control | Latin | isolates "not-English" from "low-resource" — `TODO — DECISION REQUIRED` (U1) |
| 3 | Arabic (ar) | script control | Perso-Arabic | isolates script from resource vs. Urdu |
| 4 | Hindi (hi) | linguistic-content control | Devanagari | Hindustani sibling — isolates script from linguistic content |
| 5 | **Urdu (ur)** | **low-resource target** | Perso-Arabic | native validation available |
| 6 | Bengali (bn) **or** Yoruba (yo) | very-low-resource lower anchor | Bengali / Latin | matches Onyame's low tier — `TODO — DECISION REQUIRED` (U2) |

**Resource level** operationalized as a composite of: pretraining token share (est.),
benchmark availability, tokenizer fertility (computable), zero-shot base accuracy
(Onyame's method), linguistic distance from English, script.

**Confound-separation pairs:** Hindi↔Urdu (language ~constant, script/resource varies);
Arabic↔Urdu (script family ~constant, language varies); German/Spanish↔English (resource
high, "Englishness" varies).

## 12. Models (named by blueprint; revisions to pin)

Primary generator / Milestone-1 target: **DeepSeek-R1-Distill-Qwen-7B**. Primary
multilingual generator: **Qwen3-8B (thinking)**. Additional: DeepSeek-R1-Distill-Qwen-14B
(scale), DeepSeek-R1-Distill-Llama-8B (family), Qwen3-32B (Tier-C), GPT-OSS-20B
(family/scale). Monitors: an open judge (Qwen3-32B or Llama-70B-class) + optional API
judge for calibration. Closed models excluded as generators. Detail + `TODO`s:
`experiments/EXPERIMENT_SPEC.md` §2.

## 13. Datasets

MGSM (math; Urdu translation exists in UrduBench — **VERIFIED**), GPQA/GPQA-Diamond
(science MCQ; needs new Urdu translation + native correction), CommonSenseQA / OpenBookQA
(in UrduBench — **VERIFIED**), BBH/BBQ-style (bias items; needs cultural adaptation),
plus a ~50-item safety-relevant decision set to be authored (ethically bounded, no
operational-harm content). Cross-language equivalence via the 4-step native-correction
pipeline with a ≥90% native-agreement acceptance criterion. Detail:
`experiments/EXPERIMENT_SPEC.md` §4.

## 14. Native Urdu validation

Role: the **reference standard** for what a trace discloses; the thing automated monitors
are scored against. Requirements (blueprint Phase 6, 9): native/near-native proficiency;
blind to condition and to the automated monitor's output; written rubric matching the
automated-judge instructions; ≥2 independent annotators on at least an audit subset;
Cohen's κ reported; disagreement adjudicated by a second native reviewer. The researcher
is one annotator — this introduces a researcher-as-annotator bias that must be stated as
a limitation and mitigated by blinding + independent annotators. `TODO — DECISION
REQUIRED` (U8): exact annotator count, per-item coverage, κ threshold, recruitment.
`TODO` (U15): ethics/consent/compensation. Native annotations are **collected data**,
never simulated (`CLAUDE.md` §2.1).

## 15. Interventions / cues

Centerpiece uses 3 cue types: incorrect-answer suggestion, biasing evidence, shortcut
feature. Milestone 1 uses the incorrect-answer suggestion (Turpin/Chen). Zhao truncation
+ error injection layered later as a robustness check. Full taxonomy `TODO — DECISION
REQUIRED` (U11). Detail: `experiments/EXPERIMENT_SPEC.md` §5.

## 16. The four-monitor centerpiece

Monitors: (1) automated English judge, (2) automated in-language judge, (3) native human
(ground truth), (4) translate-then-English judge. Key comparisons: M3−M1 = monitor-
validity gap (H2); M4−M1 = translation recovery (H3); M4 vs. M3; M2 vs. M1 (SQ1).
McNemar for M1 vs. M3 on identical traces. Full pipeline + `TODO`s:
`experiments/EXPERIMENT_SPEC.md` §6; `RUN2_BLUEPRINT_HANDOFF.md` §12.

## 17. Translate-then-monitor

A tested hypothesis (H3), not an assumed fix (`DECISION_LOG.md` D-004). Outcome-pattern
meanings (blueprint Phase 8/11): native fails + translated succeeds → present-but-unread,
translation is a real fix; both fail → lost at generation (H3 falsified); both succeed →
no monitor-validity problem (H2 falsified); translation *damages* detection → translation
artifact (**kill/pivot E**). `TODO — DECISION REQUIRED` (U9): translation system;
native validation of its output.

## 18. Milestone plan (Phase I)

Each milestone: **Objective · Prerequisites · Outputs · Validation checks ·
GO / PIVOT / STOP**. No milestone starts before its prerequisites and the prior
milestone's GO.

### Milestone 0 — Governance + validated research design
- **Objective:** research-integrity rules, verified blueprint integration, frozen RQs /
  hypotheses / definitions, milestone gates, reproducibility spec.
- **Prerequisites:** none.
- **Outputs:** `CLAUDE.md`, this plan, `REPRODUCIBILITY.md`, `RUN2_BLUEPRINT.pdf` +
  `RUN2_BLUEPRINT_HANDOFF.md`, `CITATION_VERIFICATION.md`, `COMPETITOR_MATRIX.md`,
  `DECISION_LOG.md`, `experiments/EXPERIMENT_SPEC.md`.
- **Validation:** all core citations VERIFIED or explicitly marked; A-vs-B distinction
  documented; no fabricated values; secret scan clean.
- **GO:** user approves the integration. **PIVOT/STOP:** verification shows the surviving
  contribution is already occupied (it is not, as of 2026-09-01).

### Milestone 1 — English hint-faithfulness baseline reproduction
- **Objective:** reproduce the Turpin/Chen signature (answer-switching with disclosure
  well below switching) on DeepSeek-R1-Distill-Qwen-7B, ~50 English items, free compute.
  Measure ≥ (a) answer-switch rate under misleading vs. correct/no hint, (b) disclosure
  rate in the visible CoT.
- **Prerequisites (BLOCKING):** U5 (primary paper: Turpin vs. Chen), U6 (dataset),
  U10 (decoding config + seeds), U12 (success band). Harness + metric unit tests.
- **Outputs:** `experiments/M1-*/` with pre-registered README, config, `PROVENANCE.md`,
  raw generations, `results/M1-*/` metrics with bootstrap CIs, disclosure/switch
  code + tests.
- **Validation:** metrics land within the pre-registered band relative to the reference
  paper; unit tests pass; provenance complete (`REPRODUCIBILITY.md` §8).
- **GO:** signature reproduced within band → proceed to Milestone 2.
  **PIVOT (kill/pivot B):** effect absent after harness debugging → pivot to a
  multilingual language-compliance / consistency study.
  **STOP:** repeated inability to run even the baseline on free compute → reassess
  feasibility with the user.

### Milestone 2 — Multilingual evaluation pipeline + small Urdu pilot
- **Objective:** generation + hint-injection + language-compliance measurement + the
  automated monitors, working across the ladder; a ≥10–50-item native-corrected Urdu
  pilot; first look at whether the automated judge can even read Urdu CoT.
- **Prerequisites:** Milestone 1 GO; U1, U2 (ladder slots); U4 (model revisions);
  translation + native-correction pipeline; ladder subset selection.
- **Outputs:** pipeline code + tests; pilot dataset with full translation provenance;
  `experiments/M2-*/`; pilot metrics (accuracy, compliance, disclosure, automated
  detection) with CIs; a written go/no-go note against kill criteria.
- **Validation:** pipeline deterministic given seed; pilot translations meet ≥90% native
  agreement; language-compliance measured not assumed.
- **GO:** pipeline stable + pilot shows measurable signal → Milestone 3.
  **PIVOT (kill/pivot C):** models cannot sustain Urdu reasoning (compliance too low) →
  pivot to compliance-as-oversight-bottleneck (builds on Qi et al.).
  **STOP:** translation quality cannot reach the acceptance bar even with native
  correction → reassess dataset/language choices with the user.

### Milestone 3 — Native Urdu validation (human ground truth)
- **Objective:** collect blinded native-human monitor judgements on the same traces;
  establish inter-annotator reliability; produce the ground-truth influence/disclosure
  labels the automated monitors are scored against.
- **Prerequisites (BLOCKING):** U8 (annotators, blinding, κ threshold), U15 (ethics /
  consent / compensation); Milestone 2 GO.
- **Outputs:** annotation protocol + rubric (versioned); raw per-annotator data;
  κ and disagreement-adjudication report; `experiments/M3-*/`.
- **Validation:** κ ≥ the pre-set threshold on the audit subset; annotators verifiably
  blind; rubric ↔ automated-judge-instruction correspondence documented.
- **GO:** reliable native labels obtained → Milestone 4.
  **PIVOT:** κ too low after rubric revision → the "native ground truth" premise is
  weak; pivot toward a methods paper on *how* to obtain reliable low-resource CoT
  annotations, or narrow the claim.
  **STOP:** cannot recruit ≥2 independent qualified annotators → reassess scope with
  the user (a single researcher-annotator is not sufficient ground truth).

### Milestone 4 — Cross-lingual monitorability experiments (the four-monitor centerpiece)
- **Objective:** run the full four-monitor design across the ladder; estimate the
  monitor-validity gap (H2) and translation recovery (H3) with uncertainty intervals.
- **Prerequisites (BLOCKING):** U3 (judge models), U9 (translation system), U13 (power
  calculation reproduced); read arXiv:2603.20172 and the other §D papers in
  `CITATION_VERIFICATION.md`; Milestone 3 GO.
- **Outputs:** full generation + monitor + annotation dataset with provenance;
  `experiments/M4-*/`; `results/M4-*/` with per-language monitor-validity gap + recovery
  + CIs; H2/H3 confirmatory analysis.
- **Validation:** pre-registered analysis executed as written; McNemar + DeLong + GLMM
  run; effects reported with CIs regardless of direction.
- **GO:** monitor-validity gap measurable with acceptable precision → Milestone 5.
  **PIVOT (kill/pivot A):** a competitor publishes native low-resource monitorability
  validation + translate-then-monitor first → pivot to a different mitigation
  (in-language / ensemble) or a different low-resource language pair.
  **PIVOT (kill/pivot E):** translate-then-monitor mostly tracks translation quality →
  reframe the paper around measurement validity (still a result).
  **STOP:** gap cannot be estimated at all at this scale → report the negative/null
  methodological finding and stop expanding.

### Milestone 5 — Controls, ablations, statistics, robustness
- **Objective:** run the Phase 9 controls and Phase 9/10 ablations; base-accuracy
  control (H4); compliance mediation (H5); script triad; family/size scaling; prompt
  sensitivity; contamination checks; final statistics with FDR.
- **Prerequisites:** Milestone 4 GO; U7 (monitorability functional form), U14 (unit of
  analysis / random-effects structure).
- **Outputs:** complete control/ablation results with CIs and effect sizes;
  H4/H5 confirmatory analyses; a robustness appendix; `experiments/M5-*/`.
- **Validation:** conclusions survive the base-accuracy control; effects consistent
  across ≥2 model families; multiple-comparison correction applied.
- **GO / PIVOT decision:** explicit written GO / PIVOT / KILL against §19 criteria and
  the observed effect sizes. **GO** = the gap is real, measurable, and robust in some
  direction; **PIVOT (D)** = language effect vanishes under accuracy control → publish
  the null as a measurement-methodology corrective; **KILL** = design confounded beyond
  repair or contribution no longer novel.

### Milestone 6 — Paper / preprint preparation (only if scientifically justified)
- **Objective:** write up whatever the evidence supports — positive, negative, or a
  measurement-methodology corrective.
- **Prerequisites:** Milestone 5 GO or PIVOT-with-a-defensible-null; U16 (data-release
  plan).
- **Outputs:** `paper/` manuscript populated only with real numbers; data + code
  release; ethics + native-annotator-credit section.
- **Validation:** every number traces to a real run (`REPRODUCIBILITY.md` §8); no
  claim of submission/acceptance/affiliation beyond what is true; Related Work positions
  Onyame, Zhao, Yang, Persian-faithfulness, Turpin/Lanham/Chen/Emmons/Korbak explicitly.
- **GO:** contribution meets the threshold (`§21`). **STOP:** it does not → arXiv
  preprint + non-archival talk, or shelve, documented honestly.

## 19. Kill / pivot criteria (Phase H — from blueprint Phase 18, verbatim in substance)

| ID | Condition | How measured | Checkpoint | Consequence |
|---|---|---|---|---|
| **A** | A new paper does essentially this exact study (native low-resource monitorability validation + translate-then-monitor). | literature monitoring each milestone | M0 → M4 | Pivot to a different mitigation (in-language monitors / ensembles) or a different low-resource language pair. |
| **B** | The English baseline faithfulness effect will not reproduce. | Milestone 1 metrics vs. pre-registered band | M1 GO gate | Debug harness; if truly absent, pivot to a multilingual language-compliance / consistency study. |
| **C** | Models cannot reliably reason in Urdu (language compliance too low). | language-compliance metric in the Urdu pilot | M2 GO gate | Pivot to the compliance-as-oversight-bottleneck angle (builds on Qi et al.). |
| **D** | Language differences vanish after base-accuracy control. | H4 analysis; gap with vs. without accuracy covariate | M5 GO gate | Report the null as a corrective (still publishable); shift emphasis to measurement methodology. |
| **E** | The monitor-validity metric mostly measures translation quality. | translation-quality control (Phase 9); M4 vs. M3 patterns; human-translated control subset | M4 → M5 | "That is the finding" — reframe the paper around measurement validity. |
| **quant. trigger** | native-vs-automated gap < 10 points | four-monitor results | M4 | pivot to mitigation / compliance framing (kill D/E). |

The project **must not be optimized to obtain a positive result.** Negative and null
findings are preserved and reported with equal prominence (`CLAUDE.md` §2.4).

## 20. Reproducibility requirements

See `REPRODUCIBILITY.md`. Minimum provenance bar per experiment: `CLAUDE.md` §2.7. No
result without a linked provenance record.

## 21. Publication objective (no acceptance implied)

Realistic target: a *CL **Findings** paper (ACL/EMNLP/NAACL/EACL) or a workshop with
proceedings (LoResLM, BlackboxNLP, TrustNLP, a NeurIPS/ICLR safety/SoLaR workshop).
Stretch: a main-conference short paper or FAccT. Fallback: arXiv preprint + non-archival
talk. Contribution threshold: **workshop = one clean native-validated result;
Findings = full ladder + mitigation.** A well-characterized null (kill/pivot D or E) is
a legitimate submission. `TODO — UNVERIFIED`: exact venue deadlines — confirm each cycle.

## 22. Faculty-review objective (no supervision claimed)

The project is built to be defensible under faculty review: milestone-gated,
pre-registered where possible, full provenance, negative results intact. The Run-2
blueprint's faculty ranking (Depeng Xu #1, UNC Charlotte TAIMing AI) and outreach email
are recorded **only** in `RUN2_BLUEPRINT_HANDOFF.md` §22 as blueprint content. No one has
agreed to supervise. The outreach email describes pilot evidence that does not yet exist
and may not be sent before Milestone 2. `TODO — confirm` (U-faculty): independent
verification of Bunescu/Fan/Zadrozny/Shaikh characterizations before any use.

## 23. Harvard alignment

Research-alignment note only (`RUN2_BLUEPRINT_HANDOFF.md` §23): Lakkaraju's group works
on CoT faithfulness/monitorability. **No admissions claim, likelihood, or implication
anywhere in the repository** (`CLAUDE.md` §5).

## 24. Known novelty risks

- The broad "monitors fail across languages" framing is occupied (Onyame HIGH, Zhao
  MEDIUM–HIGH) — stay on measurement validity + mitigation.
- Yang et al. 2025 already names the "monitorable vs. monitored-correctly" gap in
  English (MEDIUM) — cite, do not claim origination.
- Persian CoT-faithfulness native validation exists (MEDIUM) — not for monitorability,
  Urdu, or translation recovery; a follow-up from that group is a standing threat
  (kill/pivot A).
- Newer un-cited 2026 work, esp. arXiv:2603.20172 (judge/classifier sensitivity in CoT
  eval) — read before Milestone 4.
- Urdu inclusion alone is never novelty.
- Single-language scope reads as narrow — lead with the method, not the language.

## 25. Confounds to control

base-model accuracy / task difficulty; language resource level; tokenizer fertility;
script (RTL / Perso-Arabic vs. Devanagari vs. Latin); translation quality &
translation-introduced artifacts; model multilingual competence / language compliance;
prompt-template formatting; option-letter (positional) bias × RTL; CoT / response length;
dataset contamination / memorization; semantic & answer equivalence across languages;
monitor/judge in-language competence; cultural adaptation of bias items; model-family
effects; multiple comparisons; researcher-as-annotator bias; power / sample size.
Control methods: `experiments/EXPERIMENT_SPEC.md` §9.

## 26. Ablations

monitor type (4) · cue type (3) · model family (3) · model size (7B/14B/32B) · prompt
template (≥3) · with/without base-accuracy restriction · in-language vs. translated vs.
English judge · hint protocol vs. Zhao truncation protocol · seeds (≥5). Purpose of each:
`experiments/EXPERIMENT_SPEC.md` §10.

## 27. Compute plan

Three tiers (blueprint Phase 13) — **estimates, not verified costs**:
Tier A (free, Colab T4): English baseline + Urdu pilot, "tens" of GPU-hours, $0.
Tier B (Colab Pro / rented A100, ~$1–2/hr): full ladder × 7B/14B × 5 seeds, ~100–300
GPU-hours, ~$150–600. Tier C (university lab GPUs): 32B + full replication, ~500–1000
GPU-hours. Milestones 1–3 fit Tier A/B; Milestones 4–5 likely need Tier C.

## 28. Open questions / unresolved decisions

Full list with blocking classification: `RUN2_BLUEPRINT_HANDOFF.md` §27 (U1–U17).

**BLOCKING for Milestone 1:** U5 (Turpin vs. Chen as primary target + exact
protocol/metric), U6 (Milestone-1 dataset), U10 (decoding config + seed list), U12
(quantitative success band).
**BLOCKING for Milestone 3:** U8 (annotator count/blinding/κ), U15 (ethics/consent).
**BLOCKING for Milestone 4:** U3 (judge models), U9 (translation system + its native
validation), U13 (reproduce the power calculation).
**Important, not blocking:** U1/U2 (ladder slots), U4 (model revisions), U7
(monitorability functional form), U11 (cue taxonomy), U14 (unit of analysis), U17
(safety set), faculty characterizations.
**Non-blocking:** U16 (data-release plan), venue deadlines, Harvard note.

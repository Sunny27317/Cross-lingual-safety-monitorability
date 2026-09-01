# Research Decision Log

Append-only record of major scientific decisions. Each entry: date, decision, rationale,
evidence, status, and what would reverse it. Newest at the bottom.

Do not edit past entries except to change `Status:` or add a dated addendum. Decisions
are reversed by a **new** entry, not by deleting an old one.

> **Path note:** the Run-2 Phase-G instruction places this file at
> `literature/DECISION_LOG.md`; a later instruction mentioned `experiments/DECISION_LOG.md`.
> It lives here because these decisions are literature-/novelty-/scope-driven. If the
> user prefers `experiments/`, move it — do not fork it.

---

## D-001 — Reject the broad "do safety monitors fail across languages?" question as a standalone contribution
- **Date:** 2026-09-01 (recorded during Run-2 integration; decision originates in Run-2)
- **Decision:** The project will **not** contribute "monitorability degrades in
  lower-resource languages." That framing is treated as settled prior work.
- **Rationale:** Onyame et al. (arXiv:2605.27901) already report a 95.9% average
  CoT-unfaithfulness rate across 8B–120B models and "100% in low-resource languages"
  across 13 languages and 16 models; Zhao et al. (Findings EACL 2026, arXiv:2510.09555)
  independently measured multilingual CoT faithfulness/consistency/compliance. A generic
  "we added Urdu" study is RED against these.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §2; `CITATION_VERIFICATION.md` §A.1–A.2
  (both VERIFIED, incl. direct confirmation that Onyame used no native validation and
  omitted Urdu); `COMPETITOR_MATRIX.md` #1–#2.
- **Status:** ACTIVE.
- **Reversal condition:** a retraction or major correction of Onyame et al. and Zhao et
  al. that reopens the broad question (not expected).

## D-002 — Reframe to a measurement-validity contribution
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** The contribution is: *when an automated CoT monitor appears to fail on
  Urdu reasoning traces, determine — with native Urdu ground truth — whether the
  reasoning is genuinely unfaithful (A) or the monitor itself is failing (B); and test
  whether translating the trace to English before monitoring recovers the signal.*
- **Rationale:** Onyame's "100% low-resource deception" rests entirely on an
  English-centric automated judge whose low-resource competence was never validated. If
  the *judge* is what fails, the headline claim is partly a measurement artifact. That
  question is open and is where native Urdu competence is a genuine methodological asset.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §1, §4; `CITATION_VERIFICATION.md` §A.1
  (no native validation; no translate-then-monitor — both VERIFIED against the primary
  source).
- **Status:** ACTIVE.
- **Reversal condition:** kill/pivot criteria D or E (see `RESEARCH_PLAN.md`).

## D-003 — Urdu is the target language for reasons of method, not novelty
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** Urdu is the low-resource target **because** native-speaker validation is
  feasible for this project (the researcher is a native speaker; ≥1 further native
  annotator is planned) and because Urdu is absent from Onyame's 13 languages. The
  repository must never state or imply that including Urdu is itself the novel
  contribution.
- **Rationale:** Novelty comes from the native-validated measurement-validity method +
  translate-then-monitor, which are language-general; Urdu is the instance where we can
  actually obtain trustworthy ground truth.
- **Evidence:** `CLAUDE.md` §2.6, §5; `RUN2_BLUEPRINT_HANDOFF.md` §2.2(d)
  (Urdu absence VERIFIED); `COMPETITOR_MATRIX.md` novelty-audit conclusion.
- **Status:** ACTIVE.

## D-004 — Test translate-then-monitor as a mitigation, not assume it works
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** Translate-then-monitor (Urdu CoT → English → same automated monitor) is
  a **hypothesis to be tested** (H3), one of four monitor conditions. The repository must
  not present it as a solution. Possible outcomes and their meanings are enumerated in
  `RUN2_BLUEPRINT_HANDOFF.md` §14.
- **Rationale:** It is cheap and deployable if it works; if it fails, that localizes the
  signal loss to generation rather than monitoring; if it *damages* detection, that is a
  translation-artifact finding (kill/pivot E). All three are informative.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §12, §14; `CITATION_VERIFICATION.md` §A.1
  (competitors did not test this — VERIFIED).
- **Status:** ACTIVE.

## D-005 — Separate "monitor/judge failure" from "model unfaithfulness" as a first-class design goal
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** The four-monitor design (automated-English / automated-in-language /
  native-human / translate-then-English) exists specifically to make (A) and (B)
  separable. The native-human monitor is the language-independent ground truth against
  which the automated monitors are scored (McNemar on identical traces).
- **Rationale:** "Does the monitor succeed?" alone cannot tell you *why* it failed. Only
  a ground-truth label that does not depend on the automated judge can. Native readers
  supply that label.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §12; `RESEARCH_PLAN.md` (A-vs-B section);
  Yang et al. arXiv:2511.08525 already names the "monitorable vs. monitored-correctly"
  gap in English (`COMPETITOR_MATRIX.md` #10) — we cite, not claim, that distinction.
- **Status:** ACTIVE.

## D-006 — Milestone 1 reproduces an English hint-faithfulness baseline before any cross-lingual work
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** First experiment = reproduce the Turpin/Chen English hint-faithfulness
  signature (answer-switching with disclosure well below switching) on
  DeepSeek-R1-Distill-Qwen-7B, ~50 items, free compute. No Urdu, no monitors-comparison
  until this reproduces.
- **Rationale:** If the base effect does not reproduce in our harness, every downstream
  cross-lingual comparison is uninterpretable (kill/pivot B). Also matches Onyame's
  setup for later direct comparison.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §11, §25; `RESEARCH_PLAN.md` milestone table.
- **Open sub-decisions:** U5 (Turpin vs. Chen as primary target), U6 (dataset), U10
  (decoding config), U12 (success band) — all BLOCKING for Milestone 1, all listed in
  `RUN2_BLUEPRINT_HANDOFF.md` §27.
- **Status:** ACTIVE; sub-decisions PENDING.

## D-007 — YELLOW verdict re-affirmed after independent verification
- **Date:** 2026-09-01
- **Decision:** After independently verifying all 12 competitor/foundational citations
  and directly checking the Onyame primary source, the YELLOW verdict stands: proceed
  only with the narrowed measurement-validity + mitigation contribution.
- **Rationale:** The three surviving-gap claims are VERIFIED, not merely asserted by the
  blueprint: Onyame used no native validation, did not test translate-then-monitor, and
  omitted Urdu. No verified 2026 paper occupies the specific open intersection.
- **Evidence:** `CITATION_VERIFICATION.md` §E; `COMPETITOR_MATRIX.md` novelty-audit
  conclusion.
- **Caveats carried forward:** (i) newer un-cited 2026 work, esp. arXiv:2603.20172
  (judge/classifier sensitivity in CoT eval) — must be read before Milestone 4;
  (ii) the Onyame and Persian-faithfulness groups could pre-empt via a follow-up
  (kill/pivot A); (iii) Yang et al. (arXiv:2511.08525) already owns the English
  "monitorable vs. monitored-correctly" framing.
- **Status:** ACTIVE.

## D-008 — Repository directory layout: keep Milestone-0 layout, add blueprint's extras as needed
- **Date:** 2026-09-01
- **Decision:** Do not restructure the repo to match the blueprint's `xling-monitor/`
  tree wholesale. Keep the existing top-level dirs (`configs/ data/ src/ tests/
  experiments/ results/ figures/ literature/ paper/`). Add `src/` subpackages
  (`generation/`, `hint_injection/`, `monitors/`, `translation/`, `evaluation/`,
  `statistics/`) and a `models/` config area **when Milestone 1/2 needs them**, not now.
- **Rationale:** Minimize churn; the blueprint's `evaluation/` and `statistics/` become
  `src/evaluation/` and `src/statistics/`; `notebooks/` is optional and gitignore-heavy.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §19; `REPRODUCIBILITY.md` "Directory layout".
- **Status:** ACTIVE.

## D-009 — No faculty, Harvard, or publication claims enter the repo without independent confirmation
- **Date:** 2026-09-01
- **Decision:** The blueprint's faculty ranking, the Xu outreach email, and the Harvard
  alignment note are recorded in `RUN2_BLUEPRINT_HANDOFF.md` **as blueprint content
  only**. No derived document asserts supervision, admission likelihood, or institutional
  affiliation. The outreach email may not be sent until the pilot evidence it describes
  actually exists.
- **Rationale:** `CLAUDE.md` §5; research integrity.
- **Evidence:** `CITATION_VERIFICATION.md` §B (only Xu's paper and TAIMing-AI membership
  verified; Bunescu/Fan/Zadrozny/Shaikh characterizations UNVERIFIED).
- **Status:** ACTIVE.

## D-010 — U5: Milestone-1 reproduction protocol
- **Date:** 2026-09-01
- **Decision (proposed):** Milestone 1 reproduces the **Turpin/Chen paired-prompt
  hidden-influence paradigm** — English only, one model (DeepSeek-R1-Distill-Qwen-7B),
  one neutral "suggested wrong answer" hint, using **Chen et al.'s faithfulness score**
  `E[1[c_h verbalizes h] | a_u ≠ h, a_h = h]`. Control = item, no hint; treatment =
  identical item + hint → a wrong option. One automated disclosure classifier (not the
  four-monitor design). No language variable, no translate-then-monitor.
- **Rationale:** validate the measurement instrument before adding language; match the
  paradigm every competitor uses; Young 2026 (arXiv:2603.26410) is a near-replication on
  open-weight models and gives a concrete comparison point.
- **Evidence:** `experiments/MILESTONE_1_READINESS.md` §3–§4, §8; arXiv:2505.05410 HTML;
  arXiv:2305.04388; arXiv:2603.26410.
- **Alternatives rejected:** Onyame-style monitoring (that is M4); Lanham perturbation;
  Xiong/Lakkaraju counterfactual drafts; any hybrid — all in `MILESTONE_1_READINESS.md`
  §8.
- **Status:** **APPROVED (user, 2026-09-01).** English-only reproduction confirmed as the
  Milestone-1 target; explicitly *not* the final contribution.
- **Would change it:** user prefers a different paradigm; or the hint paradigm proves
  ill-posed for this model class in the pilot.

## D-011 — U6: Milestone-1 baseline dataset
- **Date:** 2026-09-01
- **Decision (proposed):** **MMLU** (`cais/mmlu`, config `all`, split `test`), 4-way MCQ.
  **PILOT / PIPELINE-VALIDATION n = 50** (5 items × 10 subjects, deterministic
  sorted-hash selection). **CONFIRMATORY n ≈ 400–600** — exact n `TODO — DECISION
  REQUIRED` from a power calculation at confirmatory-design time (not guessed now).
  GPQA-Diamond as a pre-registered confirmatory secondary (contamination check).
- **Rationale:** exactly Chen's dataset and one of Young 2026's; MIT-licensed, ungated;
  higher model accuracy than GPQA ⇒ more usable items at pilot scale.
- **Key tradeoff (needs user ruling):** MMLU is contaminated for 2025–26 models. The
  disclosure gap has no established contamination-inflation mechanism, and Chen/Young use
  MMLU for the same purpose — but the user may prefer **GPQA-Diamond as primary** for
  lower contamination at the cost of a thinner sample.
- **Evidence:** `experiments/MILESTONE_1_READINESS.md` §5, §8 (alternatives table),
  §9.1; arXiv:2505.05410; arXiv:2603.26410.
- **Status:** **APPROVED (user, 2026-09-01): MMLU PRIMARY, GPQA-Diamond SECONDARY.**
  n = 50 is PIPELINE VALIDATION ONLY and must never be reported/cited as a confirmatory
  experiment. Confirmatory n is **not frozen** — it requires a documented
  power/sample-size justification first. MMLU results are not evidence of the final
  cross-lingual contribution.
- **Open:** MMLU dataset-card licence confirmation (metadata only).
- **Would change it:** MMLU pilot yields too few model-correct items for a switch
  analysis ⇒ promote GPQA-Diamond.

## D-012 — U10: decoding configuration and seeds
- **Date:** 2026-09-01
- **Decision (proposed):** `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` @ revision
  `916b56a44061fd5cd7d6a8fb632557ed4f724f60`; vLLM (pinned); **temperature 0.6, top_p
  0.95** (model-card recommended), no system prompt, forced leading `<think>\n`,
  `max_new_tokens = 16384` (raise to 32768 if truncation > 5%), no repetition penalty,
  stochastic (greedy explicitly avoided); answer via `\boxed{}` + fallback regex;
  **k = 10 samples** per (item, condition), seeds `0–9`. Disclosure-classifier judge
  model `TODO — DECISION REQUIRED` (overlaps U3); proposal `Qwen3-32B` @ temp 0.
- **Rationale:** the model card forbids greedy/temp-0 for the distills, so **Chen's
  "temperature 0" is deliberately not adopted** — we recover a stable per-item rate via
  k samples. Every parameter is tagged SOURCE-REPORTED / MODEL-DOCUMENTATION-RECOMMENDED
  / PROJECT DESIGN DECISION / NOT REPORTED BY SOURCE in `MILESTONE_1_READINESS.md` §6.
- **Evidence:** HF model card + HF API (fetched 2026-09-01); arXiv:2505.05410 HTML
  ("we sample with temperature 0"); `MILESTONE_1_READINESS.md` §6, §8.
- **Not reported by source:** Chen's top_p, k, exact question counts; Chen released no
  code (checked).
- **Status:** **GENERATION PARAMETERS APPROVED (user, 2026-09-01)** — temp 0.6 / top_p
  0.95 / no system prompt / forced `<think>\n` / max_new_tokens 16384 / no rep-penalty /
  stochastic / `\boxed{}` extraction / k = 10 / seeds 0–9. Env pins expanded to Python +
  vLLM + PyTorch + transformers + CUDA + GPU + OS; **no perfect-determinism claim**,
  known nondeterminism documented.
- **CONDITIONAL:** the **disclosure-classifier model is NOT locked.** `Qwen3-32B` is a
  candidate only; before implementation run the §7a verification checklist
  (`MILESTONE_1_READINESS.md`): exact model/version, license, hardware/context/inference
  feasibility, deterministic config, a smaller-open-weight alternative, and the
  circularity risk of using an LLM judge to study LLM-judge failure. Human validation is
  mandatory; the classifier is audited against blinded human annotation and is never
  ground truth. This is the (A)-vs-(B) separation in miniature.
- **Would change it:** DeepSeek updates its guidance; truncation rate high; per-item
  rate variance at k=10 too large; §7a rules the candidate judge out.

## D-013 — U12: Milestone-1 reproduction success criterion
- **Date:** 2026-09-01
- **Decision:** **Structure APPROVED (user, 2026-09-01); numeric gates reclassified and
  de-frozen.** Primary success evidence = (i) pipeline correctness, (ii) expected effect
  **direction**, (iii) **uncertainty / confidence intervals**, (iv) appropriate
  **statistical evidence**, (v) **comparison to prior-work effect ranges** — *not*
  hitting a convenient number. Every remaining threshold is tagged PRIOR-WORK DERIVED /
  STANDARD-METHODOLOGY DERIVED / ENGINEERING QUALITY GATE / PROJECT DESIGN DECISION in
  `MILESTONE_1_READINESS.md` §7.
- **Changes from the proposed version:**
  - The absolute disclosure band `[10%, 60%]` and `hidden-influence ≥ 15%` were PROJECT
    DESIGN DECISIONs presented as prior-work-derived → **removed as gates**; the numbers
    survive only as *context* (prior-work range: Turpin ≤36% acc-drop; Chen ~25–39%
    faithfulness, wide by hint/dataset; Young 55.4% divergence).
  - `extraction ≥ 95%` and hint-injection `100%/0%` → explicitly **ENGINEERING QUALITY
    GATES**; the scientific requirement behind extraction is that parse failure is
    **non-differential** and unparseables are reported not dropped.
  - Disclosure-classifier agreement → target "substantial" κ, floor "moderate"
    (Landis & Koch bands — a STANDARD-METHODOLOGY convention, reported **with a CI**);
    residual classifier error propagated into disclosure-rate CIs.
  - **Pilot (n = 50) ≠ hypothesis test:** pilot PASS = pipeline correct + point
    estimates in the phenomenon's direction + CIs reported (CIs may include 0 at n = 50).
    Statistical significance / CI-excludes-0 is a **confirmatory-stage** criterion.
- **Rationale:** user directive — do not disguise project design decisions as
  literature-derived; emphasize direction + uncertainty + statistical evidence +
  prior-range comparison.
- **Evidence:** `experiments/MILESTONE_1_READINESS.md` §7 (threshold register), §7a;
  arXiv:2505.05410; arXiv:2603.26410; Landis & Koch 1977.
- **Status:** **APPROVED IN STRUCTURE.** The §7 criterion becomes the pre-registration
  and must be committed *before* any run (git history proves ordering). Numeric gates may
  still be refined *before* the run with a dated addendum here; **never** after seeing
  results.

## D-014 — Novelty re-check after Milestone-1 literature scan (framing sharpened)
- **Date:** 2026-09-01
- **Decision:** The YELLOW verdict and the surviving contribution **stand**, but the
  framing is sharpened: "automated monitors / LLM-judges fail in low-resource languages"
  is now well-established for **both** CoT monitors (Onyame 2026) **and** LLM-as-judge
  generally (arXiv:2607.02235, 2605.28710, 2607.14480, 2505.12201, 2025–26). The
  project's defensible wedge is specifically: (i) **native-human-validated** CoT
  *monitorability* (not general judge reliability), (ii) **translate-then-monitor** as a
  recovery method, (iii) explicit **model-unfaithfulness (A) vs. monitor-failure (B)**
  separation. Newer hint-faithfulness work on open-weight models (arXiv:2603.26410,
  2601.07663) corroborates the Milestone-1 paradigm and is not a threat.
- **Rationale:** research integrity — the motivation is more crowded than the Run-2
  blueprint implied; the contribution must not rest on the general "judges fail in
  low-resource languages" point.
- **Evidence:** `CITATION_VERIFICATION.md` §D (updated 2026-09-01);
  `experiments/MILESTONE_1_READINESS.md` Phase-4 result.
- **Status:** ACTIVE. **Explicitly acknowledged by the user on 2026-09-01.** Canonical
  novelty statement recorded in D-015.
- **Would escalate to STOP:** discovery of a paper doing native-validated low-resource
  CoT *monitorability* + translate-then-monitor (kill/pivot A).

## D-015 — Canonical novelty statement (user-approved)
- **Date:** 2026-09-01
- **Decision:** The project claims **no** novelty from (a) "LLM monitors/judges perform
  worse in low-resource languages" — substantial prior work (Onyame 2026 for CoT
  monitors; arXiv:2607.02235 / 2605.28710 / 2607.14480 / 2505.12201 for LLM-as-judge) —
  or (b) the inclusion of Urdu. The contribution is the **surviving intersection**:
  1. native-human-validated low-resource CoT **monitorability** (not general judge
     reliability);
  2. **translate-then-monitor** as a measurable mitigation / recovery mechanism;
  3. explicit separation of **A = reasoning/model unfaithfulness** from **B =
     monitor/judge failure**;
  4. carefully controlled **cross-lingual measurement validity** (language ladder,
     base-accuracy control, script/resource confound separation);
  5. **Urdu as a native-validated test environment**, not as the novelty claim.
- **Rationale:** user directive (approval message §5); research integrity — the framing
  in the Run-2 blueprint over-weighted the "monitors fail across languages" motivation.
- **Evidence:** `experiments/MILESTONE_1_READINESS.md` §19a; `CITATION_VERIFICATION.md`
  §D.2; `COMPETITOR_MATRIX.md`.
- **Status:** ACTIVE. Supersedes the framing emphasis in `RESEARCH_PLAN.md` §5 (which is
  updated to point here).
- **Would change it:** kill/pivot A (a paper occupying the intersection) — flag
  immediately, do not force the project forward.

## D-016 — Hint-prompt wording: freeze-before-confirmatory policy (user-approved)
- **Date:** 2026-09-01
- **Decision:** Milestone 1 uses the closest defensible **Chen-style neutral baseline**
  hint wording. The model is **not** told the input may be unusual, manipulated,
  adversarial, monitored, or deceptive (Walden & Wanner 2026, arXiv:2601.07663, show
  such alerts materially move faithfulness metrics; we want Chen's baseline). The **exact
  prompt text is written into `configs/cue/…`, version-tagged, and hashed into
  provenance before the confirmatory run.** It is not tuned after observing results.
  Wording variants investigated later are **explicitly labelled ablations**.
- **Rationale:** user directive (approval message §3); prevents post-hoc effect inflation
  and preserves comparability with Chen's baseline setting.
- **Evidence:** `experiments/MILESTONE_1_READINESS.md` §3 (wording policy), §4;
  arXiv:2505.05410; arXiv:2601.07663.
- **Status:** ACTIVE. The concrete text is authored at scaffold time (next branch), not
  in this readiness PR.
- **Would change it:** only pre-run, with a dated addendum; never post-hoc.

## D-017 — Hint-target selection: position-neutral deterministic hash (not a fixed offset)
- **Date:** 2026-09-01 (Milestone-1 scaffold correction pass)
- **Decision:** The wrong option a hint points to is chosen by a **position-neutral
  deterministic hash**, not a fixed offset from the correct index. Algorithm (frozen,
  `clsm/interventions.py`, `cue.target_rule = "hash_over_incorrect_indices"`):
  1. `incorrect = [i for i in (0,1,2,3) if i != answer_idx]` (ascending).
  2. `key = f"{experiment_id}|{item_id}|{cue_version}|{hint_seed}"`.
  3. `digest = sha256(key.encode())`; `n = int.from_bytes(digest[:8], "big")`.
  4. `target_idx = incorrect[n % 3]`; guard `target_idx != answer_idx`.
  `hint_seed` is an experiment-level config value (`pilot.yaml`, frozen `20260901`).
- **Supersedes:** the initial scaffold's `(correct + 1) mod 4` rule (`cue.target_offset`),
  which was systematically position-biased (always the option after the correct one).
- **Rationale (user directive, correction requirement 1):** deterministic + reproducible
  from config, never the correct option, seed-sensitive, and **not** systematically a
  fixed offset — the three wrong positions are selected ~uniformly across items. No RNG.
- **Provenance:** `HintSpec` records `target_idx`, `hint_seed`, and
  `selection_key_sha256`; the manifest records `cue_target_rule` + `hint_seed`.
- **Evidence:** `clsm/interventions.py` docstring; `experiments/M1-English-Baseline/README.md`
  §4 (hint-target selection); `tests/test_interventions.py` (every wrong position
  reachable; correct never selected; deterministic; seed-sensitive; not `(correct+1)%4`;
  ~uniform distribution).
- **Status:** ACTIVE. `hint_seed` is frozen before any run; changing it is a new
  experiment (new `experiment_id`) with a dated addendum here — never an in-place edit
  after seeing results.

## D-018 — Milestone-1 metric denominators made explicit; zero-denominator is UNDEFINED
- **Date:** 2026-09-01 (correction pass)
- **Decision:** Every Milestone-1 metric documents its exact population/denominator
  (`clsm/metrics.py` module docstring; `M1-English-Baseline/README.md` §8; `MetricsResult`
  docstring). Unit of analysis = the item (majority vote over the k samples). Chen-style
  `answer_switch_rate` / `disclosure_rate` / `hidden_influence_rate` are conditioned on
  the **switch-eligible** set `{a_u == correct AND hint_target != correct}` (stricter than
  Chen's `{a_u ≠ h}` — a readiness §5 choice); `control_adoption_rate` / `adoption_increase`
  are over **all** items (the eligible set makes control ≈ 0 by construction).
  **A zero denominator returns an explicit UNDEFINED `Estimate` (`n = 0`, NaN,
  `defined == False`) and a note — never a silent 0.** Unpaired control/treatment for an
  item raises `UnpairedConditionsError`.
- **Rationale (user directive, correction requirement 3).**
- **Evidence:** `tests/test_metrics.py` (16 cases incl. zero-denominator → NA,
  switch-elsewhere, disclosure present/absent, multiple seeds, unpaired → raise).
- **Status:** ACTIVE.

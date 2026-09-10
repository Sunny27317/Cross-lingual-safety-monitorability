# POWER_ANALYSIS.md — Track-A sample-size **sensitivity / design exploration**

> **PRE-OUTCOME REVIEW AMENDMENT (2026-09-10, DECISION_LOG D-058/D-063).**
> No Track-A scientific outcome had been or has been observed when this was amended.
> **This document does NOT recommend a confirmatory sample size and does NOT freeze a
> smallest effect size of interest (SESOI).** It is a *sensitivity illustration*: it
> shows how the required N moves with the assumed effect size and the assumed
> intra-item correlation (ICC). The confirmatory design — **SESOI / target effect,
> N, ICC, and the estimand it is powered for — REQUIRES A HUMAN SCIENTIFIC DECISION
> BEFORE CONFIRMATORY DESIGN.** The pilot may inform *nuisance* parameters
> (eligibility yield, parse-failure rate, missingness, descriptive switch yield) but
> must not be used to choose a favourable SESOI after seeing effects.
>
> - Previous wording: "confirmatory n ≈ 300–600 (deferred) … Recommended confirmatory
>   range: n ≈ 300–600, central 400"; SESOI = 15 %.
> - Corrected wording: **no recommended range; SESOI = REQUIRES HUMAN SCIENTIFIC
>   DECISION.**

**Prospective. Uses ONLY synthetic assumptions and prior-literature effect ranges. No
observed Track-A outcome is used — none exist.** Decision: `DECISION_LOG.md`
D-045 / D-058 / D-063.
Simulation: `experiments/M1-Mac-Feasibility/analysis/track_a_power_sim.py`
(seed `20260910`); full grid: `…/track_a_power_sim_output.txt`.

**Notation.** β = probability of a Type-II error; **power = 1 − β**. "power" in the
tables below is the simulated P(bootstrap CI lower bound > 0) under the stated
synthetic effect — a *design-exploration* quantity, not a claim about any real effect.

**Two different "bootstrap" counts (D-063).** `BOOT` in the simulation script is the
number of inner resamples used *inside each simulated confirmatory dataset* to form
that dataset's CI — a design-exploration knob, kept modest for run time.
`ExperimentConfig.bootstrap_n = 10000` is a *different* quantity: the item-clustered
percentile bootstrap applied once to the **real pilot data** for descriptive CIs. They
are unrelated.

---

## 1. What each stage is *for*

| stage | n | purpose | is it a hypothesis test? |
|---|---|---|---|
| **A. pipeline validation** | 50 | prove the harness computes what it claims; expose bugs; show the qualitative direction | **no** |
| **B. Track-A scientific pilot** | (= A here) | " " + a first, wide, descriptive estimate | **no** |
| **C. confirmatory** | **deferred — REQUIRES HUMAN SCIENTIFIC DECISION** | CI of the effect excludes 0 at a human-chosen SESOI | yes |

The Track-A **pilot IS stage A/B** — n = 50, pipeline validation + qualitative
direction. It is **underpowered by design** and its CIs are expected to be wide and to
include 0. That does **not** fail the pilot (`MILESTONE_1_READINESS.md` §7 Layer 2).

## 2. Model

- **Unit:** the item (generations within an item are correlated → item-clustered
  bootstrap; resampling unit = the item).
- **Estimands modelled:** `adoption_increase` (paired per-item, ≈ switch rate on the
  eligible set with a neutral hint) and `hidden_influence_rate`
  (= `switch × (1 − disclosure)` in expectation, over eligible items).
- **Assumptions (synthetic):** per-item switch probability ~ Beta with intra-item
  correlation **ICC = 0.10** — this is an **assumption, not a measured fact** (audit M8);
  the doc runs a sensitivity band over **ICC ∈ {0.0, 0.05, 0.10, 0.20}** (§3, ICC row).
  Majority vote over `k = 8`, minus per-generation parse-failure attrition; eligibility
  (`a_u == correct AND h != correct`) central **0.55** (sensitivity 0.40 / 0.55 / 0.70);
  parse-failure central **0.03** (sensitivity 0.00 / 0.03 / 0.10); control adoption
  ≈ 0.01 (neutral hint).
- **Effect ranges (prior-literature anchors, all VERIFIED in
  `literature/CITATION_VERIFICATION.md`):** Turpin — up to 36 % accuracy drop; Chen —
  CoT-faithfulness ~25 % (Claude 3.7) / ~39 % (DeepSeek-R1), "reveal rates often below
  20 %", lower on GPQA; Young 2026 (arXiv:2603.26410) — 55.4 % thinking-vs-answer divergence. The **locked
  model is 1.7B** — effects are **uncertain and may be smaller**, so we report a grid.
  Grid: `switch ∈ {0.05, 0.10, 0.20, 0.35}`, `disclosure ∈ {0.20, 0.40, 0.60}`.

## 3. Results (2000 sim reps/cell, `BOOT` inner resamples/rep — see header)

`hw` = mean 95 % bootstrap CI half-width; `power` = simulated P(CI lower bound > 0)
under the stated **synthetic** effect (= 1 − β for that synthetic scenario). These are
design-exploration numbers, not results.

Cells are `hw / power`, where `hw` = mean 95 % bootstrap CI half-width and
`power` = 1 − β = simulated P(CI lower bound > 0) under the stated **synthetic** effect.
No cell is a target.

### `adoption_increase` (≈ switch rate on eligible items) — synthetic

| n | s=0.05 | s=0.10 | s=0.20 | s=0.35 |
|---|---|---|---|---|
| 50 | 0.019 / 0.00 | 0.032 / 0.00 | 0.073 / 0.05 | 0.144 / 0.67 |
| 100 | 0.020 / 0.00 | 0.029 / 0.00 | 0.059 / 0.19 | 0.104 / 0.95 |
| 200 | 0.017 / 0.00 | 0.025 / 0.02 | 0.044 / 0.46 | 0.075 / 1.00 |
| 400 | 0.014 / 0.00 | 0.019 / 0.04 | 0.032 / 0.76 | 0.053 / 1.00 |
| 600 | 0.012 / 0.00 | 0.016 / 0.05 | 0.026 / 0.91 | 0.043 / 1.00 |

### `hidden_influence_rate` = `switch × (1 − disclosure)` — synthetic, disclosure = 0.40

| n | s=0.05 (h≈0.03) | s=0.10 (h≈0.06) | s=0.20 (h≈0.12) | s=0.35 (h≈0.21) |
|---|---|---|---|---|
| 50 | 0.003 / 0.00 | 0.010 / 0.00 | 0.043 / 0.01 | 0.108 / 0.40 |
| 100 | 0.003 / 0.00 | 0.011 / 0.00 | 0.037 / 0.11 | 0.080 / 0.87 |
| 200 | 0.003 / 0.00 | 0.010 / 0.01 | 0.030 / 0.47 | 0.058 / 1.00 |
| 400 | 0.003 / 0.00 | 0.009 / 0.08 | 0.022 / 0.91 | 0.042 / 1.00 |
| 600 | 0.003 / 0.01 | 0.008 / 0.22 | 0.018 / 0.99 | 0.034 / 1.00 |

(disclosure 0.20 shifts power up ~1 n-tier; disclosure 0.60 shifts it down ~1 tier —
full table in the sim output.)

### Sensitivities — `power` (= 1 − β) for `hidden_influence`, s = 0.20, d = 0.40

| n | elig 0.40 | elig 0.55 | elig 0.70 | | pf 0.00 | pf 0.03 | pf 0.10 |
|---|---|---|---|---|---|---|---|
| 50 | 0.00 | 0.01 | 0.03 | | 0.01 | 0.01 | 0.02 |
| 200 | 0.24 | 0.47 | 0.64 | | 0.36 | 0.48 | 0.57 |
| 400 | 0.75 | 0.93 | 0.98 | | 0.86 | 0.91 | 0.96 |
| 600 | 0.95 | 0.99 | 1.00 | | 0.98 | 0.99 | 0.99 |

### Sensitivity to the **assumed** intra-item correlation ICC (audit M8)

ICC = 0.10 is an **assumption, not a measured fact**. `power` (= 1 − β) for
`hidden_influence`, s = 0.20, d = 0.40:

| n | ICC 0.00 | ICC 0.05 | ICC 0.10 | ICC 0.20 |
|---|---|---|---|---|
| 50 | 0.00 | 0.00 | 0.01 | 0.07 |
| 100 | 0.00 | 0.03 | 0.10 | 0.33 |
| 200 | 0.02 | 0.18 | 0.46 | 0.83 |
| 400 | 0.12 | 0.66 | 0.91 | 1.00 |
| 600 | 0.34 | 0.90 | 0.99 | 1.00 |

The ICC dominates the CI half-width for the switch-outcome estimands: at ICC = 0 the
required N is roughly half of what the ICC = 0.10 row implies; at ICC = 0.20 it is
larger again. **This is exactly why the confirmatory N cannot be frozen here** — it
depends on a quantity the pilot has not measured.

## 4. What the grid shows (NOT a recommendation)

1. **n = 50 pilot: power ≈ 0.00–0.07** to exclude 0 for any effect smaller than a very
   large one (`switch ≥ 0.35`), across the assumed-ICC band. It **cannot** test the
   central hypotheses. It **can** validate the pipeline and produce descriptive
   point-estimates and nuisance rates. **This is the intended design.**
2. **Illustrative only — how N scales with the assumed synthetic effect** (at central
   eligibility 0.55, parse-fail 0.03, ICC 0.10), for ~90 % simulated power to exclude 0:
   synthetic h ≈ 0.16 → a few hundred items; h ≈ 0.12 → several hundred; h ≈ 0.06–0.08 →
   ≳ 600. These are **not** targets: the true effect, the SESOI, and the ICC are all
   unknown, and **the SESOI / confirmatory target effect REQUIRES A HUMAN SCIENTIFIC
   DECISION BEFORE CONFIRMATORY DESIGN.**
3. **`[AMEND D-058]` No recommended range.** The earlier "n ≈ 300–600, central 400" is
   withdrawn. Any convergence with a Track-B figure is coincidental and not evidence.
4. **Eligibility** is a large lever after N: 0.40 vs 0.55 costs roughly one N-tier. A
   4-way MMLU MCQ is *qualitatively* expected to keep eligibility workable for a small
   reasoning model (D-057) — **no benchmark number for Qwen3-1.7B is relied upon**; the
   realized eligibility yield is a pilot output. GPQA-Diamond would push eligibility
   toward chance and inflate the required N.
5. **Parse failure** at 0.10 vs 0.00 costs ~10 pp power — manageable; the protocol caps
   it as a Layer-1 gate.
6. **Adaptive design:** if a staged confirmatory run is ever used, the **only** permitted
   adaptation is on **eligibility / technical precision** (e.g. "run more items because
   the observed eligible fraction is below the assumed value") — **never** on effect
   direction or magnitude, and **no optional stopping for significance**.

## 5. What this does NOT do

- It does not use any real Track-A model output.
- It does not power the **monitor-validity gap** (`native − automated`, the research
  PRIMARY estimand, D-059) — that needs a separate calc once the native-human and judge
  arms exist (Milestone 3/4), and its precision is dominated by the **human-annotation**
  sample, not the generator sample.
- **It does not recommend a confirmatory N and it does not set a SESOI.** Both REQUIRE A
  HUMAN SCIENTIFIC DECISION BEFORE CONFIRMATORY DESIGN (D-058), informed by a
  pre-stated smallest effect of interest and by the pilot's *nuisance* estimates
  (eligibility yield, parse-failure rate, missingness, descriptive switch yield) — never
  by the pilot's observed effect direction or magnitude.

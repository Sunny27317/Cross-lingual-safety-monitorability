# POWER_ANALYSIS.md — Track-A prospective power / sample-size

**Prospective. Uses ONLY synthetic assumptions and prior-literature effect ranges. No
observed Track-A outcome is used — none exist.** Decision: `DECISION_LOG.md` D-045.
Simulation: `experiments/M1-Mac-Feasibility/analysis/track_a_power_sim.py`
(seed `20260910`); full grid: `…/track_a_power_sim_output.txt`.

---

## 1. What each stage is *for*

| stage | n | purpose | is it a hypothesis test? |
|---|---|---|---|
| **A. pipeline validation** | 50 | prove the harness computes what it claims; expose bugs; show the qualitative direction | **no** |
| **B. Track-A scientific pilot** | (= A here) | " " + a first, wide, descriptive estimate | **no** |
| **C. confirmatory** | **deferred, ~300–600** | CI of the effect excludes 0 at the pre-stated minimum effect of interest | yes |

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
  correlation `ρ = 0.10` (majority vote over `k = 8`, minus per-generation parse-failure
  attrition); eligibility (`a_u == correct AND h != correct`) central **0.55**
  (sensitivity 0.40 / 0.55 / 0.70); parse-failure central **0.03** (sensitivity
  0.00 / 0.03 / 0.10); control adoption ≈ 0.01 (neutral hint).
- **Effect ranges (prior-literature anchors, all VERIFIED in
  `literature/CITATION_VERIFICATION.md`):** Turpin — up to 36 % accuracy drop; Chen —
  CoT-faithfulness ~25 % (Claude 3.7) / ~39 % (DeepSeek-R1), "reveal rates often below
  20 %", lower on GPQA; Young 2026 — 55.4 % thinking-vs-answer divergence. The **locked
  model is 1.7B** — effects are **uncertain and may be smaller**, so we report a grid.
  Grid: `switch ∈ {0.05, 0.10, 0.20, 0.35}`, `disclosure ∈ {0.20, 0.40, 0.60}`.

## 3. Results (2000 sim reps/cell, 400 bootstrap resamples/rep)

`hw` = mean 95 % bootstrap CI half-width; `power` = P(CI lower bound > 0).

### PRIMARY: `adoption_increase` (≈ switch rate on eligible items)

| n | s=0.05 | s=0.10 | s=0.20 | s=0.35 |
|---|---|---|---|---|
| 50 | 0.021 / **0.00** | 0.032 / **0.00** | 0.073 / **0.05** | 0.143 / **0.69** |
| 100 | 0.019 / 0.00 | 0.029 / 0.00 | 0.059 / 0.20 | 0.104 / 0.95 |
| 200 | 0.017 / 0.00 | 0.025 / 0.02 | 0.044 / 0.47 | 0.074 / 1.00 |
| 400 | 0.014 / 0.00 | 0.019 / 0.04 | 0.032 / 0.77 | 0.053 / 1.00 |
| 600 | 0.012 / 0.00 | 0.016 / 0.05 | 0.026 / 0.91 | 0.043 / 1.00 |

### PRIMARY: `hidden_influence_rate` = `switch × (1 − disclosure)`

**disclosure = 0.40** (central):

| n | s=0.05 (h≈0.03) | s=0.10 (h≈0.06) | s=0.20 (h≈0.12) | s=0.35 (h≈0.21) |
|---|---|---|---|---|
| 50 | 0.004 / **0.00** | 0.011 / **0.00** | 0.042 / **0.02** | 0.106 / **0.39** |
| 100 | 0.003 / 0.00 | 0.012 / 0.00 | 0.038 / 0.12 | 0.081 / 0.87 |
| 200 | 0.003 / 0.00 | 0.010 / 0.01 | 0.030 / 0.43 | 0.058 / 1.00 |
| **400** | 0.003 / 0.00 | 0.009 / 0.09 | **0.022 / 0.91** | 0.042 / 1.00 |
| 600 | 0.003 / 0.01 | 0.008 / 0.22 | 0.018 / 0.99 | 0.034 / 1.00 |

(disclosure 0.20 shifts power up ~1 n-tier; disclosure 0.60 shifts it down ~1 tier —
full table in the sim output.)

### Sensitivities (`hidden_influence`, s = 0.20, d = 0.40)

| n | elig 0.40 | elig 0.55 | elig 0.70 | | pf 0.00 | pf 0.03 | pf 0.10 |
|---|---|---|---|---|---|---|---|
| 50 | 0.01 | 0.01 | 0.03 | | 0.01 | 0.02 | 0.03 |
| 200 | 0.24 | 0.46 | 0.64 | | 0.35 | 0.47 | 0.57 |
| 400 | 0.73 | 0.92 | 0.97 | | 0.85 | 0.92 | 0.96 |
| 600 | 0.95 | 0.99 | 1.00 | | 0.98 | 0.99 | 1.00 |

## 4. Conclusions

1. **n = 50 pilot: power ≈ 0.00–0.05** to exclude 0 for any effect smaller than a very
   large one (`switch ≥ 0.35`). It **cannot** test H1/H2/H3. It **can** validate the
   pipeline and show a point-estimate direction. **This is the intended design.**
2. **Confirmatory `hidden_influence_rate` at ~80–90 % power:**
   - true h ≈ 0.16 (s 0.20, d 0.20) → **n ≈ 300–400**
   - true h ≈ 0.12 (s 0.20, d 0.40) → **n ≈ 400**
   - true h ≈ 0.08 (s 0.20, d 0.60) → **n ≈ 400–600**
   - true h ≈ 0.06 (s 0.10, d 0.40) → **n ≈ 600+**
3. **Recommended confirmatory range: n ≈ 300–600, central 400**, stratified across
   ≥ 20 subjects — **converges with** Track B's independent "≈ 400–600 indicative".
4. **Eligibility** is the biggest lever after n: 0.40 vs 0.55 costs roughly one n-tier.
   MMLU (D-041) keeps eligibility high (~0.55–0.70 given MMLU-Redux 73.9). GPQA would
   push eligibility toward chance and blow up the required n.
5. **Parse failure** at 0.10 vs 0.00 costs ~10 pp power — manageable, and the protocol
   caps it as a Layer-1 gate.
6. **Adaptive design:** if a staged confirmatory run is used, the **only** permitted
   adaptation is on **eligibility / technical precision** (e.g. "run more items because
   the observed eligible fraction is below the assumed 0.55") — **never** on effect
   direction or magnitude, and **no optional stopping for significance**.

## 5. What this does NOT do

- It does not use any real Track-A model output.
- It does not power the **monitor-validity gap** (`native − automated`) — that needs a
  separate calc once the native-human and judge arms exist (Milestone 3/4), and its
  precision is dominated by the **human-annotation** sample, not the generator sample.
- It does not replace a confirmatory power calc — the confirmatory n must be frozen
  from a **pre-stated minimum effect of interest** at confirmatory-design time.

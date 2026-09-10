"""Track-A PROSPECTIVE power / sensitivity analysis (DECISION_LOG D-045).

Deterministic Monte-Carlo. **Uses ONLY synthetic Bernoulli/beta-binomial assumptions
and effect-size ranges from prior literature. It does NOT use any observed Track-A
model outcome** -- none exist. Run before the pilot; re-run unchanged afterwards.

Estimands modelled (frozen definitions -- see src/clsm/metrics.py):
  * adoption_increase  : paired per-item [1(a_h==h) - 1(a_u==h)], mean over items with a
                         majority answer in BOTH conditions. With a neutral hint, control
                         adoption ~ 0, so this ~ answer_switch_rate on the eligible set.
  * hidden_influence_rate : mean over eligible items of 1(switched AND not disclosed),
                            = switch_rate * (1 - disclosure_rate) in expectation.

Prior-literature anchors (all VERIFIED in literature/CITATION_VERIFICATION.md):
  * Turpin et al. 2023 (arXiv:2305.04388): up to 36% accuracy drop from biasing cues.
  * Chen et al. 2025 (arXiv:2505.05410): CoT-faithfulness ~25% (Claude 3.7) / ~39%
    (DeepSeek-R1); "reveal rates often below 20%"; lower on GPQA.
  * Young et al. 2026: 55.4% thinking-vs-answer divergence (12 open models, MMLU+GPQA).
The locked model is a 1.7B dist-scale reasoner -- effects are UNCERTAIN and may be
smaller. We therefore report a grid, not a single number.

Output: a table of, for each (n, assumed true effect), the expected 95%-CI half-width
and the approximate power to exclude 0 (item-clustered percentile bootstrap, matched by
a fast normal approximation and validated by simulation).
"""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(20260910)  # frozen seed
N_SIM = 2000                            # simulation reps per cell (planning precision)
BOOT = 400                              # bootstrap resamples inside each sim rep

# ---- assumption grid --------------------------------------------------------------
N_ITEMS = [50, 100, 200, 400, 600]
ELIGIBILITY = 0.55       # P(a_u == correct AND hint_target != correct); central
ELIGIBILITY_SENS = [0.40, 0.55, 0.70]
PARSE_FAIL = 0.03        # per-generation; central
PARSE_FAIL_SENS = [0.00, 0.03, 0.10]
K = 8                    # samples per condition (D-044)
ITEM_ICC = 0.10          # intra-item correlation of the switch outcome (beta-binomial)

SWITCH_RATES = [0.05, 0.10, 0.20, 0.35]     # answer_switch_rate on eligible items
DISCLOSURE_RATES = [0.20, 0.40, 0.60]        # disclosure among switched


def _beta_ab(mean: float, icc: float) -> tuple[float, float]:
    """Beta(a,b) with given mean and (rho = 1/(a+b+1)) intra-cluster correlation."""
    if mean <= 0 or mean >= 1 or icc <= 0:
        return (1e6 * max(mean, 1e-9), 1e6 * max(1 - mean, 1e-9))
    s = (1.0 - icc) / icc  # a + b
    return (mean * s, (1.0 - mean) * s)


def simulate_cell(
    n_items: int, switch: float, disclosure: float, eligibility: float, parse_fail: float,
) -> dict[str, float]:
    """Return CI half-width and power (P[95% CI excludes 0]) for both estimands."""
    hidden = switch * (1.0 - disclosure)
    a_sw, b_sw = _beta_ab(switch, ITEM_ICC)

    ai_hw = np.empty(N_SIM)      # adoption_increase CI half-width
    ai_excl0 = np.empty(N_SIM)   # 1 if CI excludes 0
    hi_hw = np.empty(N_SIM)
    hi_excl0 = np.empty(N_SIM)

    for r in range(N_SIM):
        # which items are switch-eligible
        elig = RNG.random(n_items) < eligibility
        n_e = int(elig.sum())
        if n_e < 2:
            ai_hw[r] = np.nan
            ai_excl0[r] = 0
            hi_hw[r] = np.nan
            hi_excl0[r] = 0
            continue
        # per-item true switch prob (beta-binomial) among eligible items
        p_item = RNG.beta(a_sw, b_sw, size=n_e)
        # majority vote over K samples, minus parse-failure attrition
        valid = RNG.binomial(K, 1.0 - parse_fail, size=n_e)
        valid = np.maximum(valid, 1)
        sw_votes = RNG.binomial(valid, p_item)
        switched = (sw_votes / valid) > 0.5                      # majority switched to hint
        # control adoption ~ 0 with a neutral hint; model a tiny base rate
        ctrl_adopt = RNG.random(n_e) < 0.01
        adoption_increase_item = switched.astype(float) - ctrl_adopt.astype(float)

        # disclosure among switched items (independent per item)
        p_disc = RNG.beta(*_beta_ab(disclosure, ITEM_ICC), size=n_e)
        disclosed = (RNG.random(n_e) < p_disc) & switched
        hidden_item = (switched & ~disclosed).astype(float)      # over ALL eligible items

        # item-clustered percentile bootstrap
        idx = RNG.integers(0, n_e, size=(BOOT, n_e))
        ai_boot = adoption_increase_item[idx].mean(axis=1)
        hi_boot = hidden_item[idx].mean(axis=1)
        ai_lo, ai_hi_ = np.percentile(ai_boot, [2.5, 97.5])
        hi_lo, hi_hi_ = np.percentile(hi_boot, [2.5, 97.5])
        ai_hw[r] = (ai_hi_ - ai_lo) / 2.0
        hi_hw[r] = (hi_hi_ - hi_lo) / 2.0
        ai_excl0[r] = 1.0 if ai_lo > 0 else 0.0
        hi_excl0[r] = 1.0 if hi_lo > 0 else 0.0

    return {
        "switch": switch, "disclosure": disclosure, "hidden": hidden,
        "adoption_increase_halfwidth": float(np.nanmean(ai_hw)),
        "adoption_increase_power": float(np.nanmean(ai_excl0)),
        "hidden_influence_halfwidth": float(np.nanmean(hi_hw)),
        "hidden_influence_power": float(np.nanmean(hi_excl0)),
    }


def main() -> None:
    print("=" * 100)
    print("TRACK-A PROSPECTIVE POWER / SENSITIVITY ANALYSIS  (D-045)")
    print("SYNTHETIC ASSUMPTIONS ONLY -- NO OBSERVED TRACK-A OUTCOME. seed=20260910")
    print(f"K={K} samples/condition, eligibility={ELIGIBILITY}, parse_fail={PARSE_FAIL}, "
          f"item ICC={ITEM_ICC}, N_SIM={N_SIM}, BOOT={BOOT}")
    print("=" * 100)

    print("\n### PRIMARY: adoption_increase  (== switch rate on eligible items, neutral hint)")
    print(f"{'n':>5} | " + " | ".join(f"s={s:.2f} hw / power" for s in SWITCH_RATES))
    for n in N_ITEMS:
        cells = [simulate_cell(n, s, 0.40, ELIGIBILITY, PARSE_FAIL) for s in SWITCH_RATES]
        row = " | ".join(
            f"{c['adoption_increase_halfwidth']:.3f} / {c['adoption_increase_power']:.2f}"
            for c in cells
        )
        print(f"{n:>5} | {row}")

    print("\n### PRIMARY: hidden_influence_rate  = switch * (1 - disclosure)")
    for d in DISCLOSURE_RATES:
        print(f"\n  disclosure among switched = {d:.2f}")
        print(f"  {'n':>5} | " + " | ".join(f"s={s:.2f} (h={s*(1-d):.3f}) hw / power"
                                            for s in SWITCH_RATES))
        for n in N_ITEMS:
            cells = [simulate_cell(n, s, d, ELIGIBILITY, PARSE_FAIL) for s in SWITCH_RATES]
            row = " | ".join(
                f"{c['hidden_influence_halfwidth']:.3f} / {c['hidden_influence_power']:.2f}"
                for c in cells
            )
            print(f"  {n:>5} | {row}")

    print("\n### SENSITIVITY to eligibility rate (hidden_influence, s=0.20, d=0.40)")
    print(f"  {'n':>5} | " + " | ".join(f"elig={e:.2f} hw / power" for e in ELIGIBILITY_SENS))
    for n in N_ITEMS:
        cells = [simulate_cell(n, 0.20, 0.40, e, PARSE_FAIL) for e in ELIGIBILITY_SENS]
        row = " | ".join(
            f"{c['hidden_influence_halfwidth']:.3f} / {c['hidden_influence_power']:.2f}"
            for c in cells
        )
        print(f"  {n:>5} | {row}")

    print("\n### SENSITIVITY to parse-failure rate (hidden_influence, s=0.20, d=0.40)")
    print(f"  {'n':>5} | " + " | ".join(f"pf={p:.2f} hw / power" for p in PARSE_FAIL_SENS))
    for n in N_ITEMS:
        cells = [simulate_cell(n, 0.20, 0.40, ELIGIBILITY, p) for p in PARSE_FAIL_SENS]
        row = " | ".join(
            f"{c['hidden_influence_halfwidth']:.3f} / {c['hidden_influence_power']:.2f}"
            for c in cells
        )
        print(f"  {n:>5} | {row}")

    print("\n" + "=" * 100)
    print("READING: 'hw' = mean 95% bootstrap CI half-width; 'power' = P(CI lower bound > 0).")
    print("The PILOT (n=50) is not powered to exclude 0 for small effects -- BY DESIGN.")
    print("Use the grid to pick the CONFIRMATORY n from a pre-stated minimum effect of interest.")
    print("=" * 100)


if __name__ == "__main__":
    main()

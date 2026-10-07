# Decision memo: R_full form and the cross-model zero-sign convention

**Date:** 2026-10-06, before any result. The memo uses no outcome and no label distribution.

## 1. R_full: RESOLVED by the locked framework (confirmation optional)

**What the sources say.**
- Framework §2.4 (locked, D-FA-2) defines R_full in the row after R:
  > R(m,k) = mean(T − D_ur) | translation change on complete H/D/T triples
  >
  > R_full(m,k) = T − D_ur [NEW-OP] | the same contrast on all eligible Urdu traces (k = 3)
- D-PG-6 requires paired arms to be computed in the same replicate.
- Plan §1 makes the trace the unit.

**Reading.**
- "The same contrast" refers to R, which is explicitly a mean of per-trace differences.
- R_full differs from R only in its population: all eligible Urdu traces, not the human-pool triples.
- The shorthand "T − D_ur" is the same notation R uses inside mean(·).
- So R_full = mean(T_t − D_t) over traces with both arms binary. This is what `recovery_r_full` implements.

**The alternative**, a difference of marginal rates T − D_ur with each arm using its own valid labels, would make R_full a *different* contrast from R. It differs from the paired mean only when the two arms have different missingness patterns.

**Recommendation.** Treat it as determined. The investigator may countersign, but no discretion is needed.

**Safeguard.** The missingness cascade reports D-valid, T-valid and complete-pair counts, so any asymmetric missingness is visible to readers either way.

## 2. Cross-model zero-sign convention: NOT DETERMINED (decision required)

**What the sources say.**
- Plan §5: "consistent" if same-sign with the difference interval containing 0, else "differs".
- Framework §2.8: "consistent means same sign and a difference-of-differences interval containing 0; otherwise differs".

**What they don't say.** Neither defines the sign of an estimate that is exactly 0. With binary labels and finite n, an exact 0 is plausible: for example, G = 0 when the discordant pairs balance.

**Current implementation.** `cross_model_flag(..., zero_sign=None)` returns `ZERO_SIGN_UNDECIDED` whenever either point estimate is exactly 0. No convention is applied silently.

| | Option A — "strict" | Option B — "compatible" |
|---|---|---|
| Rule | 0 shares a sign only with 0. (0, +) or (0, −) is "differs" | 0 is compatible with either sign. "Consistent" if the signs are not opposite and the difference interval contains 0 |
| Consequence | Fewer "consistent" flags. A null in one model never counts as replicating a direction in the other | More "consistent" flags when one model is exactly 0 |
| Fits the framework's purpose? | Yes. §2.1 lets a pattern "carry descriptive weight only when it replicates in sign across both models", and 0 has no direction to replicate | Weaker: it lets a directionless estimate count as agreeing with a directional one |
| Effect on Discussion | Branch D ("model-dependent effect") triggers more readily | Branch D triggers less readily |
| Primary or secondary? | The flag summarizes G (primary) as well as AG, ΔTM and R, but **never changes any estimate or interval**. It affects only the cross-model summary wording and Discussion branch selection | Same |

**Cleaner option:** A. It is conservative about replication claims and needs no extra reading of "same sign".

**Recommendation:** adopt **A ("strict")** before unseal. Record it as D-FA-6, then pass `zero_sign="strict"` in the analysis authorization. The decision must be recorded **before** any result is seen. If no decision is recorded, the code will emit `ZERO_SIGN_UNDECIDED`, and the cross-model summary cannot be reported until the investigator decides.

**Draft wording for D-FA-6:**
> "For the cross-model flag, a point estimate of exactly 0 has no sign. Two estimates have the same sign only if both are positive, both negative, or both exactly 0. Decided before unsealing; no result was inspected."

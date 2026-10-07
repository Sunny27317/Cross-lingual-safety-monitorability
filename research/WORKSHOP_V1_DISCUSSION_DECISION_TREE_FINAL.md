# Discussion decision tree: final outcome-to-language mapping (2026-10-07; outcome-blind)

**Precedence.** Branch *selection* is governed by the locked framework §3 (branches A–G).
This table supplies the fixed *wording*. It supersedes the scenario letters in
`WORKSHOP_V1_DISCUSSION_SCENARIOS.md`, which are retained as background.

**How to use it.** Apply mechanically, after the single unseal, per model × cue. Several rows
can apply at once. The wording is fixed (framework §2.1); square brackets are filled from
the artifact.

**Definitions:**
- **"Excludes 0"** means the 95% interval excludes 0.
- **"Replicates"** means equal sign in both models (D-FA-6, strict).
- **"Narrow"** is used only as locked framework §2.5 defines it: when AG < 0 (interval) and
  G's interval contains 0, "narrow enough" means **the upper bound of G is below |AG|**,
  stated numerically. There is no other width threshold, and "narrow" is never used outside
  that comparison.

| # | Outcome pattern | Required wording | Forbidden |
|---|---|---|---|
| D1 | **G > 0** (excludes 0), replicates | "On Urdu rationales, the monitor labelled fewer as disclosing than native readers did (G = [·], 95% CI [·]; n = [·]), in both models." If AG < 0: "The automated language gap is at least partly attributable to the monitor." | "the monitor fails in Urdu"; "models disclose more than detected" as a general claim |
| D2 | **G < 0**, replicates | "…labelled more as disclosing than native readers did…" | "over-reports in non-English languages" |
| D3 | **G near 0**: interval contains 0 **and** (if AG < 0) narrow per §2.5 | "No monitor–reader difference was resolved (G = [·], 95% CI [a, b]); within these bounds the monitor's Urdu labels tracked native readers on these rationales." AG may be called "more consistent with a rationale-side difference" (never "shows") | "equivalent", "validated", "no difference" |
| D4 | **Wide CI**: interval contains 0 and the §2.5 condition fails (or AG is not below 0) | "No difference was resolved at this sample size; the data are compatible with gaps from [a] to [b] percentage points." | Any statement of agreement or validity |
| D5 | **Mixed by model**: flag "differs" (including when one estimate is exactly 0) | "The monitor–reader relation differed between the two model configurations ([values]); the design cannot isolate why." | Attributing it to size or family |
| D6 | **Low human agreement**: κ interval low relative to raw agreement, or disagreements concentrated at `partial` (descriptive; no κ threshold) | "Reader agreement was κ = [·] ([·]); disagreements concentrated at [cells]. G should be read with this boundary ambiguity in view." | Verbal κ bands; "unreliable annotators" |
| D7 | **Second judge disagrees** (if executed): its G-analog or R_full has the opposite sign, or its interval excludes 0 where Falcon's does not | "A second, independent judge [did / did not] show the same pattern ([values]); conclusions about the monitor are specific to Falcon-H1-7B." | Choosing the judge whose result fits; averaging the judges |
| D8 | **Translation "helps"**: R points toward H **and** A > 0 | "Translating before monitoring moved automated labels toward the native readers (R = [·]; exploratory A = [·])." | "translation fixes / mitigates monitoring"; "the failure is linguistic" (no paraphrase control) |
| D9 | **Translation "hurts"**: R points away from H, or A < 0 | "Translating before monitoring moved automated labels away from the native readers ([·])." Report the audit counts (omissions and additions) | "translation-based monitoring is harmful" in general |
| D10 | **No resolvable R**: interval contains 0 | "Translation did not resolvably change automated labels ([a, b])." | "translation has no effect" |
| D11 | **Sensitivity alters the conclusion**: S1, S2 or S3 changes the sign, or whether the interval excludes 0 | "The [primary] conclusion depended on [the `partial` coding / technical failures]: under [S·], G = [·]." State this in the abstract if it affects the headline | Presenting only the variant that fits |
| D12 | **S4 or exclude-six alters R** | "R was sensitive to [audit-flagged / identity] translations ([values])." | Dropping them from the primary |
| D13 | **High missingness in one arm** | "Coverage differed: [n] [arm] traces had no binary label; estimates describe the decidable subset (bounds [·])." | Treating complete-case estimates as population values |
| D14 | **ΔTM** interval excludes 0 | "The cue shifted answers toward the suggested option in [cells]." | "models are manipulable" in general |

**Always (P-END):** state scope (one language, two small models, one monitor, one translator)
and that the conclusions describe disclosure-monitoring measurement validity on these
rationales.

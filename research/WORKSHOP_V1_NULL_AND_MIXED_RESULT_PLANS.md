# Workshop-v1 null-result and mixed-result paper plans

Written before any outcome was examined. They are not to be tuned afterward.

## 1. Null-result paper: English–Urdu difference near zero (AG and G intervals contain 0)

**Narrative.** "We tested whether an apparent cross-lingual difference in automated
disclosure monitoring would appear, and if so whether it belonged to the monitor or to the
text. In this configuration, neither an automated English–Urdu difference nor a
monitor-versus-native divergence was resolved. The intervals rule out differences larger
than [bound]."

**Why it is still informative. State only what is true:**
- **Native-reader calibration.** It provides an adjudicated native-Urdu reference on
  model rationales under a precise construct, with measured agreement.
- **Automated-judge validity.** It gives a bounded estimate of how far one open-weight
  monitor's Urdu labels diverge from native readers, in this setting.
- **Translation contrast.** It reports, descriptively, whether reading the same
  rationales in English changes the monitor's labels.
- **Methodological benchmark.** It is a reusable same-trace, input-parity protocol with
  full provenance.
- **Constraint on broader claims.** For anyone generalizing from multilingual monitoring
  studies, it shows that a monitor-language gap does not appear in every configuration.
  This is phrased as a bound, not as "no gap exists".
- **Transparent negative result.** Reported with the same prominence as a positive one.

**Must not:**
- say "monitors work in Urdu", "equivalent" or "robust";
- reframe the bounds as a success;
- go looking for subgroups to rescue a finding. Any subgroup look is labelled post-hoc
  and kept out of the abstract.

**Title:** "A Native-Reader Reference for Cross-Lingual Disclosure Monitoring: An Urdu Case
Study".
**Abstract:** Branch B.

## 2. Mixed-result plans

| Pattern | Safe claim | Unsafe claim | Limitation | Reviewer response |
|---|---|---|---|---|
| **Qwen differs, Gemma does not** | "The pattern was resolved for Qwen3-1.7B but not for Gemma-3-4B-it; the cross-model flag is 'differs' / 'not consistent'." | "Smaller models are less monitorable"; "Qwen is unfaithful in Urdu" | Two configurations cannot separate family, size, quantization or decoding | "We report it as non-replicated and do not attribute it to any single factor." |
| **Cue A differs, Cue B does not** | "Resolved for the authority-attributed cue (120 items); not resolved for the user-asserted cue (36 items)." | "User pressure does not affect monitoring" | Cue B has 36 items and wider intervals; one wording per source | "Unequal precision; we do not interpret the absence of a Cue-B difference as no difference." |
| **Translated monitoring differs from direct** | "Translating before monitoring changed the automated rate by [Δ]; (exploratory) agreement with native readers was [higher / not higher]." | "Translation fixes or degrades monitoring"; "the monitor cannot read Urdu" | No paraphrase control; one sentence-level translator; audit counts | "R is descriptive by prespecification; audit counts are reported." |
| **Human agreement is low** | "Raters agreed on [x]% (κ = [k], CI); disagreement concentrated in [cells]." | "The construct is invalid"; "the monitor is as good as humans" | Two raters; boundary ambiguity of `partial` | "We report raw and adjudicated labels (S5); G should be read with the measured agreement in view." |
| **`cannot_tell` is frequent** | "The monitor (or raters) withheld a decision for [x]% of [arm]; binary estimates describe the decidable subset." | Treating `cannot_tell` as non-disclosure; hiding coverage loss | Complete-case restriction; S1–S3 and bounds | "Coverage is reported as a finding, and bounds show how far conclusions could move." |

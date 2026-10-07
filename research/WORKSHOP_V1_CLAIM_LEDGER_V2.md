# Workshop-v1 claim ledger V2 (outcome-blind; written 2026-10-06)

This supersedes nothing; it extends `research/WORKSHOP_V1_CLAIM_LEDGER_FINAL.md` with
explicit evidence requirements.

**Venue-risk scale:** low / medium / high, meaning the likelihood that a reviewer treats the
claim as an overclaim.

| Claim | Supported now? | Needs automated results? | Needs human validation? | Primary evidence | Secondary evidence | Allowed wording | Forbidden wording | Venue risk |
|---|---|---|---|---|---|---|---|---|
| The same-trace design separates the reader/monitor pathway from model behavior more cleanly than regenerating traces per condition | **Yes (design claim)** | No | No | Design (§4.7): one persisted rationale scored three ways | — | "Scoring the same rationale directly, in translation and by native readers holds model behavior fixed across arms" | "eliminates all confounds" (translation and rewriting remain) | low |
| Urdu monitorability differs from English | No | AG | **Yes**, for any non-automated reading | G (monitor side) | AG, D_en/D_ur | "Automated disclosure rates differed / did not resolvably differ (AG)"; "on Urdu rationales the monitor diverged from native readers (G)" | "models are less monitorable in Urdu"; "Urdu reasoning hides X" | high |
| Translation recovers / does not recover the monitor's judgments | No | R_full | R, A | R, R_full | A (exploratory), S4, exclude-six | "Translating before monitoring changed automated labels by d (descriptive)"; "toward the readers" (exploratory) only if A > 0 and R points toward H | "translation fixes / mitigates monitoring"; "the failure is linguistic" | high |
| Cue effects generalize across languages | No | ΔTM by language, L_ΔTM | No | ΔTM, L_ΔTM | Cross-model flag | "Cue sensitivity [was / was not] resolved in both language versions for [model]" | "cue effects are language-universal" | medium |
| Monitor failure vs model unfaithfulness | No | AG | **Yes** | G (+ confusion matrices) | AG | "The automated gap is [at least partly] attributable to the monitor (G ≠ 0)"; "more consistent with a rationale-side difference" only if G ≈ 0 with a narrow interval (framework §2.5) | "models are unfaithful in Urdu"; "proves the gap is the model's" | high |
| Native review validates semantic equivalence of the items | **Yes, narrowly** | No | No (already done, one reviewer) | 120/120 PASS item review; verbal cue and instruction approval | — | "A native reader judged all 120 item pairs equivalent" | "validated translations"; "multiple native reviewers" | low–medium |
| The automated judge matches humans | No | — | **Yes** | G, the confusion matrices | κ (reader reliability) | "Within the stated bounds, the monitor's labels tracked / diverged from native readers on these rationales" | "accurate", "validated monitor", "x% accuracy" | high |
| Conclusions generalize beyond Urdu | **No** (never) | — | — | — | — | "for Urdu" | "multilingual", "across languages" (as generalization) | very high |
| Conclusions generalize beyond Qwen/Gemma | **No** (never) | — | — | — | — | "for these two model configurations as deployed" | "LLMs", "language models in general" | very high |
| Monitor validity should be checked in-language before automated rates are read as model behavior | Partly (an argument) | — | Strengthened by G | G | Related work | "Our results [illustrate / are consistent with] the need for…" | "monitors must not be used in non-English" | medium |
| The study is preregistered | **No** | — | — | — | — | "frozen / prospectively specified relative to result inspection" | "preregistered" | high (if misused) |
| Translations are faithful | No | — | Audit | Translation audit | S4 | "The audit flagged n translations; S4 excludes them" | "accurate translations" | medium |

**Tripwire terms**, to scan before posting: preregistered, significant, prove, demonstrate,
equivalent, no difference, robust (as a finding), ground truth, accurate (of the monitor),
hidden, multilingual (as generalization), mitigation, fixes.

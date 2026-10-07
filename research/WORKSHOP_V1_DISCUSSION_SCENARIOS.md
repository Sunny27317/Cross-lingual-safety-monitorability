# Workshop-v1 Discussion scenarios (outcome-blind; written 2026-10-06)

**How a scenario is selected.** Mechanically, from interval patterns (locked framework §3;
`WORKSHOP_V1_DISCUSSION_DECISION_TREE_V2.md`). Several scenarios may apply, per model × cue.

**Definitions used below:**
- **"Excludes 0"** means the 95% item-cluster interval excludes 0.
- **"Replicates"** means the same sign in both models, per the cross-model flag, under
  D-FA-6 (strict): signs match only when exactly equal, so an estimate of exactly 0
  never replicates a positive or negative one.

**Applies in every scenario:**
- state the family size;
- state all cells;
- no thresholds or "significant";
- no "equivalent".

| | Trigger | Allowed conclusion | Forbidden overclaim | Plausible mechanism (stated as possible, not shown) | Alternative explanation | Limitation to state | Follow-up |
|---|---|---|---|---|---|---|---|
| **A. Strong monitor degradation in Urdu** | G > 0 excludes 0 in both models (Cue A); AG < 0 | "On these Urdu rationales the monitor labelled fewer as disclosing than native readers did (G = …), replicated in both models; the automated language gap is therefore at least partly a monitor effect" | "Monitors fail in non-English languages"; "LLMs are unmonitorable in Urdu" | Weaker Urdu reading of attribution and hedging cues; the English instruction with Urdu content | Reader–monitor construct mismatch at the `partial` boundary (check the confusion matrix and S1/S2); rater leniency | One language, one monitor, small models, prompted rationales | More monitors and languages; an English human anchor |
| **B. Little or no degradation** | G intervals contain 0 in both models | "No monitor–reader difference was resolved; the data are compatible with gaps from a to b pp" | "The monitor works equally well in Urdu"; "no difference"; "robust" | — | Insufficient precision (Cue B especially); the human and monitor errors may coincide | Interval width; no SESOI | A larger human pool; an equivalence margin set in advance |
| **C. Mixed by model** | Cross-model flag = "differs" for G (or AG/ΔTM) | "The monitor–reader relation depended on the model configuration as deployed" | Attributing it to model size or family | Different rationale styles (length, script mixing, formatting) | Different missingness or compliance per model (check T1, T2, T9) | The two models differ on many axes at once | Matched-family models at different sizes |
| **D. Cue A strong, Cue B weak** | Cue-A interval excludes 0; Cue-B (36 items) contains 0 | Report both. Cue B is less precise; use the T6 contrast, not the two cells side by side | "User pressure does not cause X" | — | **Precision**: 36 clusters vs 120 | Few clusters; percentile under-coverage | — |
| **E. Cue B strong on the shared subset** | T6 Cue B − Cue A-on-36 interval excludes 0 | "On the 36 shared items, [quantity] differed between the user-asserted and the authority-attributed cue" | General claims about authority vs sycophancy | User-directed disclosure ("you said") is read differently | One wording per cue | Single wording; 36 items | Several wordings per source |
| **F. Direct vs translated disagree substantially** | R_full (or R) interval excludes 0 | "Translating before monitoring changed automated labels by d"; "toward the readers" only if A > 0 and R points toward H (exploratory) | "Translation fixes monitoring"; "the failure is linguistic" | The monitor reads the English rendering of attributions differently | MT added or dropped disclosure language (check the audit and S4); identity translations (exclude-six) | No paraphrase control (D-PG-3); one translator | A paraphrase control; a second translator |
| **G. Human validation weakens automated claims** | Large G and/or high `partial`/`cannot_tell` among readers; low κ | "Automated disclosure rates in Urdu should not be read as model behavior without native validation" | "The monitor is wrong X% of the time" (H is a reference, not truth) | — | Reader disagreement (κ) bounds what G can mean | Two raters | More raters; written rubric calibration |
| **H. Human validation supports the monitor** | G contains 0 with a narrow interval; matrices concentrated on the diagonal | "Within the stated bounds, this monitor's Urdu labels tracked native readers on these rationales"; then AG may be read as more consistent with a rationale-side difference (framework §2.5: "consistent with", never "shows") | "Validated for Urdu monitoring in general" | — | Shared bias of readers and monitor | No English anchor | Repeat with other monitors |
| **I. High missingness in one arm** | T9 cascade shows asymmetric technical failures, or many `cannot_tell`/`abstain` | "Coverage, not only accuracy, differed"; the binary estimates describe the decidable subset; give the worst-case bounds | Interpreting the complete-case estimate as the whole population | Translation or judge failures concentrated in some rationales | Informative missingness | Complete-case analysis | — |
| **J. Identity robustness changes interpretation** | Exclude-six R/R_full changes sign or interval status vs the primary | Report both. The primary stands, as Record B requires; note that the conclusion is sensitive to six identity cases | Dropping the six from the primary | Identity rationales contain no Urdu, so T = D input by construction | — | Six cases is a small, structurally special subset | — |

**When nothing fits cleanly:** write fresh interpretation from the confusion matrices and
the audits. Do not force a scenario.

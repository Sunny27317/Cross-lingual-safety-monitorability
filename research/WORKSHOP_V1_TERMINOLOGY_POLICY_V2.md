# Terminology policy V2 and audit (2026-10-06)

**Base:** `research/WORKSHOP_V1_TERMINOLOGY.md` (manuscript Appendix Table A1) remains canonical.
This file adds rules and the result of tonight's audit.

## 1. Rules

| Term | Rule |
|---|---|
| **rationale** | The default noun in the body. "Reasoning trace" is allowed as a synonym only after it is defined in §1, and in the title (Table A1). Never "chain of thought" for our outputs, which are prompted rationales; reserve it for background and related work |
| **hidden / hiding / conceal** | **Never** used for our labels or outputs. No frozen label uses them. `not_disclosed` is "does not state", not "hides" |
| **disclosure** | Only as defined: an explicit statement of the suggestion's role. Never "faithfulness" or "honesty" |
| **faithfulness / faithful** | Background citations only (17 occurrences in the preprint, all in Related Work or framing; recheck at the final scan) |
| **monitorability** | Background term only (5 occurrences); our measure is "disclosure monitoring" |
| **native reader** | Short for "native or near-native Urdu reader", defined once in §4.8. Never "native speakers" for the raters unless each is one. Never "experts" |
| **native-reader reference (H)** | Never "ground truth" or "gold labels". The preprint's two "ground truth" occurrences are negations ("not treated as ground truth"); keep them |
| **monitor / judge** | "The monitor" = Falcon-H1-7B with Judge V2. "Judge" is allowed in Methods when describing the LLM-as-judge mechanics. Never "monitors" in the plural for our results |
| **translation** | "Machine translation (IndicTrans2)" or "translate-then-monitor". Never "recovery" or "mitigation" outside the A > 0 exploratory clause |
| **causal verbs** | No "caused", "led to" or "because of Urdu" for any contrast. Use "differed", "changed", "was associated with … in this design" |
| **frozen / prospective** | "Frozen", "prospectively specified relative to result inspection", "pre-unseal". **Never "preregistered"** (0 occurrences, correct) |
| **evidence verbs** | No "proves", "demonstrates", "significant", "equivalent", "no difference", "robust" (as a finding) |

## 2. Audit of `paper/WORKSHOP_V1_PREPRINT.md` (term counts)

| Term | Count | Finding |
|---|---|---|
| hidden | 0 | PASS |
| preregist* | 0 | PASS |
| significan* | 0 | PASS |
| ground truth | 2 | PASS (both are negations) |
| "prove" substring | 22 | PASS: 17 "provenance", 3 "approved", 2 "improve(d)"; zero uses of "prove" |
| reasoning trace | 4 | PASS. Defined at line 241 as a rationale synonym; also in the title |
| near-native | 2 | PASS (defined) |
| native speaker (rater package) | 2 | OK in the qualification template (an example of how competence is established) and in the reviewer note. Not used for raters in the paper |
| reviewer name in rater-facing docs | 2 files | **ISSUE**: see `WORKSHOP_V1_HUMAN_VALIDATION_OPERATIONS.md` §1 |

**Result:** PASS for the manuscript. ISSUES in the rater-facing package (reviewer name).
Title terminology ("Reasoning Traces" vs the body's "rationale") is acceptable because it is
defined, but the investigator should confirm it when choosing the title.

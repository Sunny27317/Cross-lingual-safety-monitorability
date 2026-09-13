# Final claim audit

**Canonical, most granular claim ledger.** `paper/main.md` §Claim ledger is the
paper-facing summary (5 categories); this document adds the distinction between
*descriptive* Urdu/translation evidence and a *confirmatory* result, since those
require different evidence bars and are easy to conflate in a discussion section.
Categories: **SUPPORTED NOW**, **SUPPORTED AFTER HUMAN REFERENCE**, **SUPPORTED AFTER
URDU EXECUTION**, **SUPPORTED AFTER TRANSLATION DIAGNOSTIC**, **SUPPORTED ONLY AFTER
CONFIRMATORY RUN**, **PROHIBITED**.

| # | Claim | Category | Exact evidence needed |
|---|---|---|---|
| 1 | The shared generation pipeline produces complete, parseable, provenance-bound English traces at the frozen configuration | **SUPPORTED NOW** | `experiments/M1-Mac-Feasibility/PILOT_REPORT.md` (PR #19) — already exists |
| 2 | The English hint paradigm produces a nonzero descriptive behavioral signal (answer-switch/adoption) | **SUPPORTED NOW**, descriptive only | Same, already exists |
| 3 | Two qualified raters + an adjudicator produced a locked Urdu disclosure reference with measured agreement | **SUPPORTED AFTER HUMAN REFERENCE** | `docs/rater_package/` execution; locked `ReferenceLabel` set; Table 2 of `paper/main.md` |
| 4 | A judge candidate meets its pre-signed acceptance criteria on this construct | **SUPPORTED AFTER HUMAN REFERENCE** (calibration needs the reference first) | Signed `JudgeAcceptanceCriteria` + calibration report; Table 3 |
| 5 | A Monitor-Validity Gap `G` was descriptively observed on the collected Urdu sample | **SUPPORTED AFTER URDU EXECUTION** | Locked reference + accepted judge scoring the real Urdu traces; Table 5's descriptive interval |
| 6 | Translation changed automated detection (`R` ≠ 0), descriptively | **SUPPORTED AFTER URDU EXECUTION + TRANSLATION DIAGNOSTIC** | Real Urdu traces + locked translator + judge scoring `T`; Table 6 |
| 7 | The change in `R` is consistent with a language-specific monitor limitation, not generic rewriting | **SUPPORTED AFTER TRANSLATION DIAGNOSTIC** (English anchor + paraphrase control + audit, all three, per `research/FINAL_PROTOCOL.md` §1) | Tables 6–8; paraphrase control materially smaller than `R`; audit shows no substantial added/omitted disclosure |
| 8 | Translation "recovers" validity / is a mitigation | **SUPPORTED AFTER TRANSLATION DIAGNOSTIC**, and even then only as "consistent with," never proven | Table 6's agreement diagnostic showing improved native-reference agreement, not just a sign change |
| 9 | The pre-registered confirmatory test rejects (or fails to reject) the null hypothesis of no Monitor-Validity Gap, at a stated alpha | **SUPPORTED ONLY AFTER CONFIRMATORY RUN** | Preregistration filed (`experiments/M4-Confirmatory/CONFIRMATORY_PREREG_TEMPLATE.md`) before outcomes; the §3-validated test/interval; one run against the locked, disjoint confirmatory sample |
| 10 | Any effect-size or "scientifically important" characterization of `G`/`R` beyond a descriptive interval | **SUPPORTED ONLY AFTER CONFIRMATORY RUN** | Same as #9, compared explicitly against the investigator's independently-elicited SESOI (packet row 9) |
| 11 | The confirmatory test's reported type-I error/coverage is trustworthy at the actual confirmatory item count and ICC | **SUPPORTED ONLY AFTER CONFIRMATORY RUN**, and only if the §1a finding below is resolved first | A revised `CLUSTER_METHOD_VALIDATION.md` scenario matching the actual approved N/ICC, with its null interval containing nominal alpha (`research/FINAL_PROTOCOL.md` §1a finding 1 — currently 2 of 3 null scenarios fail this at n=8 and n=32/ICC=0.4) |
| 12 | This is the first study of its kind | **PROHIBITED** | — YELLOW novelty; adjacent work exists (`research/POST_PILOT_METHODS_DECISIONS.md` §I) |
| 13 | Translate-then-monitor itself is a novel technique | **PROHIBITED** | — DialectShift-Monitor already does this, different language pair |
| 14 | The model has private/hidden unfaithful cognition | **PROHIBITED** | — disclosure is a textual construct, not a causal-cognition claim, regardless of any future evidence |
| 15 | Results generalize to other low-resource languages | **PROHIBITED** | Not obtainable from this design at all — would require an independent replication study in another language |
| 16 | Urdu monitor degradation exists | **PROHIBITED as a premise** | This is exactly what claim 5 measures; never assumed before it |
| 17 | A null result (`G`≈0, or "no judge accepted") is a failed study | **PROHIBITED framing** | A well-characterized null is a legitimate, equally reportable outcome (CLAUDE.md §2.4); use claims 5/9 with the observed null value instead |

## How this differs from `paper/main.md`'s claim ledger

That table is the reader-facing summary at 5 categories, meant to sit in the paper
itself. This table exists so the *investigator* never accidentally writes a
confirmatory-strength claim (rows 9–11) supported only by descriptive evidence (rows
5–8), and to track the specific outstanding blocker on row 11 (the ADEMP calibration
finding) so it isn't lost between now and confirmatory design freeze.

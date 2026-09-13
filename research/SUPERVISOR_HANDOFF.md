# Supervisor handoff

**Read this first. Ten minutes, no other document required to get oriented.** Deeper
detail on any point below is one link away.

## A. Research question

When an automated safety monitor reports low disclosure of hint-reliance on an Urdu
reasoning trace, is that because the model didn't disclose, or because the monitor
can't read Urdu disclosure as well as a native human can? A second question: does
translating the trace to English before monitoring change that detection, and if so,
is that a language-competence fix or just generic rewriting sensitivity?

## B. Why it matters

Automated CoT monitors are increasingly relied on for safety oversight. If a monitor
silently degrades outside English, that creates false confidence exactly where it's
hardest to verify locally — and conflating "the monitor is broken" with "the model
behaves differently" leads to the wrong fix.

## C. What is genuinely novel/defensible

Not the individual pieces. Multilingual CoT monitoring degradation has prior art
(Onyame et al.). Translate-then-monitor itself has prior art (Ercolano's
DialectShift-Monitor, a different language pair). **The combination** — native-human-
anchored reference + same-trace translate-then-monitor + explicit English-paraphrase
artifact control, for Urdu — is not yet combined anywhere found in review.
**Novelty: YELLOW.** Full positioning: `paper/main.md` §Related Work.

## D. What has already been executed

- English feasibility pilot: 800/800 generations, integrity **PASS WITH DOCUMENTED
  LIMITATIONS** (PR #19, still open/unmerged — its own report is authoritative).
- Nothing else. Zero human labels, zero judge scores, zero translations exist.

## E. English pilot results (observed, descriptive — not evidence about Urdu)

| Quantity | Value |
|---|---:|
| Valid parsed generations | 787/800 (98.4%) |
| Unhinted accuracy | 36/50 = 0.7200 |
| Hinted accuracy | 29/49 = 0.5918 |
| Control adoption | 5/50 = 0.1000 |
| Hinted adoption | 13/49 = 0.2653 |
| **Answer-switch rate** | **6/35 = 0.1714** [0.057, 0.314] |

These validate the shared pipeline only. They carry zero evidential weight for the
Urdu/monitor/translation questions.

## F. What has NOT been executed

Any human annotation, any judge call, any translation, any Urdu inference, any
confirmatory analysis. All engineering scaffolding for these stages exists and is
tested; none has been run against real data.

## G. Primary estimand

`G = mean(H − D)` — native-human minus direct-automated disclosure detection, on
complete matched Urdu trace pairs. Positive means the monitor under-detects relative
to a human; `G=0` can hide equal-and-opposite false positives/negatives, so it's
always reported with the confusion matrix, never as a bare number.

## H. Secondary estimand

`R = mean(T − D)` — translated-automated minus direct-automated detection, on the
common complete native/direct/translated (H/D/T) triple population. A separate
exploratory agreement diagnostic `mean(1[T=H] − 1[D=H])` checks whether translation
improves *agreement* with the human reference, not just the raw positive rate.

## I. What H/D/T/P mean

- **H** — native-human disclosure label on the original Urdu trace.
- **D** — direct automated-judge label on the same original Urdu trace.
- **T** — automated-judge label on that same trace's locked English translation
  (same judge spec as D).
- **P** — an English-to-English paraphrase-control label, used only on English-original
  anchor traces, to check whether an `R` effect is language-specific or just generic
  rewriting sensitivity. **MUST HAVE**, not optional, given this project's framing.

## J. Remaining 13 human decisions

All in `research/SUPERVISOR_DECISION_PACKET.md`: (1) ethics/IRB determination,
(2) rater recruitment/qualification, (3) compensation, (4) storage/release governance,
(5) judge selection, (6) numeric judge acceptance criteria, (7) translator selection,
(8) Urdu rubric-language approval, (9) SESOI, (10) alpha/target power,
(11) multiplicity rule, (12) confirmatory N, (13) final go/no-go.

## K. Exact order decisions must be made

1 → 2/3/4 (can be parallel) → 6 → 5 → 8 → 7 → 9 → 10 → 11 → 12 → 13. Full dependency
chain and rationale: `research/EXECUTION_ROADMAP.md`.

## L. What each decision unlocks

See the "Unblocks" field on every row of `research/SUPERVISOR_DECISION_PACKET.md` —
each decision names exactly what it gates, so approving one at a time makes visible
progress rather than requiring all 13 before anything moves.

## M. Exact next scientific stage after approval

Once decisions 1–4 and 6 are resolved: run judge calibration against the signed
acceptance criteria, using the rubric package (`experiments/M2-Monitor-Validation/
JUDGE_RUBRIC_PACKAGE.md`) and a locked human reference collected via `docs/
rater_package/`. Full roadmap: `research/EXECUTION_ROADMAP.md`.

## N. Risks/limitations

One quantized 1.7B-parameter model, one benchmark family, one hint design, one
language. Disclosure is a textual construct, not a causal-cognition claim. Human and
automated references are both fallible. Translation can add or remove disclosure
independent of any monitor-language effect — this is why the paraphrase control is a
MUST HAVE, not a nice-to-have. Full list: `paper/main.md` §Limitations.

## O. Claims currently allowed

That the shared pipeline works end-to-end at the frozen English config, and that the
English hint paradigm produces a nonzero descriptive behavioral signal (§E) —
pipeline-validation only, not evidence about Urdu or monitor validity.

## P. Claims currently prohibited

"First" of anything; translate-then-monitor as a novel technique; private/hidden
cognition; generalization beyond this one model/task/language; Urdu monitor
degradation asserted before measurement; translation as a "mitigation" without
improved native-reference agreement. Full ledger: `research/FINAL_CLAIM_AUDIT.md`.

## Q. Current PR/branch status

| Item | State |
|---|---|
| Scientific work | `research/next-stage-scientific-freeze` (PR #26), open, mergeable, clean |
| Engineering gates | PR #27 (`research/final-scientific-execution-readiness`), open, actively developed by Codex |
| English pilot | PR #19 (`research/track-a-english-pilot-execution`), open, complete, **do not merge until its stale body/decision-log entry are updated — see the merge-sequence recommendation below** |
| Novelty | YELLOW, unchanged |
| Scientific completion | ~95% of everything achievable without real humans or new data |

**Recommended merge order (do not merge without supervisor sign-off):** PR #26 first
(pure documents, no dependency on the others), then PR #27 once its two open findings
(`research/FINAL_PROTOCOL.md` §1a) are addressed, then PR #19 last, with its own
colliding decision-log entry renumbered at that moment to whatever `main`'s actual
next-free `D-` number is — never a number written in advance in any document, since
that number has already been invalidated three times by concurrent work.

## R. What the supervisor should review first

1. This document (done).
2. `research/SUPERVISOR_DECISION_PACKET.md` — make decisions 1–4 to unblock recruitment.
3. `docs/rater_package/RATER_INSTRUCTIONS.md` — confirm the task is one you'd want a
   real rater to actually do.
4. `paper/main.md` §Research Questions and §Claim ledger — confirm the framing before
   anything is collected.

**To actually make the 13 decisions:** use `research/SUPERVISOR_MEETING_AGENDA.md`,
which groups them into a ~60-minute meeting sequence rather than 13 unordered rows.
**For a 60-second version of this document:** `research/SCIENTIFIC_STATUS.md`.

## Venue strategy (fit, not prestige — full detail in `research/
FINAL_SCIENTIFIC_READINESS.md` §Publication strategy)

- **Ambitious:** an ACL/EMNLP/NAACL main-conference track, or a top AI-safety/
  alignment venue's main track, if the executed evidence and scope actually meet that
  bar — fit depends on whether the result reads as general multilingual-NLP work or
  safety-oversight methodology.
- **Realistic strong:** Findings of ACL/EMNLP/NAACL, or a focused trustworthy-ML /
  AI-safety-evaluation workshop with full review — matches this project's actual scope
  (one language, one model, one task family) better than a main-track venue's
  generalization expectations.
- **Workshop/backup:** a low-resource-language NLP workshop, general NLP-evaluation
  workshop, or interpretability/safety workshop — appropriate regardless of outcome
  direction; a well-characterized null is a legitimate contribution at this tier.
- **`VERIFY AT SUBMISSION TIME`:** no deadline, cycle, or current call-for-papers is
  named or assumed anywhere in this repository. Confirm the actual current deadline
  and scope from the venue's own site before committing.

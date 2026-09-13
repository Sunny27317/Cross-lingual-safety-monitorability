# Scientific-lead final audit — 2026-09-11

**Independent, outcome-blind consistency audit of the merged downstream/scientific
package (PRs #20–#24), not a re-derivation of it.** This document does not duplicate
`research/POST_PILOT_METHODS_DECISIONS.md`, `research/FINAL_SCIENTIFIC_READINESS.md`,
`docs/HUMAN_URDU_VALIDATION_PACKAGE.md`, `docs/ETHICS_AND_DATA_GOVERNANCE_CHECKLIST.md`,
`docs/PROJECT_COMPLETION_CHECKLIST.md`, `experiments/downstream/
POST_ENGLISH_PILOT_EXECUTION_PLAN.md`, or `paper/main.md` — it reads all of them,
records what was independently re-checked, and lists only concrete findings.

**Access statement.** This audit did not open, read, or reason about
`generations.jsonl`, any raw pilot output, PR #19's checkout, or any partial/complete
outcome of the active English run. PR #19 was not modified, commented on for merge,
or merged. Track B, Track-A scientific parameters, and the frozen English generator
config are unchanged.

## 1. What was independently verified today (not re-trusted from prior text)

- **Citation spot-check (4 sources, direct fetch/search, not a re-read of the prior
  verification table):**
  - Onyame et al., arXiv:2605.27901 — confirmed real; title and author list
    (Onyame, Zhou, Thopalli, Kailkhura, Agarwal) match exactly. `literature/
    CITATION_VERIFICATION.md` §E already logs a primary-source-verified finding that
    this paper "used no native validation, did not test translate-then-monitor, and
    does not include Urdu" — the abstract alone (checked today) neither confirms nor
    contradicts this; the existing verification is against the fuller text, and is not
    contradicted by anything found today. **No change needed.**
  - Doğruöz et al., arXiv:2607.02235 — confirmed real; title and author list match.
  - Zhao et al., arXiv:2510.09555 — confirmed real; title matches.
  - Ercolano, *DialectShift-Monitor* README — **the exact cited URL was fetched
    directly and the repository exists.** Its content matches the characterization in
    `POST_PILOT_METHODS_DECISIONS.md` footnote 35 (Spanish-dialect/Spanglish
    monitoring, a translate-then-monitor finding that translation *sanitizes* risk
    signal, and Prolific-crowdsourced human semantic-adequacy/authenticity validation
    with reported Krippendorff's alpha). The existing footnote's caution ("mutable,
    unreviewed... not an independent replication") remains appropriate, but the
    citation itself is **not** fabricated and is accurately described. No edit made.
  - No fabricated, misattributed, or unverifiable citation was found in this spot-check.
    A full re-verification of all ~35 footnotes was out of scope for this pass; the
    four checked were chosen as the highest novelty-stakes items.

- **Engineering regression, found and fixed (safe, prospective, non-scientific):**
  `tests/test_track_a_run.py::test_readiness_fails_closed_with_no_env`,
  `::test_authorize_raises_when_not_ready`, and
  `::test_human_auth_present_but_still_blocked_by_external_resources` fail on `main`
  whenever a real `experiments/M1-Mac-Feasibility/DATASET_CONTENT_PIN.json` exists in
  the working copy (it is git-ignored by design, D-067, so this is invisible to `git
  status` but real on any machine that has run the dataset-pin step — including this
  one). The three tests assumed the default pin path would never resolve to a real
  pin; they now pass an explicit, guaranteed-absent `tmp_path` pin path. **This is a
  test-hermeticity fix only** — no scientific parameter, threshold, or gate logic
  changed, and it does not touch Track-A/Track-B scientific config. Verified: 398
  passed after the fix (was 395 passed / 3 failed before it), ruff and mypy clean.

- **Full offline validation re-run on this branch:** 398 passed, ruff clean, mypy
  clean (see §7).

## 2. Consistency audit: one real, unresolved contradiction

**`literature/DECISION_LOG.md` has two different entries both numbered `D-069`.**

- Main's `D-069` (merged, PR #20): *"Independent downstream infrastructure after
  merged PR #18."*
- **PR #19's `D-069`** (still open, unmerged, on `research/track-a-english-pilot-
  execution`): *"Real-environment smoke finding: llama.cpp v0.4.0 (build b10809) does
  not expose a parseable default token-count signal..."* — an entirely different,
  unrelated finding, added independently on a different branch before either author
  knew the other had also claimed `D-069`.

This is a genuine numbering collision, not yet a contradiction on any single branch
(each branch is internally consistent), but it **will** become one the moment PR #19
merges into a main that already has a `D-069`. **This audit does not fix it**, because
fixing it means editing PR #19's content, and this task is explicit that PR #19 must
not be touched while its run is incomplete. **Action required at PR #19 merge time:**
whoever merges PR #19 must renumber its `D-069` entry to the next free number (`D-073`
as of this audit; recheck at merge time) before or as part of the merge, and update any
cross-reference to it. Flagged here so it is not missed.

No other numbering collision, broken cross-reference, or contradiction was found
between `RESEARCH_PLAN.md`, `literature/DECISION_LOG.md`, `research/
POST_PILOT_METHODS_DECISIONS.md`, `research/FINAL_SCIENTIFIC_READINESS.md`,
`experiments/downstream/POST_ENGLISH_PILOT_EXECUTION_PLAN.md`, and `paper/main.md`.
The estimand signs (`G = H − D`, `R = T − D`), the MMLU-primary/UrduBench-secondary
dataset hierarchy, the Latin-A–D-primary/Perso-Arabic-exploratory extraction contract,
and the "no frozen SESOI/N/threshold" position are stated identically everywhere they
appear.

## 3. Small documentation addition made (not a duplicate)

`docs/HUMAN_URDU_VALIDATION_PACKAGE.md` had a complete recruitment/blinding/
adjudication/reporting procedure and a decision tree, but no concrete worked examples
for `disclosed` / `not_disclosed` / `partial` / `cannot_tell` / `abstain`. Added a
short **synthetic-only** worked-examples table (clearly labeled as invented training
material, not experimental data, and not itself usable as a training/calibration set)
directly below the decision tree. Nothing else in that file was changed.

## 4. Critical review of PR #22's major recommendations (independent second pass)

`research/FINAL_SCIENTIFIC_READINESS.md` already carries a table of ACCEPT/MODIFY
verdicts on PR #22. Independently re-derived, this audit agrees with every verdict in
that table:

| Recommendation | Verdict (independently re-derived) |
|---|---|
| GPT-5.4 dated snapshot, primary judge candidate | **MODIFY** — candidate, not selection; no Urdu-disclosure validation exists for it; calibration against a locked human reference is the actual gate. |
| Claude Sonnet 4.6, backup candidate | **MODIFY** — candidate only; independent-family value is real, but exact version/terms/Urdu applicability need reverification at freeze, not now. |
| Two independent Urdu raters + adjudicator | **ACCEPT** — resource-proportionate to a bounded 50-item-class study; three-rater is a legitimate SHOULD-HAVE upgrade, not a requirement. |
| Human translation + independent bilingual review | **ACCEPT** — no defensible substitute for a small, high-stakes item set. |
| English→English paraphrase control | **MODIFY** — SHOULD HAVE in general; **MUST HAVE** the moment any claim invokes a language-specific mechanism (which this project's framing does). |
| Source-item clustered bootstrap | **ACCEPT** for descriptive reporting; **UNRESOLVED** for confirmatory use until a matching test/interval is validated by simulation — this is already stated, not glossed over, in the existing docs. |
| Monitor-Validity Gap definition (`G = H − D`) | **ACCEPT** — correctly kept as a detection contrast, not accuracy or causal faithfulness; FN/FP reported separately so a null `G` cannot be misread as validity. |
| Translate-then-monitor recovery (`R = T − D`) | **ACCEPT** — correctly scoped to common complete triples with a separate agreement-recovery diagnostic. |
| Novelty verdict YELLOW | **ACCEPT** — reaffirmed independently in §5 below with a fresh (if partial) citation spot-check. |

No recommendation was accepted merely because Codex (or a prior agent) proposed it;
each is re-justified above independently of authorship, and the two **MODIFY** rows are
modifications, not blanket acceptances.

## 5. Final novelty position (reaffirmed, not re-litigated)

**YELLOW.** Adjacent, materially overlapping work exists (Onyame et al. — large-scale
multilingual CoT monitoring fragility, no native reference, no Urdu, no translate-then-
monitor; Zhao et al. and Yang et al. — multilingual CoT faithfulness/monitorability;
Doğruöz et al. and related LLM-as-judge multilingual reliability work; Ercolano's
DialectShift-Monitor — closest pipeline overlap, Spanish/Spanglish not Urdu, human
validation via crowdsourcing not native-competent adjudicated raters). None of the
inspected sources combines a native-Urdu-human-anchored reference with a same-trace
translate-then-monitor diagnostic and explicit translation-artifact controls.

**WE CAN CLAIM:** a controlled, source-trace-matched measurement study design that
estimates automated Urdu disclosure detection relative to an independently obtained
native-human reference on the same traces, and that tests whether that gap changes
after translation while explicitly auditing and reporting translation-induced
disclosure changes (additions, omissions, and both false-positive and false-negative
directions) — once the design is actually executed and reviewed.

**WE CANNOT CLAIM:** that this is the first such study; that textual disclosure
measures private causal cognition; that a positive or null gap by itself proves
monitor failure or monitor validity; that a positive recovery constitutes a mitigation;
that Urdu results generalize to other low-resource languages or to frontier models;
or that any of this is established before the relevant human/judge/translation stages
are actually run and reviewed.

## 6. Readiness snapshot (status, not a re-write of the underlying docs)

| Protocol | Status |
|---|---|
| Human Urdu reference protocol | **READY** (design); recruitment/ethics/labels not started |
| Urdu material equivalence protocol | **READY** (design); no Urdu content translated yet |
| Translate-then-monitor diagnostic | **READY** (design); translator unselected |
| Judge calibration protocol | **READY** (design); no candidate selected, no calibration run |
| Statistical plan | **READY** (descriptive); confirmatory test/interval still needs simulation validation before freeze |
| Confirmatory decision procedure | **READY** (process); SESOI/N/alpha explicitly not chosen |
| Ethics/governance memo | **READY** (checklist); no institutional determination exists yet |
| Paper (pre-results) | **~80% complete** — Abstract/Intro/Related Work/RQs/Methods/Limitations/Ethics/Reproducibility drafted with correct hedging; Results/Discussion/Conclusion correctly blank; a short explicit "Hypotheses" subsection and a "Dataset" subsection separate from Methods would tidy structure but are not blocking |
| Supervisor package | **READY** — `research/FINAL_SCIENTIFIC_READINESS.md` §"Supervisor package and critical path" is a workable 5-minute briefing |

## 7. Validation

Python 3.11, offline suite only, no scientific inference:

```
pytest:            398 passed (0 failed) — see §1 for the 3-test fix that changed this from 395/3-failed
ruff (src tests):  All checks passed
mypy:              Success: no issues found in 36 source files
config-validate:   OK (Track B config_hash 7e7c236bdaec... unchanged; Track-A generator
                    blockers unchanged — dataset_content_pin, plus this clone's
                    ambient real pin does not change any *frozen* scientific setting)
git diff --check:  clean
secret/path scan:  clean (no keys, tokens, or /Users/<name> paths introduced)
```

Track B (`configs/milestone1/`, `experiments/M1-English-Baseline/`,
`experiments/MILESTONE_1_READINESS.md`) and all Track-A scientific parameters are
byte-unchanged by this branch.

## 8. What Sana must personally do (condensed from the existing decision tables)

Everything below is a genuine human act; no amount of further documentation
substitutes for it:

1. Commission or perform the **English pilot integrity review** once PR #19's run
   completes (or is documented as incomplete) — this is the actual first gate.
2. Take `research/FINAL_SCIENTIFIC_READINESS.md` and `docs/
   HUMAN_URDU_VALIDATION_PACKAGE.md` to a UNC Charlotte supervisor and get an explicit
   decision on: target Urdu population, judge candidate approval (or rejection),
   human-reference staffing/governance, translator selection, and confirmatory
   SESOI/N/alpha — none of this can be delegated to Codex or Claude.
3. Determine whether an institutional ethics/IRB consultation is required before
   recruiting annotators, and obtain it if so — no exemption is asserted anywhere in
   this repository.
4. Recruit the actual two Urdu/English-competent raters and the adjudicator; verify
   their competence; arrange compensation if applicable.
5. Approve (or reject) the GPT-5.4 / Claude Sonnet 4.6 judge candidates against a real
   calibration run against the real human reference — this cannot happen before step 4.
6. At PR #19 merge time, renumber that branch's `D-069` decision entry (see §2) before
   or as part of the merge.

## 9. Publication strategy (pointer, not a re-write)

Unchanged from `research/FINAL_SCIENTIFIC_READINESS.md` §"Publication strategy":
ASPIRATIONAL = ACL/EMNLP/NAACL main conference; REALISTIC = Findings track or a
focused trustworthy-AI/safety-evaluation venue; BACKUP = a low-resource-language, NLP
evaluation, or AI-safety workshop. No acceptance is promised and venue choice must not
change the frozen design.

## 10. Scope note

This audit intentionally did not re-run the full literature search from Section 3 of
the task prompt end-to-end; it re-verified the four highest novelty-stakes citations
directly (all checked out) and reviewed the existing, already-extensive verification
record rather than duplicating it. If a full independent re-search is wanted, it
should be scoped as its own task, not folded into a "final consistency audit."

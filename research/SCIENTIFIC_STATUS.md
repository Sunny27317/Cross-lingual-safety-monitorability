# Scientific status — fastest orientation

**Relationship to `research/SUPERVISOR_HANDOFF.md`:** this is the 60-second Q&A version;
that document is the ≤10-minute version built specifically to walk a supervisor through
the 13 pending decisions (estimands, H/D/T/P, merge status, meeting agenda link). Read
this one first if you have a minute; read that one before making any decision.

**What question are we answering?** When an automated safety monitor reports low
disclosure of a hint's influence on an Urdu reasoning trace, is that because the model
didn't disclose, or because the monitor can't read Urdu disclosure as well as a native
human can? A same-trace translate-then-monitor step then asks whether translating to
English before monitoring changes that detection, with explicit controls to rule out
"any rewriting changes things" as a confound.

**What is novel enough to defend?** Not the individual pieces — multilingual CoT
monitoring degradation, and even translate-then-monitor itself, both have prior art
(Onyame et al.; Ercolano's DialectShift-Monitor). The combination — native-human-anchored
reference + same-trace translate-then-monitor + explicit English-paraphrase artifact
control, for Urdu — is not yet combined anywhere found in review. Novelty status:
**YELLOW**. Full positioning: `paper/main.md` §Related Work.

**What has actually been completed?**
- English feasibility pilot: 800/800 generations, integrity PASS WITH DOCUMENTED
  LIMITATIONS (PR #19, open, unmerged — its own report is the source of truth).
- Full frozen design: estimands, disclosure construct, human/judge/translation
  protocols, statistical plan, item-partition rule, missingness policy
  (`research/FINAL_PROTOCOL.md`).
- Full operational packages: rater onboarding/instructions/qualification/adjudication
  (`docs/rater_package/`), Urdu translator/reviewer instructions (`docs/
  TRANSLATOR_INSTRUCTIONS.md`, `docs/BILINGUAL_REVIEWER_INSTRUCTIONS.md`), judge rubric
  package (`experiments/M2-Monitor-Validation/JUDGE_RUBRIC_PACKAGE.md`), ethics request
  and consent drafts (`docs/ETHICS_REVIEW_REQUEST_TEMPLATE.md`, `docs/
  RATER_CONSENT_TEMPLATE.md`), reproducibility release plan (`docs/
  REPRODUCIBILITY_RELEASE_PLAN.md`).
- Paper scaffold with real English numbers, empty Urdu tables, scaffolded discussion
  branches, and a claim ledger (`paper/main.md`).

**What evidence already exists?** Only the English pilot's descriptive/behavioral
numbers (answer-switch rate, adoption, accuracy) — pipeline-validation evidence, not
evidence about Urdu, monitor validity, or translation recovery.

**What evidence does not exist yet?** Any human label, judge score, or translation —
zero exist. No Urdu inference has run.

**What are the remaining blockers?** Exclusively human decisions and resources: ethics
determination, rater/adjudicator recruitment, judge/translator selection with real
calibration evidence, numeric acceptance thresholds, SESOI/alpha/power/N, and the final
go/no-go — the complete list with recommendations is `research/
SUPERVISOR_DECISION_PACKET.md`.

**What is the exact next scientific stage?** Resolve `research/
SUPERVISOR_DECISION_PACKET.md` rows 1–4 (ethics, recruitment, compensation, governance),
then row 6 (numeric judge acceptance criteria) — everything else in the roadmap
(`research/EXECUTION_ROADMAP.md`) is gated behind these.

**What claims are currently prohibited?** "First" of anything; translate-then-monitor
itself as a novel technique; any claim about private/hidden cognition; any
generalization beyond this one model, task, and language; any claim that Urdu
degradation exists (that is what the study measures, not a premise); any claim that
translation "recovers" or "mitigates" without improved native-reference agreement, not
just a sign change. Full ledger: `paper/main.md` §Claim ledger.

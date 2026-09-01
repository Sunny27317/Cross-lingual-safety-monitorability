# Research Decision Log

Append-only record of major scientific decisions. Each entry: date, decision, rationale,
evidence, status, and what would reverse it. Newest at the bottom.

Do not edit past entries except to change `Status:` or add a dated addendum. Decisions
are reversed by a **new** entry, not by deleting an old one.

> **Path note:** the Run-2 Phase-G instruction places this file at
> `literature/DECISION_LOG.md`; a later instruction mentioned `experiments/DECISION_LOG.md`.
> It lives here because these decisions are literature-/novelty-/scope-driven. If the
> user prefers `experiments/`, move it — do not fork it.

---

## D-001 — Reject the broad "do safety monitors fail across languages?" question as a standalone contribution
- **Date:** 2026-09-01 (recorded during Run-2 integration; decision originates in Run-2)
- **Decision:** The project will **not** contribute "monitorability degrades in
  lower-resource languages." That framing is treated as settled prior work.
- **Rationale:** Onyame et al. (arXiv:2605.27901) already report a 95.9% average
  CoT-unfaithfulness rate across 8B–120B models and "100% in low-resource languages"
  across 13 languages and 16 models; Zhao et al. (Findings EACL 2026, arXiv:2510.09555)
  independently measured multilingual CoT faithfulness/consistency/compliance. A generic
  "we added Urdu" study is RED against these.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §2; `CITATION_VERIFICATION.md` §A.1–A.2
  (both VERIFIED, incl. direct confirmation that Onyame used no native validation and
  omitted Urdu); `COMPETITOR_MATRIX.md` #1–#2.
- **Status:** ACTIVE.
- **Reversal condition:** a retraction or major correction of Onyame et al. and Zhao et
  al. that reopens the broad question (not expected).

## D-002 — Reframe to a measurement-validity contribution
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** The contribution is: *when an automated CoT monitor appears to fail on
  Urdu reasoning traces, determine — with native Urdu ground truth — whether the
  reasoning is genuinely unfaithful (A) or the monitor itself is failing (B); and test
  whether translating the trace to English before monitoring recovers the signal.*
- **Rationale:** Onyame's "100% low-resource deception" rests entirely on an
  English-centric automated judge whose low-resource competence was never validated. If
  the *judge* is what fails, the headline claim is partly a measurement artifact. That
  question is open and is where native Urdu competence is a genuine methodological asset.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §1, §4; `CITATION_VERIFICATION.md` §A.1
  (no native validation; no translate-then-monitor — both VERIFIED against the primary
  source).
- **Status:** ACTIVE.
- **Reversal condition:** kill/pivot criteria D or E (see `RESEARCH_PLAN.md`).

## D-003 — Urdu is the target language for reasons of method, not novelty
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** Urdu is the low-resource target **because** native-speaker validation is
  feasible for this project (the researcher is a native speaker; ≥1 further native
  annotator is planned) and because Urdu is absent from Onyame's 13 languages. The
  repository must never state or imply that including Urdu is itself the novel
  contribution.
- **Rationale:** Novelty comes from the native-validated measurement-validity method +
  translate-then-monitor, which are language-general; Urdu is the instance where we can
  actually obtain trustworthy ground truth.
- **Evidence:** `CLAUDE.md` §2.6, §5; `RUN2_BLUEPRINT_HANDOFF.md` §2.2(d)
  (Urdu absence VERIFIED); `COMPETITOR_MATRIX.md` novelty-audit conclusion.
- **Status:** ACTIVE.

## D-004 — Test translate-then-monitor as a mitigation, not assume it works
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** Translate-then-monitor (Urdu CoT → English → same automated monitor) is
  a **hypothesis to be tested** (H3), one of four monitor conditions. The repository must
  not present it as a solution. Possible outcomes and their meanings are enumerated in
  `RUN2_BLUEPRINT_HANDOFF.md` §14.
- **Rationale:** It is cheap and deployable if it works; if it fails, that localizes the
  signal loss to generation rather than monitoring; if it *damages* detection, that is a
  translation-artifact finding (kill/pivot E). All three are informative.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §12, §14; `CITATION_VERIFICATION.md` §A.1
  (competitors did not test this — VERIFIED).
- **Status:** ACTIVE.

## D-005 — Separate "monitor/judge failure" from "model unfaithfulness" as a first-class design goal
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** The four-monitor design (automated-English / automated-in-language /
  native-human / translate-then-English) exists specifically to make (A) and (B)
  separable. The native-human monitor is the language-independent ground truth against
  which the automated monitors are scored (McNemar on identical traces).
- **Rationale:** "Does the monitor succeed?" alone cannot tell you *why* it failed. Only
  a ground-truth label that does not depend on the automated judge can. Native readers
  supply that label.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §12; `RESEARCH_PLAN.md` (A-vs-B section);
  Yang et al. arXiv:2511.08525 already names the "monitorable vs. monitored-correctly"
  gap in English (`COMPETITOR_MATRIX.md` #10) — we cite, not claim, that distinction.
- **Status:** ACTIVE.

## D-006 — Milestone 1 reproduces an English hint-faithfulness baseline before any cross-lingual work
- **Date:** 2026-09-01 (originates in Run-2)
- **Decision:** First experiment = reproduce the Turpin/Chen English hint-faithfulness
  signature (answer-switching with disclosure well below switching) on
  DeepSeek-R1-Distill-Qwen-7B, ~50 items, free compute. No Urdu, no monitors-comparison
  until this reproduces.
- **Rationale:** If the base effect does not reproduce in our harness, every downstream
  cross-lingual comparison is uninterpretable (kill/pivot B). Also matches Onyame's
  setup for later direct comparison.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §11, §25; `RESEARCH_PLAN.md` milestone table.
- **Open sub-decisions:** U5 (Turpin vs. Chen as primary target), U6 (dataset), U10
  (decoding config), U12 (success band) — all BLOCKING for Milestone 1, all listed in
  `RUN2_BLUEPRINT_HANDOFF.md` §27.
- **Status:** ACTIVE; sub-decisions PENDING.

## D-007 — YELLOW verdict re-affirmed after independent verification
- **Date:** 2026-09-01
- **Decision:** After independently verifying all 12 competitor/foundational citations
  and directly checking the Onyame primary source, the YELLOW verdict stands: proceed
  only with the narrowed measurement-validity + mitigation contribution.
- **Rationale:** The three surviving-gap claims are VERIFIED, not merely asserted by the
  blueprint: Onyame used no native validation, did not test translate-then-monitor, and
  omitted Urdu. No verified 2026 paper occupies the specific open intersection.
- **Evidence:** `CITATION_VERIFICATION.md` §E; `COMPETITOR_MATRIX.md` novelty-audit
  conclusion.
- **Caveats carried forward:** (i) newer un-cited 2026 work, esp. arXiv:2603.20172
  (judge/classifier sensitivity in CoT eval) — must be read before Milestone 4;
  (ii) the Onyame and Persian-faithfulness groups could pre-empt via a follow-up
  (kill/pivot A); (iii) Yang et al. (arXiv:2511.08525) already owns the English
  "monitorable vs. monitored-correctly" framing.
- **Status:** ACTIVE.

## D-008 — Repository directory layout: keep Milestone-0 layout, add blueprint's extras as needed
- **Date:** 2026-09-01
- **Decision:** Do not restructure the repo to match the blueprint's `xling-monitor/`
  tree wholesale. Keep the existing top-level dirs (`configs/ data/ src/ tests/
  experiments/ results/ figures/ literature/ paper/`). Add `src/` subpackages
  (`generation/`, `hint_injection/`, `monitors/`, `translation/`, `evaluation/`,
  `statistics/`) and a `models/` config area **when Milestone 1/2 needs them**, not now.
- **Rationale:** Minimize churn; the blueprint's `evaluation/` and `statistics/` become
  `src/evaluation/` and `src/statistics/`; `notebooks/` is optional and gitignore-heavy.
- **Evidence:** `RUN2_BLUEPRINT_HANDOFF.md` §19; `REPRODUCIBILITY.md` "Directory layout".
- **Status:** ACTIVE.

## D-009 — No faculty, Harvard, or publication claims enter the repo without independent confirmation
- **Date:** 2026-09-01
- **Decision:** The blueprint's faculty ranking, the Xu outreach email, and the Harvard
  alignment note are recorded in `RUN2_BLUEPRINT_HANDOFF.md` **as blueprint content
  only**. No derived document asserts supervision, admission likelihood, or institutional
  affiliation. The outreach email may not be sent until the pilot evidence it describes
  actually exists.
- **Rationale:** `CLAUDE.md` §5; research integrity.
- **Evidence:** `CITATION_VERIFICATION.md` §B (only Xu's paper and TAIMing-AI membership
  verified; Bunescu/Fan/Zadrozny/Shaikh characterizations UNVERIFIED).
- **Status:** ACTIVE.

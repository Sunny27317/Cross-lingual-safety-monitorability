# CLAUDE.md — Permanent Research Governance

These are **permanent, non-negotiable instructions for every future Claude Code
session** working in this repository. Read this file in full before taking any
action. If a request conflicts with these rules, stop and surface the conflict to
the user rather than proceeding.

This repository is a **research project**. GitHub is the single source of truth.
The scientific integrity of what is committed here matters more than speed,
convenience, or producing a positive-looking result.

---

## 1. Project summary (orientation only — see `RESEARCH_PLAN.md` for detail)

- **Title:** Cross-lingual safety monitorability — native-validated measurement of
  the monitor-validity gap for Urdu reasoning traces.
- **Current verdict:** **YELLOW — PROCEED, BUT ONLY WITH A NARROWED
  CONTRIBUTION.** Re-affirmed 2026-09-01 after independent verification of the Run-2
  blueprint's citations (`literature/DECISION_LOG.md` D-007).
- **Provenance chain:** `literature/RUN2_BLUEPRINT.pdf` (immutable original) →
  `literature/RUN2_BLUEPRINT_HANDOFF.md` (structured extraction) →
  `literature/{CITATION_VERIFICATION,COMPETITOR_MATRIX,DECISION_LOG}.md` →
  `RESEARCH_PLAN.md`, `experiments/EXPERIMENT_SPEC.md`, `REPRODUCIBILITY.md`. Never edit
  the PDF; update derived docs, not history.
- **Narrowed contribution:** A measurement-validity study. When automated safety
  monitoring *appears* to degrade on Urdu reasoning traces, determine whether this
  reflects (A) genuine model unfaithfulness or (B) failure of the automated
  monitor itself to understand/evaluate Urdu. Also test **translate-then-monitor
  recovery**: translate the Urdu trace to English, apply the same monitor, and
  measure whether the safety signal recovers.
- **Not a contribution:** "Do safety monitors fail across languages?" on its own,
  or novelty claimed **solely** because Urdu is included. Recent 2026 multilingual
  CoT-faithfulness and monitoring work already occupies the broad problem.

---

## 2. Research integrity — NON-NEGOTIABLE

### 2.1 Never fabricate

Never invent, simulate, guess, extrapolate, or "fill in" any of the following:

- experimental results
- model outputs / generations / reasoning traces
- citations, papers, author lists, venues, years, DOIs, URLs
- dataset statistics or dataset contents
- benchmark scores
- human annotations or native-speaker judgements
- GPU runs or "completed" experiments
- accuracy, AUROC, F1, precision/recall
- p-values, confidence intervals, effect sizes
- sample sizes that were not actually used
- random seeds that were not actually run

**A result may only be reported if it was produced by an actually executed
experiment or a genuinely collected annotation process.** If it was not run, the
correct output is "not yet run", not a plausible number.

### 2.2 Never manufacture the appearance of completed work

- Never hand-construct, hand-edit, or synthesize files in `results/` (or anywhere
  else) to make an experiment look completed.
- Never create example/placeholder result values that could later be mistaken for
  real data. Placeholders must be obviously non-numeric and clearly labelled
  (e.g. `TODO`, `PENDING RUN`).
- `results/` must contain **no fabricated result data at any time**.

### 2.3 Hypotheses and scientific decisions

- Never alter a hypothesis after seeing results without **explicitly documenting
  the change and labelling the new analysis as exploratory / post-hoc**.
- Confirmatory and exploratory analyses must always be distinguishable in the
  repository.
- Scientific decisions (model choice, language set, dataset, metric, threshold,
  statistical test, inclusion/exclusion criteria) must never be changed silently.
  Every change is a documented, dated, committed decision.

### 2.4 Negative and null results

- Never hide, discard, or downplay negative results.
- Never delete a null finding because it weakens the hypothesis.
- A null or negative result is a valid research outcome and must be reported with
  the same prominence as a positive one.

### 2.5 No cherry-picking

Never select among the following to manufacture a desired conclusion:

- random seeds
- models
- languages
- examples / items
- prompts
- datasets
- evaluation metrics
- decoding configurations

The selection rule must be fixed **before** looking at outcomes, and documented.

### 2.6 Citations

- All citations must be **verified** before being treated as factual literature
  evidence (title, authors, venue, year, and that the paper actually says what it
  is cited for).
- If a citation cannot be verified, mark it **`TODO — UNVERIFIED`** with whatever
  partial metadata exists. Never invent missing metadata.
- Never claim novelty solely because Urdu (or any low-resource language) is
  included in the study.

### 2.7 Provenance (required for every experiment, eventually)

Every experiment must record enough provenance to reproduce it. Where applicable:

- model name
- exact model ID / version / revision / checkpoint hash
- dataset name
- dataset version / split / revision
- language(s)
- full prompt(s) / prompt template + variables
- intervention / condition applied
- decoding configuration
- random seed
- temperature
- top-p
- max tokens
- other sampling params (top-k, repetition penalty, stop sequences)
- environment info (hardware, key library versions, Python version)
- code commit hash
- timestamp (UTC)
- evaluation configuration (judge model + version, rubric, parsing rules)

An experiment without recorded provenance is not a finished experiment.

---

## 3. Milestone gating

Work is **milestone-gated**. Do not skip ahead. Do not expand scope (e.g. to the full
six-language ladder) before the Milestone 4 gate, or to a manuscript before Milestone 5.
Full objectives / prerequisites / outputs / validation / GO-PIVOT-STOP criteria for each
milestone are in `RESEARCH_PLAN.md` §18; kill/pivot criteria in §19.

- **Milestone 0 — Governance + validated research design.** (Current. No experiments, no
  model downloads, no compute.) Includes the Run-2 blueprint import + verification.
- **Milestone 1 — English hint-faithfulness baseline reproduction** (~50 items,
  `DeepSeek-R1-Distill-Qwen-7B`, free compute): answer-switch rate under misleading vs.
  correct/no hint, and disclosure rate in the visible CoT. **Blocked on decisions
  U5/U6/U10/U12 (`RESEARCH_PLAN.md` §28). Do not implement yet.**
- **Milestone 2 — Multilingual evaluation pipeline + small Urdu pilot** (~10–50 items).
- **Milestone 3 — Native Urdu validation** (blinded human ground truth; ≥2 annotators;
  Cohen's κ). Blocked on U8/U15.
- **Milestone 4 — Four-monitor cross-lingual experiments** (automated-English /
  automated-in-language / native-human / translate-then-English) across the ladder;
  estimate the **monitor-validity gap** and translation recovery. Blocked on U3/U9/U13.
- **Milestone 5 — Controls, ablations, statistics, robustness** → explicit
  **GO / PIVOT / KILL** decision on observed effect sizes and measurement validity.
- **Milestone 6 — Paper / preprint**, only if scientifically justified (a
  well-characterized null is justified).

---

## 4. Operating rules for Claude Code sessions

1. **Never work directly on `main`.** Create a topic branch
   (`research/<milestone>-<topic>`) before modifying files.
2. **Never commit or push without explicit user approval.** When a task is done,
   report status/diff and stop.
3. Before any commit, inspect the diff for: secrets, credentials, API keys,
   personal access tokens, private data, and fabricated / generated result data.
4. Do not download models or datasets, or run expensive compute, unless the
   current milestone explicitly calls for it and the user has approved it.
5. When information required by the plan (a paper, threshold, language set, model,
   dataset, hypothesis, statistical method) is **not** in `literature/RUN2_BLUEPRINT.pdf`
   / `RUN2_BLUEPRINT_HANDOFF.md`, **not** supplied by the user, and **not** independently
   verifiable, write **`TODO — DECISION REQUIRED`** (a choice) or **`TODO — UNVERIFIED`**
   (a citation) rather than guessing. Decisions the blueprint left open are catalogued as
   U1–U17 in `RUN2_BLUEPRINT_HANDOFF.md` §27.
6. Do not invent the contents of `literature/RUN2_BLUEPRINT.pdf`; read it. Do not edit it.
   Update derived documents, never the provenance artifact.
7. Keep confirmatory vs. exploratory framing explicit in every analysis artefact.
8. If asked to do something that violates Section 2, refuse and explain why.

---

## 5. What must NOT be claimed anywhere in this repo

- Results that have not been produced by a real run.
- Publication / acceptance / submission that has not happened.
- Harvard affiliation.
- UNC Charlotte faculty supervision, unless it actually exists and is confirmed by
  the user.
- Novelty derived solely from the inclusion of Urdu.

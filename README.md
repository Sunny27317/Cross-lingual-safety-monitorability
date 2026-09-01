# Cross-lingual safety monitorability

Native-validated measurement of whether apparent degradation in **automated safety
monitoring of Urdu reasoning traces** reflects genuine model unfaithfulness or failure of
the automated monitor itself — plus a **translate-then-monitor** recovery test.

## Research problem

Reasoning-based oversight monitors a model's visible chain-of-thought (CoT) for signs of
unsafe or unfaithful reasoning. When an automated monitor appears to do worse on Urdu
traces than on English ones, the observed degradation is confounded:

- **(A) genuine unfaithfulness** — the Urdu reasoning really discloses less; or
- **(B) monitor failure** — the reasoning is faithful, but the automated (English-centric)
  monitor cannot correctly read/judge Urdu and misreads it.

Existing multilingual monitoring results cannot separate (A) from (B): they use automated
judges with no native-speaker ground truth on the same traces (verified for Onyame et
al. 2026, arXiv:2605.27901 — see `literature/CITATION_VERIFICATION.md`).

## Narrowed contribution

A **measurement-validity study**, not another multilingual benchmark:

1. Compare, on the **same reasoning traces**, four monitors: (i) automated **English**
   judge, (ii) automated **in-language** judge, (iii) **native Urdu** human, (iv) Urdu
   trace **translated to English** then judged.
2. `(iii) − (i)` per language is the **monitor-validity gap**.
3. `(iv) − (i)` measures **translate-then-monitor recovery**.

Primary question: *When automated monitoring appears to fail on Urdu reasoning traces,
how much is genuine model unfaithfulness versus monitor/judge measurement failure — and
does translating the CoT to English before monitoring recover the safety signal?*

The broad question "do safety monitors fail across languages?" is **settled prior work**
(Onyame et al. 2026; Zhao et al., Findings EACL 2026) and is **not** our contribution.
Urdu inclusion alone is **not** claimed as novelty — Urdu is the low-resource language
where trustworthy native ground truth is obtainable and which Onyame et al. omit.

## Current status

- **Verdict:** YELLOW — proceed only with the narrowed contribution above. Re-affirmed
  2026-09-01 after independent verification of all core citations
  (`literature/DECISION_LOG.md` D-007).
- **Current milestone:** **Milestone 0 — governance + validated research design.**
  The Run-2 Deep Research blueprint has been imported, verified, and operationalized.
  No experiments, model downloads, or compute have been run. No results exist.
- **Next milestone:** **Milestone 1 — reproduce an English hint-faithfulness baseline**
  (Turpin/Chen signature) on `DeepSeek-R1-Distill-Qwen-7B`, ~50 items, free compute —
  gated on four blocking decisions (see `RESEARCH_PLAN.md` §28).

Milestones: `0` governance → `1` English baseline → `2` multilingual pipeline + Urdu
pilot → `3` native Urdu validation → `4` four-monitor experiments → `5` controls /
ablations / statistics → `6` paper (only if justified). The project does **not** expand
to the full language ladder before Milestone 4, or to a manuscript before Milestone 5's
GO/PIVOT decision.

## Repository structure

| Path | Contents |
|------|----------|
| `CLAUDE.md` | Permanent research-integrity and governance rules for all sessions. |
| `RESEARCH_PLAN.md` | Frozen RQs, 5 hypotheses, operational definitions, A-vs-B distinction, milestone gates, kill/pivot criteria. |
| `REPRODUCIBILITY.md` | Provenance requirements; environment / model / dataset / seed capture. |
| `literature/RUN2_BLUEPRINT.pdf` | **Immutable provenance:** the original Run-2 Deep Research report. |
| `literature/RUN2_BLUEPRINT_HANDOFF.md` | Structured extraction of the PDF for implementation. |
| `literature/CITATION_VERIFICATION.md` | Independent check of every imported citation and number. |
| `literature/COMPETITOR_MATRIX.md` | Per-paper novelty audit + threat levels. |
| `literature/DECISION_LOG.md` | Append-only record of major scientific decisions. |
| `experiments/EXPERIMENT_SPEC.md` | Planned experimental matrix (planning only — nothing run). |
| `configs/` `data/` `src/` `tests/` `results/` `figures/` `paper/` | Empty until the milestone that needs them; `results/` holds only real-run outputs. |

## Research-integrity commitment

Per `CLAUDE.md`: no fabricated results, outputs, citations, annotations, or statistics;
no hand-built files that make an experiment look done; hypotheses and scientific
decisions never change silently; negative and null results reported with equal
prominence; no cherry-picking of seeds/models/languages/items/prompts/metrics; every
experiment records full provenance; unverified citations marked `TODO — UNVERIFIED`;
planned values labelled `PLANNED`, never presented as observed.

## What is *not* claimed

No results. No publication, submission, or acceptance. No Harvard affiliation or
admissions implication. No UNC Charlotte faculty supervision (no one has agreed). No
novelty from Urdu inclusion alone. The broad multilingual-CoT-monitoring question is not
presented as open.

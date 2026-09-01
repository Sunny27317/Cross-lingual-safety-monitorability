# Cross-lingual safety monitorability

Native-validated measurement of whether apparent degradation in **automated
safety monitoring of Urdu reasoning traces** reflects genuine model
unfaithfulness or failure of the automated monitor itself — plus a
**translate-then-monitor** recovery test.

## Research problem

Reasoning-based oversight monitors a model's visible chain-of-thought for signs
of unsafe or unfaithful reasoning. When an automated monitor appears to do worse
on Urdu traces than on English ones, the observed degradation is confounded:

- **(A) genuine unfaithfulness** — the Urdu reasoning really discloses less; or
- **(B) monitor failure** — the reasoning is faithful, but the automated monitor
  cannot correctly read/judge Urdu and misreads it.

Existing multilingual monitoring results generally cannot separate (A) from (B),
because they lack a native-speaker ground truth on the same traces.

## Narrowed contribution

This is a **measurement-validity study**, not another multilingual benchmark:

1. Compare, on the **same reasoning traces**: (i) an automated monitor operating
   directly on Urdu, (ii) native Urdu-speaker evaluation, (iii) the Urdu trace
   translated to English then monitored by the same automated monitor.
2. The gap between (i) and (ii) is the **monitor-validity gap**.
3. The change from (i) to (iii) measures **translate-then-monitor recovery**.

Primary question: *When automated monitoring appears to fail on Urdu reasoning
traces, is the reasoning genuinely less faithful, or is the monitor failing
because of language limitations?*
Secondary question: *Can translating the trace to English before monitoring
recover the safety signal?*

The broad question "do safety monitors fail across languages?" is **not** treated
as a standalone contribution — recent 2026 work already occupies it — and Urdu
inclusion alone is **not** claimed as novelty.

## Current status

- **Verdict:** YELLOW — proceed, but only with the narrowed contribution above.
- **Current milestone:** **Milestone 0 — research governance & reproducibility
  infrastructure.** No experiments, model downloads, or compute have been run.
- **Next milestone:** **Milestone 1 — reproduce an established English
  hint-faithfulness baseline** on ~50 items (initial target model:
  `DeepSeek-R1-Distill-Qwen-7B`), measuring at least answer switching under
  misleading vs. correct hints and disclosure of hint influence in visible
  reasoning.

Milestones: `0` governance → `1` English baseline → `2` Urdu native-validated
pilot → `3` automated-vs-native Urdu comparison → `4` translate-then-monitor →
`5` GO/PIVOT. The project does **not** expand to multiple languages before
Milestone 5. See `RESEARCH_PLAN.md`.

## Repository structure

| Path | Contents |
|------|----------|
| `CLAUDE.md` | Permanent research-integrity and governance rules for all sessions. |
| `RESEARCH_PLAN.md` | Full project specification, definitions, milestones, confounds, open questions. |
| `configs/` | Version-controlled experiment configs (empty until M1). |
| `data/` | Task items, traces, translations, annotations — real data only. |
| `src/` | Source code (empty until M1). |
| `tests/` | Automated tests (empty until M1). |
| `experiments/` | One directory per experiment, with pre-specified analysis + provenance. |
| `results/` | Outputs of actually executed experiments only — no fabricated data. |
| `figures/` | Figures reproducible from real results only. |
| `literature/` | Verified citations; Run-2 review not yet imported. |
| `paper/` | Manuscript (empty until there is something real to write). |

## Research-integrity commitment

This project follows the rules in `CLAUDE.md`. In brief: no fabricated results,
outputs, citations, annotations, or statistics; no hand-built files that make an
experiment look done; hypotheses and scientific decisions are never changed
silently; negative and null results are reported with equal prominence; no
cherry-picking of seeds/models/languages/items/prompts/metrics; every experiment
records full provenance; unverified citations are marked `TODO — UNVERIFIED`.

## What is *not* claimed

No results. No publication, submission, or acceptance. No Harvard affiliation. No
UNC Charlotte faculty supervision (not established). No novelty from Urdu
inclusion alone.

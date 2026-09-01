# RESEARCH_PLAN.md

> This document is the project specification for Milestone 0. It records the
> research design at the level of intent and governance. Anything not supplied by
> the user or independently verifiable from repository materials is marked
> `TODO — import/verify from Run-2 blueprint`. Nothing here reports a result.

---

## 1. Project title

Cross-lingual safety monitorability: native-validated measurement of the
monitor-validity gap for Urdu reasoning traces, with a translate-then-monitor
recovery test.

## 2. Current status / verdict

**YELLOW — PROCEED, BUT ONLY WITH A NARROWED CONTRIBUTION.**

The project has completed a deep literature-validation phase (Run-2). The broad
research question was judged **not sufficiently novel on its own**. A narrowed,
measurement-validity contribution survives and is the basis for this plan.

Current milestone: **Milestone 0 — research governance & reproducibility
infrastructure.** No experiments, model downloads, or compute have been run.

## 3. Background

Reasoning-based oversight (monitoring a model's visible chain-of-thought for
signs of unsafe intent, deception, or hidden influence) is a leading approach to
scalable AI safety oversight. Its validity depends on the monitor being able to
*read and correctly evaluate* the reasoning it is given.

Recent 2026 work on multilingual chain-of-thought faithfulness and on monitoring
has substantially occupied the broad question of whether such oversight degrades
in non-English / low-resource languages. Specific papers, findings, and numeric
claims from that literature: `TODO — import/verify from Run-2 blueprint`.

Urdu is the focal low-resource language for this project. `TODO —
import/verify from Run-2 blueprint` for the rationale (speaker population,
script, resource level, tokenizer coverage, availability of native annotators).

## 4. Problem statement

When an automated safety monitor appears to perform worse on Urdu reasoning
traces than on English ones, that observed degradation is **confounded**. It
could arise from:

- **(A) genuine model unfaithfulness** — the model's Urdu reasoning really does
  disclose less, rationalize more, or hide influence more than its English
  reasoning; or
- **(B) monitor failure** — the reasoning is just as faithful, but the automated
  monitor cannot correctly parse, understand, or judge Urdu, so it *misreads* a
  faithful trace as unfaithful (or misses a genuinely unfaithful one).

Existing multilingual monitoring results generally cannot separate (A) from (B)
because they lack a native-speaker ground truth on the *same* traces.

## 5. Broad question that was rejected as insufficiently novel

> "Do safety monitors fail across languages?"

Rejected as a standalone contribution: recent 2026 multilingual CoT-faithfulness
and monitoring research already covers this framing. Novelty is **not** conferred
by the inclusion of Urdu alone.

## 6. Narrowed contribution

A **measurement-validity study**, not another multilingual benchmark:

1. Measure whether apparent degradation in automated monitoring of Urdu reasoning
   traces is driven by (A) model unfaithfulness or (B) monitor failure, by
   comparing the automated monitor against **native Urdu-speaker evaluation on the
   same traces**.
2. Test **translate-then-monitor recovery**: translate each Urdu trace into
   English, apply the same automated monitor, and measure whether detection
   performance recovers toward the native-human standard.

## 7. Primary research question

When automated safety monitoring appears to fail on Urdu reasoning traces, is the
underlying reasoning genuinely less faithful, or is the automated monitor itself
failing because of language limitations?

## 8. Secondary research question

Can translating an Urdu reasoning trace into English before monitoring recover
the safety signal?

## 9. Definition of monitorability

For this project: **the extent to which an oversight process can correctly detect,
from a model's visible reasoning trace, a target property of interest** (initially:
hint influence / unfaithfulness — see Milestone 1). Monitorability is a property of
the *pairing* of (trace, monitor), not of the trace alone. A trace that is
perfectly monitorable by a native human may be poorly monitorable by a given
automated monitor.

Operational metric(s): `TODO — import/verify from Run-2 blueprint` (candidate:
detection rate / AUROC of the monitor against a defined ground-truth label for
hint influence).

## 10. Definition of the monitor-validity gap

The **monitor-validity gap** is the difference in measured monitoring performance
between:

- the **automated monitor operating directly on the Urdu trace**, and
- **native Urdu-speaker human evaluation of the same trace** (treated as the
  reference standard).

A large gap indicates that observed "degradation" is substantially explanation
(B) — monitor failure — rather than (A) — genuine unfaithfulness. A small gap
indicates the automated monitor is tracking the same signal a native reader sees,
so observed degradation is more likely genuine.

Exact estimand, metric, and aggregation: `TODO — import/verify from Run-2
blueprint`.

## 11. Conceptual experiment

On the **same set of reasoning traces**, obtain three monitoring readings:

1. **Automated monitor, Urdu-direct** — automated monitor applied to the original
   Urdu trace.
2. **Native human, Urdu** — native Urdu-speaking evaluator judges the same trace
   against the same rubric.
3. **Automated monitor, translate-then-monitor** — Urdu trace translated to
   English, then the same automated monitor applied.

Comparisons:

- (2) − (1) = monitor-validity gap (core quantity).
- (3) − (1) = translate-then-monitor recovery.
- (3) vs. (2) = how close translation gets the automated monitor to the native
  human standard.

Traces are generated by a reasoning model performing a hint-faithfulness task
(see Milestone 1) so that a defined ground-truth notion of "hint influence"
exists independently of any monitor.

Model(s), task items, hint types, rubric text, number of traces, number of
annotators, and inter-annotator agreement targets: `TODO — import/verify from
Run-2 blueprint`.

## 12. Human / native-speaker validation role

Native Urdu speakers provide the **reference standard** for what the reasoning
trace actually discloses. Their judgements are what the automated monitor is
measured against. Requirements (to be finalized):

- native or near-native Urdu proficiency; `TODO` for exact screening.
- blind to condition and to the automated monitor's output.
- fixed written rubric matching the automated monitor's instructions as closely
  as possible.
- at least `TODO` independent annotators per trace; inter-annotator agreement
  reported (metric: `TODO`).
- annotation protocol, consent, and compensation: `TODO — import/verify from
  Run-2 blueprint`.

Native annotations are **collected data**, subject to all Section 2 rules in
`CLAUDE.md`; they are never simulated or filled in by a model.

## 13. Translate-then-monitor mitigation

Hypothesis: if the monitor-validity gap is driven by the automated monitor's
weak Urdu comprehension, then translating the trace to English before monitoring
should recover much of the lost signal.

Design points to fix:

- translation system / model and version: `TODO — import/verify from Run-2
  blueprint`.
- whether translation quality is itself validated by native speakers (recommended):
  `TODO`.
- risk that translation *introduces* or *removes* disclosure signal (translation
  artefact) — must be assessed, not assumed away.

## 14. Milestone sequence

| Milestone | Goal | Gate to next |
|-----------|------|--------------|
| **0** | Research governance + reproducibility infrastructure. No compute. | Governance files reviewed & approved. |
| **1** | Reproduce an established **English hint-faithfulness baseline** on ~50 items. Initial model: `DeepSeek-R1-Distill-Qwen-7B`. Measure ≥ (a) answer switching under misleading vs. correct hints, (b) disclosure of hint influence in visible reasoning. | Baseline numbers land in a defensible range vs. the reference work (`TODO` define range). |
| **2** | Small **native-validated Urdu pilot** (~10–50 items). | Pilot produces usable traces + native annotations; protocol works. |
| **3** | Compare **automated Urdu monitoring vs. native-human Urdu evaluation** on the same traces → estimate the monitor-validity gap. | Gap estimated with an uncertainty interval. |
| **4** | **Translate Urdu traces to English, rerun monitoring** → estimate recovery. | Recovery estimated with an uncertainty interval. |
| **5** | **GO / PIVOT decision** based on observed effect sizes and measurement validity. | Explicit written decision. |

Do **not** jump directly to six languages. Expansion toward the larger
multilingual experiment happens only after Milestone 5.

## 15. Reproducibility requirements

- Every experiment records the full provenance list in `CLAUDE.md` §2.7.
- Configs live in `configs/` and are version-controlled; runs reference a config
  path + commit hash.
- Raw model outputs and raw annotations are stored (or, if large / sensitive,
  their retrieval is documented) so that every reported number can be
  recomputed.
- Analysis code is deterministic given a seed; seeds are recorded, not chosen
  post hoc.
- Confirmatory analyses are pre-specified in the experiment's config/README
  before data are seen; exploratory analyses are labelled as such.
- `results/` contains only outputs of real runs.

## 16. Known novelty risks

- The broad "monitors fail across languages" framing is already occupied by 2026
  work — the contribution must stay on **measurement validity** (separating A
  from B) and **translate-then-monitor recovery**.
- Risk that a 2026 paper already does native-speaker validation of monitor
  outputs for a low-resource language: `TODO — verify against Run-2 blueprint /
  fresh literature check`.
- Risk that translate-then-monitor is already reported as a mitigation: `TODO —
  verify`.
- Urdu inclusion alone is not novelty and must never be presented as such.
- Single-language (Urdu-only) scope may be seen as narrow — framing must lead
  with the methodological contribution, not the language.

## 17. Confounds that must eventually be controlled

- **Translation artefacts** — translation adding/removing disclosure signal.
- **Annotator effects** — proficiency, rubric interpretation, fatigue, low
  inter-annotator agreement.
- **Rubric mismatch** — automated-monitor instructions vs. human rubric not
  equivalent.
- **Monitor model choice** — results specific to one judge model; needs ≥ `TODO`
  monitor models.
- **Generator model choice** — Urdu reasoning behaviour specific to
  `DeepSeek-R1-Distill-Qwen-7B`; may need additional generators.
- **Tokenizer / script coverage** effects distinct from semantic comprehension.
- **Task / domain** — hint-faithfulness task may not generalize to other unsafe-
  reasoning targets.
- **Item difficulty and answerability** differing across languages.
- **Prompt-language effects** (system/user prompt language vs. reasoning
  language).
- **Base task accuracy** differences between English and Urdu confounding
  faithfulness measurement.
- **Multiple comparisons** across conditions/metrics — correction method: `TODO`.
- **Sample size / power** — pilot sizes (10–50) are for feasibility, not
  inference; powered N: `TODO`.

## 18. GO / PIVOT philosophy

- The GO/PIVOT decision at Milestone 5 is driven by **observed effect sizes and
  measurement validity**, not by whether the result is exciting.
- **GO** if: the monitor-validity gap is measurable with acceptable precision,
  the native-annotation protocol is reliable, and the effect is large enough that
  a scaled study is informative — regardless of the direction of the finding.
- **PIVOT** if: the gap is not reliably measurable at pilot scale, annotation
  agreement is too low, the design is confounded beyond repair, or fresh
  literature shows the contribution is no longer novel.
- A null result (no meaningful monitor-validity gap; or translation does not
  recover signal) is a legitimate, publishable outcome and is **not** a reason to
  quietly abandon or re-scope the project without documentation.

## 19. Publication objective

Produce a short, rigorous **measurement-validity paper**: it establishes whether
apparent cross-lingual monitoring degradation for Urdu reflects model
unfaithfulness or monitor failure, and whether translate-then-monitor is a viable
mitigation. Target venue / format / length: `TODO — import/verify from Run-2
blueprint`. No claim of submission or acceptance until it actually happens.

## 20. Faculty-review objective

The project is intended to be defensible under faculty review: milestone-gated,
pre-registered where possible, with all provenance and negative results intact.
Any claim of specific institutional affiliation or faculty supervision requires
explicit confirmation from the user before it appears in the repository. `TODO —
confirm reviewing faculty / institution, if any`.

## 21. Open questions still requiring validation

1. Exact 2026 papers, findings, and numeric thresholds from the Run-2 literature
   review — all `TODO — import/verify from Run-2 blueprint`.
2. Reference English hint-faithfulness paper(s) and dataset to reproduce in
   Milestone 1.
3. Final generator model(s) beyond `DeepSeek-R1-Distill-Qwen-7B`.
4. Automated monitor model(s) and versions.
5. Monitoring metric(s) and the formal estimand for the monitor-validity gap.
6. Native-annotator screening, count per item, agreement metric and threshold.
7. Translation system and whether its output is native-validated.
8. Item source for the Urdu pilot (translated English items vs. native Urdu
   items) and how equivalence is established.
9. Statistical analysis plan: tests, uncertainty quantification, multiple-
   comparison handling, target power / N.
10. Whether any existing 2026 work already performs native-validated monitor
    evaluation or translate-then-monitor for a low-resource language.
11. Ethics / consent / compensation framework for human annotation.
12. Data release plan for traces and annotations.

# EXPERIMENT_SPEC.md — Track A (Mac-Feasibility)

**Status:** PLANNING ONLY. No inference, no downloads, no results. This is a design
document for a screening phase, not a run authorization.

---

## 1. Design overview

Track A has two sequential phases, both gated before any inference occurs:

1. **Model screening** (§2–4 below) — paper-only comparison of 3–5 candidate small
   open-weight models against pre-registered criteria. Produces `MODEL_SCREEN.md`.
   No winner chosen yet.
2. **Tiny feasibility benchmark** (§5) — once a runtime is selected (`READINESS.md`) and
   the user authorizes any download/compute, a deliberately tiny, non-scientific smoke
   test across the screened candidates. Purpose: runtime, parsing, latency, memory,
   trace visibility. (It also records a hint-movement diagnostic — D-039 — which is
   never a model pass/fail.) **Not a hypothesis test.**

Only after a GO from the feasibility benchmark (§5.4) would a pilot-scale Track-A
experiment (analogous to the `n=50` MMLU pilot in `experiments/M1-English-Baseline/`) be
designed — that design does not exist yet and is out of scope for this document.

---

## 2. Candidate class (pre-registered, before any model is examined)

To be screened at all, a candidate must be, on paper:

- roughly **sub-1B to ~3B parameters** (dense) — or a mixture-of-experts model whose
  **total** (not just activated) parameter count still fits a 32 GB-RAM Mac in the
  target dtype/quantization, since the whole model must be resident in memory even if
  only a fraction of parameters is used per token;
- **open-weight**, with a license permissive enough for academic research (Apache 2.0,
  MIT, or a research-permitting community license such as Llama 3.x's or Gemma's — the
  exact terms are recorded per candidate in `MODEL_SCREEN.md`, not assumed);
  a Responsible-AI-License-style model (e.g. BLOOMZ) is not excluded a priori but its
  use-restriction clauses must be checked before selection;
- plausibly runnable on a 32 GB Intel Mac via a **CPU-compatible or Mac-friendly local
  runtime** (`READINESS.md`) — plausibility is a paper judgment at screening time, never
  an asserted runtime/latency number;
- **instruction-following** (an instruct/chat-tuned checkpoint, not a base LM);
  preferably **multilingual with some Urdu exposure** (evidence graded, never assumed —
  `MODEL_SCREEN.md` "Urdu capability evidence" column);
  **ideally** able to produce a reasoning-like trace (an explicit "thinking" mode, a
  chain-of-thought elicitable by prompting, or at minimum a structured step-by-step
  explanation format) — required for the disclosure-scoring paradigm to have any content
  to score.

## 3. Model-selection criteria (pre-registered BEFORE testing — Task 4)

> **SUPERSEDED FOR SELECTION PURPOSES (2026-09-10, `literature/DECISION_LOG.md` D-034,
> D-039).** The Track-A generator is **locked** to `Qwen/Qwen3-1.7B` (Q8_0 GGUF), chosen
> on neutral pre-scientific grounds before any inference existed. **No further model
> selection will occur**, and in particular **no model may be chosen, rejected, or
> replaced on the basis of any behavioural or scientific outcome** — see the "Explicit
> exclusion" box below and D-039. The criteria in this section are retained as the
> historical screening record and are re-scoped: A/B/D/E remain **infrastructure
> readiness** checks that apply to the locked model; **Criterion C is DIAGNOSTIC-ONLY**
> (see C below). Model replacement is possible only on a neutral infrastructure failure
> (enumerated in the "Explicit exclusion" box).

These were fixed before any candidate was run, specifically so that the choice could not
be steered toward whichever model produces the most interesting hint-effect or the most
dramatic monitor-validity gap.

### A. Runtime feasibility
- no OOM / crash across the tiny benchmark's repeated calls;
- latency acceptable for iterative development (an explicit ceiling is set once the
  feasibility benchmark's baseline numbers exist — not guessed now);
- stable across repeated invocations (no silent truncation drift, no crash on the k-th
  call that did not occur on the first).

### B. Output usability
- valid answer extraction under the same extractor contract as `clsm.extraction`
  (`ParseStatus.VALID` achievable, not systematically `AMBIGUOUS`/`NO_ANSWER`);
- a visible reasoning/explanation span the disclosure classifier can be pointed at (a
  `<think>`-style block, a numbered-steps format, or an equivalent the model reliably
  produces when asked);
- low truncation rate at a context/`max_new_tokens` budget the Mac can actually run in
  reasonable time.

### C. Experimental responsiveness — **DIAGNOSTIC-ONLY (D-039). NOT a selection gate.**

The generator is locked (D-034). This criterion **no longer gates model retention** and
**must never** be used to choose, reject, or replace a model. The feasibility screen and
any smoke run **record** the following as diagnostics, and nothing here is a pass/fail
condition on the model:

- how many benchmark items the model answers correctly (context for how large a
  switch-eligible set a future *pilot* would have — `RESEARCH_PLAN.md` §9, `a_u == correct`);
- whether the misleading-hint intervention appears to move any answer, in either
  direction (recorded as an observation, with the raw generations preserved).

**Explicitly:** a zero hint effect, zero answer switches, `adoption_increase ≈ 0`, no
disclosure effect, a zero cross-lingual gap, or near-chance base accuracy are all
**valid scientific outcomes** to be reported, **not** model failures and **not** grounds
to swap the model. True intervention responsiveness is a scientific question that will be
evaluated **only** in a separately pre-registered, adequately powered pilot (Phase 11) —
never inferred from this tiny non-scientific screen, and never used to pick a model.

### D. Language capability
- produces usable, coherent English text;
- produces usable Urdu, or at minimum reliably **follows** Urdu-language prompts/instructions
  even if generation quality is imperfect;
- Urdu outputs are interpretable by a native Urdu speaker (a qualitative screen — full
  native-validation methodology is Milestone 3's scope, `RESEARCH_PLAN.md` §14; here it
  is only "can a native speaker tell what the model is trying to say").

### E. Reproducibility
- deterministic decoding available, or the stochastic configuration (temperature, top-p,
  seed handling) is fully documented per `CLAUDE.md` §2.7;
- exact model revision/checkpoint hash pinned before any comparison run;
- exact local-runtime version (llama.cpp build / `transformers` version / GGUF
  quantization tool version, whichever applies) pinned before any comparison run.

### Explicit exclusion — what model retention must NOT depend on (D-039)

The locked generator (`Qwen/Qwen3-1.7B`, D-034) **must not** be replaced, and no model
**may ever** be chosen or rejected, on the basis of any of:

- hint-adoption magnitude / answer-switch rate / `adoption_increase` (in any direction)
- hidden-influence rate / `conditional_hidden_influence_rate`
- disclosure rate or any disclosure effect
- task accuracy (including near-chance accuracy)
- cross-lingual gap / Urdu-specific behaviour / monitor-validity gap
- monitor detection rate or monitor failure (any of the four monitors)
- a result being "interesting", "boring", preferred, or more publishable-looking

**A scientific null is not an infrastructure failure. Zero switches are not a model
failure. No disclosure effect is not a model failure. A zero Urdu gap is not a model
failure. All nulls are retained and reported.**

Model **replacement** is permitted **only** after a neutral, pre-scientific
**infrastructure** failure, and then only with a dated `literature/DECISION_LOG.md`
entry naming which one occurred:

- the model artifact is unavailable, or its download fails an integrity check
- the artifact is corrupted / the hash no longer matches
- runtime incompatibility (the pinned llama.cpp build cannot load or execute the file)
- an impossible resource requirement on the target machine (cannot allocate the memory
  it needs)
- a persistent crash across repeated invocations
- an unrecoverable parser/output-format failure that cannot be resolved transparently
  (note: the D-038 parser hardening already covers the known `<think>` /
  `[Start thinking]` case — a *flagged* `MALFORMED`/`EMPTY` span is a diagnostic, not
  by itself an unrecoverable failure)
- a license/access condition becomes invalid
- the exact revision / quantization / build cannot be pinned or reproduced

"Output usability" (Criterion B) can fail for one of these infrastructure reasons
**independently** of any scientific effect — e.g. the model systematically emits no
parseable answer letter at all. That is an infrastructure failure. A model that answers
cleanly but is simply unmoved by the hint is **not**.

## 4. Selection procedure

> **CLOSED (2026-09-10, D-034 / D-039).** Model selection is **done**: the Track-A
> generator is `Qwen/Qwen3-1.7B` (Q8_0 GGUF), locked on neutral pre-scientific grounds
> in D-034. The multi-candidate procedure below is the **historical** plan and is **not
> executed** — no candidate scoring, ranking, or choosing will take place. It is kept
> for provenance. Any future model change follows the neutral-infrastructure-failure
> rule in the "Explicit exclusion" box in §3, not this procedure.

*Historical plan (not executed):*

1. Screen 3–5 candidates on paper against §2 (`MODEL_SCREEN.md`).
2. Run the tiny feasibility benchmark (§5) on all screened candidates that pass the
   paper screen.
3. Score each candidate against criteria A, B, D, E (infrastructure readiness) using the
   benchmark's actual outputs. **Criterion C is diagnostic-only and is never scored as a
   pass/fail (§3, D-039).**
4. ~~Select the smallest/cheapest candidate that clears A/B/D/E and does not fail C by
   having zero measurable effect.~~ **Superseded** — the model is locked (D-034); a null
   hint effect is never a reason to reject a model.
5. If the locked model fails an **infrastructure** check (A/B/D/E — see the enumerated
   list in §3), document which one and escalate to the user before any replacement.

## 5. Tiny feasibility benchmark — design only, NOT run

Modeled on the two-stage timing-probe pattern already used for Track B
(`experiments/M1-English-Baseline/PRE_RUN_READINESS.md` §3, D-025), scaled down further
because this is a screen across *multiple* candidate models, not a single locked one.

### 5.1 Scope

- **Candidates:** the 3–5 models that pass the `MODEL_SCREEN.md` paper screen.
- **Items:** 3–5 questions per candidate (fixed, small, deterministic selection — reuse
  the existing MMLU pilot-selection machinery, `clsm.data`, restricted to a tiny `n`,
  so the selection rule is not invented ad hoc for this benchmark).
- **Conditions:** control + misleading-hint treatment (the same paired-prompt design as
  Track B, `clsm.interventions`), **English only** for this first pass.
- **Samples:** small `k`, e.g. 1–2 per (item, condition) — enough to see whether output
  is stable, not enough to estimate a rate with any precision.
- **Disclosure scoring:** not required for this benchmark — the point is runtime/parsing/
  trace-visibility, not a scientific disclosure estimate. A trace either visibly discusses
  the hint or it does not; a human skim is sufficient at this scale.

### 5.2 What it measures

runtime (wall-clock per generation on this Mac); parsing (does `clsm.extraction` recover
a valid answer letter); trace visibility (is there a reasoning span to score at all);
latency (acceptable for iterative dev, not for a real pilot's scale); memory (peak RSS).
It also **records, as a diagnostic only (D-039)**, whether the hint appears to move any
answer — this is never a pass/fail on the model and never a selection input (§3 C, §5.4
G5).

### 5.3 What it explicitly does NOT do

No hypothesis test. No scientific claim of any kind. No publication-level metric
(no `answer_switch_rate`, `disclosure_rate`, `hidden_influence_rate`, or
`conditional_hidden_influence_rate` — added 2026-09-06, `literature/DECISION_LOG.md`
D-031 — computed or reported from this benchmark's output — exactly as Track B's timing
probe does not compute scientific metrics, `PRE_RUN_READINESS.md` §3.4). Its numbers are
**operational** only and must never be cited as evidence about cross-lingual
monitorability.

### 5.4 GO / NO-GO criteria (design only)

| # | Criterion | Consequence if failed |
|---|---|---|
| G1 | Model loads and completes all generations without crash/OOM on this Mac | candidate eliminated from further screening |
| G2 | Per-generation latency is within an iterative-development budget (ceiling set once G1-passing candidates' actual numbers exist — not guessed now) | candidate flagged, not automatically eliminated (a slower model may still be usable for a small pilot) |
| G3 | Answer-extraction succeeds (`ParseStatus.VALID`) on a majority of generations | candidate eliminated unless a prompt-format fix (not a scientific change) resolves it, then re-probed |
| G4 | A reasoning/explanation span is present and readable in the large majority of generations | candidate eliminated — nothing for the disclosure paradigm to score |
| G5 | **DIAGNOSTIC-ONLY (D-039) — NOT a GO/NO-GO gate.** Whether the hint appears to move any item's answer, in either direction, is **recorded** (with raw generations preserved) as an observation. | **No consequence for the model.** A zero hint effect is a valid scientific null, retained and reported — never a reason to flag, weigh-against, or replace the locked model. Genuine intervention responsiveness is measured only in the pre-registered pilot (Phase 11). |

A NO-GO on G1/G3/G4 for **every** screened candidate would be reported to the user as a
genuine feasibility problem for Track A at this model scale — not silently worked around
by lowering the candidate-class floor without a documented reason.

## 6. Quantization policy for Track A (Task 8)

The **Track B** baseline is unchanged and is not touched by this document:
`configs/milestone1/runtime.yaml` remains `dtype: bfloat16`, `quantization: none`
(`literature/DECISION_LOG.md` D-023/D-024).

For **Track A only**, quantization is an open methodological question, not a settled
choice:

- **Why it may be necessary:** several screened candidates may exceed comfortable
  full-precision (fp16/bf16) memory/latency budgets on a 32 GB Intel Mac once activation
  memory, the OS, and the runtime's own overhead are accounted for, even though their
  raw weight size alone would fit. Quantization (e.g. GGUF Q4_K_M/Q5_K_M/Q8_0 for a
  llama.cpp-style runtime, or a `bitsandbytes`/AWQ scheme for a `transformers`-CPU path)
  is a plausible way to make a candidate fit or run faster.
- **Exact quantization format/level:** `TODO — DECISION REQUIRED`. Not selected here.
  Any selection happens only after the runtime is chosen (`READINESS.md`) and is
  recorded, with its exact format/bit-width and the tool/version that produced it, in a
  dated `literature/DECISION_LOG.md` entry before any comparison run.
- **Potential effect on model behavior:** quantization changes numerics and can change
  which answer a model gives, how coherent its reasoning trace is, and how sensitive it
  is to the hint. A quantized Track-A number is a statement about *that quantized
  checkpoint*, not about the base model.
- **Fixed within a comparison:** whatever quantization level is chosen must be held
  **fixed across all conditions being compared** in a given Track-A experiment (no mixing
  quantization levels between control/treatment, or between languages, within one
  primary comparison). Ablating quantization level itself is allowed only as an
  explicitly labelled robustness check, never as the primary result.
- **No mixing within the primary experiment:** restated — a single Track-A pilot uses one
  quantization level (or none) for every condition it reports as its primary result.
- **Future full-precision replication:** if/when resources permit (a GPU becomes
  available, or a future Mac has more usable memory bandwidth), a full-precision
  (fp16/bf16) rerun of the same Track-A protocol is planned as a check on whether
  quantization changed the measured effect — this is a **future work** item, not
  scheduled.

No quantization level is chosen in this document for the general Track-A policy above.

**Update (2026-09-06, Gate B):** for the specific Gate-B/C smoke-test model,
`Qwen/Qwen3-1.7B`, the quantization question above **has** been resolved: `Q8_0`,
because it is the only quantization the official GGUF repo publishes for it (see
`READINESS.md` §1.7, §3; `literature/DECISION_LOG.md` D-034). This resolves the
question for that one candidate only — the general policy for the other four screened
candidates, and the quantization-change triggers (pre-scientific/infrastructure
reasons only — `READINESS.md` §3), are unchanged by this update.

## 7. The future Mac experiment pipeline (Task 9 — design only)

Unchanged in *structure* from the project's four-monitor design (`RESEARCH_PLAN.md`
§16; `experiments/EXPERIMENT_SPEC.md` §6); restated here for the Mac-scale execution:

```
English reasoning         → misleading-hint intervention → monitoring (English judge)
Urdu reasoning             → misleading-hint intervention → direct monitoring (in-language judge)
Urdu reasoning             → native Urdu human judgment
Urdu reasoning             → translate to English → English monitor (translate-then-monitor)
```

Then compare: task behavior (accuracy, adoption/switch rate); hint adoption; observable
disclosure; automated monitor judgment; native human judgment; translate-then-monitor
judgment. The primary cross-lingual quantity remains the **monitor-validity gap**
(`RESEARCH_PLAN.md` §9), computed identically to Track B's definition — only the
generator model and execution environment differ.

**Distinguish explicitly, at every reporting stage (Task 9):**

| | Quantity | Where it is measured |
|---|---|---|
| A | model behavior | task accuracy, answer-switch rate |
| B | reasoning verbalization | disclosure rate (does the CoT mention the hint) |
| C | monitor/judge behavior | automated monitor detection rate (English / in-language / translate-then-English) |
| D | human validation | native Urdu human judgment (ground truth) |

This four-way distinction is unchanged from the project's core design and is *why*
Track A is a legitimate methodology-validation track rather than a different study: it
exercises the same A/B/C/D separation, just at a scale the Mac can execute.

No dataset, translation system, or judge model is selected for this pipeline yet; those
remain the same open decisions (`RESEARCH_PLAN.md` §28, U1–U17) the project already
tracks, now inherited by Track A as well as Track B.

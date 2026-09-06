# M1-Mac-Feasibility — Resource-Constrained Track (overview)

**Status:** PLANNING ONLY. No model downloaded, no dataset downloaded, no inference run,
no results exist. This directory documents a **new, separate experimental track**; it
does not replace, delete, or retroactively edit `experiments/M1-English-Baseline/`
(the original GPU-based Milestone-1 design), which remains intact and is now the
**deferred replication track** (Track B — see below).

---

## 0. Why this track exists

`literature/DECISION_LOG.md` D-020/D-027 already recorded that the project's development
machine — a 2019 Intel MacBook Pro (i7-9750H, 32 GB RAM, AMD Radeon Pro 5300M 4 GB, no
NVIDIA GPU, no CUDA) — cannot run the original GPU design (`DeepSeek-R1-Distill-Qwen-7B`,
BF16, vLLM, CUDA, NVIDIA L4/A100). That finding is a **hardware fact**, not a change of
mind about the science, and it is not reversed here.

This track is the project's answer to that constraint: keep the **research question and
measurement-validity design** unchanged, and re-scope **execution** (model size, runtime,
scale) to what is actually runnable on the user's Mac, while being explicit — in every
document this track produces — that results at this scale are a **methodology and
infrastructure validation**, not a claim about frontier-reasoning-model behavior.

See `literature/DECISION_LOG.md` D-028 onward for the dated decision record.

## 1. Two tracks, going forward

| | **Track A — Resource-Constrained Mac Study** | **Track B — Larger-Model GPU Replication** |
|---|---|---|
| Directory | `experiments/M1-Mac-Feasibility/` (this one) | `experiments/M1-English-Baseline/` (unchanged) |
| Status | **active development** | **deferred** until GPU resources are available |
| Model class | sub-1B–~3B open-weight, CPU/Mac-runnable (screening only so far — `MODEL_SCREEN.md`) | `DeepSeek-R1-Distill-Qwen-7B`, BF16, vLLM, CUDA, NVIDIA L4/A100 (unchanged; `configs/milestone1/runtime.yaml`) |
| Purpose | test the measurement framework locally; validate English→Urdu→translate-back methodology and native-Urdu-comparison methodology at small scale | replicate the same methodology on a frozen larger reasoning model once GPU compute is available |
| Relationship | **does not** invalidate or supersede Track B | remains the **stronger** future replication and the track the paper's headline claim (if any) should ultimately rest on |

Track A is **not** a cheaper substitute for Track B. It exists to let development,
pipeline validation, and English/Urdu methodology work continue now, on hardware the user
actually has, while Track B waits for GPU access. Both tracks read the *same* frozen
research questions, hypotheses (`RESEARCH_PLAN.md` §6–§8), and operational definitions
(`RESEARCH_PLAN.md` §9); they differ only in model scale and execution environment.

## 2. Revised scope statement for Track A

**Working title:** *"Cross-Lingual Reliability of Reasoning Monitors Under
Resource-Constrained Inference."*

**Primary purpose (Track A only):**
- test the measurement framework (hint injection, disclosure scoring, the four-monitor
  design) end-to-end on hardware the user controls;
- evaluate whether cross-lingual monitorability differences of the kind the project
  studies are even *observable* under small-model conditions;
- validate the English → Urdu → translate-back monitoring methodology mechanically
  (does the pipeline run, parse, and log correctly across that path?);
- validate the native-Urdu-human-comparison methodology (annotation protocol, rubric,
  blinding procedure) independent of which model produced the traces being annotated.

**Explicit limitation (must appear wherever Track A results are reported):** results
from a sub-3B model are **not** assumed to generalize to frontier reasoning models
(DeepSeek-R1-class, GPT-5-class, Claude-class). A small model may fail to reason
coherently in Urdu at all, may fail to produce a usable chain-of-thought, or may be
insensitive to the hinting intervention for reasons that have nothing to do with
cross-lingual monitorability (see `MODEL_SCREEN.md`, `READINESS.md` §4 GO/NO-GO). Any
Track A finding is reported as **methodology validation and a small-model data point**,
never as evidence about frontier-model cross-lingual monitorability. Larger-model
replication (Track B) remains necessary before any claim about frontier reasoning models.

Compute constraints changed the **execution scale**, not the **research question**: the
primary research question (`RESEARCH_PLAN.md` §6), the five hypotheses H1–H5, the
four-monitor design, and the A-vs-B (model unfaithfulness vs. monitor failure)
distinction are unchanged and apply identically to both tracks.

## 3. What is NOT decided by this document

- No model is chosen (`MODEL_SCREEN.md` — screening only, criteria in `EXPERIMENT_SPEC.md` §4).
- No Mac runtime (llama.cpp / transformers-CPU / other) is chosen (`READINESS.md` §3).
- No quantization level is chosen (`EXPERIMENT_SPEC.md` §6).
- No inference has occurred, no weights or datasets have been downloaded
  (`READINESS.md` §1–§2).

## 4. Contents of this directory

- `README.md` — this file: why the track exists, the two-track framing, revised scope.
- `EXPERIMENT_SPEC.md` — model-selection criteria (pre-registered), quantization policy,
  the future four-condition Mac pipeline, the tiny non-scientific feasibility benchmark
  design.
- `MODEL_SCREEN.md` — 3–5 candidate small open-weight models, screened on paper only
  (license, multilingual/Urdu evidence, context length, memory class, runtime options,
  reasoning-trace elicitability) — no winner selected.
- `READINESS.md` — Mac runtime-architecture options (Intel Mac, not Apple Silicon),
  compatibility research, and the overall GO/NO-GO checklist for the tiny feasibility
  benchmark (design only — not run).

## 5. Relationship to the existing harness

`src/clsm/` (schemas, metrics, disclosure, pipeline) is shared by both tracks — the
metric definitions, denominators, and majority-vote / tie policy
(`literature/DECISION_LOG.md` D-018) do not change because the model is smaller. Any
Mac-track-specific code (a CPU/llama.cpp generation backend, a Mac-specific config
group) is a *new* module alongside the existing `clsm.generation.VLLMBackend`, added
only when this track is authorized to write code — not yet.

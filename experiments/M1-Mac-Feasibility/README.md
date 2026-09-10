# M1-Mac-Feasibility — Resource-Constrained Track (overview)

**Status (2026-09-10):**
- **Infrastructure:** complete. Gates A/B/C done on the Apple M5 (`READINESS.md` §0);
  generator locked (`Qwen/Qwen3-1.7B` Q8_0, D-034/D-037); pinned llama.cpp built for
  arm64 (D-036); one synthetic infrastructure Gate-C smoke passed (D-040).
- **Scientific protocol:** **methodology FROZEN, execution BLOCKED** (2026-09-10,
  D-041…D-049, **as amended by D-050…D-063 after independent review — pre-outcome**).
  The Track-A English hint-faithfulness pilot is fully specified (`PILOT_PROTOCOL.md`),
  sensitivity-analysed (`POWER_ANALYSIS.md` — **no confirmatory N or SESOI is frozen**,
  D-058), and implemented + mock-validated (`clsm.track_a_backend`, `clsm.track_a_run`,
  `clsm.track_a_manifest`). A **technically-enforced fail-closed run gate**
  (`clsm.track_a_run`, D-050) means no real generation can occur without an authorized
  `RunToken`. The run is blocked by **external resources** — a dataset content pin
  (D-056), a disclosure judge, a blinded human audit, and an ethics determination
  (`MONITOR_VALIDATION_PROTOCOL.md`, `PILOT_PREREGISTRATION.md`).
- **Scientific data:** **none.** No dataset downloaded, no scientific generation, no
  metric computed, no human annotation. **No run is authorized** — only the user
  authorizes one, after review.

This directory documents a **separate experimental track**; it does not replace or edit
`experiments/M1-English-Baseline/` (the GPU-based Milestone-1 design), which remains the
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

## 3. What is (and is NOT) decided as of this writing

**Decided:**
- the Mac runtime is llama.cpp, built from pinned commit
  `5266f24da75dc449bd56cbed7addb9c8e4a6a73e` (tag `v0.4.0`), CPU-only
  (`-DGGML_METAL=OFF`), locally installed and verified — Gate A, complete 2026-09-06
  (`READINESS.md` §0, §1.6; `literature/DECISION_LOG.md` D-033).
- exactly one Gate-B/C **smoke-test** model has been downloaded and verified:
  `Qwen/Qwen3-1.7B`, GGUF `Qwen3-1.7B-Q8_0.gguf`, selected on neutral
  hardware/methodology/provenance criteria only, with no inference having occurred on
  any candidate before selection — Gate B, complete 2026-09-06 (`READINESS.md` §0,
  §1.7; `literature/DECISION_LOG.md` D-034). **This is not the Gate-D scientific
  winner** — see `MODEL_SCREEN.md`'s 2026-09-06 update.

**Still NOT decided:**
- **Model selection is CLOSED, not pending (D-034/D-039):** the generator is locked to
  `Qwen/Qwen3-1.7B`. The former "Gate-D scientific winner" screen is **not** run —
  no model is chosen or rejected on any behavioural/scientific outcome
  (`EXPERIMENT_SPEC.md` §3/§4; Criterion C / G5 are diagnostic-only).
- No general Track-A quantization policy for the other four *screened* candidates
  (`EXPERIMENT_SPEC.md` §6; `READINESS.md` §3) — Q8_0 is locked for Qwen3-1.7B.
- **No scientific dataset has been downloaded; no scientific inference has been run; no
  scientific metric has been computed.** The only real generation is the synthetic
  infrastructure Gate-C smoke (`READINESS.md` §1.8, D-040). A scientific pilot requires
  a frozen `PILOT_PREREGISTRATION.md` (still a DRAFT with open `TODO`s).

## 4. Contents of this directory

- `README.md` — this file: why the track exists, the two-track framing, revised scope.
- `EXPERIMENT_SPEC.md` — model-selection criteria (pre-registered), quantization policy,
  the future four-condition Mac pipeline, the tiny non-scientific feasibility benchmark
  design.
- `MODEL_SCREEN.md` — 3–5 candidate small open-weight models, screened on paper only
  (license, multilingual/Urdu evidence, context length, memory class, runtime options,
  reasoning-trace elicitability) — no winner selected.
- `READINESS.md` — Mac runtime architecture: the **historical Intel** environment and
  the **current Apple M5 (arm64)** environment (§0), the authorization-gate sequence
  (Gate A–D) and per-gate records (Gate A §1.6/§1.6.2, Gate B §1.7/§1.7.1, Gate C §1.8),
  runtime-option research, quantization policy.
- `REASONING_MARKER_FORENSICS.md` — no-inference audit (D-038) of where reasoning-span
  markers come from: the model emits literal `<think>…</think>`; `[Start thinking]` is a
  pinned-llama.cpp CLI presentation transform.
- `PILOT_PREREGISTRATION.md` — **DRAFT, NOT FROZEN** scaffold for the future Track-A
  scientific pilot: freezes the decided items, marks every open design choice
  `TODO — DECISION REQUIRED`. No scientific run is authorized.
- `environment_checks/` — dated, non-scientific provenance records: Intel preflight +
  Gate A (2026-09-06), Intel Gate B (2026-09-06), M5 Gate A (2026-09-08), M5 Gate B
  (2026-09-10), M5 Gate C synthetic smoke (2026-09-10). Infrastructure provenance only;
  none is scientific data.
- `fixtures/` — `smoke_questions.jsonl`, 5 hand-written synthetic MCQ items for
  infrastructure testing only. Not MMLU, not GPQA, no scientific value.
- `run_feasibility.py` — the feasibility-screen entrypoint. Its default (`--dry-run`)
  mode exercises the full harness plumbing against `MockFeasibilityBackend` (TEST-ONLY);
  `--real` refuses unconditionally — Gate A (runtime installation) is complete, but
  Gates B–D (`READINESS.md` §0) are not.
- `runtime.local.example.yaml` — a documented (not code-validated) template recording
  the locked runtime (llama.cpp, pinned commit) alongside the still-`UNSELECTED`
  model/quantization fields and the gate status.
- `feasibility_runs/` (git-ignored) — output of `run_feasibility.py`; never `results/`.

## 5. Relationship to the existing harness

`src/clsm/` (schemas, metrics, disclosure, pipeline) is shared by both tracks — the
metric definitions, denominators, and majority-vote / tie policy
(`literature/DECISION_LOG.md` D-018) do not change because the model is smaller.
`src/clsm/feasibility.py` is Track-A-specific scaffold code: a deliberately **separate**
data model (`FeasibilityRecord`, not `GenerationRecord`) so a feasibility-screen output
can never be passed into `clsm.metrics.compute_metrics` by accident (verified by a
dedicated test, `tests/test_feasibility.py`). A CPU/llama.cpp real backend
(implementing `clsm.feasibility.FeasibilityBackend`) is a *new* module added only once
Gate A/B are authorized — not yet; only the TEST-ONLY mock exists today.

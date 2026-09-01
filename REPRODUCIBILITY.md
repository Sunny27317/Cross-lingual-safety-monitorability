# Reproducibility Plan

**Status:** infrastructure specification. No experiment has run; no provenance record
exists yet. This document defines what MUST be captured once experiments begin.
**Derived from:** `literature/RUN2_BLUEPRINT.pdf` Phase 12, plus `CLAUDE.md` §2.7.
**Binding rule:** *No experimental output may exist in this repository without a
traceable provenance record.* A result file with no linked provenance is treated as
fabricated and must be deleted.

---

## 1. Environment capture

| Item | Requirement |
|---|---|
| Python | Single pinned version (e.g. 3.11.x); recorded in `pyproject.toml` / `.python-version`. `TODO — DECISION REQUIRED`: exact minor version. |
| Dependency manager | `uv` (preferred) or `conda`; a **fully pinned** lockfile committed (`uv.lock` / `requirements.txt` with hashes). Blueprint says "uv/conda + pinned requirements.txt". |
| Inference engine | vLLM (blueprint). Version pinned. Record CUDA / driver version. |
| Config management | Hydra / OmegaConf. Every run resolves a single composed config; the resolved config is saved with the run. |
| OS / kernel | captured in the run manifest (`platform.platform()`). |
| Hardware | GPU model, count, VRAM; CPU; RAM; whether Colab / rented A100 / lab node. Captured per run. |
| Determinism | deterministic decoding option available and recorded (on/off); note vLLM/CUDA nondeterminism caveats explicitly. |
| `make reproduce` | a target that re-runs a named experiment from its config + seed and re-checks the recorded metrics within tolerance. |

## 2. Model provenance (per model, per run)

- exact model name + Hugging Face repo id
- **revision / commit hash** of the HF repo (not just the tag) — `TODO — IMPORT/VERIFY`
  for every model in `experiments/EXPERIMENT_SPEC.md` §2 (U4)
- quantization (none / 4-bit / 8-bit) and the exact quantization config
- tokenizer revision
- chat template / `<think>` handling used
- download timestamp + SHA256 of the weights snapshot where feasible (or the HF
  revision hash as the minimum)

## 3. Dataset provenance (per dataset, per run)

- exact name, source URL, version / HF revision / git commit
- split and item ids used (store the id list, not just a count)
- license + any usage restrictions (GPQA has restrictions — verify before redistribution)
- for translated items: MT system + version, native-corrector id(s), correction diff,
  back-translation audit result, acceptance decision per item
- contamination / paraphrase-check status
- checksum of the exact item file consumed by the run

## 4. Prompt & intervention provenance

- every prompt **template** stored as a versioned file; the run records the template
  path + a hash of the fully-rendered prompt per item
- intervention/cue: type, exact injected text, position, and the control counterpart
- monitor prompts (English judge, in-language judge, translate-then-monitor, native-human
  rubric) stored as versioned files; the human rubric must match the automated judge
  instructions as closely as possible and any divergence is documented

## 5. Decoding / sampling configuration (per run)

temperature · top-p · top-k · max tokens · repetition penalty · stop sequences ·
n samples per item · **random seed list** (recorded, never chosen after seeing results) ·
batch size (if it affects outputs) · vLLM version.
`TODO — DECISION REQUIRED` (U10): the canonical decoding config + seed list for
Milestone 1.

## 6. Experiment identity & logging

- **Experiment ID:** `M<milestone>-<shortname>-<YYYYMMDD>-<git7>` (e.g.
  `M1-en-hint-baseline-20260915-a1b2c3d`).
- Each experiment lives in `experiments/<experiment-id>/` containing:
  - `README.md` — objective, **pre-registered confirmatory analysis** (written before
    data), hypotheses, success/failure criteria
  - `config/` — the resolved Hydra config(s)
  - `PROVENANCE.md` / `manifest.json` — every field in §§2–5, plus code commit,
    UTC start/end timestamps, environment block, operator
  - `analysis/` — deterministic analysis scripts + their outputs
  - links to raw outputs (in `data/` or an external store) and processed outputs (in
    `results/`)
- **Structured JSONL logging** (blueprint): one line per generation with at least
  `{experiment_id, model, model_revision, language, dataset, item_id, cue_type, seed,
  temperature, prompt_hash, timestamp, answer, cot, raw_output}`.
- Logging backend: CSV or Weights & Biases (blueprint offers either). If W&B, the run URL
  and a local export are both stored.

## 7. Raw vs. processed outputs

| Layer | Location | Rule |
|---|---|---|
| Raw generations | `data/generations/<experiment-id>/*.jsonl` (git-lfs or DVC if large; else a documented external store + manifest) | never edited by hand; append-only |
| Monitor outputs | `data/monitor/<experiment-id>/*.jsonl` | includes monitor id, prompt hash, rationale |
| Native annotations | `data/annotations/<experiment-id>/*.jsonl` | raw per-annotator; never model-filled |
| Processed / metrics | `results/<experiment-id>/*.{json,csv}` | must record the raw-input checksums + analysis script commit that produced them |
| Figures | `figures/<experiment-id>/*` | reproducible from `results/` + a committed script |

`results/` currently contains only its `README.md` and must stay free of any value not
produced by a real run.

## 8. Provenance requirements (the minimum bar — from `CLAUDE.md` §2.7)

model name · exact model ID/version/revision/hash · dataset · dataset version/split ·
language · full prompt(s) · intervention/condition · decoding config · random seed ·
temperature · top-p · max tokens · environment info · code commit hash · UTC timestamp ·
evaluation configuration (judge model + version, rubric, parsing rules).

An experiment without all applicable fields is **not finished** and its numbers may not
be reported.

## 9. Directory layout (reconciliation with the blueprint)

The blueprint's `xling-monitor/` tree (`RUN2_BLUEPRINT_HANDOFF.md` §19) maps onto the
Milestone-0 layout as:

| Blueprint dir | This repo |
|---|---|
| `data/` | `data/` |
| `src/` | `src/` |
| `models/` | `configs/model/` + loader code in `src/generation/` |
| `experiments/` | `experiments/` |
| `configs/` | `configs/` |
| `notebooks/` | (optional) `notebooks/`, gitignored outputs |
| `evaluation/` | `src/evaluation/` |
| `statistics/` | `src/statistics/` |
| `results/` | `results/` |
| `figures/` | `figures/` |
| `paper/` | `paper/` |
| `tests/` | `tests/` |

New directories are created **when a milestone needs them**, not preemptively
(`DECISION_LOG.md` D-008).

## 10. Secrets & data hygiene

- No API keys, tokens, or credentials in the repo. HF / W&B / API tokens go in a
  gitignored `.env` (already covered by `.gitignore`).
- Native-annotator personal data is not committed; annotators are referred to by an id.
- Large model weights and large generation dumps are never committed to git directly.

## 11. Milestone-1 pinned artifacts (as of 2026-09-01)

| Artifact | Pin | Status |
|---|---|---|
| Generator model | `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` @ `916b56a44061fd5cd7d6a8fb632557ed4f724f60` | SOURCE-CODE-VERIFIED (HF API); re-confirm at run time |
| **MMLU dataset** | `cais/mmlu` @ **`c30699e8356da336a370243923dbaf21066bb9fe`** (branch `main`; MIT) | VERIFIED via HF refs API 2026-09-01 (D-019) |
| MMLU parquet-convert branch | `d183e18c31b6d5563d00fb87257819c64e76b985` | recorded for parquet loads |
| Disclosure judge | not selected — only a licence/context screen done | ⚠️ UNRESOLVED (D-021 rev.) — lock milestone in `PRE_RUN_READINESS.md` §4.2 |
| Execution environment | `configs/milestone1/runtime.yaml` — Linux x86_64, Python 3.11, CUDA 12.4, **GPU min NVIDIA L4 24 GB** (A100 pref), **bf16, quantization: none**; **T4 excluded** (D-024); not the dev machine | specified (D-020/D-023/D-024) |
| `[run]` deps (`vllm 0.8.5.post1`/`torch 2.6.0`/`transformers 4.51.3`/`datasets 3.5.0`) + `uv.lock` | **proposed** in `runtime.yaml` (compatibility-driven, not newest); confirm on the box (§2.3), `uv lock` (§2.4), commit | ❌ UNRESOLVED |

## 12. Open reproducibility decisions

`TODO — DECISION REQUIRED`: exact Python minor version on the GPU box; git-lfs vs. DVC
for `data/`; CSV vs. W&B; the finalized `[run]` version set (locked on the box, §2.3);
whether to pin generator weights by SHA in addition to the HF revision hash.

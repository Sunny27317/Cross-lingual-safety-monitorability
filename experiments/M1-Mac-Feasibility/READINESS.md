# READINESS.md — Track A Mac runtime architecture (design only, nothing installed)

**Status:** RESEARCH ONLY. Nothing in this document has been installed, downloaded, or
run. It documents runtime *options* for the machine actually available:

| Property | Value |
|---|---|
| Model | 2019 MacBook Pro |
| CPU | Intel Core i7-9750H (6c/12t) |
| RAM | 32 GB |
| GPU | AMD Radeon Pro 5300M, 4 GB VRAM |
| Architecture | **x86_64 (Intel), not Apple Silicon (ARM64)** |
| OS | macOS (Darwin) |
| CUDA | none |

**This is an Intel Mac. Every recommendation below is qualified by that fact — nothing
here assumes Apple Silicon.** This distinction matters because several popular
"run LLMs on your Mac" toolchains (most notably Apple's own MLX) are Apple-Silicon-only
and do not run at all on this machine.

---

## 1. Runtime options considered

### 1.1 llama.cpp (+ GGUF quantized models)

| Aspect | Assessment |
|---|---|
| Intel Mac compatibility | **Yes.** llama.cpp's CPU backend targets x86_64 generically (AVX/AVX2/FMA on Intel); it does not require Apple Silicon or CUDA. This is a general-purpose C/C++ CPU inference engine, not GPU-specific. |
| Model-format requirement | Requires conversion to **GGUF**; most popular open-weight models (Qwen, Llama, Gemma, Phi families) have community or vendor-published GGUF conversions, but a candidate not yet converted would need local conversion (adds a step + a place to introduce silent error if not verified). |
| Quantization implications | GGUF's primary use case *is* quantization (Q4_K_M, Q5_K_M, Q8_0, etc.) — this is the natural path to the quantization policy in `EXPERIMENT_SPEC.md` §6. Full fp16 GGUF is also possible but defeats much of llama.cpp's CPU-speed advantage. |
| Reproducibility implications | The exact GGUF file (its own hash), the exact llama.cpp build/commit, and the exact quantization scheme all need pinning — three additional provenance fields beyond the base-model revision (`REPRODUCIBILITY.md` §2 would need a Track-A addendum). |
| Ease of pinning versions | Moderate: llama.cpp is under very active development; a specific release tag or commit hash must be pinned, and GGUF format has changed across llama.cpp history (older GGUF files can become incompatible with newer builds) — this must be checked at selection time, not assumed. |
| Reasoning traces capturable? | Yes — llama.cpp returns raw text completions; whatever the model emits (a `<think>` block, a numbered chain) is captured exactly like any other text output. |
| Seeded generation supported? | Yes — llama.cpp exposes an explicit `--seed` and standard sampling parameters (temperature, top-p, top-k), comparable in spirit to the vLLM decoding config already used for Track B. |
| Expected tradeoffs | Best-documented, most widely used pure-CPU-inference path for this exact hardware class; quantization is close to mandatory for larger candidates to run at acceptable speed; ecosystem moves fast, so version pinning needs active attention. |

### 1.2 MLX

| Aspect | Assessment |
|---|---|
| Intel Mac compatibility | **NO — explicitly unsupported.** MLX is designed around Apple Silicon's unified-memory architecture and does not run on Intel Macs (verified via a 2026-09-06 web check of Apple's own MLX materials and third-party MLX guides; a CUDA backend was added to MLX in early 2026, but that targets NVIDIA GPUs, not Intel-Mac CPUs, and does not change Intel-Mac status). |
| Recommendation | **Do not use MLX for this track.** Recorded here specifically because the task instructions warn against assuming MLX compatibility without verification — it is verified *incompatible*, not merely unverified. |

### 1.3 `transformers` (Hugging Face) on CPU

| Aspect | Assessment |
|---|---|
| Intel Mac compatibility | **Yes**, via the PyTorch CPU backend. `literature/DECISION_LOG.md` D-020 already established that PyTorch dropped macOS-x86 GPU-relevant wheels after `torch 2.2.2`, but a **CPU-only** PyTorch install is a different, still-supported path on Intel macOS — this needs re-confirming at selection time (exact latest CPU-wheel version available for this Python/macOS combination), not assumed from the GPU-wheel finding in D-020. |
| Model-format requirement | Native — no conversion needed; runs the same safetensors/HF checkpoint used on GPU, just on the CPU device. |
| Quantization implications | `bitsandbytes` GPU-oriented quantization is not applicable on CPU; CPU-relevant options are more limited (e.g. `torch.quantization` dynamic quantization, or simply running at fp32/bf16 CPU and accepting the memory/speed cost). This makes `transformers`-CPU the *least* quantization-friendly of the three options screened. |
| Reproducibility implications | Simplest provenance story (same HF revision hash as any other `transformers` usage; no separate quantization-tool version to pin) if run unquantized. |
| Ease of pinning versions | Easy — `transformers`/`torch` versions pin exactly as they already do for the Track-B `[run]` extra, just a CPU wheel instead of a CUDA wheel. |
| Reasoning traces capturable? | Yes — identical generation/decoding interface to any other `transformers` usage. |
| Seeded generation supported? | Yes — standard `torch.manual_seed` / `generation_config` seeding. |
| Expected tradeoffs | Likely the **slowest** of the three options for a given model size on this CPU (no CPU-specific inference optimizations the way llama.cpp has); simplest to reason about provenance-wise; best fallback if a candidate has no usable GGUF conversion. |

### 1.4 Other options considered and set aside for now

- **ONNX Runtime** — plausible for the Phi family specifically (Microsoft ships ONNX
  builds), but adds a third distinct runtime/provenance story for only one candidate;
  not adopted as a primary option, but not ruled out if Phi-4-mini screens well and its
  ONNX build offers a meaningful CPU speed advantage over `transformers`-CPU.
- **Ollama** — in practice a llama.cpp-based wrapper with a friendlier CLI/model-registry
  layer; considered equivalent to §1.1 for compatibility purposes, but its model registry
  and default quantization choices are less directly inspectable/pinnable than driving
  llama.cpp (or a GGUF file) directly. Not adopted as the primary runtime, but noted as a
  fallback if raw llama.cpp integration proves harder than expected.

## 2. Recommendation (not a decision — for discussion at selection time)

**llama.cpp + GGUF** is the strongest fit for this Intel Mac given the candidate class in
`MODEL_SCREEN.md` (models likely to need quantization to run comfortably in 32 GB
alongside everything else, and a runtime built specifically for consumer-CPU inference).
**`transformers`-CPU** is the natural fallback for any candidate without a trustworthy
GGUF conversion, or if full-precision Track-A numbers are wanted as a reference point
against a quantized run (`EXPERIMENT_SPEC.md` §6, "future full-precision replication").
**MLX is excluded** — verified incompatible with this hardware, not merely deprioritized.

**No runtime is selected yet.** This is a recommendation to weigh once the feasibility
benchmark (`EXPERIMENT_SPEC.md` §5) is authorized, not a locked choice.

## 3. Overall Track-A GO / NO-GO checklist (design only)

This restates and consolidates the gates already defined in `EXPERIMENT_SPEC.md` §5.4,
as the single place to check before requesting authorization for the tiny feasibility
benchmark:

| Step | Gate | Status |
|---|---|---|
| Model screen | ≥1 candidate in `MODEL_SCREEN.md` clears the license + candidate-class checks on a primary-source re-read | **not done** — current screen used secondary sources only |
| Runtime selection | a runtime chosen from §1 above, with its version pinned | **not done** |
| Download authorization | user explicitly authorizes downloading a specific model weight + specific runtime/tool versions | **not requested** |
| Tiny feasibility benchmark | run per `EXPERIMENT_SPEC.md` §5; G1–G5 evaluated with real numbers | **not run** |
| Model-selection decision | criteria A–E scored per candidate; a dated `literature/DECISION_LOG.md` entry records the choice (or the "no candidate cleared" outcome) | **not done** |

Nothing past "model screen" has started. This document, `MODEL_SCREEN.md`, and
`EXPERIMENT_SPEC.md` are the complete state of Track A as of this writing.

# READINESS.md — Track A Mac runtime architecture

**Status:** Runtime research and design, PLUS the completed Gate-A runtime installation
(§1.6 — llama.cpp built and locally verified, 2026-09-06). No model has been
downloaded, no dataset has been downloaded, and no inference has occurred anywhere in
this document's history. It documents runtime *options* for the machine actually
available:

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

Observed-machine facts (confirmed, not assumed) are archived in
`environment_checks/2026-09-06-intel-mac-runtime-preflight.txt` — a non-destructive,
read-only preflight (no install, no download).

## 0. Authorization gates (sequential — do not skip ahead)

Everything past model/runtime screening requires explicit, sequential authorization.
Each gate below is a distinct, separately-authorized step:

| Gate | What it authorizes | Status |
|---|---|---|
| **Gate A** | Runtime installation (build/verify llama.cpp locally) | **✅ AUTHORIZED AND COMPLETE (2026-09-06)** — see §1.6 below and `environment_checks/2026-09-06-llamacpp-gate-a.txt` |
| **Gate B** | Model-weight download (exactly ONE model, selected on neutral criteria) | **✅ AUTHORIZED AND COMPLETE (2026-09-06)** — `Qwen/Qwen3-1.7B-GGUF` (Q8_0), see `environment_checks/2026-09-06-gate-b-model-download.txt` |
| **Gate C** | A single-model tiny smoke run (infrastructure plumbing check on ONE real candidate, analogous to Track B's Stage-A smoke, `M1-English-Baseline/PRE_RUN_READINESS.md` §3.0) | **NOT AUTHORIZED** |
| **Gate D** | The multi-candidate tiny feasibility screen (`EXPERIMENT_SPEC.md` §5, G1–G5) across all screened candidates | **NOT AUTHORIZED** |

**Gates A and B are complete; Gates C and D remain unauthorized and unreached.** A
runtime **implementation** exists (built and locally verified — §1.6), and exactly ONE
model has been downloaded and verified (Qwen3-1.7B, Q8_0 GGUF — selected on neutral,
pre-scientific hardware/methodology/provenance criteria, with no inference having
occurred on any candidate before selection). This does **not** mean the scientific
study is "ready": no quantization *comparison* has occurred, and — critically — no
inference of any kind has occurred with this or any model. The feasibility *runner*
(`experiments/M1-Mac-Feasibility/run_feasibility.py`, `src/clsm/feasibility.py`) has
been written and self-tested end-to-end against `MockFeasibilityBackend` only — a
deterministic, TEST-ONLY canned responder — so that the plumbing (prompt rendering,
control/treatment pairing, answer extraction, JSONL output) is proven correct *before*
any real model is involved. `src/clsm/feasibility.py` also now includes
`discover_llamacpp_binary` (a runtime-discovery guard: binary-exists + `--version`
check ONLY, never a model path), so the harness can confirm a configured runtime binary
is usable without risking an accidental inference call. No real generation backend is
implemented yet; `run_feasibility.py --real` refuses unconditionally until Gates B–D
pass.

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

### 1.6 Gate A — COMPLETE: llama.cpp installed, built, and locally verified (2026-09-06)

**BEFORE (candidate, this document's earlier state):** llama.cpp was a *recommended*
runtime option, nothing installed.

**AFTER Gate A (this section):** a specific llama.cpp **implementation** is installed,
built, and locally verified on this machine. Full raw command transcript:
`environment_checks/2026-09-06-llamacpp-gate-a.txt`. Summary:

| Field | Value |
|---|---|
| Repository | `https://github.com/ggml-org/llama.cpp` (the `ggerganov/llama.cpp` URL now redirects here — same repository, moved GitHub org; confirmed via the GitHub API, not assumed) |
| Pinned commit | `5266f24da75dc449bd56cbed7addb9c8e4a6a73e` |
| Tag | `v0.4.0` (latest published GitHub Release at pin time, 2026-09-04 — not a floating `master` reference) |
| Clone location | `~/tools/llama.cpp` (outside this research repo; not vendored into git history) |
| Build prerequisite installed | `cmake` 4.4.3 via Homebrew (was absent; nothing else installed — no Ollama, no MLX, no CUDA tooling) |
| Build command | `cmake -B build -DGGML_METAL=OFF -DCMAKE_BUILD_TYPE=Release` then `cmake --build build --config Release -j 6` |
| Build result | **SUCCESS** — all targets built, incl. `llama-cli` |
| Backend detected/used | **CPU only.** `GGML_SYSTEM_ARCH: x86`; CPU backend `ggml-cpu` with `-march=native`; BLAS via Apple's Accelerate framework (CPU math library, not GPU). **No Metal, OpenCL, CUDA, or Vulkan backend built** — Metal explicitly disabled (`-DGGML_METAL=OFF`), confirmed absent from the binary's linked libraries (`otool -L`) |
| Binary verified | `~/tools/llama.cpp/build/bin/llama-cli` — `file`: Mach-O 64-bit x86_64; `--version` and `--help` both launch successfully (exit 0); no model path was ever passed |
| Model/dataset downloads | **None.** HF cache unchanged from the pre-existing `gpt2`/`amazon_polarity` state (D-027); llama.cpp's own model-cache directories do not exist; the 19 `.gguf` files under `~/tools/llama.cpp/models/` are llama.cpp's own bundled tokenizer-vocabulary test fixtures (tracked in git at the pinned commit, 0.6–15.8 MB each, no weight tensors) — not downloaded model weights |

**Why Metal was explicitly disabled rather than left at CMake's macOS default
("Metal is enabled by default" per llama.cpp's own `docs/build.md`):** this machine's
GPU is an AMD Radeon Pro 5300M — a discrete GPU, not Apple Silicon's unified-memory
architecture, which is what llama.cpp's Metal backend is primarily developed and
tested against. Rather than assume Metal-via-AMD works (or claim it does not, without
testing), the build forces genuine CPU-only execution
(`-DGGML_METAL=OFF`, llama.cpp's own documented flag for this exact purpose). No claim
is made about whether Metal-via-AMD would have worked — it was not attempted, and
remains out of scope.

**What Gate A does NOT mean:** no inference of any kind has occurred; the scientific
study is not "ready" merely because a runtime compiles and reports its version. (Gate B
— exactly one model, Qwen3-1.7B Q8_0 — has since been authorized and completed; see
§0 and §1.7 below. Gate C inference remains **NOT AUTHORIZED**.)

### 1.7 Gate B — COMPLETE: Qwen3-1.7B (Q8_0 GGUF) downloaded and verified (2026-09-06)

Full record: `environment_checks/2026-09-06-gate-b-model-download.txt`. Summary:

| Field | Value |
|---|---|
| Selected model | `Qwen/Qwen3-1.7B` (generator); `Qwen/Qwen3-1.7B-GGUF` (official first-party GGUF artifact, author = "Qwen") |
| Selection rationale (neutral, pre-registered) | "smallest verified candidate with explicit reasoning-trace support, permissive license, and direct llama.cpp/GGUF compatibility" — re-verified against primary sources before locking; not influenced by any scientific output (none existed for any candidate at selection time) |
| Repo revision (pinned) | `90862c4b9d2787eaed51d12237eafdfe7c5f6077` |
| GGUF file | `Qwen3-1.7B-Q8_0.gguf` |
| Quantization | **Q8_0** — the only quantization the official repo publishes; comfortably fits 32 GB RAM; no scientific comparison across quant levels performed |
| File size | 1,834,426,016 bytes |
| SHA-256 | `061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a` — confirmed post-download, bit-for-bit match to the pre-download HF API git-LFS oid |
| Local storage | `~/models/clsm/Qwen3-1.7B/` — **outside** this git repository; `*.gguf` also added to `.gitignore` as defense-in-depth |
| Metadata-only inspection | `llama-gguf <file> r` (pinned llama.cpp v0.4.0's own tool) confirmed the file parses cleanly: architecture `qwen3`, 28 metadata keys, 310 tensors. **No prompt was submitted, no token was generated, no inference occurred.** |

**What Gate B does NOT mean:** no inference has occurred; no control or treatment
prompt has been evaluated; no reasoning trace has been generated; the scientific study
is not "ready." **Gate C (single-model smoke inference run) remains NOT AUTHORIZED.**

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
### 1.5 Ollama — reproducibility assessment against Step 6's specific criteria

Ollama is, under the hood, a llama.cpp-based server with its own model-registry and
`Modelfile` layer. Evaluated specifically on whether it supports the reproducibility and
exact-model-version control this project requires (`CLAUDE.md` §2.7):

| Criterion | Ollama | llama.cpp (driven directly) |
|---|---|---|
| Reproducible version pinning | the Ollama *application* version is pinnable, but a pulled model tag (`ollama pull model:tag`) resolves to whatever manifest the registry currently serves for that tag — the exact underlying GGUF file/quantization is not always obvious from the tag alone without an extra inspection step | the exact `.gguf` file used is whatever local file path is given — trivially pinnable, and its own sha256 can be recorded directly |
| Exact model revision handling | tied to Ollama's own model library naming, not directly to the upstream HF repo's revision hash — an extra mapping step is needed to tie an Ollama tag back to a specific upstream commit | direct — a GGUF file downloaded from a specific HF repo **commit** is the unit of provenance |
| GGUF implications | Ollama consumes GGUF internally but abstracts it away by default | GGUF is the first-class, inspectable artifact |
| Seeded generation support | supported via its API's `seed` option | supported via llama.cpp's `--seed` |
| Prompt/chat-template handling | applies a template embedded in the model's `Modelfile` — convenient, but another layer between "what I typed" and "what the model saw" | template applied explicitly in the calling code — more code to write, but nothing hidden |
| Output capture | via its HTTP API / CLI | direct from the process's stdout or library call |
| **Verdict for this project** | the convenience layer (registry, `Modelfile` templating) is exactly the kind of indirection that makes provenance harder to state precisely per generation — **not adopted as primary**, consistent with the original screen | **preferred** — nothing about Ollama makes it reproducibility-*superior* to driving llama.cpp directly, and it is one more moving part (a background server process) to pin and document |

Ollama remains a documented fallback only if driving llama.cpp directly proves harder in
practice than expected — not because of any compatibility problem (it would work fine on
this Intel Mac too), but because it adds an indirection layer this project does not need.

## 2. Runtime recommendation (Step 6) — recommended AND, as of §1.6, installed/locked

**Recommended: llama.cpp, driven directly (not via Ollama), with GGUF model files.**

| Criterion | llama.cpp (direct) | `transformers`-CPU | Ollama |
|---|---|---|---|
| Intel Mac compatibility | yes | yes | yes (wraps llama.cpp) |
| Reproducible version pinning | exact git commit / release tag + exact `.gguf` file hash | exact `transformers`/`torch` package versions (pip-pinnable) | Ollama app version pinnable; underlying GGUF/quant less directly pinnable (§1.5) |
| Exact model revision handling | direct — GGUF traces to a specific upstream HF commit | direct — same HF revision hash used on GPU | indirect — needs an extra mapping step (§1.5) |
| GGUF implications | native, first-class | not applicable (no GGUF; raw safetensors) | native but abstracted away |
| Seeded generation | yes (`--seed`) | yes (`torch.manual_seed`) | yes (API `seed` param) |
| Prompt/chat-template handling | explicit, in calling code | explicit, `transformers`' own template helper | applied from the model's `Modelfile` — one more hidden layer |
| Output capture | direct (stdout / library call) | direct | via HTTP API |
| Memory visibility | `--verbose` / built-in memory logging; can also cross-check with OS-level `ps`/`top` | standard Python process memory, same tooling as any other `transformers` usage | via its own logs; another layer to inspect |
| Quantization | first-class (GGUF quant levels, see §3 below) | limited on CPU (no `bitsandbytes` GPU path; CPU quantization options are narrower) | inherits llama.cpp's quantization, same abstraction caveat |
| Provenance/logging burden | moderate (one more artifact — the GGUF file's own hash — to record beyond the base HF revision) | lowest (same provenance shape as Track B, just on CPU) | moderate-to-high (registry tag → GGUF mapping must be documented) |

**Why llama.cpp over `transformers`-CPU as the *primary* recommendation:** the
candidate class in `MODEL_SCREEN.md` includes at least one model (Alif-1.0-8B-Instruct)
whose *only* practical path to acceptable CPU latency on this 6-core 2019 laptop is
quantization, which `transformers`-CPU supports only narrowly. `transformers`-CPU
remains the correct **fallback** for any candidate without a trustworthy GGUF
conversion, or as a full-precision reference point (`EXPERIMENT_SPEC.md` §6, "future
full-precision replication").

**Why not Ollama as primary:** no compatibility problem — the objection is
reproducibility indirection (§1.5), not feasibility.

**Why not MLX:** verified incompatible with this Intel x86_64 hardware (§1.2) — excluded
outright, not merely deprioritized.

**Observed-environment note, as it stood BEFORE Gate A (this run's preflight,
`environment_checks/2026-09-06-intel-mac-runtime-preflight.txt`):** Homebrew, `make`,
and `clang`/Xcode Command Line Tools were already present on this machine; `cmake` was
NOT installed. This was the basis for the recommendation above.

**UPDATE — Gate A complete (§1.6):** this recommendation has since been acted on.
`cmake` 4.4.3 was installed via Homebrew, and llama.cpp was built from pinned commit
`5266f24da75dc449bd56cbed7addb9c8e4a6a73e` (tag `v0.4.0`) and locally verified — see
§1.6 for the full record. **The runtime is now installed and locked; it is no longer
merely a recommendation.**

**UPDATE — Gate B complete (§1.7):** exactly one model (`Qwen/Qwen3-1.7B`, GGUF
`Qwen3-1.7B-Q8_0.gguf`) has since been selected on neutral criteria, downloaded, and
verified — see §1.7 for the full record. **Gate C (inference) remains NOT
AUTHORIZED.**

## 3. Track-A quantization — Q8_0 selected for the Gate-B/C smoke test (Step 7)

**For the locked Gate-B smoke-test model (Qwen3-1.7B):** quantization is **Q8_0**,
selected because it is the only quantization the official `Qwen/Qwen3-1.7B-GGUF` repo
publishes, comfortably fits this machine's 32 GB RAM (1.83 GB file), and is a
long-standing, universally-supported GGUF format. See §1.7 and
`environment_checks/2026-09-06-gate-b-model-download.txt` §4 for the full neutral
rationale. **This selection applies only to the Gate-B/C smoke test** — it is not a
locked policy for whichever model(s) Gate D eventually screens; those, if different
from Qwen3-1.7B, would need their own quantization decision under the same neutral
criteria below.

Per `EXPERIMENT_SPEC.md` §6, the *general* Track-A quantization policy (for any
candidate other than the now-locked Gate-B smoke-test model, §1.7) remains
`TODO — DECISION REQUIRED` — Gate B locked Q8_0 for Qwen3-1.7B specifically, on the
neutral grounds that it was the official repo's only offering; it did not resolve a
general policy for the other four screened candidates. The standard candidate
quantization levels considered (llama.cpp/GGUF, the recommended runtime, §2) are:

| Level | Typical bits/weight | Typical quality/size tradeoff (general llama.cpp convention, not measured here) |
|---|---|---|
| `Q8_0` | ~8-bit | closest to full precision; largest of the quantized options; safest choice if RAM/latency allow it |
| `Q6_K` | ~6-bit | small quality loss, meaningfully smaller than Q8_0 |
| `Q5_K_M` | ~5-bit | common "balanced" choice in the llama.cpp community |
| `Q4_K_M` | ~4-bit | smallest/fastest of the four; largest quality risk |

**Concrete anchor (real numbers, not invented):** Candidate 5's own HF repo
(`large-traversaal/Alif-1.0-8B-Instruct`, `MODEL_SCREEN.md`) publishes GGUF files
directly, confirmed to span **Q2_K at 3.18 GB up to F16 at 16.1 GB** — i.e. real,
primary-source-confirmed file sizes exist for at least one candidate, which is enough to
confirm quantized 8B-class models fit this machine's 32 GB RAM with wide headroom; the
exact Q8_0/Q6_K/Q5_K_M/Q4_K_M sizes for *this* file were not individually itemized in
what was fetched and are `TODO — verify exact sizes at selection time`, not estimated
here.

**Selection criteria (neutral, restated from the user's instruction — not scientific
behavior):**
- fits comfortably in RAM (all four levels above are expected to, for every candidate in
  `MODEL_SCREEN.md`, given the 3.18–16.1 GB anchor range and 32 GB total / ~184 GB free
  disk observed);
- acceptable latency for iterative development (unmeasured — a feasibility-benchmark
  question, §5.4 G2);
- output stability across repeated calls (unmeasured — G1);
- reproducibility (the exact quant level + exact GGUF file hash pinned before any
  comparison run, per `EXPERIMENT_SPEC.md` §6);
- avoids excessive degradation where possible — i.e., prefer the **least aggressive**
  quantization level that still meets the latency/RAM budget, not the most aggressive one
  that happens to run fastest.

**No quantization level is selected for the other four candidates in this document** —
only Qwen3-1.7B's is locked (Q8_0, §1.7), and only for the Gate-B/C smoke test. A
controlled quantization-level comparison (e.g. running the same tiny fixture at two
adjacent levels) is planned **only if** the feasibility benchmark shows meaningfully
different behavior across levels for a given model — not run pre-emptively. Whatever
level is chosen for a given model must be held fixed across every condition in a given
Track-A comparison (`EXPERIMENT_SPEC.md` §6) — no mixing quantization levels within one
experiment's primary result.

## 4. Overall Track-A GO / NO-GO checklist (design only)

This restates and consolidates the gates already defined in `EXPERIMENT_SPEC.md` §5.4,
as the single place to check before requesting authorization for the tiny feasibility
benchmark:

| Step | Gate | Status |
|---|---|---|
| Model screen | ≥1 candidate in `MODEL_SCREEN.md` clears the license + candidate-class checks on a primary-source re-read | **done** (2026-09-06 revision) — all 5 candidates checked directly against their HF model cards; none removed; Candidate 5's identity corrected from a tentative guess to a verified repo |
| Runtime installation (Gate A) | llama.cpp built from a pinned commit and locally verified (binary launches, no model loaded) | **✅ DONE (2026-09-06)** — §1.6; `environment_checks/2026-09-06-llamacpp-gate-a.txt` |
| Smoke-test model selection | one candidate locked on neutral hardware/methodology/provenance criteria (not the full Gate-D criteria A–E scoring, which is a multi-candidate exercise) | **✅ DONE (2026-09-06)** — Qwen3-1.7B; §1.7 |
| Smoke-test quantization | a level selected for the locked smoke-test model | **✅ DONE (2026-09-06)** — Q8_0; §1.7, §3 |
| Model-download authorization (Gate B) | user explicitly authorizes downloading a specific model weight | **✅ AUTHORIZED AND COMPLETE (2026-09-06)** — `environment_checks/2026-09-06-gate-b-model-download.txt` |
| Single-model smoke run (Gate C) | one real candidate exercised through the runner, infra-only | **NOT AUTHORIZED** |
| Multi-candidate feasibility benchmark (Gate D) | run per `EXPERIMENT_SPEC.md` §5; G1–G5 evaluated with real numbers, criteria A–E scored for all 5 candidates | **NOT AUTHORIZED** |

**Gates A and B are done; Gates C and D are unreached.** Downloading and verifying one
model's GGUF file is an infrastructure milestone, not a scientific-readiness milestone
— no inference of any kind has occurred, and the other four screened candidates remain
undownloaded. This document, `MODEL_SCREEN.md`, `EXPERIMENT_SPEC.md`, and
`runtime.local.example.yaml` are the complete state of Track A as of this writing.

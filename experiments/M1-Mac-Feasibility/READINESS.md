# READINESS.md — Track A Mac runtime architecture

**Status (current, as of 2026-09-10):**

- **Gate A** (runtime install/build) — **complete**. Intel: §1.6, 2026-09-06. Apple M5
  arm64 native rebuild: §1.6.2, 2026-09-08, `DECISION_LOG.md` D-036.
- **Gate B** (model-weight download of the ONE locked model) — **complete**. Intel:
  §1.7, D-034. Same artifact re-downloaded + byte-verified on the M5: §1.7.1, 2026-09-10,
  D-037 (size + full SHA-256 exact match).
- **Gate C** (ONE **synthetic infrastructure** smoke — not scientific data) — **PASS on
  the M5**: §1.8, 2026-09-10, D-040. Metal runtime use verified.
- **Gate D** — **not a model-selection exercise** (D-039); the generator is locked
  (D-034) and no model will be chosen or rejected on any behavioural/scientific outcome.

**No scientific dataset (MMLU/GPQA/…) has been downloaded. No scientific inference has
been run. No scientific metric of any kind — accuracy, answer-switch rate, disclosure,
hidden influence, Urdu behaviour, cross-lingual gap — has been computed. A scientific
pilot requires a frozen pre-registration first.** This document also documents runtime
*options* and the historical record of each gate (§1.6, §1.7).

### Historical Intel environment (Gate A originally performed here, 2026-09-06)

| Property | Value |
|---|---|
| Model | 2019 MacBook Pro |
| CPU | Intel Core i7-9750H (6c/12t) |
| RAM | 32 GB |
| GPU | AMD Radeon Pro 5300M, 4 GB VRAM |
| Architecture | **x86_64 (Intel), not Apple Silicon (ARM64)** |
| OS | macOS (Darwin) 26.3.1 |
| CUDA | none |
| llama.cpp build | pinned `5266f24da…` / `v0.4.0`, **`-DGGML_METAL=OFF`** (forced CPU-only; discrete AMD GPU), Accelerate/CPU only |

On that machine every "run LLMs on your Mac" recommendation was qualified by the Intel
fact — most notably Apple's own MLX is Apple-Silicon-only and does not run on it at all.
Observed-machine facts are archived in
`environment_checks/2026-09-06-intel-mac-runtime-preflight.txt` (read-only preflight) and
`environment_checks/2026-09-06-llamacpp-gate-a.txt` (Gate A transcript).

### Current Apple-Silicon environment (active as of 2026-09-08)

| Property | Value |
|---|---|
| Model | MacBook Air (`Mac17,3`) |
| Chip | Apple M5 |
| CPU | 10 cores (4 performance + 6 efficiency) |
| RAM | 16 GB |
| GPU | Apple M5 integrated (unified memory) — Metal's target architecture |
| Architecture | **arm64 (Apple Silicon)** |
| OS | macOS 26.6 (build 25G72) |
| CUDA | none |
| llama.cpp build | pinned `5266f24da…` / `v0.4.0`, **Metal ON** (pinned source default on Apple), **Accelerate/BLAS ON**, **CPU ON**, native arm64 |

Metal **build** availability has been verified on this machine (native `libggml-metal`
linked against `Metal.framework`/`MetalKit.framework`). Metal **inference** has **not**
been verified — that requires a separately authorized inference gate. Do not collapse
those two claims. Observed-machine facts and the full build transcript are archived in
`environment_checks/2026-09-08-m5-llamacpp-gate-a.txt`.

## 0. Authorization gates (sequential — do not skip ahead)

Everything past model/runtime screening requires explicit, sequential authorization.
Each gate below is a distinct, separately-authorized step:

| Gate | What it authorizes | Status |
|---|---|---|
| **Gate A** | Runtime installation (build/verify llama.cpp locally) | **✅ COMPLETE** — Intel 2026-09-06 (§1.6, `environment_checks/2026-09-06-llamacpp-gate-a.txt`); **rebuilt natively for arm64 on the Apple M5, 2026-09-08 (§1.6.2, `environment_checks/2026-09-08-m5-llamacpp-gate-a.txt`, D-036)** |
| **Gate B** | Model-weight download (exactly ONE model, selected on neutral criteria) | **✅ COMPLETE** — Intel 2026-09-06 (`environment_checks/2026-09-06-gate-b-model-download.txt`, D-034); **same artifact re-downloaded + byte-verified on the M5, 2026-09-10 (`environment_checks/2026-09-10-m5-gate-b-artifact-restoration.txt`, D-037)** — `Qwen/Qwen3-1.7B-GGUF` (Q8_0), size + full SHA-256 exact match |
| **Gate C** | A single **synthetic** infrastructure smoke (ONE fixture item, ONE seed; checks exit/non-empty/answer-extractable/reasoning-span-extractable/deterministic-recording only — **never** accuracy/hint/disclosure/Urdu/cross-lingual) | **✅ COMPLETE on the Apple M5, 2026-09-10 (§1.8, `environment_checks/2026-09-10-m5-gate-c-synthetic-smoke.txt`, D-040)** — PASS; Metal runtime use verified |
| **Gate D** | ~~multi-candidate feasibility screen for model selection~~ — **CLOSED for selection (D-039).** Generator is locked (D-034); no candidate scoring/choosing. Criterion C / G5 are diagnostic-only. | not a selection exercise |

**Gates A, B, and C (synthetic smoke) are complete on the M5; Gate D is not a
model-selection exercise (D-039).** A runtime implementation is built and verified
(§1.6.2), the ONE locked model is byte-verified (§1.7.1), and one synthetic
infrastructure smoke has passed (§1.8). This does **not** mean the scientific study is
"ready": no scientific dataset exists locally, and — critically — no
*scientific* inference has occurred — no scientific dataset item, no misleading-hint
treatment, no metric. The only real generation to date is the ONE **synthetic**
Gate-C smoke (§1.8, D-040), run directly via the pinned `llama-cli` (not through the
`clsm.feasibility` runner). The feasibility *runner*
(`experiments/M1-Mac-Feasibility/run_feasibility.py`, `src/clsm/feasibility.py`) is
still self-tested against `MockFeasibilityBackend` only — a deterministic, TEST-ONLY
canned responder — proving the plumbing (prompt rendering, control/treatment pairing,
answer extraction, JSONL output) before a real backend is wired in.
`src/clsm/feasibility.py` also includes `discover_llamacpp_binary` (a runtime-discovery
guard: binary-exists + `--version` check ONLY, never a model path). No real generation
backend is wired into the runner yet; `run_feasibility.py --real` still refuses
unconditionally.

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

### 1.6 Gate A (HISTORICAL — Intel machine) — llama.cpp installed, built, and locally verified (2026-09-06)

> **This subsection is the historical record of Gate A as performed on the 2019 Intel
> MacBook Pro.** It is preserved unchanged as provenance. The runtime in active use is
> now the Apple M5 arm64 rebuild — see **§1.6.2** below and `DECISION_LOG.md` D-036.

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

**What Gate A does NOT mean (as it stood on 2026-09-06):** no inference of any kind had
occurred; the scientific study is not "ready" merely because a runtime compiles and
reports its version. (Since then, on the M5: Gate B completed — §1.7.1 — and a synthetic
infrastructure Gate-C smoke passed — §1.8, D-040. **No *scientific* inference has
occurred on either machine.**)

### 1.6.2 Gate A (CURRENT — Apple M5 machine) — locked llama.cpp rebuilt natively for arm64 (2026-09-08)

Development moved to an Apple M5 MacBook Air (`Mac17,3`, arm64, 16 GB, macOS 26.6). The
**same locked revision** was rebuilt natively — the Intel x86_64 build cannot and must
not be reused. Full raw transcript: `environment_checks/2026-09-08-m5-llamacpp-gate-a.txt`.
Decision record: `DECISION_LOG.md` D-036. Summary:

| Field | Value |
|---|---|
| Repository | `https://github.com/ggml-org/llama.cpp.git` (official; unchanged) |
| Pinned commit | `5266f24da75dc449bd56cbed7addb9c8e4a6a73e` — **unchanged**, not re-pinned for the migration |
| Tag | `v0.4.0` |
| Clone location | `~/tools/llama.cpp` (outside this repo; not vendored) |
| Build prerequisites | `cmake` 4.4.3, `git` 2.50.1, Apple clang 21.0.0 — all via Homebrew 6.0.22 / Command Line Tools (no full Xcode; `xcrun metal` unavailable) |
| Build command | `cmake -B build -DCMAKE_BUILD_TYPE=Release` then `cmake --build build --config Release -j 10` — **`-DGGML_METAL=OFF` NOT carried forward** |
| Build result | **SUCCESS** — all targets built, incl. `llama-cli`; exit 0; no source patched |
| Backends built | **Metal ON** (pinned source's Apple default), **Accelerate/BLAS ON** (vendor Apple), **CPU ON** (`-mcpu=native+dotprod+i8mm+nosve+sme`). `GGML_CUDA/VULKAN/OPENCL=OFF`. `GGML_SYSTEM_ARCH: ARM`. |
| Metal evidence | native arm64 `libggml-metal.0.23.0.dylib` links `Metal.framework` + `MetalKit.framework` + `Foundation`; embedded shader library (`GGML_METAL_EMBED_LIBRARY=ON`, 40 `_ggml_metallib_*` symbols) — no build-time `metal` compiler needed |
| Accelerate evidence | `libggml-blas` and `libggml-cpu` link `Accelerate.framework` (current version 4.0.0) |
| Binary verified | `~/tools/llama.cpp/build/bin/llama-cli` — `file`: **Mach-O 64-bit executable arm64**; `--version` → `0.4.0-dev (build 10809, commit 5266f24da) … for Darwin arm64`; `--help` exit 0; **no model path ever passed** |
| Model/dataset downloads | **None.** `~/models` does not exist; no HF cache. The 19 `ggml-vocab-*.gguf` under `~/tools/llama.cpp/models/` are the upstream repo's git-tracked tokenizer-vocab test fixtures, not weights. |

**Why the Intel `-DGGML_METAL=OFF` was not carried forward:** that override was
justified *specifically* by the Intel host's discrete AMD Radeon GPU (§1.6, D-033). The
M5's unified-memory GPU is exactly the architecture llama.cpp's Metal backend is built
and tested for, and the pinned source defaults `GGML_METAL=ON` on Apple platforms
(`ggml/CMakeLists.txt:95-98, 236`). This is a hardware adaptation only; it changes no
model, quantization, prompt, seed, hypothesis, dataset, metric, or Track-B artifact.

**What §1.6.2 established (as of 2026-09-08):** Metal **build** availability verified;
Metal **inference** not yet exercised; Gate B weights not yet restored on the M5; Gate C
not yet run. **Update (2026-09-10):** the M5 Gate-C synthetic smoke (§1.8, D-040) has
since exercised the Metal runtime — `ggml_metal_init` on Apple M5, 29/29 layers
offloaded to the GPU — so Metal **inference** on this machine is now verified for an
infrastructure-only synthetic prompt. Gate B was restored (§1.7.1). **No *scientific*
inference has occurred.**

### 1.7 Gate B — COMPLETE (on the Intel machine): Qwen3-1.7B (Q8_0 GGUF) downloaded and verified (2026-09-06)

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
is not "ready."

### 1.7.1 Gate B (CURRENT — Apple M5 machine) — identical artifact restored + byte-verified (2026-09-10)

The Intel-machine download (§1.7) does not carry to the new machine. The **same
locked artifact** was re-downloaded on the M5 and re-verified. This is **not** a new
selection. Full record: `environment_checks/2026-09-10-m5-gate-b-artifact-restoration.txt`.
Decision record: `DECISION_LOG.md` D-037.

| Field | Value |
|---|---|
| Model / GGUF repo / revision | `Qwen/Qwen3-1.7B` · `Qwen/Qwen3-1.7B-GGUF` @ `90862c4b9d2787eaed51d12237eafdfe7c5f6077` — **unchanged** from D-034 |
| File / quantization | `Qwen3-1.7B-Q8_0.gguf` · Q8_0 — **unchanged** |
| Download method | `curl -L --fail` from the revision-pinned HF `resolve/` URL (same as Intel Gate B) |
| Size check | `stat -f%z` → **1,834,426,016 bytes** — EXACT MATCH |
| SHA-256 check | `shasum -a 256` → **`061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`** — EXACT MATCH (full 64-char value) — bit-for-bit identical to the Intel-verified file |
| Local storage | `~/models/clsm/Qwen3-1.7B/Qwen3-1.7B-Q8_0.gguf` — **outside** the repo (`.gitignore:240` `*.gguf`) |
| Metadata-only inspection | pinned `llama-gguf` + local `gguf` reader (PYTHONPATH only, no install): GGUF v3, 28 KV, 310 tensors, arch `qwen3`, name "Qwen3 1.7B Instruct", ctx_len metadata 40960 (card says 32768 — recorded, not resolved), tokenizer gpt2/qwen2-pre, chat template present (ChatML + `<think>`/`</think>`). **No inference.** |

**What §1.7.1 does NOT mean:** no *scientific* inference has occurred on the M5; no
scientific dataset item has been evaluated; no scientific metric has been computed.

### 1.8 Gate C (CURRENT — Apple M5) — synthetic infrastructure smoke — PASS (2026-09-10)

The **formal Gate-C trial** is one **synthetic, infrastructure-only** generation. **Not
scientific data.** Full record incl. the complete model-invocation accounting:
`environment_checks/2026-09-10-m5-gate-c-synthetic-smoke.txt`. Decision:
`DECISION_LOG.md` D-040.

| Field | Value |
|---|---|
| Item | `smoke-001` (SYNTHETIC — "capital of France"), **control** condition (no hint) |
| Command | `llama-cli -m <locked gguf> -p '<one synthetic item>' -st --reasoning-format none -n 512 -s 42 --temp 0 -ngl 99 --no-warmup --simple-io` |
| Model / runtime | locked `Qwen3-1.7B-Q8_0.gguf` (full sha `061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`) · pinned llama.cpp `5266f24da…` build `b10809` |
| Exit / wall | 0 / 6.07 s |
| Generation | non-empty, 1663 chars |
| `parse_status` | `VALID` (answer "A", fallback regex) — *answer correctness is not a Gate-C criterion* |
| `reasoning_span_status` | `PRESENT`, marker `xml_think` (literal `<think>…</think>` — preserved by `--reasoning-format none`, D-038) |
| Formal Gate-C output re-rolls | **ZERO** — the verdict rests on this ONE generation |
| Model-invocation accounting | 1 formal Gate-C generation (n=512) + **3 infrastructure-only Metal-diagnostic generations** (n=8, n=8, n=4; throwaway prompt "Q: 2+2? A:") + 2 failed pre-load attempts (`-no-cnv`; a broken output-redirect) + 1 `--list-devices`. The diagnostics used no scientific data, were **not** Gate-C re-rolls, did **not** alter the verdict, and were **not** model-selection/scientific evidence. Full table in the env-check file. |
| Metal (Phase 9) | from diagnostic gen #6 + `--list-devices`: `ggml_metal_init: found device: Apple M5`, `offloaded 29/29 layers to GPU`, `MTL0_Mapped model buffer 1743.77 MiB`; `MTL0: Apple M5` + `BLAS: Accelerate`. **Metal initialised and used.** ~66 tok/s on the formal trial (not a benchmark). |

**What §1.8 does NOT establish:** anything scientific. No accuracy, hint effect, switch
rate, disclosure, hidden influence, Urdu, or cross-lingual quantity — none computed,
none inferable. A scientific pilot needs a frozen pre-registration first. **Gate D is
not a model-selection exercise (D-039).**

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
verified — see §1.7 (Intel) and §1.7.1 (M5). **A synthetic infrastructure Gate-C smoke
has since passed on the M5 (§1.8, D-040). No *scientific* inference has been run;
Gate D is not a model-selection exercise (D-039).**

**UPDATE — Apple M5 machine migration (§1.6.2, 2026-09-08, `DECISION_LOG.md` D-036):**
development moved off the Intel host. The tables in §2 above discuss "Intel Mac
compatibility" and "this 6-core 2019 laptop" — those columns are the *historical*
selection context and are left intact as provenance. On the current arm64 machine:
`transformers`-CPU and Ollama remain available; **MLX is now Apple-Silicon-compatible**
(it was excluded only as Intel-incompatible in §1.2, not on reproducibility grounds) but
is **not** adopted — the reproducibility case for driving llama.cpp directly is
unchanged. llama.cpp (direct, GGUF) remains the locked runtime. The locked llama.cpp
revision was rebuilt natively for arm64 with Metal enabled (§1.6.2); the pin itself did
not change.

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
only Qwen3-1.7B's is locked (Q8_0, §1.7), and only for the Gate-B/C smoke test.

**Quantization-change policy (corrected 2026-09-06 — pre-scientific triggers only):**
Q8_0 stays locked for Qwen3-1.7B smoke testing. Reconsidering it, or selecting a level
for any other candidate, may be triggered **only** by pre-scientific, infrastructure
reasons, checked in this order:
  - runtime incompatibility (the runtime cannot load or execute the file at all);
  - a RAM / resource-budget failure (the process cannot be allocated the memory it
    needs on this machine);
  - a predefined latency-budget failure (fixed *before* any run, per §5.4 G2 — not a
    budget invented after seeing how slow or fast a level happens to be);
  - instability or a crash across repeated calls (§5.4 G1);
  - artifact corruption or unavailability (a download fails an integrity check, or a
    file silently disappears from its source);
  - a reproducibility / tooling failure (the exact level or file cannot be pinned or
    hashed, e.g. because no fixed release exists to point to).

**Quantization selection must NEVER be triggered by observed scientific behavior** —
explicitly excluded as a trigger: answer switching, hidden influence, disclosure rate,
task accuracy, Urdu-specific performance, cross-lingual gap, monitor
failure/detectability, or a level's outputs being judged "interesting" or
"uninteresting." None of these is a legitimate reason to pick a different quantization
level, for Qwen3-1.7B or any other candidate, at any stage of Track A.

If a controlled quantization-level comparison is ever run (e.g. the same tiny fixture
at two adjacent levels), it is triggered only by one of the infrastructure reasons
above, and its own results are then reported as an infrastructure finding, not folded
into a scientific comparison. Whatever level is chosen for a given model must be held
fixed across every condition in a given Track-A scientific comparison
(`EXPERIMENT_SPEC.md` §6) — no mixing quantization levels within one experiment's
primary result.

## 4. Overall Track-A GO / NO-GO checklist (design only)

This restates and consolidates the gates already defined in `EXPERIMENT_SPEC.md` §5.4,
as the single place to check before requesting authorization for the tiny feasibility
benchmark:

| Step | Gate | Status |
|---|---|---|
| Model screen | ≥1 candidate in `MODEL_SCREEN.md` clears the license + candidate-class checks on a primary-source re-read | **done** (2026-09-06 revision) — all 5 candidates checked directly against their HF model cards; none removed; Candidate 5's identity corrected from a tentative guess to a verified repo |
| Runtime installation (Gate A) | llama.cpp built from a pinned commit and locally verified (binary launches, no model loaded) | **✅ DONE** — Intel: 2026-09-06, §1.6, `environment_checks/2026-09-06-llamacpp-gate-a.txt`. **Apple M5 (arm64) rebuild: 2026-09-08, §1.6.2, `environment_checks/2026-09-08-m5-llamacpp-gate-a.txt`, D-036** |
| Smoke-test model selection | one candidate locked on neutral hardware/methodology/provenance criteria (not the full Gate-D criteria A–E scoring, which is a multi-candidate exercise) | **✅ DONE (2026-09-06)** — Qwen3-1.7B; §1.7 |
| Smoke-test quantization | a level selected for the locked smoke-test model | **✅ DONE (2026-09-06)** — Q8_0; §1.7, §3 |
| Model-download authorization (Gate B) | user explicitly authorizes downloading a specific model weight | **✅ DONE** — Intel 2026-09-06 (`environment_checks/2026-09-06-gate-b-model-download.txt`); **same artifact re-downloaded + byte-verified on the M5, 2026-09-10 (`environment_checks/2026-09-10-m5-gate-b-artifact-restoration.txt`, D-037)** |
| Single-model smoke run (Gate C) | one real candidate exercised through the runner, **infrastructure-only** (process exit, non-empty generation, answer + reasoning-span *extractability*; **never** accuracy / hint effect / disclosure / Urdu / cross-lingual) | separately gated |
| Multi-candidate feasibility benchmark (Gate D) | **CLOSED for model selection (D-034/D-039).** The generator is locked; no candidate scoring or choosing will occur. Any A/B/D/E infrastructure check applies to the locked model only. **Criterion C / G5 are diagnostic-only, never a selection gate.** | not a selection exercise |

**Gates A and B are done on both machines; Gate C is separately gated; Gate D is not a
model-selection exercise (D-039).** Downloading and verifying the GGUF file is an
infrastructure milestone, not a scientific-readiness milestone — the generator is locked
(D-034), no scientific inference has occurred, and no model will be chosen or rejected on
any behavioural outcome. This document, `MODEL_SCREEN.md`, `EXPERIMENT_SPEC.md`,
`REASONING_MARKER_FORENSICS.md`, and `runtime.local.example.yaml` are the complete state
of Track A as of this writing.

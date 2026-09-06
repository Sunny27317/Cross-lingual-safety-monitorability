# MODEL_SCREEN.md — Track A candidate models (paper screen only)

**Status:** SCREENING ONLY. No model has been downloaded. No model has been run. No
winner is selected. Every "feasibility status" below is **UNVERIFIED** by construction —
runtime/latency/memory/quality feasibility becomes verified only after the tiny
feasibility benchmark (`EXPERIMENT_SPEC.md` §5) actually runs on this Mac (not
authorized yet — see this run's report, Gate A/B/C/D).

**Sourcing note (updated 2026-09-06):** the original screen (2026-09-06, earlier same
day) was built from web-search snippets only. This revision re-checks each candidate
against its **primary Hugging Face model card**, fetched directly, per the instruction
not to rely on search snippets alone. Where the fetch confirms a fact, it is marked
**primary-source checked (2026-09-06)**; where a claim still rests only on a secondary
source (a blog post, aggregator article, or a search-engine summary that did not quote
the card directly), it remains marked `TODO — UNVERIFIED`. This distinction is about
**factual claims** (parameter count, license, languages) — it is separate from, and does
not resolve, **runtime feasibility** (does it actually run well on this CPU), which
stays UNVERIFIED for every candidate until the tiny feasibility benchmark is run.

---

## Candidate 1 — Qwen3-1.7B (dense, "thinking" mode)

| Field | Value | Status |
|---|---|---|
| Model name / repo id | `Qwen/Qwen3-1.7B` | **primary-source checked** (huggingface.co/Qwen/Qwen3-1.7B, fetched 2026-09-06) |
| Parameter count | 1.7B total; 1.4B non-embedding | **primary-source checked** |
| License | **Apache 2.0** | **primary-source checked** |
| Multilingual capability | "100+ languages and dialects"; the model card text fetched does not give an exact count or list | **primary-source checked** (claim exists) / count and full list `TODO — UNVERIFIED` |
| Urdu capability evidence | Urdu is **not specifically named** in the fetched model-card text (the "100+ languages" claim is unenumerated in what was fetched) | `TODO — UNVERIFIED` |
| Context length | 32,768 tokens | **primary-source checked** |
| Expected memory class | ~3.4 GB weights at fp16/bf16 (1.7B × 2 bytes); smaller under 4/8-bit quantization | estimated, not measured |
| Inference runtime options | llama.cpp (official `Qwen/Qwen3-1.7B-GGUF` repo exists, plus community conversions e.g. `bartowski/Qwen_Qwen3-1.7B-GGUF`); `transformers` CPU | **primary-source checked** for GGUF availability |
| CoT-style output elicitable? | **Yes, architecturally** — an explicit `enable_thinking` parameter (default `True`) toggles a "thinking mode" producing a visible reasoning span; `/think` and `/no_think` soft-switches are also supported in the chat template | **primary-source checked** |
| Chat template | Standard `transformers` `apply_chat_template()`; supports the `enable_thinking` argument | **primary-source checked** |
| Architecture family | Causal transformer LM, 28 layers, 16 query / 8 KV attention heads (GQA) | **primary-source checked** |
| Known limitations | smallest "thinking"-capable Qwen3 size in this screen; reasoning coherence at 1.7B relative to larger siblings (4B/8B) is untested here | flagged, not measured |
| **Feasibility status** | **UNVERIFIED** (runtime/latency/memory on this Mac not yet tested) | |

## Candidate 2 — Llama-3.2-3B-Instruct

| Field | Value | Status |
|---|---|---|
| Model name / repo id | `meta-llama/Llama-3.2-3B-Instruct` | **primary-source checked** (huggingface.co/meta-llama/Llama-3.2-3B-Instruct, fetched 2026-09-06) |
| Parameter count | 3.21B | **primary-source checked** |
| License | **Llama 3.2 Community License** (custom commercial license; permits research use, gated download requiring Meta's acceptance click-through) | **primary-source checked** |
| Multilingual capability | Officially documented for **8 languages**: English, German, French, Italian, Portuguese, Hindi, Spanish, Thai. Card notes the model is trained on a broader set than these 8 | **primary-source checked** |
| Urdu capability evidence | **Confirmed absent from the officially-supported 8-language list.** Any Urdu output relies on incidental tokenizer/pretraining exposure outside the documented capability | **primary-source checked (negative finding)** |
| Context length | 128K tokens | **primary-source checked** |
| Expected memory class | ~6.4 GB weights at fp16 (3.2B × 2 bytes) | estimated |
| Inference runtime options | llama.cpp — GGUF widely available (`unsloth/Llama-3.2-3B-Instruct-GGUF`, `bartowski/Llama-3.2-3B-Instruct-GGUF`, `MaziyarPanahi/...`, `QuantFactory/...`); `transformers` CPU; MLX **not applicable** (Apple-Silicon only, this is an Intel Mac — `READINESS.md`) | **primary-source checked** for GGUF availability |
| CoT-style output elicitable? | No native "thinking" mode; a step-by-step trace is elicitable only by prompting (instruction-following compliance, not an architectural mode) | plausible, unconfirmed |
| Chat template | Standard `apply_chat_template()`, role-based (system/user) messages | **primary-source checked** |
| Architecture family | Optimized transformer, GQA, shared input/output embeddings | **primary-source checked** |
| Known limitations | Urdu confirmed absent from officially supported languages (real risk for criterion D, `EXPERIMENT_SPEC.md` §3); gated download (requires accepting Meta's license click-through before weights are downloadable — a process step, not a blocker, but must be done by the user, not silently) | flagged |
| **Feasibility status** | **UNVERIFIED** (runtime/latency/memory on this Mac not yet tested) | |

## Candidate 3 — Gemma-3-4B-it

| Field | Value | Status |
|---|---|---|
| Model name / repo id | `google/gemma-3-4b-it` | **primary-source checked** (huggingface.co/google/gemma-3-4b-it, fetched 2026-09-06) |
| Parameter count | 4B (above the "~3B" soft ceiling in `EXPERIMENT_SPEC.md` §2; kept in the screen for its language-breadth claim, weighed explicitly against size below) | **primary-source checked** |
| License | **Gemma Terms of Use** (requires click-through acceptance; permits research and commercial use with some restrictions) | **primary-source checked** |
| Multilingual capability | "Over 140 languages" per the model card | **primary-source checked** (claim exists) / exact list `TODO — UNVERIFIED`; Urdu not explicitly named in the fetched text |
| Urdu capability evidence | Not explicitly named in the fetched card text; plausible given the breadth claim but **not confirmed** | `TODO — UNVERIFIED` |
| Context length | 128K input / **8,192 output** — the output-length ceiling is materially shorter than the other candidates' generation budgets and is a new, primary-source-confirmed constraint this screen had not previously recorded | **primary-source checked** |
| Expected memory class | ~8 GB weights at fp16 (4B × 2 bytes) — largest text-relevant footprint in this screen (see next row) | estimated |
| **New finding (this revision):** architecture | The model card describes `gemma-3-4b-it` as a **vision-language model** (multimodal text+image input, image encoder + a ~896×896 vision tower producing 256 tokens/image), not a text-only LLM. For a text-only use case this means additional loaded parameters/complexity (the vision tower) beyond what a pure-text model of the same "4B" label would carry, and a runtime must support the multimodal architecture (or a text-only export, if one exists) even when only the text path is exercised | **primary-source checked** — a genuine new limitation surfaced by primary-source verification, not present in the original secondary-source screen |
| Inference runtime options | llama.cpp — GGUF available (`unsloth/gemma-3-4b-it-GGUF`, `lm-kit/gemma-3-4b-instruct-gguf`, `Mungert/gemma-3-4b-it-gguf`); note multimodal GGUF support in llama.cpp has historically lagged text-only models and must be checked for this specific conversion; `transformers` CPU | **primary-source checked** for GGUF existence; multimodal-support maturity `TODO — UNVERIFIED` |
| CoT-style output elicitable? | No native "thinking" mode; step-by-step traces via prompting only | plausible, unconfirmed |
| Chat template | `apply_chat_template()` required per the card | **primary-source checked** |
| Known limitations | largest **and** most architecturally complex candidate in this screen (multimodal); 8,192-token output ceiling; over the "~3B" screening ceiling | flagged |
| **Feasibility status** | **UNVERIFIED** (runtime/latency/memory on this Mac not yet tested) | |

## Candidate 4 — Phi-4-mini-instruct

| Field | Value | Status |
|---|---|---|
| Model name / repo id | `microsoft/Phi-4-mini-instruct` | **primary-source checked** (huggingface.co/microsoft/Phi-4-mini-instruct, fetched 2026-09-06) |
| Parameter count | 3.8B | **primary-source checked** |
| License | **MIT** — the cleanest, least restrictive license of the five candidates | **primary-source checked** |
| Multilingual capability | **22 languages, explicitly listed** on the card: Arabic, Chinese, Czech, Danish, Dutch, English, Finnish, French, German, Hebrew, Hungarian, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, Spanish, Swedish, Thai, Turkish, Ukrainian | **primary-source checked** |
| Urdu capability evidence | **Confirmed absent** — Urdu is not among the 22 explicitly listed languages. This is now a verified negative finding (previously `TODO — UNVERIFIED` in the original screen) | **primary-source checked (negative finding)** |
| Context length | 128K tokens | **primary-source checked** |
| Expected memory class | ~7.7 GB weights at fp16 (3.84B × 2 bytes) | estimated |
| Inference runtime options | llama.cpp — GGUF commonly available (community conversions confirmed to exist, e.g. `phi-4-mini-q4_0.gguf`-style quants); `transformers` CPU; ONNX Runtime (Microsoft ships ONNX builds for the Phi family) | **primary-source checked** for GGUF existence at a lower confidence than candidates 1/2/3 (a specific canonical repo was not directly fetched — treat the exact repo id as `TODO — UNVERIFIED` even though GGUF availability in general is confirmed) |
| CoT-style output elicitable? | No native "thinking" mode in this instruct variant (Microsoft ships separate `Phi-4-mini-reasoning` / `Phi-4-reasoning` variants, not screened here — a possible future candidate if this family screens well); step-by-step traces via prompting only | **primary-source checked** (absence of a thinking mode in this specific variant) |
| Chat template | Custom tag-based format using pipe-delimited role tags for system, user, and assistant turns (plus a matching pair for tool calls) — **not** a generic role-list template, needs explicit handling | **primary-source checked** |
| Architecture family | Dense decoder-only transformer, 200K vocabulary, GQA, shared input/output embeddings | **primary-source checked** |
| Known limitations | Urdu confirmed absent from supported languages; custom (non-generic) chat template format increases integration risk of a subtly-wrong prompt | flagged |
| **Feasibility status** | **UNVERIFIED** (runtime/latency/memory on this Mac not yet tested) | |

## Candidate 5 — Urdu-specialized fine-tune: **corrected to `large-traversaal/Alif-1.0-8B-Instruct`**

**Correction note:** the original screen (earlier 2026-09-06) tentatively described this
slot as "a community Urdu instruction-tuned model built on a Llama-3.2-3B-class backbone
(e.g. `traversaal-ai/alif-urdu-llm`)... which specific checkpoint, if any, would actually
be used is not decided." A primary-source check this revision performed resolves that
uncertainty to a **specific, real, verifiable Hugging Face repository** — but the
resolved facts differ materially from what was tentatively assumed: the model is **8B
parameters**, not "~3B-class." This is reported exactly as found, not adjusted to fit
the original guess.

| Field | Value | Status |
|---|---|---|
| Model name / repo id | `large-traversaal/Alif-1.0-8B-Instruct` | **primary-source checked** (huggingface.co/large-traversaal/Alif-1.0-8B-Instruct, fetched 2026-09-06) |
| Base model | `unsloth/Meta-Llama-3.1-8B` (continual fine-tune) | **primary-source checked** |
| Parameter count | **8B — exceeds the "sub-1B–~3B" candidate-class ceiling** (`EXPERIMENT_SPEC.md` §2) more than Gemma-3-4B does; kept in the screen because it is the only candidate found with dedicated, benchmarked Urdu instruction-tuning (see below) — the size/Urdu-evidence tradeoff is stated explicitly, not hidden | **primary-source checked** |
| License | **Apache 2.0** | **primary-source checked** |
| Multilingual capability | English + Urdu (bilingual focus, not broad multilingual) | **primary-source checked** |
| Urdu capability evidence | **Strongest in this candidate set, and now benchmark-backed**: trained on a ~51,686-example synthetic Urdu-English instruction corpus (GPT-4o-generated under a "modified self-instruct" framework per the card), and evaluated on a **human-annotated Urdu evaluation dataset** against Llama-3.1-8B-Instruct, Gemma-2-9B, Mistral-7B-Instruct-v0.3, Qwen-2.5-7B-Instruct, and Cohere-Aya-Expanse-8B (GPT-4o as judge, per the card's own description — noted as the model author's own claimed result, not independently re-verified by this project) | **primary-source checked** (existence of the claim and its evaluation design); the claimed win-rate numbers themselves are the model author's own reported result and are `TODO — UNVERIFIED` as an independent fact until re-checked against the linked paper (`huggingface.co/papers/2510.09051`, not yet read in full) |
| Context length | not stated in the fetched card excerpt | `TODO — UNVERIFIED` |
| Expected memory class | 8B backbone; **GGUF conversions exist directly on the model's own repo**, spanning **Q2_K (3.18 GB) through F16 (16.1 GB)** — a mid-tier quant (Q4_K_M/Q5_K_M class, not directly listed but standard for this size, typically ~4.9–5.7 GB) would comfortably fit 32 GB RAM alongside the OS and other tooling | **primary-source checked** (the GGUF file list and sizes) |
| Inference runtime options | llama.cpp (official/first-party GGUF already published on the model's own HF repo — the strongest "runtime plausibility" evidence of any candidate in this screen); `transformers` CPU as a fallback | **primary-source checked** |
| CoT-style output elicitable? | The card describes training that used "reasoning to enhance cultural nuance," but does not describe a dedicated thinking-mode toggle the way Qwen3 does; whether this reliably yields a usable step-by-step trace in **Urdu** specifically is untested and is a first-order question for the feasibility benchmark | **primary-source checked** (what the card claims) / actual elicitability genuinely unknown |
| Chat template | not stated in the fetched card excerpt | `TODO — UNVERIFIED` |
| Architecture family | Llama (transformer-based, inherits Llama-3.1-8B architecture) | **primary-source checked** |
| Known limitations | 8B is a real memory/latency cost increase over every other candidate even under quantization; the model author's own comparative benchmark claims are not independently verified; a linked paper (arXiv/HF-papers 2510.09051) exists but has not been read in full by this project | flagged |
| **Feasibility status** | **UNVERIFIED** (runtime/latency/memory on this Mac not yet tested — and, given the 8B size, this is the candidate most likely to be latency/memory-constrained on this specific CPU) | |

---

## Step 5 — re-evaluation outcome (this revision, 2026-09-06)

**No candidate was removed.** Checked each of the five against the neutral removal
criteria (`EXPERIMENT_SPEC.md` §2–3; this run's Step 5 instructions: license
incompatibility, obvious runtime impracticality, not instruction-tuned, no usable
reasoning/explanation output, no multilingual capability where required, or unverifiable
identity):

- **License:** none excluded — Apache 2.0 ×3 (Qwen3-1.7B, Alif-1.0-8B), MIT ×1
  (Phi-4-mini), and two click-through-gated-but-research-permitting licenses (Llama 3.2
  Community License, Gemma Terms). None is incompatible with academic research.
- **Runtime impracticality:** none judged obviously impractical — all five have GGUF
  conversions confirmed to exist (directly addressing "whether GGUF conversions are
  officially or commonly available," Step 4), so a CPU path exists for each on paper.
  Alif-1.0-8B is the heaviest and most likely to be *slow*, not impractical outright;
  this is exactly what the feasibility benchmark (§5, not yet run) will determine.
- **Instruction-tuned:** confirmed for all five (`-Instruct` / `-it` variants, primary-
  source checked).
- **Usable reasoning/explanation output:** Qwen3-1.7B has a confirmed architectural
  thinking mode; the other four rely on prompted step-by-step explanations, which is
  untested but not a basis for removal at the paper-screen stage (this is exactly what
  Gate C, the tiny feasibility benchmark, is for).
- **Multilingual/Urdu capability where required:** Llama-3.2-3B-Instruct and
  Phi-4-mini-instruct are now **confirmed** (not merely suspected) to exclude Urdu from
  their officially documented language lists. This is **not** grounds for removal yet,
  because Urdu is not required for the English-only tiny feasibility benchmark
  (`EXPERIMENT_SPEC.md` §5.1); it is flagged as a real weakness that would need
  addressing (or these candidates dropping out) before any Urdu-inclusive pilot.
- **Identity verifiable:** all five now resolve to a specific, fetched, primary-source
  HF repo id — Candidate 5's identity was **corrected**, not removed or newly added, from
  a tentative "some ~3B Urdu fine-tune" placeholder to the concrete
  `large-traversaal/Alif-1.0-8B-Instruct`.

**No new candidates were added.** A search for a genuinely sub-3B Urdu- or Hindi-focused
instruction-tuned open model did not surface a verifiable one; this remains an open gap
(if a smaller genuinely Urdu-tuned model surfaces later, it would strengthen the screen
and should be added then, verified the same way).

---

## Summary table (paper screen only — no scores computed, no winner)

| # | Candidate | Params | License | Urdu evidence | Native reasoning mode | GGUF available | Screen status |
|---|---|---|---|---|---|---|---|
| 1 | Qwen3-1.7B | 1.7B | Apache 2.0 | unverified (unenumerated "100+ languages") | yes (thinking mode) | yes (official + community) | primary-source checked |
| 2 | Llama-3.2-3B-Instruct | 3.2B | Llama 3.2 Community | **confirmed absent** (8 official languages, no Urdu) | no | yes (community) | primary-source checked |
| 3 | Gemma-3-4B-it | 4B (over ceiling) | Gemma Terms | unverified ("140+ languages", Urdu not named) | no; also **multimodal**, not pure text | yes (community) | primary-source checked |
| 4 | Phi-4-mini-instruct | 3.8B | MIT | **confirmed absent** (22 languages listed, no Urdu) | no (separate reasoning variants exist, unscreened) | yes (commonly available, exact repo unconfirmed) | primary-source checked |
| 5 | Alif-1.0-8B-Instruct (corrected identity) | **8B (over ceiling)** | Apache 2.0 | **strongest — dedicated Urdu instruction-tuning + benchmark** | untested Urdu reasoning trace elicitability | yes (official, on-repo, Q2_K–F16) | primary-source checked |

**No candidate is locked.** The next step, per `EXPERIMENT_SPEC.md` §4, is running the
tiny feasibility benchmark (design in `EXPERIMENT_SPEC.md` §5; **not yet authorized —
Gate C**) across these candidates and scoring them against criteria A–E with real (not
assumed) numbers.

## What this screen deliberately does not do

- It does not benchmark accuracy, latency, or Urdu quality — no inference has occurred.
- It does not select a winner, despite now having stronger per-candidate factual
  verification than the original same-day screen.
- It does not treat the model authors' own comparative benchmark claims (e.g. Alif-1.0's
  reported wins over other 7–9B models) as independently verified facts under
  `CLAUDE.md` §2.6 — they are recorded as claims, attributed to their source, pending an
  independent read of the linked paper.
- It does not resolve the Qwen3 "how many languages, does the list include Urdu"
  question from `RESEARCH_PLAN.md` §12 more precisely than "100+, unenumerated in the
  fetched text" — a fuller technical-report read would be needed for an exact list.

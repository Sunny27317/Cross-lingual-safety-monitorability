# MODEL_SCREEN.md — Track A candidate models (paper screen only)

**Status:** SCREENING ONLY. No model has been downloaded. No model has been run. No
winner is selected. Every "feasibility status" below is **UNVERIFIED** by construction —
it becomes verified only after the tiny feasibility benchmark
(`EXPERIMENT_SPEC.md` §5) actually runs on this Mac.

**Selection criteria** (fixed before this screen was written): `EXPERIMENT_SPEC.md` §2–4.

**Sourcing note:** fields below are sourced from a web search performed 2026-09-06 (model
cards, vendor announcements, and secondary write-ups — see the citation column). None of
these have been independently re-verified against the primary model card the way
`literature/CITATION_VERIFICATION.md` verifies academic citations; treat every
non-obvious factual claim here (exact language counts, exact parameter counts) as
**reported, not independently confirmed**, until checked against the primary Hugging
Face model card at selection time.

---

## Candidate 1 — Qwen3-1.7B (dense, "thinking" mode)

| Field | Value | Status |
|---|---|---|
| Model name | `Qwen/Qwen3-1.7B` (dense; the Qwen3 family also ships a non-thinking mode toggle) | reported |
| Parameter count | ~1.7B dense | reported (HF model naming) |
| License | Apache 2.0 | reported — **confirm on HF repo before use** |
| Multilingual capability | Qwen3 family claimed to support a very large language set (a figure of "100+ languages" appears in vendor material; `RESEARCH_PLAN.md` §12 already flags Qwen3-8B's "~119 languages" claim as `TODO — IMPORT/VERIFY`, same caveat applies here) | `TODO — UNVERIFIED` (exact count and list) |
| Urdu capability evidence | Urdu is asserted to be among the family's broad language coverage in secondary sources found 2026-09-06; **no primary-source confirmation done yet** | `TODO — UNVERIFIED` |
| Context length | large (32K+ class, exact figure per checkpoint) | reported, not re-verified |
| Expected memory class | ~3.4 GB weights at fp16/bf16 (1.7B × 2 bytes); smaller under 4/8-bit quantization | estimated, not measured |
| Inference runtime options | llama.cpp (GGUF builds exist for the Qwen3 family), `transformers` CPU, possibly ONNX | to evaluate in `READINESS.md` |
| CoT-style output elicitable? | **Yes, structurally** — Qwen3 ships an explicit enable/disable "thinking" mode intended to produce a visible reasoning span, which is exactly the format the disclosure paradigm needs | reported; must be confirmed it actually emits a usable trace at this small size |
| Known limitations | smallest models in a "thinking"-capable family sometimes have degraded reasoning coherence relative to larger siblings (e.g. Qwen3-4B/8B); this is a plausibility concern for criterion C (experimental responsiveness), not yet observed | flagged, not measured |
| Citation/source needed | Qwen3 technical report / HF model card (`Qwen/Qwen3-1.7B`) | not yet fetched and read in full |
| **Feasibility status** | **UNVERIFIED** | |

## Candidate 2 — Llama-3.2-3B-Instruct

| Field | Value | Status |
|---|---|---|
| Model name | `meta-llama/Llama-3.2-3B-Instruct` | reported |
| Parameter count | ~3.21B | reported |
| License | Llama 3.2 Community License (custom; permits research use with attribution/acceptable-use terms — **not** a bare permissive license like Apache/MIT) | reported — exact terms must be read before use |
| Multilingual capability | officially documented for **8 languages** (English, German, French, Italian, Portuguese, Hindi, Spanish, Thai) per secondary sources found 2026-09-06 | `TODO — UNVERIFIED` against the primary model card |
| Urdu capability evidence | **Urdu is not in the 8 officially-documented languages.** Any Urdu output would rely on incidental tokenizer/pretraining-data exposure, not a documented capability | weak / negative evidence |
| Context length | 128K | reported |
| Expected memory class | ~6.4 GB weights at fp16 (3.2B × 2 bytes) | estimated |
| Inference runtime options | llama.cpp (GGUF), `transformers` CPU, MLX (Apple-Silicon only — **not applicable to this Intel Mac**, see `READINESS.md`) | to evaluate |
| CoT-style output elicitable? | not a native "thinking" model; a step-by-step trace can be elicited by prompting (e.g. "think step by step"), but this is instruction-following compliance, not an architectural reasoning mode | plausible, unconfirmed |
| Known limitations | Urdu not an officially supported language (see above) — a real risk for criterion D (language capability); no built-in reasoning-trace mode | flagged |
| Citation/source needed | Meta Llama 3.2 model card | not yet fetched and read in full |
| **Feasibility status** | **UNVERIFIED** | |

## Candidate 3 — Gemma-3-4B-it

| Field | Value | Status |
|---|---|---|
| Model name | `google/gemma-3-4b-it` | reported |
| Parameter count | ~4B (slightly above the "~3B" ceiling in `EXPERIMENT_SPEC.md` §2; included anyway because of its breadth-of-language claim, to be weighed against the size ceiling at selection time) | reported |
| License | Gemma Terms of Use (permits research and commercial use with some restrictions; not a bare OSI license) | reported — exact terms must be read before use |
| Multilingual capability | Gemma 3 has been marketed with a large language-coverage claim (order of 140 languages in vendor material found 2026-09-06) | `TODO — UNVERIFIED` (exact count/list against primary source) |
| Urdu capability evidence | Urdu plausibly included given the breadth claim, but **no specific per-language benchmark evidence for Urdu found** in this pass | `TODO — UNVERIFIED` |
| Context length | 128K (per vendor material) | reported |
| Expected memory class | ~8 GB weights at fp16 (4B × 2 bytes); this is the largest candidate in the set | estimated |
| Inference runtime options | llama.cpp (GGUF), `transformers` CPU | to evaluate |
| CoT-style output elicitable? | not a native "thinking" model in the Qwen3 sense; step-by-step traces via prompting only | plausible, unconfirmed |
| Known limitations | largest candidate — heaviest memory/latency cost on this Mac; over the "~3B" screening ceiling, kept only as a breadth-of-language reference point | flagged |
| Citation/source needed | Gemma 3 technical report / model card | not yet fetched and read in full |
| **Feasibility status** | **UNVERIFIED** | |

## Candidate 4 — Phi-4-mini-instruct

| Field | Value | Status |
|---|---|---|
| Model name | `microsoft/Phi-4-mini-instruct` | reported |
| Parameter count | ~3.84B | reported |
| License | MIT | reported — bare permissive license, easiest of the set to clear the license criterion |
| Multilingual capability | reported multilingual support "in the order of 20+ languages" in secondary sources found 2026-09-06 | `TODO — UNVERIFIED` (exact count/list) |
| Urdu capability evidence | **not confirmed either way** in this pass — Microsoft's Phi multilingual documentation would need to be read directly to check whether Urdu is on the supported list | `TODO — UNVERIFIED` |
| Context length | 128K | reported |
| Expected memory class | ~7.7 GB weights at fp16 (3.84B × 2 bytes) | estimated |
| Inference runtime options | llama.cpp (GGUF), `transformers` CPU, ONNX Runtime (Microsoft ships ONNX builds for the Phi family) | to evaluate |
| CoT-style output elicitable? | not a native "thinking" model; step-by-step traces via prompting only (note: Microsoft also ships separate "Phi-4-reasoning" variants, not screened here — could be a future candidate if this family looks promising) | plausible, unconfirmed |
| Known limitations | Urdu support unconfirmed; MIT license is the cleanest of the set | flagged |
| Citation/source needed | Phi-4-mini model card / technical report | not yet fetched and read in full |
| **Feasibility status** | **UNVERIFIED** | |

## Candidate 5 — Urdu-specialized fine-tune (e.g. `traversaal-ai/alif-urdu-llm`, or an "UrduLLaMA-3B"-class continual-pretrain)

| Field | Value | Status |
|---|---|---|
| Model name | a community Urdu instruction-tuned model built on a Llama-3.2-3B-class backbone (e.g. `traversaal-ai/alif-urdu-llm`; a distinct "UrduLLaMA" line built on Llama-3.1-8B/3.2-3B via continual pretraining on Urdu tokens + LoRA instruction tuning is also documented in a 2026 LREC paper found 2026-09-06 — these may or may not be the same artifact; **which specific checkpoint, if any, would actually be used is not decided**) | reported, identity not yet pinned |
| Parameter count | ~3B class (backbone-dependent) | reported |
| License | inherits the backbone's license (Llama Community License) plus whatever terms the fine-tuning project itself states — **must be checked per-repository**, not assumed permissive | `TODO — UNVERIFIED` |
| Multilingual capability | primarily Urdu + English (bilingual focus), not broad multilingual | reported |
| Urdu capability evidence | **strongest in this candidate set on paper** — continual pretraining on hundreds of millions of Urdu tokens plus Urdu instruction-tuning data is exactly the kind of targeted evidence the other four candidates lack | reported, not independently benchmarked |
| Context length | backbone-dependent (128K if Llama-3.2-3B-based) | reported |
| Expected memory class | comparable to Candidate 2 (~6–7 GB weights at fp16, backbone-dependent) | estimated |
| Inference runtime options | same as its backbone (llama.cpp GGUF likely available or convertible; `transformers` CPU) | to evaluate |
| CoT-style output elicitable? | not a native "thinking" model; step-by-step traces via prompting only; **unknown whether Urdu-instruction-tuning preserved or degraded the backbone's instruction-following well enough to elicit a structured reasoning trace in Urdu** | genuinely unknown — a first-order question for the feasibility benchmark |
| Known limitations | smaller community-maintained fine-tunes carry more provenance risk (training-data documentation, reproducibility of the exact checkpoint, license clarity) than a vendor release; exact checkpoint identity must be pinned (repo + revision hash) before any use | flagged |
| Citation/source needed | the fine-tuning project's model card/repo (`github.com/traversaal-ai/alif-urdu-llm`) and/or the LREC 2026 Urdu-LLM paper found 2026-09-06 — **neither has been read in full**; treat both as `TODO — UNVERIFIED` pending a full read | not yet fetched and read in full |
| **Feasibility status** | **UNVERIFIED** | |

---

## Summary table (paper screen only — no scores computed, no winner)

| # | Candidate | Params | License | Urdu evidence | Native reasoning mode | Screen status |
|---|---|---|---|---|---|---|
| 1 | Qwen3-1.7B | ~1.7B | Apache 2.0 | weak/unverified | yes (thinking mode) | UNVERIFIED |
| 2 | Llama-3.2-3B-Instruct | ~3.2B | Llama 3.2 Community | negative (not in 8 documented langs) | no | UNVERIFIED |
| 3 | Gemma-3-4B-it | ~4B | Gemma Terms | weak/unverified | no | UNVERIFIED |
| 4 | Phi-4-mini-instruct | ~3.84B | MIT | unverified | no | UNVERIFIED |
| 5 | Urdu-specialized fine-tune (backbone-dependent) | ~3B class | inherits backbone + repo terms | strongest on paper | no | UNVERIFIED |

**No candidate is locked.** The next step, per `EXPERIMENT_SPEC.md` §4, is running the
tiny feasibility benchmark (design in `EXPERIMENT_SPEC.md` §5; not yet authorized) across
whichever of these candidates clear a basic paper re-check of license terms, and scoring
them against criteria A–E with real (not assumed) numbers.

## What this screen deliberately does not do

- It does not benchmark accuracy, latency, or Urdu quality — no inference has occurred.
- It does not resolve the Qwen3 "how many languages, does the list include Urdu" question
  from `RESEARCH_PLAN.md` §12 — that remains open there and is inherited here, not
  independently re-litigated.
- It does not treat any secondary source (blog posts, aggregator articles) as equivalent
  to a verified citation under `CLAUDE.md` §2.6 — every non-obvious claim above is marked
  `TODO — UNVERIFIED` or "reported" precisely because it has not been checked against a
  primary source the way `literature/CITATION_VERIFICATION.md` verifies academic
  citations.

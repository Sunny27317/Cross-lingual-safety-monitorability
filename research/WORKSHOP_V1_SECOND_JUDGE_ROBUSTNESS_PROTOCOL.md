# Second-judge robustness protocol (PROSPECTIVE; NOT RUN; 2026-10-07)

> **RECOMMENDATION ONLY — INVESTIGATOR DECISION REQUIRED.** No second judge is selected
> or authorized. No study rationale has been sent to any second judge.

## 1. Why

A single 7B quantized monitor (Falcon-H1-7B-Instruct, Judge V2) is the study's largest
external-validity weakness. A second judge from a different model family, run on the
**same frozen rationales** with the **same rubric**, shows whether the direct/translated
patterns and the judge-versus-human divergence are specific to Falcon.

## 2. Fixed rules (to be frozen in the authorization before any second-judge call)

1. **Secondary only.** The primary judge, primary estimand G and all frozen analyses are
   unchanged. Second-judge quantities are reported separately, labelled "secondary
   robustness (second judge)". They never replace, average with, or select between
   primary values.
2. **Different family.** Not Falcon, not Qwen and not Gemma. The last two are the
   generators, and avoiding them also avoids self-preference.
3. **Same inputs.** The identical task population: 1,871 direct tasks (936 English, 935
   Urdu) and 935 translated tasks. Each task gets the identical Judge V2 instruction and
   the same non-instruction inputs (question, options, suggestion, rationale), from the
   same sealed stages (direct `3077fae1…`, translation `14175ab5…`).
4. **Same labels and parser.** `disclosed / not_disclosed / partial / cannot_tell`; the
   same EVIDENCE/LABEL format and precedence. One identical retry, for runtime errors only.
5. **Frozen identity and configuration.** Exact model ID or snapshot (or weights hash),
   decoding (greedy or temperature 0), maximum tokens, seed if supported, and provider
   version evidence. All are recorded before the first call.
6. **Chosen before any outcome inspection.** The choice must be recorded before the single
   unseal. If it is made after unseal, every second-judge result is labelled
   **post-hoc**.
7. **Independent provenance.** Its own task manifest, authorization, immutable outputs, QC
   and stage seal, and its own output directory. Retries and failures are retained.
8. **Reporting.** Second-judge D_ur, T, AG and R_full. Second-judge-versus-human confusion
   matrices and a "G-analog" (H − D2), reported separately from G. Agreement between the
   two judges on identical inputs (raw counts and contingency). No pooling, no "majority
   judge", no threshold.
9. **No search.** If the selected judge fails technically or on terms, report "second
   judge not completed". Do not try further models until one agrees.
10. **Data governance.** Rationales contain item text from a dataset with an unstated
    licence. Before any hosted API call, verify and record the provider's data-retention
    and training terms and the investigator's approval to send the text.

## 3. Candidates (recommendation only)

Evidence is drawn from `research/POST_PILOT_METHODS_DECISIONS.md` (checked 2026-09-11) and
`research/frozen_sources/JUDGE_GOVERNANCE_RECORD.md`. **No candidate has verified Urdu
*disclosure-judging* evidence.** Recheck every price and version before deciding.

| Candidate | Family | Size / access | Urdu capability evidence | Feasibility and cost | Independence from Falcon and the generators | Reproducibility |
|---|---|---|---|---|---|---|
| **A. Llama-3.1-8B-Instruct** (`meta-llama`) | Meta Llama | 8B; local GGUF via the same llama.cpp build | **Weak / unverified for Urdu.** Already named as the frozen format-fallback backup judge; Urdu is not among the languages the developers officially list (re-verify) | Local, no API cost; about the same runtime as Falcon. Requires accepting the Llama licence | Different family from Falcon, Qwen and Gemma | Exact weights hash, local, greedy; Metal is not bitwise deterministic |
| **B. GPT-5.4** (`gpt-5.4-2026-03-05`) or **GPT-4.1** (`gpt-4.1-2025-04-14`) | OpenAI | Hosted API; no weights | Multilingual family. GPT-5.4 was used as a CoT verification judge by Onyame et al. (relevance, not validity). No verified Urdu disclosure benchmark | API cost (recorded rates: GPT-5.4 $2.50 / $15 per M tokens; GPT-4.1 $2 / $8). About 2,806 judgments with short outputs, plausibly tens of USD (estimate it from token counts before approval). Needs a data-terms check | Fully independent family | Dated snapshot; retain the raw request and response; the provider may deprecate the snapshot |
| **C. Claude Sonnet 4.6** (`claude-sonnet-4-6`) | Anthropic | Hosted API | Provider multilingual benchmarks (GMMLU/MILU) are indirect evidence. No verified Urdu disclosure result | Recorded release pricing $3 / $15 per M tokens; similar scale of cost | Independent of Falcon and the generators. **Note:** the analysis assistant on this project is an Anthropic model. Disclose this, or prefer A or B to avoid an appearance of a conflict | Version identity per provider model-ID evidence; lifecycle recheck |

**Not recommended:**
- Qwen3-32B: same family as a generator.
- Gemini 2.5 Pro: no stable weight or snapshot identity beyond the provider name.
- Larger Gemma models: generator family.

**Suggested choice for the investigator:**
- **B** if hosted-API data terms are acceptable: the strongest independent second judge.
- Otherwise **A**: weaker, but fully local and already named in the governance record.

Either is acceptable *if chosen before unseal*.

## 4. Files

- `engineering/workshop_v1_second_judge_spec.template.json`: the spec to fill and freeze.
- `engineering/INVESTIGATOR_SECOND_JUDGE_AUTHORIZATION.template.json`: the authorization
  (status TEMPLATE; not an authorization).

Implementation, when authorized, reuses the Judge V2 prompt renderer and parser, and the
direct and translated task manifests, with a new output directory and seal. No code is
written tonight.

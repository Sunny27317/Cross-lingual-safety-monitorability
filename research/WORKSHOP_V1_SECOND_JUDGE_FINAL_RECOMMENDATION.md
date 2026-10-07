# Second judge: final recommendation (2026-10-07; NOT RUN; investigator approval required)

**Fixed rules** (from `WORKSHOP_V1_SECOND_JUDGE_ROBUSTNESS_PROTOCOL.md`):
- The Falcon-H1-7B Judge V2 stays primary and unchanged.
- The second judge is secondary robustness only. It uses the same frozen prompt and rubric
  and the same 2,806 tasks (1,871 direct + 935 translated).
- It must be selected and frozen **before** the result unseal. Otherwise its results are
  post-hoc.

## Workload (measured technical metadata, no labels)

The primary judge's logged prompt lengths total **4,735,292 tokens** (Falcon tokenizer):
3,150,049 direct and 1,585,243 translated. The maximum prompt is 17,172 tokens. Output
tokens were not logged; the outputs are two short lines (EVIDENCE, LABEL) capped at 256
tokens. Other tokenizers may count Urdu text differently, so the costs below use a
**0.7–2.0×** tokenizer range and **≤ 150** output tokens per call (about 0.42M output
tokens in total).

## Options compared

| | Llama-family local | Other open-weight, independent family | API (OpenAI dated snapshot) |
|---|---|---|---|
| Model | `meta-llama/Llama-3.1-8B-Instruct` (already the frozen format-fallback backup) | No strong candidate verified. Aya and Command-family models are independent, but their Urdu coverage is **unverified** here; Qwen3-32B is excluded (generator family) | `gpt-4.1-2025-04-14` (non-reasoning; supports temperature 0), or `gpt-5.4-2026-03-05` |
| Independence from Falcon, Qwen, Gemma | Yes | Yes | Yes |
| Urdu ability | **Weak.** Urdu is not among the languages the developers officially support (re-verify) | Unverified | Strong multilingual family. No verified Urdu-*disclosure* benchmark for any candidate |
| Reproducibility | Weights hash; local; greedy | — | Dated snapshot; retain raw requests and responses; snapshot retirement risk; temperature-0 determinism is not guaranteed by the provider |
| Cost | $0 (about 10–16 h of local compute, similar to the Falcon stages) | — | GPT-4.1 at recorded $2 / $8 per M: input ≈ $6.6–19, output ≈ $3.4, so **≈ $10–25** with retries. GPT-5.4 at $2.50 / $15: **≈ $15–40+**, higher if reasoning tokens are billed |
| Data policy | None (local) | — | **Required check:** sending rationales that contain item text from a dataset with an unstated licence to a hosted API, and the provider's retention and training terms. Needs investigator approval |

## Recommendation

**RECOMMENDED MODEL:** `gpt-4.1-2025-04-14` (OpenAI), as the single secondary robustness
judge. If that snapshot is retired, use `gpt-5.4-2026-03-05` with temperature or reasoning
settings frozen as the API allows. If the data-policy check fails, use the local
`Llama-3.1-8B-Instruct` and state its weak Urdu evidence.

**WHY:** It is the strongest independent-family judge available at low cost. It is a
non-reasoning dated snapshot, so decoding can be fixed at temperature 0 and the
configuration frozen. It is independent of Falcon and of both generators. A weak local
second judge would add little evidence against the "single 7B judge" criticism.

**LOCAL/API:** API (with the local Llama as fallback).

**COST:** about $10–25 (GPT-4.1) or about $15–40+ (GPT-5.4), estimated from measured prompt
tokens. Re-estimate with the provider's tokenizer before approval.

**DATA POLICY CHECK NEEDED:** YES. Check the provider's data retention and training use,
and whether sending dataset-derived text to an API is acceptable under the unstated
dataset licence. Record the investigator's approval.

**INVESTIGATOR APPROVAL REQUIRED:** YES. Fill and freeze
`engineering/workshop_v1_second_judge_spec.template.json` and
`engineering/INVESTIGATOR_SECOND_JUDGE_AUTHORIZATION.template.json` **before** the result
unseal.

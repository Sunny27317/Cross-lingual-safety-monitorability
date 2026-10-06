# Workshop-v1 Pending Governance Packet

Neutral decision brief; no recommendation is made here.

## Frozen study facts

- Models: Qwen3-1.7B and Gemma-3-4B-it.
- Languages: English and Urdu; 120 main source items; 36-item Cue-B subset.
- Samples: k=3, paired across language and condition.
- Planned generation: 3,312 calls.
- Planned Urdu-to-English translations: 936.
- Planned automated judge calls: 2,808: 936 English direct, 936 Urdu direct, 936 translated Urdu.
- Dataset revision and manifests remain frozen; no prompt, cue, decoding, model, or N changes occurred.

## Excluded pilot findings

- Gemma: technical PASS.
- Qwen Urdu: 3/3 language-compliance failures; Unicode, prompt rendering, prompt hashes, visible traces, final-answer parsing, and runtime completion otherwise passed.
- No benchmark content is reproduced here.

## Falcon synthetic format finding

- 40/40 non-study fixture outputs had one evidence line and one canonical label.
- Labels were uppercase (`DISCLOSED`, `NOT_DISCLOSED`, `PARTIAL`, `CANNOT_TELL`).
- The current frozen parser forbids case normalization; no normalization was applied.

## Decisions requested

1. Is a Qwen Urdu language-control amendment authorized?
2. If so, must it be applied symmetrically to both models?
3. What exact rerun pass criterion should apply?
4. Is deterministic Falcon case normalization authorized while preserving raw output and raw label?
5. Should the human reference pool include all 312 candidates or a prospective subset?
6. Which items are pre-main blockers versus downstream-stage blockers?

## Explicit boundaries

- NO MAIN DATA GENERATED.
- NO SCIENTIFIC JUDGE DATA GENERATED.
- NO TRANSLATION DATA GENERATED.
- NO HUMAN LABELING PERFORMED.

# IndicTrans2 translation-stage approval block

This block is technical preparation only. No scientific translation has been
performed.

## Already frozen

- Primary identity: `ai4bharat/indictrans2-indic-en-1B`
- Direction: Urdu to English
- Source code: `urd_Arab`
- Target code: `eng_Latn`
- Expected workload: 936 Urdu Cue-A/Cue-B traces
- Backup identity: `facebook/nllb-200-distilled-600M`

## Reference package, not silently adopted

The repository records the author's Transformers + IndicTransToolkit
pre/post-processing and `num_beams=5`, `max_length=256` as candidates. They
are not frozen values. No local checkpoint, tokenizer, or package installation
is present in this environment.

## Investigator decisions required before translation

1. Exact immutable primary checkpoint/revision and tokenizer revision.
2. Backend and exact package versions, including Transformers, PyTorch, and
   IndicTransToolkit commit/version.
3. Adoption of the reference preprocessing/postprocessing implementation.
4. Decoding values, including whether `num_beams=5` and `max_length=256` are
   approved; batching/device/runtime settings.
5. No-truncation behavior and explicit context-limit failure handling.
6. Fallback activation rule: backup only after a documented technical failure
   of the primary, with no silent per-item substitution.
7. Immutable checkpoint schema, retry, resume, and duplicate policy.

The translation executor remains fail-closed until these values and artifact
hashes are recorded. This does not block preservation of raw generation
outputs or downstream planning artifacts.

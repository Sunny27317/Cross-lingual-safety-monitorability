# IndicTrans2 setup after direct judging

This is a non-executing setup plan. It must be run only after the translator
contract is frozen and scientific translation is separately authorized.

Primary artifact: `ai4bharat/indictrans2-indic-en-1B`, revision
`ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a`. Direction is `urd_Arab` to
`eng_Latn`, using the reference `Transformers` plus `IndicTransToolkit` path.
The repository records the reference commits and model-weight hash, but the
gated config/tokenizer hashes and runtime package lock are still required before
the contract can become executable.

## Non-scientific setup commands

```bash
cd /Users/sullah1/clsm-codex
source .venv/bin/activate
uv pip install --python .venv/bin/python \
  'transformers==4.51.3' \
  'torch==2.6.0' \
  'tokenizers==0.21.1' \
  'sentencepiece==0.2.2' \
  'sacremoses==0.2.0' \
  'sacrebleu==2.6.0' \
  'indic-nlp-library-itt==0.1.1' \
  'huggingface-hub==0.36.2' \
  'IndicTransToolkit @ git+https://github.com/VarunGumma/IndicTransToolkit@3efb8418d0721b4ce267c2b3586899d313191357'
```

These pins are the repository's Python 3.11/macOS-arm64 compatibility set,
selected from the existing project lock and the toolkit's declared runtime
requirements. Record the installed environment before the contract is frozen.
Download the exact primary
revision into the governed cache, hash model/config/tokenizer files, and write
those hashes plus device/dtype/package metadata into
`engineering/indictrans2_final_contract.json`. Do not run translation during
setup.

The approved segmentation implementation is
`clsm.workshop_v1.translation.segment_source_chunks`: line, sentence, clause,
then hard token boundaries, with at most 200 source tokens per chunk. It keeps
source order, records chunk metadata, reassembles every chunk, and fails the
whole trace if any chunk cannot be translated after the governed retry.
Decoding is deterministic beam search with `num_beams=5`, `max_length=256`,
`min_length=0`, `num_return_sequences=1`, and `use_cache=true`; no silent
truncation is permitted. The NLLB backup is permitted only after a documented
technical primary failure and must never silently substitute per item.

Required pre-translation evidence: cache path, exact revisions, all artifact
hashes, package versions, preprocessing/postprocessing API identifiers, device,
dtype, batch size, and a synthetic Urdu smoke test. Scientific translation
remains disabled until all are frozen.

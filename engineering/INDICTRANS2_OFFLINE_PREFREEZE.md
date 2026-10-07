# IndicTrans2 offline pre-freeze package

Prepared without downloading or loading model weights. The official model page
states that the repository is gated: access requires a Hugging Face account and
agreement to share contact information/accept the access conditions. The
investigator must complete that action in a browser before the CLI download.

## Access

- Repository: `ai4bharat/indictrans2-indic-en-1B`
- Frozen revision: `ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a`
- Login: required for gated file access (`hf auth login` or an equivalent token
  already configured in the normal terminal).
- Terms/contact sharing: required on the model page before files are accessible.
- User action: open the model page, sign in, accept the displayed conditions,
  then authenticate the normal terminal with a read-enabled HF token.

## Candidate environment (not installed)

- Python 3.11 (repository runtime)
- `transformers<5.0.0` (official model usage requirement)
- PyTorch version: unresolved; record the installed version before freeze
- `sentencepiece`: unresolved; record exact installed version
- IndicTransToolkit 1.1.1 at commit `3efb8418d0721b4ce267c2b3586899d313191357`
- `accelerate`: install only if the selected Transformers device map requires it

Exact package versions, device, dtype, tokenizer/config hashes, and fallback
revision remain unresolved until the isolated environment is created and
recorded. No scientific choice is made by this document.

## Post-Falcon commands

```bash
cd /Users/sullah1/clsm-codex
source .venv/bin/activate
hf auth login
mkdir -p experiments/_artifacts/indictrans2/ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a
hf download ai4bharat/indictrans2-indic-en-1B \
  --revision ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a \
  --local-dir experiments/_artifacts/indictrans2/ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a
.venv/bin/python engineering/indictrans2_artifact_hash.py \
  experiments/_artifacts/indictrans2/ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a \
  --output engineering/indictrans2_artifact_inventory.json
.venv/bin/python engineering/indictrans2_runtime_record.py \
  --output engineering/indictrans2_runtime_inventory.json
```

Then run the synthetic-only real-backend smoke test and tokenizer segmentation
validator. Neither may consume Workshop-v1 traces. Freeze the resulting
contract only after all artifact/package/runtime hashes are recorded.

## Resource estimate

The recorded model weight is approximately 4.09 GB (`model.safetensors`). Plan
at least 6 GB free for weights, tokenizer/config files, cache, and inventories.
Peak RAM is not frozen by upstream metadata; a conservative planning envelope
is 8–12 GB for CPU inference plus Python/framework overhead. Measure it during
the synthetic smoke test. MPS is not required for reproducibility and should
not be enabled while the Falcon job is active; device/dtype remain to be
recorded at freeze time.

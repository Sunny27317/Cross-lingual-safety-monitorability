#!/usr/bin/env bash
set -euo pipefail

# Run only after active model workloads finish. This performs environment and
# artifact setup; it never performs scientific translation.
ROOT="/Users/sullah1/clsm-codex"
MODEL_ID="ai4bharat/indictrans2-indic-en-1B"
REVISION="ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a"
TOOLKIT_COMMIT="3efb8418d0721b4ce267c2b3586899d313191357"
CACHE="$ROOT/experiments/_artifacts/indictrans2/$REVISION"
PYTHON=".venv/bin/python"

# These pins are the repository's Python 3.11/macOS-arm64 compatibility set:
# transformers/torch/tokenizers are already locked by the project; the
# remaining runtime packages are pinned so the resulting environment is
# reproducible rather than resolving latest versions.
TRANSFORMERS_VERSION="4.51.3"
TORCH_VERSION="2.6.0"
TOKENIZERS_VERSION="0.21.1"
SENTENCEPIECE_VERSION="0.2.2"
SACREMOSES_VERSION="0.2.0"
SACREBLEU_VERSION="2.6.0"
INDIC_NLP_ITT_VERSION="0.1.1"
HF_HUB_VERSION="0.36.2"

cd "$ROOT"
source .venv/bin/activate

if ! env -u HF_TOKEN hf auth whoami >/tmp/clsm-hf-whoami.txt 2>&1; then
  cat /tmp/clsm-hf-whoami.txt >&2
  echo "FAIL_CLOSED: authenticate with 'hf auth login' and accept the gated model terms in a browser" >&2
  exit 2
fi

uv pip install --python "$PYTHON" \
  "transformers==$TRANSFORMERS_VERSION" \
  "torch==$TORCH_VERSION" \
  "tokenizers==$TOKENIZERS_VERSION" \
  "sentencepiece==$SENTENCEPIECE_VERSION" \
  "sacremoses==$SACREMOSES_VERSION" \
  "sacrebleu==$SACREBLEU_VERSION" \
  "indic-nlp-library-itt==$INDIC_NLP_ITT_VERSION" \
  "huggingface-hub==$HF_HUB_VERSION" \
  "IndicTransToolkit @ git+https://github.com/VarunGumma/IndicTransToolkit@$TOOLKIT_COMMIT"

mkdir -p "$CACHE"
if ! env -u HF_TOKEN hf download "$MODEL_ID" --revision "$REVISION" \
  --local-dir "$CACHE"; then
  echo "FAIL_CLOSED: exact model revision is unavailable to this HF account." >&2
  echo "Required action: request/accept access for $MODEL_ID at https://huggingface.co/$MODEL_ID, then rerun." >&2
  exit 3
fi

"$PYTHON" - "$CACHE" "$MODEL_ID" "$REVISION" <<'PY'
from pathlib import Path
import sys
from huggingface_hub import HfApi

cache, model_id, revision = sys.argv[1:]
info = HfApi().model_info(model_id, revision=revision)
if info.sha != revision:
    raise SystemExit(f"FAIL_CLOSED: resolved revision {info.sha!r} != {revision!r}")
required = (Path(cache) / "config.json", Path(cache) / "tokenizer_config.json")
missing = [str(p) for p in required if not p.exists()]
if missing:
    raise SystemExit(f"FAIL_CLOSED: pinned snapshot missing required files: {missing}")
print({"model": model_id, "revision": revision, "resolved_sha": info.sha})
PY

"$PYTHON" engineering/indictrans2_artifact_hash.py "$CACHE" \
  --model-id "$MODEL_ID" --revision "$REVISION" \
  --output engineering/indictrans2_artifact_inventory.json
"$PYTHON" engineering/indictrans2_runtime_record.py \
  --output engineering/indictrans2_runtime_inventory.json

echo "SETUP_COMPLETE: review inventories, freeze contract, and obtain separate translation authorization"

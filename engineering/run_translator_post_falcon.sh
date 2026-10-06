#!/usr/bin/env bash
set -euo pipefail

# Prepared for post-Falcon use; do not run during an active model workload.
cd /Users/sullah1/clsm-codex
source .venv/bin/activate
bash engineering/indictrans2_bootstrap.sh
.venv/bin/python engineering/indictrans2_synthetic_smoke.py \
  experiments/_artifacts/indictrans2/ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a
.venv/bin/python engineering/indictrans2_segmentation_validator.py \
  experiments/_artifacts/indictrans2/ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --preflight
echo "NEXT: obtain/validate explicit translation authorization before --execute"

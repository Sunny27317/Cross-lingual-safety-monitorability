#!/usr/bin/env bash
set -euo pipefail

# C6: non-model validation of the amended D-TR translation_units/reassemble path.
# Loads only the pinned tokenizer (never the model); reads completed translation records
# structurally and read-only; writes a NEW immutable JSON artifact and refuses to
# overwrite it or the historical engineering/indictrans2_segmentation_validation.json.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.amended_path_validation \
  --output engineering/indictrans2_amended_path_validation_2026-10-06.json

#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Technical checks only.  The canonical seal is written separately and only by
#   PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --seal
# Each command below exits non-zero when its gate fails.
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.post_translation_pipeline --translation-qc
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --verify-seal
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --preflight
if [[ "${1:-}" != "--execute" ]]; then
  echo 'POST_TRANSLATION_PREFLIGHT_PASS'
  echo 'No scientific judging was executed.'
  exit 0
fi
if [[ -z "${2:-}" ]]; then
  echo 'FAIL_CLOSED: translated-judge authorization path is required' >&2
  exit 2
fi
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --execute --authorization "$2"
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --post-qc

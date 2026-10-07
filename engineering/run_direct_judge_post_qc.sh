#!/usr/bin/env bash
set -euo pipefail

# Run only after the active direct-judge process has exited. This wrapper does
# technical QC/sealing and never prints scientific label distributions.
cd /Users/sullah1/clsm-codex
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.direct_judge_post_qc --post-qc
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.direct_judge_post_qc --post-qc --seal

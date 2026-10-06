# Workshop-v1 post-translation commands

Run these only after the translation launcher reports zero remaining tasks. Every step is
fail-closed (non-zero exit on failure) and none of them inspects label distributions.

**One seal writer.** The canonical translation stage seal
(`experiments/_runs/workshop-v1-translation/translation_stage_seal.json`, schema
`workshop-v1-translation-seal/2`) is written **only** by `translator_launcher --seal`. The
former `post_translation_pipeline --seal-translation` writer was removed on 2026-10-06.

```bash
cd /Users/sullah1/clsm-codex
# 1. Technical QC (read-only)
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --post-qc
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.post_translation_pipeline --translation-qc
# 2. Canonical seal (immutable; refuses if a seal exists or QC/amendment/authorization fail)
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --seal
# 3. Independent re-verification of the seal from disk
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --verify-seal
# 4. Translated-judge preflight (consumes and re-verifies the seal; prints translation_stage_hash)
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --preflight
```

Translated judging requires a separate investigator authorization. That authorization
must bind the `translation_stage_hash` printed by step 4. Only after approval, run:

```bash
bash engineering/run_workshop_v1_post_translation.sh --execute engineering/INVESTIGATOR_TRANSLATED_URDU_JUDGE_AUTHORIZATION.json
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --progress
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --post-qc
```

Analysis-table construction is a later, separately authorized step. It emits one row per
judge task. `.retry-2.json` attempts merge into their task, and the terminal attempt is
the highest attempt number. The summary records `analysis_input_layer_sha256`; see
`research/WORKSHOP_V1_PRE_RESULT_ANALYSIS_FREEZE_ADDENDUM_V2.json`.

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
from pathlib import Path
from clsm.workshop_v1.post_translation_pipeline import build_analysis_table
build_analysis_table(
    generation_dir=Path('experiments/_runs/workshop-v1-main-attempt-2'),
    direct_judge_dir=Path('experiments/_runs/workshop-v1-direct-judge'),
    translated_judge_dir=Path('experiments/_runs/workshop-v1-translated-urdu-judge'),
    output=Path('experiments/_runs/workshop-v1-analysis/analysis_records.jsonl'),
)
PY
```

The QC, seal, verify and preflight commands are technical checks. Judge execution and
analysis each require their own explicit governance authorization.

# Workshop-v1 fast-follow commands

Prepared while direct Falcon judging is active. Do not run any command marked
WAIT or AUTH until its gate is satisfied. Commands here do not authorize a
scientific stage.

```bash
cd /Users/sullah1/clsm-codex

# 1. WAIT — direct-judge technical count check (after process exits)
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.direct_judge_post_qc --post-qc

# 2. WAIT — non-substantive post-QC and 3. WAIT — immutable stage sealing
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.direct_judge_post_qc --post-qc --seal

# 4. WAIT — translator environment setup
bash engineering/indictrans2_bootstrap.sh

# 5. WAIT — artifact inventory/hash verification
.venv/bin/python engineering/indictrans2_artifact_hash.py \
  experiments/_artifacts/indictrans2/ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a \
  --output engineering/indictrans2_artifact_inventory.json

# 6. WAIT — synthetic-only segmentation/backend smoke test
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --preflight

# 7. AUTH — translation authorization validation
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --preflight

# 8. AUTH — 935 translation launch
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --execute --authorization engineering/INVESTIGATOR_TRANSLATION_AUTHORIZATION.json

# 9. WAIT — translation progress
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --progress

# 10. WAIT — translation QC
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --post-qc

# 11. WAIT — translation stage sealing is recorded by its post-QC workflow

# 12. AUTH — translated-Urdu judge authorization/preflight
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --preflight

# 13. AUTH — translated-Urdu judge launch (after a production executor exists)
# PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --execute --authorization engineering/INVESTIGATOR_TRANSLATED_URDU_JUDGE_AUTHORIZATION.json

# 14. WAIT — translated-Urdu judge QC
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --post-qc

# 15. HUMAN/ORPI — deterministic pool validation/export only after institutional approval
PYTHONPATH=src .venv/bin/python -c 'from clsm.workshop_v1.human_pool import validate_pool; print(validate_pool())'

# 16. AUTH — final locked descriptive analysis
# PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.analysis --run-locked-analysis

# 17. WAIT — manuscript artifact generation from verified outputs
# PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.tables --from-locked-artifacts
```

The active judge process must finish before steps 1–6. Translation and
translated judging should run sequentially on the 16 GB MacBook Air to avoid
RAM/Metal contention. Human steps additionally require ORPI/institutional
determination, recruitment, consent, and compensation decisions.

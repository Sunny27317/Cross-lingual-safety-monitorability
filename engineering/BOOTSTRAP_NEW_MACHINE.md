# New-machine bootstrap (non-executing scientific setup)

This procedure never launches generation, translation, judging, annotation, or
analysis.

```bash
set -euo pipefail
export REPO_ROOT="${REPO_ROOT:-$HOME/src/Cross-lingual-safety-monitorability}"
export DATA_ROOT="${DATA_ROOT:-$HOME/data/clsm}"
export MODEL_ROOT="${MODEL_ROOT:-$HOME/models/clsm}"
export LLAMA_ROOT="${LLAMA_ROOT:-$HOME/tools/llama.cpp}"

git clone --branch research/workshop-v1-post-translation-pipeline   https://github.com/Sunny27317/Cross-lingual-safety-monitorability.git "$REPO_ROOT"
cd "$REPO_ROOT"
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Restore the external dataset at the pinned revision and verify its three file
hashes against `engineering/workshop_v1_dataset_summary.json`. Authenticate
interactively; never put the token in a script:

```bash
hf auth login
hf download large-traversaal/openbookqa_urdu_final   --repo-type dataset --revision e4186f6ba5c3395c6f5cc99e1efadd7755ed4055   --local-dir "$DATA_ROOT/openbookqa_urdu_final/e4186f6ba5c3395c6f5cc99e1efadd7755ed4055"
```

Restore IndicTrans2 exactly with `engineering/indictrans2_bootstrap.sh` and
verify `engineering/indictrans2_artifact_inventory.json`. Restore the GGUF
files listed in `MODEL_ARTIFACT_RECOVERY_MANIFEST.json`; verify each SHA-256.
Build llama.cpp at the recorded commit and verify the binary hash.

```bash
python -m pytest -q
python -m ruff check src tests
python -m mypy src/clsm
git diff --check
```

Before any resume, replace hard-coded local paths through environment/config
values and confirm all frozen hashes. Never use an unpinned model revision or
an empty output directory as a substitute for archived outputs.

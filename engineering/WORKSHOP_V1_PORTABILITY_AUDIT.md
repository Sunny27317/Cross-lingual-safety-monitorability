# Workshop-v1 portability audit

| Paths | Classification | Portable replacement |
|---|---|---|
| `configs/workshop_v1/models.yaml`, `judge_model.yaml` | RUNTIME_BLOCKING | `${CLSM_MODEL_ROOT}` and `${CLSM_LLAMA_ROOT}` or machine-local config. |
| `src/clsm/workshop_v1/gemma_download.py` | RUNTIME_BLOCKING | Require explicit output directory or `${CLSM_MODEL_ROOT}`. |
| IndicTrans2/bootstrap/run wrappers | RUNTIME_BLOCKING | Derive repo root from script location; accept `${CLSM_REPO_ROOT}`. |
| Engineering command documents | DOCUMENTATION_ONLY | Use `$REPO_ROOT`, `$DATA_ROOT`, `$MODEL_ROOT`. |
| Research readiness/handoffs | HISTORICAL_PROVENANCE | Add erratum; preserve observed commands. |
| Mac environment checks | HISTORICAL_PROVENANCE | Preserve exactly. |
| `.git` worktree file | LOCAL-ONLY | Recreate worktrees from Git refs. |

No portability patch was applied because the live judge uses current
configuration. A future patch must not alter frozen scientific hashes.

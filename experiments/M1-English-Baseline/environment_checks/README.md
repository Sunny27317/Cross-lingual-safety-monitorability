# environment_checks/

Archive of **unsuccessful or exploratory** environment/provisioning checks. Nothing
here is the canonical observed environment for an authorized Stage-A/Stage-B/pilot run.

## Artifact roles (do not conflate)

| Artifact | Role |
|---|---|
| `configs/milestone1/runtime.yaml` | The **proposed / required target** environment. Permanently `runtime_role: proposed` (D-026) — never mutated into an observation record. |
| `environment_checks/*.txt` (this directory) | Dated logs of **unsuccessful or exploratory** provisioning/environment checks — e.g. an attempt run from a machine that turned out not to be a GPU box. Kept for provenance; never authoritative. |
| `experiments/M1-English-Baseline/observed_env.txt` | **Reserved.** Created only once a real NVIDIA GPU environment has been provisioned and validated for the experiment (`PRE_RUN_READINESS.md` §2.3–2.4) — the actual observed environment that will run Stage A / Stage B. **Does not exist yet.** |
| `manifest.json` / `clsm.provenance` | Per-run observed provenance, captured automatically by the harness once a real run executes. |

## Contents

- `2026-09-01-local-mac.txt` — an exploratory provisioning attempt from this project's
  local development machine (Intel Mac, no NVIDIA GPU, not Linux). Confirmed the host
  cannot run the pilot and that this tool session has no mechanism to reach a remote GPU
  box. See `literature/DECISION_LOG.md` D-027.

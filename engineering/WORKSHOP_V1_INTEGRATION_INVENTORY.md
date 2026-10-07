# Workshop-v1 integration inventory

This is an inventory only; no branch was merged and no other worktree was modified.

## Files from Codex that must eventually merge

- `src/clsm/workshop_v1/**` and `src/clsm/workshop_v1_readiness.py`
- `tests/workshop_v1/**`
- `engineering/WORKSHOP_V1_ENGINEERING_PLAN.md`
- `engineering/WORKSHOP_V1_IMPLEMENTATION_STATUS.md`
- `engineering/workshop_v1_dataset_summary.json` and eventual frozen population manifest
- `research/CODEX_WORKSHOP_V1_HANDOFF.md`

## Files from Claude that must eventually merge

- The scientific decision record and frozen selections, including `research/CLAUDE_WORKSHOP_V1_HANDOFF.md` and any authoritative model/dataset/cue decisions.
- `README.md` only if Claude adds the planned scientific status section.
- `paper/main.md` and paper assets when the analysis is complete.
- Any Claude-authored updates to `literature/DECISION_LOG.md`; Codex must not overwrite them.

## Likely conflict points

`README.md`, both research handoffs, `literature/DECISION_LOG.md`, and any shared
configuration YAML are likely conflict points. Resolve by keeping the scientific
decision record authoritative and retaining Codex engineering provenance references.

# Workshop-v1 parallel preprint acceleration status

This document records static preparation performed while direct Falcon Judge V2
evaluation is active. No judge output was inspected substantively and no model,
translation, annotation, or real analysis call was made.

## Stage boundaries

- Direct judging: active in `experiments/_runs/workshop-v1-direct-judge`; do not
  touch until its owner reports completion and post-QC is authorized.
- Translation: 935 Urdu cued traces, excluding retained missing generation
  `9-1065`; not executable until the IndicTrans2 contract is fully frozen and
  scientific translation is authorized.
- Translated-Urdu judging: 935 tasks, separately namespaced and authorization
  templated; it cannot use direct-judge output or human output as a substitute.
- Human validation: 312 candidates (240 Cue-A, 72 Cue-B), parity packet is
  question + ordered options + exact suggestion + trace; annotation requires
  institutional and investigator approval.
- Analysis: Cue-A and Cue-B remain separate; no confirmatory testing; primary
  compliance is descriptive quality/covariate, with only the pre-approved
  >=0.50 exploratory sensitivity; no causal paraphrase-control claim.

## Static readiness

`engineering/workshop_v1_translation_manifest.json` and
`engineering/workshop_v1_translated_urdu_judge_manifest.json` are deterministic
935-task plans. `src/clsm/workshop_v1/translator_launcher.py` remains fail-closed
while the contract status is unresolved. The translated-judge authorization
template is `engineering/INVESTIGATOR_TRANSLATED_URDU_JUDGE_AUTHORIZATION_TEMPLATE.json`.
No authorization file is approved by this preparation sprint.

The IndicTrans2 setup checklist is in `engineering/workshop_v1_translator_setup.md`.
It records the pinned model revision and reference commits, but deliberately
leaves gated artifact hashes and runtime package versions as blockers. The
approved no-truncation segmentation and fallback rules are already encoded in
`engineering/indictrans2_final_contract.json` and the translation module.

## Human and institutional package

The parity export functions are in `src/clsm/workshop_v1/human_pool.py`; the
latest rater instructions and adjudicator instructions are in `docs/rater_package/`.
Draft institutional inquiry and recruitment language are in
`docs/ORPI_INQUIRY_WORKSHOP_V1.md` and `docs/RATER_RECRUITMENT_MESSAGE.md`.
They are drafts, do not claim an exemption, and contain no annotation results.

## Fast-follow critical path

After direct-judge completion: (A) direct-judge post-QC; (B) acquire/hash the
approved IndicTrans2 environment; (C) translator preflight; (D) run 935
translations after authorization; (E) translation QC and stage lock; (F) run
935 translated-Urdu judge calls after separate authorization; (G) institutional
approval and human annotation; (H) locked descriptive analysis; (I) fill
manuscript tables/figures; (J) claim/provenance audit.

Translation setup, human paperwork, and static manuscript slots may proceed in
parallel. Model-backed translation and any judging must be sequentially gated;
on a 16 GB MacBook Air they should not be run concurrently because of RAM and
Metal/backend contention.

## Commands after gates close

These are prepared commands, not executed commands:

```bash
cd /Users/sullah1/clsm-codex
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --preflight
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --execute --authorization engineering/INVESTIGATOR_TRANSLATION_AUTHORIZATION.json
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --progress
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --resume --authorization engineering/INVESTIGATOR_TRANSLATION_AUTHORIZATION.json
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translator_launcher --post-qc
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.translated_judge_launcher --preflight
PYTHONPATH=src .venv/bin/python -m clsm.workshop_v1.direct_judge_launcher --preflight
```

The translated-judge launcher is currently planning-only: its preflight stays
false until complete translation artifacts and a frozen translation contract
exist. The direct-judge launcher must be post-QC'd by its active-run owner
before any downstream work is authorized.

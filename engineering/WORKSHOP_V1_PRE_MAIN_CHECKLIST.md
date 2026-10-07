# Workshop-v1 pre-main checklist

This is an engineering checklist. It never authorizes execution by itself.

| Gate | Current status | Evidence / required action |
|---|---|---|
| Frozen dataset/manifests/source rows | PASS | `frozen_validation.py`; 120 main, 36 Cue-B |
| Qwen D5 configuration and amended pilot | PASS / CLOSED | D5 study hash `d3af8414...d002c014`; six-call evidence preserved |
| Gemma artifact/configuration | PASS | pinned local artifact and llama.cpp identity |
| Formal Urdu equivalence packet | PASS | Original PDF preserved; three blank Meaning-preserved fields closed by separate investigator-recorded telephone clarification |
| Mismatch/uncertainty governance | PASS (not triggered) | 120 PASS, no MINOR_LANGUAGE_ONLY/MATERIAL_MISMATCH/UNCERTAIN |
| IndicTrans2 implementation | DOWNSTREAM: READY_AWAITING_INVESTIGATOR_DECISION | required before translation, not raw generation |
| Judge format contract | PASS | synthetic format gate and hashes pass; no scientific judging |
| Human pool/export tooling | PASS | deterministic 312 candidates; no annotation executed |
| Main workload planner | PASS | 3,312 generation, 936 translation, 2,808 judge, 312 human candidates |
| Main executor | TECHNICAL_BLOCKER | boundary implemented fail-closed; scientific backend disabled |
| Generation configuration hash | PASS | `7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec` |
| Final whole-study hash | DOWNSTREAM: READY_AWAITING_ARTIFACT | translator/judge/human contracts remain unresolved |
| Main generation authorization | READY_AWAITING_HUMAN_ACTION | explicit authorization tied to generation hash required |
| Human/ORPI/rater authorization | DOWNSTREAM: READY_AWAITING_HUMAN_ACTION | required before human annotation |

The main preflight must remain `MAIN_GENERATION_READY: false` until every required
gate is satisfied and explicit authorization is recorded. No `--force` or bypass
switch exists. D5 must not be rerun.

## Post-generation downstream closure (2026-10-04)

- Generation lock: PASS/LOCKED at 3312 structural tasks, 3311 runtime successes, one retained missing timeout `9-1065` under D-PG-2.
- Compliance: no primary inclusion floor; one exploratory sensitivity using the existing >=0.50 parser flag.
- Rater parity export: READY for institutional authorization; versioned 312-row packet v2 contains question, ordered options, exact suggestion, and trace with model/item/condition/sample blinded.
- Translation: NOT READY; no-truncation segmentation is approved, but exact IndicTrans2 checkpoint/tokenizer/backend/package provenance remains unresolved.
- Direct Judge V2: contract and separate manifests READY_AWAITING_AUTHORIZATION (936 English, 935 Urdu); no scientific calls performed.
- Translated judging: downstream of translation and not ready.
- Human annotation: institutional/rater authorization remains required.

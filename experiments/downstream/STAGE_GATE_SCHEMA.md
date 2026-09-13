# Downstream stage-gate schema

`clsm.downstream.stage_gates` provides one immutable ledger format for every
post-pilot stage. Each approval binds a protocol hash and evidence hash, names
an approver, records UTC time and a signature, and is rejected when absent,
duplicated, stale, pending, or unsigned. Chat messages and environment flags are
not substitutes.

| Gate | Required decision/artifact |
| --- | --- |
| G0 | English completion/integrity artifact |
| G1 | institutional ethics/data-governance determination |
| G2 | approved human-reference protocol |
| G3 | approved rater recruitment/competence record |
| G4 | locked human reference |
| G5 | signed judge acceptance criteria |
| G6 | calibration report and investigator decision |
| G7 | locked Urdu equivalence manifest |
| G8 | Urdu execution authorization |
| G9 | translation diagnostic authorization |
| G10 | signed confirmatory parameters, including SESOI/N decisions |
| G11 | confirmatory execution authorization |
| G12 | final-analysis authorization |

The ledger is a contract, not an automatic workflow: it does not select models,
translators, thresholds, annotators, or statistical parameters.

# Project completion checklist

Outcome-blind checklist from the active English pilot to submission. No item authorizes
scientific execution by itself.

| Task | Status | Gate / owner |
|---|---|---|
| Frozen English collection | IN PROGRESS | Blocked until active pilot completes |
| English integrity and descriptive instrumentation review | BLOCKED BY ENGLISH PILOT | Pilot owner |
| Downstream population and estimands | REQUIRES SUPERVISOR | Before labels |
| Judge candidate identity and acceptance rule | REQUIRES HUMAN | Investigator |
| Human reference recruitment/governance | REQUIRES HUMAN | Institution and supervisor |
| Human rubric and annotation training | REQUIRES HUMAN | Native bilingual lead |
| Judge calibration and heldout validation | REQUIRES COMPUTE + HUMAN | After reference lock |
| Urdu item translation/equivalence lock | REQUIRES HUMAN | Before Urdu outputs |
| Urdu generator configuration/authorization | REQUIRES SUPERVISOR | Separate stage gate |
| Native Urdu annotation | REQUIRES HUMAN | After Urdu traces |
| Translator selection and control freeze | REQUIRES SUPERVISOR | Before translation outputs |
| Same-trace translation diagnostic | REQUIRES COMPUTE | After translator lock |
| Primary/secondary paired analysis | REQUIRES COMPUTE | Frozen code and manifests |
| Confirmatory test coverage validation | REQUIRES COMPUTE | Before N freeze |
| SESOI, alpha, multiplicity and N | REQUIRES SUPERVISOR | Must not use favorable pilot effects |
| Confirmatory preregistration | REQUIRES SUPERVISOR | Before confirmation |
| Paper pre-results methods | DONE | This branch / existing scaffold |
| Paper results/discussion/conclusion | BLOCKED BY SCIENTIFIC DATA | Results owner |
| Reproducibility release and governance review | REQUIRES HUMAN | Steward/institution |

## Critical path

English integrity review → downstream freeze → human reference → judge calibration → Urdu
equivalence → Urdu inference/reference → translator diagnostic → paired analysis →
confirmatory design freeze → confirmatory experiment → paper results.

## Scope labels

**MUST HAVE:** native reference, provenance, item-disjoint calibration, matched H/D/T
triples, translation audit, missingness, both error directions, clustered uncertainty,
governance and a validated confirmatory method.

**SHOULD HAVE:** backup judge, rewrite control, adjudicated sensitivity, small second
translator audit and native-original robustness subset.

**OPTIONAL / FUTURE:** judge ensembles, additional languages/models, latent-cognition
claims, mediation and broad generalization.


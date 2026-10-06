# Post-judge reproducibility attack surface

| Risk | Classification | Control |
|---|---|---|
| mid-run code changes | already addressed | execution commit/hash and stage seal |
| uncommitted historical execution | document before submission | base commit plus dirty-tree snapshot |
| identity translations | already addressed | D-TR-2 provenance and secondary-only exclusion |
| amendment ambiguity | already addressed | base/amendment/effective hashes |
| historical failures | already addressed | immutable attempt artifacts |
| retry flexibility | already addressed | two-attempt state machine, no attempt 3 |
| human packet leakage | engineering fix before annotation | packet QC and blinding manifest |
| post-result flexibility | document before submission | pre-result freeze/addenda |
| missingness | investigator decision required if unresolved | explicit terminal states |
| stage sealing | engineering fix before judging completion | one canonical writer and independent verification |
| model/runtime drift | document before submission | runtime/artifact inventory |

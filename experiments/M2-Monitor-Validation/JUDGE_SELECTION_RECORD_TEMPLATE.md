# Judge selection record — EMPTY TEMPLATE

**No candidate selected. No acceptance threshold fixed by this package.** Complete
prospectively; link the signed/dated decision before candidate scientific evaluation.

| Field | Investigator entry |
|---|---|
| Record/version, investigator, UTC date | [REQUIRED] |
| Construct, population, languages, intended use | [REQUIRED] |
| Independence from English pilot outcomes | [ATTESTATION + access history] |
| Candidate specs/hashes and immutable identity evidence | [UNRESOLVED] |
| Candidate rationale independent of desired effects | [REQUIRED] |
| Rubric/version and human reference protocol | [UNRESOLVED] |
| Partial/cannot-tell/abstain policy and rationale | [UNRESOLVED] |
| Calibration/heldout trace and item manifests/hashes | [UNRESOLVED] |
| Human reference hashes, raw sources and lock times | [PENDING HUMAN WORK] |
| Acceptance metrics, error tradeoffs, thresholds if justified | [HUMAN SCIENTIFIC DECISION] |
| Evidence/utility basis for any threshold | [REQUIRED; no model-size heuristic] |
| Interval/resampling plan; multiplicity policy | [UNRESOLVED] |
| Missingness/coverage comparability rule | [UNRESOLVED] |
| Resource/privacy constraints and identity verification | [REQUIRED] |
| Calibration report hashes | [PENDING] |
| Selection decision and all rejected candidates | [PENDING; none is allowed] |
| Chosen spec locked before heldout access | [PENDING] |
| Heldout validation report; acceptance/rejection | [PENDING] |
| Deviations, uncertainty propagation and validity limits | [PENDING] |
| Separate stage authorization | [NOT PRESENT] |

Do not fill pending scores from invented examples. A complete computational report is
not a scientific acceptance decision or permission to execute downstream stages.

## Judge acceptance sign-off (fills `JudgeAcceptanceCriteria` exactly)

Complete this table **before any candidate output exists**, one row per field, matching
`clsm.downstream.contracts.JudgeAcceptanceCriteria` one-to-one so this form and the code
contract cannot drift apart. The code rejects candidate scoring unless a record built
from these exact fields is signed and hashed first (`research/NEXT_STAGE_SCIENTIFIC_
FREEZE.md` item 12, D-073). **No value in the "Entry" column is filled in by this
repository or by Codex — every row is an investigator judgment about error costs.**

| Field (= code field) | Meaning | Entry |
|---|---|---|
| `plan_hash` | Content hash of the exact `ProspectiveCandidatePlan` this criteria binds to | |
| `investigator` | Name/role of the person signing | |
| `max_false_negative_rate` | Maximum tolerable rate of missing a real acknowledgment, with one sentence on the real-world consequence of exceeding it | |
| `max_false_positive_rate` | Maximum tolerable rate of inventing an acknowledgment, with one sentence on the real-world consequence of exceeding it | |
| `minimum_coverage` | Minimum acceptable non-abstention rate | |
| `required_interval_half_width` | Required precision (interval half-width) at the planned calibration-set size | |
| `selection_if_unmet` | `primary` / `backup` / `neither` — which candidate is used if criteria are not met | |
| `decision_record` | Free-text rationale for the four numeric values above; must not cite a borrowed threshold from an unrelated benchmark | |
| `signed_utc` | Timestamp, must include a timezone | |
| `investigator_signature` | Must be an actual name/identifier — not `UNSIGNED`, `HUMAN REQUIRED`, or `PENDING`, all of which the code rejects | |

**Enforcement, not a numeric gate:** the code checks that this record exists, binds to
the correct plan, and was signed strictly before the first candidate output's
`created_utc` — it never evaluates whether the numbers here are good enough, and it
never uses them to auto-select a candidate. Reading the calibration report and deciding
whether the achieved metrics meet these criteria remains a separate, human act recorded
in the main table above.

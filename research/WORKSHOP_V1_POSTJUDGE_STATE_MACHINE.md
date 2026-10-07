# Post-translated-judge technical state machine

This is a technical execution contract. Scientific label values are never
counted by the status/progress tools.

| State | Terminal | Retry/model call | Analysis | Required action |
|---|---:|---:|---:|---|
| SUCCESS | yes | no | eligible | none |
| SUCCESS_ON_RETRY | yes | no | eligible | none |
| RUNTIME_ERROR_RETRY_AVAILABLE | no | one governed retry | not yet | resume under same authorization |
| RETRY_EXHAUSTED | yes | no attempt 3 | missing | retain failure and escalate only under protocol |
| FORMAT_ERROR | yes | no automatic retry | missing | preserve artifact; investigator decision if needed |
| MALFORMED_ARTIFACT | yes | no | missing | preserve and repair infrastructure |
| MISSING | yes | no | missing | reconcile task/provenance |
| ORPHAN_RETRY | yes | no | missing | preserve and reconcile artifact lineage |
| CONFLICTING_ATTEMPTS | yes | no | missing | investigator review |

Only `RUNTIME_ERROR` receives the single identical retry already frozen in the
Judge V2 contract. There is no path to attempt 3.

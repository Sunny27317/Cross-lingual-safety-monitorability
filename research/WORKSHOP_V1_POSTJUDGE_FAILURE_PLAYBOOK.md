# Post-judge failure playbook

| Event | Do not do | Safe diagnostic | Resume/authorization | Preserve |
|---|---|---|---|---|
| process crash/reboot | restart with a fresh namespace | `--progress` / `--post-qc` | governed resume only | all immutable attempts |
| disk full | delete outputs | filesystem/directory checks | investigator review after repair | partial files and error logs |
| runtime error | retry for content reasons | technical state report | one frozen retry | original attempt |
| retry exhausted | attempt 3 | state-machine QC | new decision required | exhausted artifact |
| malformed output | edit JSON | schema QC | infrastructure repair | malformed artifact |
| duplicate | overwrite | duplicate-ID QC | investigator review | both artifacts |
| interrupted QC/seal | rerun destructively | rerun read-only QC | seal only after PASS | prior QC artifacts |
| human-file corruption | edit submitted file | packet/import QC | collect governed correction | original file/hash |
| analysis failure | overwrite results | wrapper diagnostics | rerun into new directory | failed run/provenance |

# Workshop-v1 Attempt-2 Unicode persistence failure

Attempt 2 persisted 30 complete generation records, then stopped while
processing task `generation-1a9600ac68c7ee0c204c800c3b0115b5d0724f10a63e9382f81fe56199a6e3fe`
(item `10-220`, Qwen, Urdu, Control, sample 0). The task's subprocess
returned to Python, but persistence failed while hashing `raw_runtime_output`.
No record was written for that task, and no partial JSON record exists.

The llama.cpp adapter captures subprocess bytes and decodes with
`errors="surrogateescape"`. A non-UTF-8 byte therefore became a reversible
transport surrogate (`U+DCDA`). `str.encode("utf-8")` in `content_hash` rejected
that value. The exception was a serialization boundary failure, after the
runtime call returned and before the scientific record was atomically written.
The raw output is not recoverable from the preserved files or the execution
manifest; it was held only in memory at the time of the crash. Its inference
completion status is consequently not inferable from durable evidence.

The engineering-only fix adds a reversible runtime-text byte encoder: transport
surrogates map to their original bytes, while any other lone surrogate uses
`surrogatepass`; valid Unicode remains ordinary UTF-8. JSON persistence uses
ASCII escapes, which round-trip surrogate values without lossy replacement.
No output is dropped, replaced, prompts/models/parameters/seeds/tasks change,
or scientific hash changes. Existing records remain untouched and immutable.

The task is recorded separately in
`experiments/_runs/workshop-v1-main-attempt-2/attempt_2_task_30_persistence_failure.json`.
The existing resume policy may rerun this same frozen task once persistence is
fixed; successful records are skipped and never overwritten. This metadata is
not a scientific result and is not counted as a successful task.

On resume, the original `execution_manifest.json` remains byte-for-byte
immutable. Its `created_utc` differs from a newly constructed runtime
manifest, but all non-dynamic identity fields match the frozen generation
configuration. Resume validates those identity fields and records the
engineering change separately in
`experiments/_runs/workshop-v1-main-attempt-2/attempt_2_resume_provenance.json`.

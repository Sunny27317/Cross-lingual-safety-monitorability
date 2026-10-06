# Workshop-v1 main-generation infrastructure failure

Date: 2026-10-02

The investigator authorization for generation configuration hash
`7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec` was
recorded and the bounded runner attempted exactly 3,312 authorized task IDs.
The run used the frozen 120-item manifest, both pinned models, both languages,
all three conditions, and three samples. No translation, judging, or human
annotation was attempted.

Every call failed before inference with llama.cpp's embedded server error:
`failed to get a free port`. Every record has an empty generated completion,
no visible trace, and no parsed final answer. The raw runtime output and stderr
are preserved in `experiments/_runs/workshop-v1-main/`; records are immutable.
The failure is infrastructure-only and matches the previously documented
restricted-sandbox TCP-bind limitation. No scientific output was produced.

The output directory must not be deleted, overwritten, or silently resumed.
Any future attempt requires an unrestricted environment and explicit governed
handling of these failed checkpoints; no automatic retry was performed here.

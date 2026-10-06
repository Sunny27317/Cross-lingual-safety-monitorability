# Workshop-v1 Attempt-2 retry preparation

Attempt 1 is classified `INFRASTRUCTURE_FAILURE_ZERO_INFERENCE`. All 3,312
records failed before model initialization/inference with llama.cpp's
`common_http_get_free_port()` returning no port. The restricted Codex sandbox
also fails a direct `127.0.0.1:0` bind with `EPERM`; this is the same failure
documented during D5. The normal macOS Terminal is expected to permit the bind.

The original investigator authorization remains scientifically valid because
zero inference occurred and no scientific state, prompt, model, manifest,
sampling, condition, seed, or task ID changed. A new authorization is required
for the retry namespace because the original authorization explicitly names the
Attempt-1 output directory. The exact proposed text is in
`engineering/ATTEMPT_2_AUTHORIZATION_TEMPLATE.txt`; it has not been recorded
as an active authorization.

Attempt 1 remains immutable at `experiments/_runs/workshop-v1-main/`, with its
attempt-level provenance record. Attempt 2 is prepared at
`experiments/_runs/workshop-v1-main-attempt-2/` and is empty. Its deterministic
plan is recorded in `engineering/workshop_v1_main_attempt_2_plan.json`, linked
to Attempt 1 and the unchanged generation configuration hash.

Use the repository's `main_retry --preflight` from an unrestricted normal
Terminal. It performs the socket, artifact, frozen-input, hash, count, and
empty-directory checks without model inference. Only after that preflight and
explicit Attempt-2 authorization may `main_generation --authorization ...`
be launched. Translation, judging, and annotation remain disabled.

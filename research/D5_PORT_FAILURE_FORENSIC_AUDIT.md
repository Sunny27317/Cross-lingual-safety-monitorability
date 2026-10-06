# D5 llama.cpp port failure forensic audit

This audit is non-generative. It preserves the original D5 failure record and made
zero model calls.

## EXPECTED

The pinned `llama-cli` build 10809 starts an embedded `llama-server` child for a
normal `-p` invocation. `cli-server.h` calls `common_http_get_free_port()`, which
creates an IPv4 TCP socket, binds to `INADDR_ANY` with port 0, reads the assigned
ephemeral port, closes that socket, and then starts the embedded server on the
selected port. The server is stopped and joined when the CLI exits. No fixed port,
PID file, or persistent server state is configured by the Workshop harness.

## ACTUAL

The preserved D5 record shows return code 1, no generated completion, and stderr:
`failed to get a free port`. The failure occurs during `Loading model...`, before
model inference, prompt processing, or output generation. The exact D5 scientific
argv and model/prompt configuration were recorded unchanged.

A direct non-generative Python socket test reproduced the environment condition:
binding either `0.0.0.0:0` or `127.0.0.1:0` raises `PermissionError(1,
'Operation not permitted')`. This is exactly the operation performed by the
pinned llama.cpp allocator.

Current `lsof` shows unrelated listening services and no visible llama process. The
environment denies `ps`, so process enumeration is permission-limited; no stale
llama PID, D5 PID/state file, or Workshop server state file exists in the D5 output
directory. The failure is therefore not attributable to a stale llama process,
TIME_WAIT collision, fixed-port collision, or a discovered race. No Workshop code
performs port discovery, retains a selected port, or launches concurrent servers.

## ROOT CAUSE

The execution environment sandbox forbids creating/binding TCP listening sockets.
llama.cpp reports this bind failure using the generic message `failed to get a free
port`. This is an infrastructure permission failure before model load/inference,
not a scientific configuration or prompt failure.

The allocator has a small theoretical TOCTOU window (close the port-0 probe, then
bind the chosen port), but there is no evidence that window was reached here: the
initial bind to port 0 is denied. No stale process or competing Workshop server was
found.

## FIX

No repository fix was applied. Retrying, selecting a fixed port, or changing the
llama.cpp binary would require changing the execution environment/runtime
authorization and could invalidate the pinned runtime identity. A future approved
run must use an environment that permits loopback/ephemeral TCP bind, then rerun the
unchanged frozen D5 harness. The D5 runner treats a recorded runtime failure as
terminal and refuses an automatic retry.

## WHY THE FIX IS SCIENTIFICALLY INERT

The required remediation is environmental socket permission/lifecycle availability.
It does not alter model weights, prompt bytes, chat template, decoding, seed, item,
condition, target letter, parser, compliance metric, or scientific output. No port
value is part of the scientific state; it only connects the CLI's internal client to
its temporary server.

## TESTS

- Preserved D5 stderr/argv inspection: PASS.
- Process/listener audit: no visible stale llama process; `ps` restricted; `lsof`
  showed only unrelated listeners.
- Direct socket lifecycle probe: expected bind denied with `EPERM`, reproducing the
  failure condition without a model.
- Existing full Workshop suite: 670 passed.
- Ruff, mypy, and `git diff --check`: PASS.

The original D5 failure artifact remains unchanged. No model, translation, main run,
judge, or human annotation was executed.

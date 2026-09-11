# Post-pilot handoff — English Track-A generator stage

**Status: the English pilot has NOT run.** This file is a placeholder handoff, written
before any scientific outcome exists, so the next steps are recorded once — not because
there is a result to hand off yet.

## What is true right now

- Every generator-stage prerequisite this agent can independently prepare and verify
  passes: real dataset content pin created and audited, model + runtime identity
  independently reverified on the target machine, scientific config hash recomputed
  and matched, workload confirmed at exactly 800, repository clean at a recorded commit.
  See `PRE_RUN_SNAPSHOT_2026-09-11.md` for the full record.
- The **only** remaining generator blocker is the human authorization token. No
  scientific inference has occurred. `experiments/_runs/` does not exist.
- One instrumentation limitation was found and documented pre-outcome (DECISION_LOG
  D-069): `stop_reason` will read `UNKNOWN` rather than `EOS` for ordinary successful
  generations with the current (unmodified) CLI invocation. This does not block the
  pilot and does not affect the primary behavioural estimands.

## What does NOT change for downstream (judge / human-reference / Urdu / translation / confirmatory) infrastructure

Nothing here authorizes, implies, or should prompt any change to judge validation,
human-reference/annotation infrastructure, Urdu experiment infrastructure, translation
infrastructure, or confirmatory-design tooling. Those remain separate, later-stage,
human-gated decisions regardless of what this English generator stage eventually
produces. In particular: **no future favourable or unfavourable English-pilot outcome
is a reason to alter any frozen downstream design** (judge selection, annotator
protocol, translator selection, N/SESOI). If and when the pilot does run, its report
will explicitly restate that it cannot establish the Monitor-Validity Gap,
cross-lingual degradation, Urdu monitor failure, translation recovery, or
frontier-model generalization — so no downstream stage should treat "the pilot ran" as
evidence for or against any of those questions.

## If/when a human provides authorization

1. Review `PRE_RUN_SNAPSHOT_2026-09-11.md` (or a later snapshot, if the reviewed commit
   has advanced) and `PRE_RUN_FINAL_CHECKLIST.md`.
2. Fill in the two human-only fields in the ready-to-authorize template (reviewer,
   reviewed_utc) — nothing else — and set `CLSM_TRACK_A_RUN_AUTHORIZED`.
3. Run the documented preflight, then (only if it reports ready) the documented
   execute command from `SCIENTIFIC_RUN_PLAN.md`.
4. After a complete run: run `clsm.track_a_analyze`, fill `PILOT_REPORT.md` from
   `PILOT_REPORT_TEMPLATE.md` using only observed values, and only then reassess
   whether instrumentation quality justifies proceeding toward the separately-gated
   downstream stages — that assessment belongs to a human, not to an automated
   continuation of this task.

**AUTHORIZED TO RUN: NO.**

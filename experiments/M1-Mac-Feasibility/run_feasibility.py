#!/usr/bin/env python3
"""Track-A feasibility-screen entrypoint.

STATUS: SCAFFOLD ONLY. Gate A (runtime build) and Gate B (model download) are complete
on both machines (`environment_checks/2026-09-08-m5-llamacpp-gate-a.txt`,
`environment_checks/2026-09-10-m5-gate-b-artifact-restoration.txt`), and a synthetic
infrastructure Gate-C smoke has PASSED on the M5
(`environment_checks/2026-09-10-m5-gate-c-synthetic-smoke.txt`, D-040) -- but that smoke
was run DIRECTLY via the pinned llama-cli, not through this runner, and THIS runner
still has no real GENERATION backend wired in. Running this script with no flags (or with
``--dry-run``) exercises the harness plumbing end-to-end using
``clsm.feasibility.MockFeasibilityBackend`` -- a deterministic, TEST-ONLY canned
responder -- against the synthetic fixture in
``experiments/M1-Mac-Feasibility/fixtures/smoke_questions.jsonl``. This proves the
control/treatment pipeline, prompt rendering, answer extraction, and JSONL output work,
WITHOUT running any real model.

Passing ``--real`` does NOT run a real model -- it exits immediately with an
explanation, because no real backend is implemented in this runner. No *scientific*
Track-A run is authorized (a frozen pilot pre-registration is required first --
`PILOT_PREREGISTRATION.md`).

NOTE (DECISION_LOG D-039): the generator is locked (Qwen/Qwen3-1.7B, D-034). This
screen NEVER chooses, rejects, or replaces a model based on a behavioural/scientific
outcome. Any hint-movement observation it records is a DIAGNOSTIC only; a zero hint
effect is a valid scientific null, not a model failure.

Output never lands in ``results/`` -- see ``clsm.feasibility.write_feasibility_records``.
This script never imports or calls ``clsm.metrics.compute_metrics``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from clsm.feasibility import (  # noqa: E402
    MockFeasibilityBackend,
    load_feasibility_items,
    run_feasibility_screen,
    write_feasibility_records,
)

_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "smoke_questions.jsonl"
_OUT_ROOT = Path(__file__).resolve().parent / "feasibility_runs"


def _mock_responder(prompt: str, seed: int) -> str:
    """Deterministic TEST-ONLY responder: 'reasons' briefly, then answers the
    hint_target when a hint is present in the prompt, else answers A (arbitrary,
    fixed) -- exists only to exercise the pipeline, not to model real behavior."""
    if "colleague suggested the answer is (" in prompt:
        letter = prompt.split("colleague suggested the answer is (")[1][0]
    else:
        letter = "A"
    return f"<think>Working through the options for seed {seed}.</think>\n\\boxed{{{letter}}}"


def dry_run() -> int:
    print("=" * 72)
    print("TRACK-A FEASIBILITY SCREEN -- DRY RUN (MockFeasibilityBackend, TEST-ONLY)")
    print("THIS IS NOT A SCIENTIFIC RESULT. No real model is downloaded or run.")
    print("=" * 72)

    items = load_feasibility_items(_FIXTURE_PATH)
    backend = MockFeasibilityBackend(_mock_responder, i_understand_this_is_test_only=True)

    records = run_feasibility_screen(
        items,
        backend,
        model_name="mock-feasibility-backend-v0",
        model_revision=None,
        runtime_name="mock",
        runtime_version=None,
        quantization=None,
        seeds=[0, 1],
    )

    out_dir = _OUT_ROOT / "dry-run"
    out_path = write_feasibility_records(records, out_dir)

    n_errors = sum(1 for r in records if r.error is not None)
    n_parsed = sum(1 for r in records if r.parsed_answer is not None)
    n_reasoning = sum(1 for r in records if r.has_reasoning_span)

    print(f"items: {len(items)}  generations: {len(records)}")
    print(f"parsed OK: {n_parsed}/{len(records)}  reasoning span present: {n_reasoning}/{len(records)}  errors: {n_errors}")
    print(f"wrote: {out_path}")
    print()
    print("This is a dry run of the harness plumbing only (MockFeasibilityBackend). No")
    print("real model was run through this runner; no scientific data was produced.")
    return 0


def real_run() -> int:
    print(
        "No real Track-A generation backend is implemented in THIS runner yet.\n"
        "Gate sequence (READINESS.md §0):\n"
        "  Gate A -- runtime install/build          [DONE -- Intel 2026-09-06; M5 arm64 rebuild 2026-09-08 (D-036)]\n"
        "  Gate B -- model-weight download          [DONE -- Intel 2026-09-06; M5 byte-verified 2026-09-10 (D-037)]\n"
        "  Gate C -- synthetic infrastructure smoke [PASS on the M5, 2026-09-10 (D-040) -- run directly via\n"
        "                                            the pinned llama-cli, NOT through this runner; this\n"
        "                                            runner still has no real generation backend]\n"
        "  Gate D -- NOT a model-selection exercise (D-039); the generator is locked (D-034)\n"
        "This runner's --real mode has no backend and no scientific run is authorized. Refusing to proceed.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--real",
        action="store_true",
        help="Attempt a real run (always refuses -- this runner has no backend; no scientific run authorized).",
    )
    args = parser.parse_args()
    if args.real:
        return real_run()
    return dry_run()


if __name__ == "__main__":
    raise SystemExit(main())

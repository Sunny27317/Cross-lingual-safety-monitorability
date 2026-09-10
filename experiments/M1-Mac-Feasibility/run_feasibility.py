#!/usr/bin/env python3
"""Track-A feasibility-screen entrypoint.

STATUS: SCAFFOLD ONLY. Gate A (runtime installation) and Gate B (model download) are
both complete -- llama.cpp is built and locally verified
(`experiments/M1-Mac-Feasibility/environment_checks/2026-09-06-llamacpp-gate-a.txt`),
and exactly one model (`Qwen/Qwen3-1.7B`, GGUF `Qwen3-1.7B-Q8_0.gguf`) has been
downloaded and verified
(`experiments/M1-Mac-Feasibility/environment_checks/2026-09-06-gate-b-model-download.txt`)
-- but there is still no real GENERATION backend wired in: Gate C (single-model smoke
run) and Gate D (multi-candidate feasibility screen) have not been authorized
(`experiments/M1-Mac-Feasibility/READINESS.md` §0). Running this script with no flags
(or with ``--dry-run``) exercises the harness plumbing end-to-end using
``clsm.feasibility.MockFeasibilityBackend`` -- a deterministic, TEST-ONLY canned
responder -- against the synthetic fixture in
``experiments/M1-Mac-Feasibility/fixtures/smoke_questions.jsonl``. This proves the
control/treatment pipeline, prompt rendering, answer extraction, and JSONL output work,
WITHOUT running any real model.

Passing ``--real`` does NOT run a real model either -- it exits immediately with an
explanation, because no real backend is implemented yet. This is a deliberate guard, not
an oversight: implementing the real backend is Gate C work, done only after explicit
authorization.

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
    print("This is a dry run of the harness plumbing only -- no candidate model from")
    print("MODEL_SCREEN.md has been downloaded, installed, or run.")
    return 0


def real_run() -> int:
    print(
        "No real Track-A generation backend is implemented yet.\n"
        "Gate sequence (READINESS.md §0):\n"
        "  Gate A -- runtime installation authorization      [DONE 2026-09-06 -- llama.cpp built + verified]\n"
        "  Gate B -- model-download authorization             [DONE 2026-09-06 -- Qwen3-1.7B Q8_0 downloaded + verified]\n"
        "  Gate C -- a single-model tiny smoke run             [NOT AUTHORIZED]\n"
        "  Gate D -- the multi-candidate feasibility screen (this script's real mode)  [NOT AUTHORIZED]\n"
        "Gates C-D have not been passed. Refusing to proceed.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--real",
        action="store_true",
        help="Attempt a real run (currently always refuses -- no backend implemented, no gate passed).",
    )
    args = parser.parse_args()
    if args.real:
        return real_run()
    return dry_run()


if __name__ == "__main__":
    raise SystemExit(main())

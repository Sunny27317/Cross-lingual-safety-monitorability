"""Tests for the Track-A (Mac-Feasibility) feasibility-screen scaffold.

Everything here is offline: MockFeasibilityBackend only, no real model, no download.
Also verifies the "feasibility-only" guards (Task 10): mode guard, results/ path guard,
and that FeasibilityRecord is structurally incompatible with clsm.metrics.compute_metrics.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from clsm.feasibility import (
    MODE,
    FeasibilityItem,
    FeasibilityRecord,
    MockFeasibilityBackend,
    assert_feasibility_mode,
    discover_llamacpp_binary,
    load_feasibility_items,
    render_control_prompt,
    render_treatment_prompt,
    run_feasibility_screen,
    write_feasibility_records,
)
from clsm.metrics import compute_metrics

_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = _ROOT / "experiments" / "M1-Mac-Feasibility" / "fixtures" / "smoke_questions.jsonl"


def _responder(prompt: str, seed: int) -> str:
    if "colleague suggested the answer is (" in prompt:
        letter = prompt.split("colleague suggested the answer is (")[1][0]
    else:
        letter = "A"
    return f"<think>reasoning seed={seed}</think>\n\\boxed{{{letter}}}"


def test_fixture_file_loads_and_has_expected_shape() -> None:
    items = load_feasibility_items(FIXTURE)
    assert len(items) == 5
    for item in items:
        assert item.hint_target != item.correct_answer
        assert set(item.choices) == {"A", "B", "C", "D"}
        assert "SYNTHETIC" in item.note.upper() or "INFRASTRUCTURE" in item.note.upper()


def test_prompt_rendering_control_is_prefix_of_treatment() -> None:
    item = FeasibilityItem(
        id="x1", question="Q?", choices={"A": "a", "B": "b", "C": "c", "D": "d"},
        correct_answer="A", hint_target="B", note="SYNTHETIC / INFRASTRUCTURE-ONLY",
    )
    control = render_control_prompt(item)
    treatment = render_treatment_prompt(item)
    hint_sentence = "colleague suggested the answer is (B)"
    assert treatment.startswith(control)
    assert treatment != control
    assert hint_sentence in treatment  # hint names the wrong option
    assert hint_sentence not in control  # hint is NOT in the control prompt


def test_mock_backend_requires_explicit_consent() -> None:
    with pytest.raises(RuntimeError):
        MockFeasibilityBackend(_responder)  # missing i_understand_this_is_test_only
    backend = MockFeasibilityBackend(_responder, i_understand_this_is_test_only=True)
    assert backend.generate_one("hello", seed=0)


def test_assert_feasibility_mode_rejects_anything_else() -> None:
    assert_feasibility_mode(MODE)  # no raise
    with pytest.raises(ValueError):
        assert_feasibility_mode("scientific")
    with pytest.raises(ValueError):
        assert_feasibility_mode("confirmatory")


def test_run_feasibility_screen_end_to_end_offline() -> None:
    items = load_feasibility_items(FIXTURE)
    backend = MockFeasibilityBackend(_responder, i_understand_this_is_test_only=True)
    records = run_feasibility_screen(
        items, backend,
        model_name="mock-v0", model_revision=None,
        runtime_name="mock", runtime_version=None, quantization=None,
        seeds=[0, 1],
    )
    # 5 items x 2 conditions x 2 seeds
    assert len(records) == 5 * 2 * 2
    assert all(r.error is None for r in records)
    assert all(r.parsed_answer is not None for r in records)
    assert all(r.has_reasoning_span for r in records)
    assert all(r.wall_clock_seconds >= 0 for r in records)
    # treatment records should parse to the item's hint_target (the mock always
    # follows the hint) -- proves the control/treatment pipeline actually differs
    by_item = {item.id: item for item in items}
    for r in records:
        if r.condition == "treatment":
            assert r.parsed_answer == by_item[r.item_id].hint_target


def test_feasibility_records_reasoning_span_status_and_marker_style() -> None:
    # SYNTHETIC responder: emits the pinned llama-cli PRESENTATION wrapper, not <think>.
    def bracket_responder(prompt: str, seed: int) -> str:
        letter = "A"
        if "colleague suggested the answer is (" in prompt:
            letter = prompt.split("colleague suggested the answer is (")[1][0]
        return f"[Start thinking]\nthinking about it (seed {seed})\n[End thinking]\n\\boxed{{{letter}}}"

    items = load_feasibility_items(FIXTURE)
    backend = MockFeasibilityBackend(bracket_responder, i_understand_this_is_test_only=True)
    records = run_feasibility_screen(
        items, backend,
        model_name="mock-v0", model_revision=None,
        runtime_name="mock", runtime_version=None, quantization=None,
        seeds=[0],
    )
    assert all(r.reasoning_span_status == "PRESENT" for r in records)
    assert all(r.reasoning_marker_style == "bracket_thinking" for r in records)
    assert all(r.has_reasoning_span for r in records)


def test_feasibility_malformed_span_is_flagged_not_silently_dropped() -> None:
    def truncated_responder(prompt: str, seed: int) -> str:
        return "<think>reasoning cut off mid-sentence"

    items = load_feasibility_items(FIXTURE)
    backend = MockFeasibilityBackend(truncated_responder, i_understand_this_is_test_only=True)
    records = run_feasibility_screen(
        items, backend,
        model_name="mock-v0", model_revision=None,
        runtime_name="mock", runtime_version=None, quantization=None,
        seeds=[0],
    )
    # the format problem is recorded explicitly; it is NOT reported as "no reasoning"
    assert all(r.reasoning_span_status == "MALFORMED" for r in records)
    assert all(not r.has_reasoning_span for r in records)
    assert all(r.parse_status == "NO_ANSWER" for r in records)
    assert all(r.error is None for r in records)  # a format issue is not a backend crash


def test_zero_hint_effect_does_not_flag_or_reject_the_model() -> None:
    # SYNTHETIC responder that IGNORES the hint entirely (always answers "A").
    # A null hint effect is a valid scientific outcome (D-039) -- the screen must just
    # record it, never mark the model as failed / to-be-replaced.
    def hint_insensitive_responder(prompt: str, seed: int) -> str:
        return "<think>I will answer A regardless of any suggestion.</think>\n\\boxed{A}"

    items = load_feasibility_items(FIXTURE)
    backend = MockFeasibilityBackend(hint_insensitive_responder, i_understand_this_is_test_only=True)
    records = run_feasibility_screen(
        items, backend,
        model_name="mock-v0", model_revision=None,
        runtime_name="mock", runtime_version=None, quantization=None,
        seeds=[0, 1],
    )
    # control and treatment answers are identical for every item -> zero hint movement
    assert {r.parsed_answer for r in records} == {"A"}
    # ... and nothing in the record schema encodes a selection/rejection verdict
    forbidden = {"selected", "rejected", "eliminated", "passed", "failed",
                 "switch_rate", "adoption_increase", "hint_effect", "verdict"}
    assert forbidden.isdisjoint(FeasibilityRecord.model_fields)
    # records are complete and clean; a null effect is not an error
    assert all(r.error is None for r in records)
    assert all(r.parse_status == "VALID" for r in records)


def test_feasibility_module_does_not_import_metrics() -> None:
    import ast

    import clsm.feasibility as feas_mod

    tree = ast.parse(Path(feas_mod.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any(m == "clsm.metrics" or m.startswith("clsm.metrics.") for m in imported)


def test_run_feasibility_screen_records_backend_errors_without_crashing() -> None:
    def flaky_responder(prompt: str, seed: int) -> str:
        raise RuntimeError("simulated backend failure")

    items = load_feasibility_items(FIXTURE)
    backend = MockFeasibilityBackend(flaky_responder, i_understand_this_is_test_only=True)
    records = run_feasibility_screen(
        items, backend,
        model_name="mock-v0", model_revision=None,
        runtime_name="mock", runtime_version=None, quantization=None,
        seeds=[0],
    )
    assert len(records) == 5 * 2 * 1
    assert all(r.error is not None for r in records)
    assert all(r.parsed_answer is None for r in records)


def test_write_feasibility_records_refuses_results_path(tmp_path: Path) -> None:
    rec = FeasibilityRecord(
        model_name="m", model_revision=None, model_checksum=None,
        runtime_name="mock", runtime_version=None, quantization=None,
        prompt_template_version="v0", item_id="x", condition="control",
        sample_idx=0, seed=0, wall_clock_seconds=0.0, peak_rss_bytes=None,
        raw_output="", parsed_answer=None, parse_status="NO_ANSWER",
        has_reasoning_span=False, error=None, timestamp_utc="2026-09-06T00:00:00+00:00",
    )
    with pytest.raises(ValueError, match="results"):
        write_feasibility_records([rec], tmp_path / "results" / "whatever")

    out_dir = tmp_path / "experiments" / "M1-Mac-Feasibility" / "feasibility_runs" / "run1"
    out_path = write_feasibility_records([rec], out_dir)
    assert out_path.exists()
    assert out_path.parent == out_dir


# --------------------------------------------------------------------------------------
# discover_llamacpp_binary (Gate-A runtime-discovery guard) -- never loads a model.
# Uses a temp fake executable, NEVER the user's real ~/tools/llama.cpp path.
# --------------------------------------------------------------------------------------


def test_discover_llamacpp_binary_missing_path(tmp_path: Path) -> None:
    result = discover_llamacpp_binary(tmp_path / "does-not-exist")
    assert not result.exists
    assert not result.executable
    assert result.version_output is None
    assert result.error is not None


def test_discover_llamacpp_binary_not_executable(tmp_path: Path) -> None:
    f = tmp_path / "not-executable"
    f.write_text("not a real binary")
    f.chmod(0o644)  # explicitly non-executable
    result = discover_llamacpp_binary(f)
    assert result.exists
    assert not result.executable
    assert result.error is not None


def test_discover_llamacpp_binary_fake_executable_reports_version(tmp_path: Path) -> None:
    # A tiny fake "llama-cli"-shaped script -- proves the discovery guard only ever
    # calls `--version`, never a model path, and works against ANY executable, not
    # a real llama.cpp build.
    fake = tmp_path / "fake-llama-cli"
    fake.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "--version" ]; then\n'
        '  echo "version: 0.0.0-fake (build 1, commit deadbeef)"\n'
        "  exit 0\n"
        "fi\n"
        'echo "unexpected args: $@" >&2\n'
        "exit 2\n"
    )
    fake.chmod(0o755)
    result = discover_llamacpp_binary(fake)
    assert result.exists
    assert result.executable
    assert result.error is None
    assert result.returncode == 0
    assert result.version_output is not None
    assert "0.0.0-fake" in result.version_output


def test_discover_llamacpp_binary_never_passes_a_model_argument(tmp_path: Path) -> None:
    # A fake binary that FAILS if invoked with anything other than exactly ["--version"]
    # -- proves the guard cannot accidentally pass a model path or trigger inference.
    fake = tmp_path / "strict-fake-llama-cli"
    fake.write_text(
        "#!/bin/sh\n"
        'if [ "$#" -eq 1 ] && [ "$1" = "--version" ]; then\n'
        '  echo "ok"\n'
        "  exit 0\n"
        "fi\n"
        'echo "FAIL: unexpected invocation: $@" >&2\n'
        "exit 1\n"
    )
    fake.chmod(0o755)
    result = discover_llamacpp_binary(fake)
    assert result.error is None
    assert result.returncode == 0
    assert result.version_output == "ok"


def test_feasibility_record_is_structurally_incompatible_with_compute_metrics() -> None:
    # A FeasibilityRecord must never be usable where a GenerationRecord is expected --
    # compute_metrics must reject it outright rather than silently "working."
    rec = FeasibilityRecord(
        model_name="m", model_revision=None, model_checksum=None,
        runtime_name="mock", runtime_version=None, quantization=None,
        prompt_template_version="v0", item_id="x", condition="control",
        sample_idx=0, seed=0, wall_clock_seconds=0.0, peak_rss_bytes=None,
        raw_output="", parsed_answer=None, parse_status="NO_ANSWER",
        has_reasoning_span=False, error=None, timestamp_utc="2026-09-06T00:00:00+00:00",
    )
    with pytest.raises(AttributeError):
        compute_metrics([rec], [], experiment_id="e", role="pilot", bootstrap_seed=1)  # type: ignore[list-item]

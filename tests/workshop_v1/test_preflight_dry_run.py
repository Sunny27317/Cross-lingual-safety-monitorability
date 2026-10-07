from __future__ import annotations

import json
import socket
import subprocess
from pathlib import Path

import pytest

from clsm.downstream.contracts import canonical, content_hash
from clsm.workshop_v1.config import load_study
from clsm.workshop_v1.dry_run import run, synthetic_records
from clsm.workshop_v1.population import select_population
from clsm.workshop_v1.preflight import (
    REQUIRED_GATES,
    Evidence,
    ReviewBundle,
    Stage,
    check_review,
    preflight,
    safe_unused_output,
)
from clsm.workshop_v1.records import SYNTHETIC_LABEL
from clsm.workshop_v1_preflight import main

from .conftest import changed

ROOT = Path(__file__).resolve().parents[2]


def test_default_preflight_is_read_only_and_fails_closed(tmp_path: Path, capsys) -> None:
    out = tmp_path / "unused"
    assert main(["--root", str(ROOT), "--output", str(out)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["execution_ready"] is False
    assert payload["structural_checks_passed"] is False
    assert any("unresolved designation" in b or "unresolved model" in b for b in payload["blockers"])
    assert any("authorization" in b for b in payload["blockers"])
    assert not out.exists()


def test_invalid_config_reports_refusal_without_traceback(tmp_path: Path, capsys) -> None:
    path = tmp_path / "malformed.yaml"
    path.write_text("[invalid\n")
    assert main(["--config", str(path)]) == 1
    assert json.loads(capsys.readouterr().out)["execution_ready"] is False


@pytest.mark.parametrize("stage", list(Stage))
def test_synthetic_fixture_cannot_pass_scientific_stage(design, tmp_path: Path, stage) -> None:
    study, snapshot = design
    population = select_population(study, snapshot)
    report = preflight(
        study,
        root=ROOT,
        output=tmp_path / "unused",
        stage=stage,
        expected_study_hash=study.artifact_hash,
        snapshot=snapshot,
        population=population,
    )
    assert not report.execution_ready
    assert "synthetic fixtures cannot pass scientific preflight" in report.blockers
    if stage is not Stage.GENERATION:
        assert any("source-generation manifest" in b for b in report.blockers)


def test_stage_specific_monitor_human_translator_blockers(tmp_path: Path) -> None:
    study = load_study(ROOT / "configs/workshop_v1/study.yaml")
    for stage, message in (
        (Stage.DIRECT_MONITOR, "automated monitor unresolved"),
        (Stage.HUMAN_REFERENCE, "native human-reference protocol unresolved"),
        (Stage.TRANSLATED_MONITOR, "translator unresolved"),
    ):
        report = preflight(study, root=ROOT, output=tmp_path / "unused", stage=stage)
        assert message in report.blockers


def review_fixture(study, population, root: Path, output: Path, stage=Stage.GENERATION):
    artifact = root / "synthetic-review.txt"
    artifact.write_text("SYNTHETIC TEST EVIDENCE; NOT REAL AUTHORIZATION")
    return ReviewBundle(
        data_kind="scientific",
        stage=stage,
        study_hash=study.artifact_hash,
        population_hash=population.artifact_hash,
        source_manifest_hash=None,
        reviewed_commit="a" * 40,
        output_directory=str(output),
        evidence=tuple(
            Evidence(
                gate=gate,
                relative_path=artifact.name,
                sha256=content_hash(artifact.read_text()),
                approver="synthetic-reviewer",
                attestation="synthetic-only; NOT AUTHORIZATION",
                approved_utc="2000-01-01T00:00:00+00:00",
            )
            for gate in sorted(REQUIRED_GATES[stage])
        ),
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("stage", "translated_monitor"),
        ("study_hash", "b" * 64),
        ("population_hash", "b" * 64),
        ("reviewed_commit", "b" * 40),
        ("output_directory", "/synthetic-wrong-output"),
        ("source_manifest_hash", "b" * 64),
    ],
)
def test_review_cannot_be_replayed_across_bindings(design, tmp_path: Path, field, value) -> None:
    study, snapshot = design
    pop = select_population(study, snapshot)
    output = tmp_path / "unused"
    review = review_fixture(study, pop, tmp_path, output)
    with pytest.raises(ValueError, match="stale"):
        check_review(
            changed(review, **{field: value}),
            study=study,
            population=pop,
            stage=Stage.GENERATION,
            output=output,
            root=tmp_path,
            commit="a" * 40,
            source_manifest_hash=None,
        )


def test_missing_duplicate_and_drifted_gate_evidence(design, tmp_path: Path) -> None:
    study, snapshot = design
    pop = select_population(study, snapshot)
    output = tmp_path / "unused"
    review = review_fixture(study, pop, tmp_path, output)
    kwargs = dict(
        study=study,
        population=pop,
        stage=Stage.GENERATION,
        output=output,
        root=tmp_path,
        commit="a" * 40,
        source_manifest_hash=None,
    )
    check_review(review, **kwargs)
    with pytest.raises(ValueError, match="missing review gates"):
        check_review(changed(review, evidence=[]), **kwargs)
    with pytest.raises(ValueError, match="duplicate"):
        changed(review, evidence=[review.evidence[0].model_dump(mode="json")] * 2)
    (tmp_path / "synthetic-review.txt").write_text("changed")
    with pytest.raises(ValueError, match="drift"):
        check_review(review, **kwargs)


def test_git_guard_uses_real_cleanliness_and_reviewed_commit(tmp_path: Path) -> None:
    from clsm.track_a_preflight import git_integrity

    # Temporary empty git repository, no commits or user identity needed.
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    with pytest.raises(subprocess.CalledProcessError):
        git_integrity(tmp_path, None)
    # Current topic worktree has uncommitted scaffold changes, so it cannot pass.
    with pytest.raises(ValueError, match=r"dirty|missing reviewed"):
        git_integrity(ROOT, None)


@pytest.mark.parametrize("suffix", ["results/synthetic-workshop-v1-x", "ReSuLtS/synthetic-workshop-v1-x"])
def test_results_paths_forbidden(tmp_path: Path, suffix) -> None:
    with pytest.raises(ValueError, match="results"):
        safe_unused_output(tmp_path / suffix, synthetic=True)
    assert not (tmp_path / "results").exists()


def test_results_symlink_alias_and_existing_outputs_forbidden(tmp_path: Path) -> None:
    results = tmp_path / "results"
    results.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(results, target_is_directory=True)
    with pytest.raises(ValueError, match="results"):
        safe_unused_output(alias / "synthetic-workshop-v1-x", synthetic=True)
    existing = tmp_path / "synthetic-workshop-v1-existing"
    existing.mkdir()
    with pytest.raises(ValueError, match="collision"):
        run(existing)
    with pytest.raises(ValueError, match="must start"):
        run(tmp_path / "looks-like-real-run")
    dangling = tmp_path / "synthetic-workshop-v1-dangling"
    dangling.symlink_to(tmp_path / "missing")
    with pytest.raises(ValueError, match="collision"):
        safe_unused_output(dangling, synthetic=True)


def test_synthetic_run_offline_labels_hashes_no_answers_no_annotations(tmp_path: Path, monkeypatch) -> None:
    def no_network(*args, **kwargs):
        raise AssertionError("network forbidden")

    monkeypatch.setattr(socket, "socket", no_network)
    out = tmp_path / "synthetic-workshop-v1-test"
    manifest = run(out)
    assert manifest["label"] == SYNTHETIC_LABEL
    assert manifest["fixture_generation_count"] == 24
    assert manifest["scientific_outcomes"] == "NOT RUN"
    for file, sha in manifest["artifact_hashes"].items():
        assert content_hash((out / file).read_text()) == sha
    generations = [json.loads(line) for line in (out / "generations.jsonl").read_text().splitlines()]
    assert all(r["label"] == SYNTHETIC_LABEL for r in generations)
    assert all("NO ANSWER OR COT" in r["output_text"] for r in generations)
    assert all(r["confounds"]["base_task_correctness"] is None for r in generations)
    routing = json.loads((out / "routing.json").read_text())
    assert len(routing["bindings"]) == 48
    assert all("label" not in b for b in routing["bindings"])
    assert not list(tmp_path.rglob("results"))
    with pytest.raises(ValueError, match="collision"):
        run(out)


def test_fixed_synthetic_inputs_reproduce_exact_records() -> None:
    kwargs = dict(
        code_commit="0" * 40,
        working_tree_hash="1" * 64,
        environment_hash="2" * 64,
        created_utc="2000-01-01T00:00:00+00:00",
    )
    first_pop, first_records = synthetic_records(**kwargs)
    second_pop, second_records = synthetic_records(**kwargs)
    assert first_pop == second_pop
    assert canonical([r.model_dump(mode="json") for r in first_records]) == canonical(
        [r.model_dump(mode="json") for r in second_records]
    )


def test_partial_schedule_remains_a_preflight_blocker(design, tmp_path: Path) -> None:
    study, _ = design
    study = changed(study, sampling={**study.sampling.model_dump(mode="json"), "pairing": "partial"})
    report = preflight(study, root=ROOT, output=tmp_path / "unused")
    assert any("partial scheduling" in b for b in report.blockers)
    assert not report.execution_ready


def test_review_hashing_detects_newline_bytes_and_blocks_path_escape(design, tmp_path: Path) -> None:
    study, snapshot = design
    pop = select_population(study, snapshot)
    output = tmp_path / "unused"
    review = review_fixture(study, pop, tmp_path, output)
    kwargs = dict(
        study=study,
        population=pop,
        stage=Stage.GENERATION,
        output=output,
        root=tmp_path,
        commit="a" * 40,
        source_manifest_hash=None,
    )
    evidence = tmp_path / "synthetic-review.txt"
    evidence.write_bytes(b"SYNTHETIC TEST EVIDENCE; NOT REAL AUTHORIZATION\r\n")
    with pytest.raises(ValueError, match="content drift"):
        check_review(review, **kwargs)
    changed_evidence = review.model_dump(mode="json")["evidence"]
    changed_evidence[0]["relative_path"] = "../outside.txt"
    with pytest.raises(ValueError, match="repository-relative"):
        check_review(changed(review, evidence=changed_evidence), **kwargs)


def test_approvals_require_utc_and_cannot_be_future_dated() -> None:
    fields = dict(
        gate="design_review",
        relative_path="synthetic.txt",
        sha256="a" * 64,
        approver="synthetic-reviewer",
        attestation="synthetic-only",
    )
    with pytest.raises(ValueError, match="UTC"):
        Evidence(**fields, approved_utc="2000-01-01T00:00:00")
    with pytest.raises(ValueError, match="future-dated"):
        Evidence(**fields, approved_utc="2999-01-01T00:00:00+00:00")


def test_synthetic_cli_does_not_accept_scientific_inputs(tmp_path: Path, capsys) -> None:
    from clsm.workshop_v1.dry_run import main as dry_main

    out = tmp_path / "synthetic-workshop-v1-cli"
    with pytest.raises(SystemExit) as exc:
        dry_main(["--output", str(out), "--config", "configs/workshop_v1/study.yaml"])
    assert exc.value.code == 2
    assert not out.exists()
    assert dry_main(["--output", str(out)]) == 0
    assert json.loads(capsys.readouterr().out)["label"] == SYNTHETIC_LABEL
    assert dry_main(["--output", str(out)]) == 1
    assert "error" in json.loads(capsys.readouterr().out)

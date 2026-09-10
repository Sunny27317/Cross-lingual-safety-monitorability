"""PRE-OUTCOME safeguards. Synthetic records/temp files only; no execution entrypoint calls."""

from __future__ import annotations

import dataclasses
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from clsm.config import load_experiment_config
from clsm.schemas import Condition, ParseStatus, StopReason
from clsm.track_a_analyze import describe_records
from clsm.track_a_artifacts import completion_from_records, validate_records, write_new
from clsm.track_a_backend import RawInvocation, artifact_stem, backend_config_hash, record_from_invocation
from clsm.track_a_dataset_pin import (
    DatasetContentPin,
    canonical_json,
    create_real_pin,
    digest,
    fixture_pin,
    load_pin,
    write_pin,
)
from clsm.track_a_dataset_pin import (
    main as pin_main,
)
from clsm.track_a_manifest import BlockKind, Field_, RunStage, Status, build_pilot_manifest
from clsm.track_a_plan import build_plan, validate_pilot_workload
from clsm.track_a_preflight import check_output_directory, git_integrity, preflight
from clsm.track_a_run import _AUTH_ASSERTION, ENV_AUTH, _check_human_authorization, scientific_config_hash

CFG = Path("configs/track_a_pilot/pilot.yaml")
RT = Path("configs/track_a_pilot/runtime_llamacpp.yaml")


@pytest.fixture
def cfg():
    return load_experiment_config(CFG)


@pytest.fixture
def pin(cfg):
    return fixture_pin(cfg.dataset)


def test_fixture_full_pipeline_offline(pin, cfg, monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("network must not be imported")

    monkeypatch.setattr("clsm.track_a_dataset_pin.importlib.import_module", forbidden)
    assert pin_main(["fixture-check"]) == 0
    path = tmp_path / "fixture.json"
    write_pin(pin, path)
    assert load_pin(path, cfg.dataset).content_sha256 == pin.content_sha256
    with pytest.raises(ValueError, match="fixture pin"):
        load_pin(path, cfg.dataset, require_real=True)
    with pytest.raises(FileExistsError):
        write_pin(pin, path)
    with pytest.raises(ValueError, match=r"opt|allow"):
        create_real_pin(cfg.dataset, allow_dataset_download=False)


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": "bad"},
        {"resolved_revision": "f" * 40},
        {"content_sha256": "0" * 64},
        {"number_of_items": 49},
        {"schema_verified": False},
        {"choice_order_verified": False},
        {"label_mapping_verified": False},
        {"extra": "unrecognized"},
        {"source_files_sha256": {}},
    ],
)
def test_pin_rejects_malformed_metadata(pin, change):
    with pytest.raises(ValueError):
        DatasetContentPin.model_validate({**pin.model_dump(), **change})


@pytest.mark.parametrize(
    "field,value",
    [
        ("choices", ["A", "B", "C"]),
        ("choices", ["", "B", "C", "D"]),
        ("answer_idx", 4),
        ("answer_idx", True),
        ("subject", "wrong"),
        ("question", ""),
        ("question", "ALTERED"),
    ],
)
def test_pin_rejects_bad_content(pin, field, value):
    payload = pin.model_dump()
    payload["selected_items"][0][field] = value
    with pytest.raises(ValueError):
        DatasetContentPin.model_validate(payload)


def test_duplicate_ids_rejected(pin):
    payload = pin.model_dump()
    payload["selected_items"][1] = payload["selected_items"][0]
    with pytest.raises(ValueError, match="duplicate"):
        DatasetContentPin.model_validate(payload)


def test_pin_choice_order_and_answer_are_hashed(pin):
    for field, value in [
        ("choices", list(reversed(pin.selected_items[0].choices))),
        ("answer_idx", (pin.selected_items[0].answer_idx + 1) % 4),
    ]:
        payload = pin.model_dump()
        payload["selected_items"][0][field] = value
        with pytest.raises(ValueError, match="content hash"):
            DatasetContentPin.model_validate(payload)


def test_pin_metadata_is_bound_into_content_hash(pin):
    """D-067 (hotfix take-over): the content SHA binds identifying dataset metadata
    (library version, resolved revision, exact IDs, ...), not only item content. The
    pin file is git-ignored, so a metadata-only swap must not keep the same hash."""
    # datasets_library_version alone must move the hash (would otherwise be unbound).
    from clsm.track_a_dataset_pin import content_digest

    kw = dict(
        dataset_repo=pin.dataset_repo, dataset_config=pin.dataset_config,
        dataset_split=pin.dataset_split, requested_revision=pin.requested_revision,
        resolved_revision=pin.resolved_revision, selection_rule=pin.selection_rule,
        subjects=pin.subjects, items_per_subject=pin.items_per_subject,
        number_of_items=pin.number_of_items, exact_item_ids=pin.exact_item_ids,
        selected_items=pin.selected_items,
    )
    base = content_digest(datasets_library_version=pin.datasets_library_version, **kw)
    assert base == pin.content_sha256
    assert content_digest(datasets_library_version="datasets==9.9.9", **kw) != base
    assert content_digest(**{**kw, "exact_item_ids": pin.exact_item_ids[::-1]},
                          datasets_library_version=pin.datasets_library_version) != base


def test_pin_selection_deterministic(cfg, pin):
    again = fixture_pin(cfg.dataset)
    assert again.content_sha256 == pin.content_sha256
    assert again.exact_item_ids == pin.exact_item_ids
    with pytest.raises(ValueError, match="config mismatch"):
        pin.validate_config(cfg.dataset.model_copy(update={"split": "validation"}))


@pytest.mark.parametrize(
    "stage, required, absent",
    [
        (RunStage.GENERATOR, {"dataset_content_pin"}, {"disclosure_judge", "ethics_determination"}),
        (RunStage.JUDGE, {"disclosure_judge", "human_disclosure_audit", "ethics_determination"}, set()),
        (RunStage.HUMAN_VALIDATION, {"human_disclosure_audit", "ethics_determination"}, {"disclosure_judge"}),
        (RunStage.URDU, {"translation_protocol", "native_urdu_validation"}, set()),
        (RunStage.CONFIRMATORY, {"confirmatory_sample_size", "translation_protocol"}, set()),
    ],
)
def test_stage_requirements(stage, required, absent):
    unresolved = set(build_pilot_manifest().stage_unresolved(stage))
    assert required <= unresolved and not absent & unresolved


@pytest.mark.parametrize("field", ["generator_model", "seed_schedule", "hint_wording", "parser_version"])
def test_methodology_cannot_be_disabled_with_flags(field):
    m = build_pilot_manifest()
    m = m.model_copy(
        update={field: Field_(status=Status.BLOCKED, block_kind=BlockKind.NONE, blocking_for_run=False)}
    )
    assert field in m.stage_unresolved(RunStage.GENERATOR)


def test_frozen_workload_and_hint_identity(cfg, pin):
    specs = build_plan(cfg, pin, cfg.experiment_name)
    validate_pilot_workload(specs)
    assert len(specs) == 800 and len({artifact_stem(s) for s in specs}) == 800
    assert [dataclasses.asdict(s) for s in specs] == [
        dataclasses.asdict(s) for s in build_plan(cfg, pin, cfg.experiment_name)
    ]
    with pytest.raises(ValueError, match="experiment_id"):
        build_plan(cfg, pin, cfg.experiment_name + "-date")
    with pytest.raises(ValueError, match="800"):
        validate_pilot_workload(specs[:-1])


def test_scientific_hash_covers_experiment_id(cfg):
    runtime = yaml.safe_load(RT.read_text())
    assert scientific_config_hash(cfg, runtime) != scientific_config_hash(
        cfg.model_copy(update={"experiment_name": "changed"}), runtime
    )


def test_backend_binding_covers_decoding_and_paths(cfg, tmp_path):
    from clsm.track_a_backend import LlamaCppRuntime

    runtime = LlamaCppRuntime("fake", "fake.gguf", "f" * 40)
    before = backend_config_hash(cfg.model, cfg.decoding, runtime)
    assert (
        backend_config_hash(cfg.model, cfg.decoding, dataclasses.replace(runtime, timeout_seconds=1))
        != before
    )
    assert (
        backend_config_hash(cfg.model, cfg.decoding, dataclasses.replace(runtime, model_path="other"))
        != before
    )


def auth_payload():
    return {
        "scientific_hash": "a" * 64,
        "reviewer": "fixture reviewer",
        "reviewed_utc": "2026-01-01T00:00:00+00:00",
        "assertion": _AUTH_ASSERTION,
        "stage": "generator",
        "git_commit": "b" * 40,
        "dataset_content_hash": "c" * 64,
        "output_dir": "/fixture-output",
        "experiment_id": "fixture",
    }


@pytest.mark.parametrize("bad", [None, "true", "false", "1", "{}", '"authorized"', "[]"])
def test_authorization_rejected(bad, monkeypatch):
    monkeypatch.delenv(ENV_AUTH, raising=False)
    if bad is not None:
        monkeypatch.setenv(ENV_AUTH, bad)
    assert not _check_human_authorization("a" * 64)[0]


@pytest.mark.parametrize(
    "field", ["scientific_hash", "stage", "git_commit", "dataset_content_hash", "output_dir", "experiment_id"]
)
def test_stale_authorization_binding(field, monkeypatch):
    payload = auth_payload()
    bindings = {
        k: payload[k] for k in ("stage", "git_commit", "dataset_content_hash", "output_dir", "experiment_id")
    }
    payload[field] = "stale"
    monkeypatch.setenv(ENV_AUTH, json.dumps(payload))
    assert not _check_human_authorization("a" * 64, bindings=bindings)[0]


@pytest.mark.parametrize(
    "field,value",
    [("reviewer", ""), ("assertion", True), ("reviewed_utc", "not-a-date"), ("scientific_hash", 1)],
)
def test_malformed_auth_fields_fail_closed(field, value, monkeypatch):
    payload = auth_payload()
    payload[field] = value
    monkeypatch.setenv(ENV_AUTH, json.dumps(payload))
    assert not _check_human_authorization("a" * 64)[0]


def test_git_integrity_clean_dirty_wrong_hash(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "--allow-empty",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    sha = subprocess.check_output(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True).strip()
    assert git_integrity(tmp_path, sha) == (sha, False)
    with pytest.raises(ValueError, match="commit mismatch"):
        git_integrity(tmp_path, "0" * 40)
    (tmp_path / "dirty").write_text("synthetic")
    with pytest.raises(ValueError, match="dirty"):
        git_integrity(tmp_path, sha)


def test_preflight_is_fail_closed_without_inputs(tmp_path, monkeypatch):
    monkeypatch.delenv(ENV_AUTH, raising=False)
    monkeypatch.delenv("CLSM_LLAMA_CLI", raising=False)
    monkeypatch.delenv("CLSM_QWEN_GGUF", raising=False)
    report = preflight(pin_path=tmp_path / "missing", output_dir=tmp_path / "output")
    assert not report.ready
    text = " ".join(report.blockers)
    assert all(word in text for word in ["repository", "hash", "pin", "authorization", "runtime"])
    assert not (tmp_path / "output").exists()


def test_output_reservation_and_collision(tmp_path):
    out = tmp_path / "run"
    check_output_directory(out)
    out.mkdir()
    with pytest.raises(ValueError, match="collision"):
        check_output_directory(out)
    target = out / "fixture.txt"
    write_new(target, "synthetic")
    with pytest.raises(FileExistsError):
        write_new(target, "changed")
    assert target.read_text() == "synthetic" and not list(out.glob(".pending-*"))


def small_plan(cfg, pin):
    specs = build_plan(cfg, pin, cfg.experiment_name)[:16]
    records = []
    for s in specs:
        answer = s.correct_letter if s.condition is Condition.CONTROL else s.hint_target_letter
        raw = RawInvocation(
            [], 0, f"<think>SYNTHETIC</think>\\boxed{{{answer}}}", "eval time = 1 ms / 10 runs", 0.01, False
        )
        rec = record_from_invocation(s, raw, cfg.model, cfg.decoding)
        rec.is_mock = True
        records.append(rec)
    return specs, records


def test_descriptive_existing_metrics_and_missingness(cfg, pin):
    specs, records = small_plan(cfg, pin)
    cfg = cfg.model_copy(update={"bootstrap_n": 10})
    report = describe_records(cfg, specs, records)
    assert report["present_records"] == 16 and report["missing_records"] == 0
    assert report["behavioural_metrics"]["unhinted_accuracy"]["est"] == 1.0
    assert report["behavioural_metrics"]["answer_switch_rate"]["est"] == 1.0
    assert report["confirmatory"] is False
    incomplete = describe_records(cfg, specs, records[:-1])
    assert incomplete["missing_records"] == 1 and incomplete["behavioural_metrics"] is None
    with pytest.raises(ValueError, match="duplicate"):
        validate_records(specs, records + records[:1])


@pytest.mark.parametrize(
    "raw,reason,status",
    [
        (RawInvocation([], -1, "", "", 1, True), StopReason.TIMEOUT, ParseStatus.PARSE_ERROR),
        (RawInvocation([], 2, "", "", 1, False), StopReason.NONZERO_EXIT, ParseStatus.PARSE_ERROR),
        (RawInvocation([], 0, "<think>broken", "", 1, False), StopReason.UNKNOWN, ParseStatus.NO_ANSWER),
        (
            RawInvocation([], 0, "\\boxed{A}", "eval time = 1 ms / 16384 runs", 1, False),
            StopReason.LENGTH,
            ParseStatus.VALID,
        ),
    ],
)
def test_failure_diagnostics(cfg, pin, raw, reason, status):
    specs, _ = small_plan(cfg, pin)
    rec = record_from_invocation(specs[0], raw, cfg.model, cfg.decoding)
    assert rec.stop_reason is reason and rec.parse_status is status
    report = describe_records(cfg, specs, [rec])
    assert report["stop_reason_counts"][reason.value] == 1
    assert report["missing_records"] == 15


def test_completion_schema_requires_complete_evidence(cfg, pin):
    specs, records = small_plan(cfg, pin)
    hashes = {
        f"{artifact_stem(s)}.{suffix}": digest("fixture")
        for s in specs
        for suffix in ("stdout.txt", "stderr.txt", "cleaned.txt", "meta.json")
    }
    kwargs = dict(
        scientific_hash="a" * 64,
        git_commit="b" * 40,
        dataset_content_hash=pin.content_sha256,
        raw_hashes=hashes,
        started_utc="2026-01-01T00:00:00+00:00",
        finished_utc="2026-01-01T00:01:00+00:00",
    )
    completion = completion_from_records(specs, records, **kwargs)
    assert completion.completed_generations == 16 and completion.raw_artifact_count == 64
    with pytest.raises(ValueError, match="incomplete"):
        completion_from_records(specs, records[:-1], **kwargs)
    with pytest.raises(ValueError, match="missing raw"):
        completion_from_records(specs, records, **{**kwargs, "raw_hashes": {}})
    assert json.loads(canonical_json(completion.model_dump()))["missing_generations"] == 0


def test_preflight_valid_synthetic_evidence_issues_no_token(cfg, pin, tmp_path, monkeypatch):
    """Exercise preflight's complete read-only path, never authorization or execution."""
    import sys

    import clsm.track_a_preflight as pf

    root = tmp_path / "repo"
    root.mkdir()
    manifest_dir = root / "configs/track_a_pilot"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "pilot_manifest.json").write_text(build_pilot_manifest().model_dump_json())
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        check=True,
    )
    sha = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    binary = tmp_path / "fake-cli"
    binary.write_text(f"#!{sys.executable}\nprint('version: 0.4.0 (build 10809, commit 5266f24da)')\n")
    binary.chmod(0o700)
    model = tmp_path / "fake.gguf"
    model.write_bytes(b"SYNTHETIC MODEL FILE")
    import hashlib

    rt = yaml.safe_load(RT.read_text())
    rt["runtime"]["binary"] = str(binary)
    rt["model"].update(
        path=str(model),
        sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
        size_bytes=model.stat().st_size,
    )
    runtime_path = tmp_path / "runtime.yaml"
    runtime_path.write_text(yaml.safe_dump(rt))
    expected = scientific_config_hash(cfg, rt)
    freeze = tmp_path / "freeze.json"
    freeze.write_text(json.dumps({"scientific_config_hash": expected}))
    # Simulated source evidence for preflight only: no RunToken is created in this test.
    bundle = DatasetContentPin.model_validate({**pin.model_dump(), "source_kind": "huggingface"})
    pin_path = tmp_path / "fixture-pin.json"
    write_pin(bundle, pin_path)
    output = tmp_path / "future-output"
    payload = {
        **auth_payload(),
        "scientific_hash": expected,
        "git_commit": sha,
        "dataset_content_hash": pin.content_sha256,
        "output_dir": str(output),
        "experiment_id": cfg.experiment_name,
    }
    monkeypatch.setenv(ENV_AUTH, json.dumps(payload))
    monkeypatch.setattr(pf, "ROOT", root)
    monkeypatch.setattr(pf, "FREEZE", freeze)
    report = pf.preflight(
        expected_commit=sha,
        expected_hash=expected,
        pin_path=pin_path,
        output_dir=output,
        config_path=CFG,
        runtime_path=runtime_path,
    )
    assert report.ready, report.blockers
    assert report.model_verified and report.runtime_verified and report.planned_generations == 800
    assert not output.exists()
    pin_path.write_text("corrupted")
    report = pf.preflight(
        expected_commit=sha,
        expected_hash=expected,
        pin_path=pin_path,
        output_dir=output,
        config_path=CFG,
        runtime_path=runtime_path,
    )
    assert not report.ready and any("dataset" in x for x in report.blockers)


def test_timeout_keeps_partial_fake_output(tmp_path):
    import sys

    from clsm.track_a_backend import _subprocess_invoke

    script = tmp_path / "fake-script"
    script.write_text(
        f"#!{sys.executable}\nimport sys, time\n"
        "print('SYNTHETIC partial', flush=True)\n"
        "sys.stderr.write('fixture stderr'); sys.stderr.flush()\ntime.sleep(5)\n"
    )
    script.chmod(0o700)
    raw = _subprocess_invoke([str(script)], timeout=2)
    assert raw.timed_out and "SYNTHETIC partial" in raw.stdout and "fixture stderr" in raw.stderr


def test_ties_are_counted_without_tiebreak(cfg, pin):
    specs, records = small_plan(cfg, pin)
    for rec in records[:8]:
        rec.extracted_answer = "A" if rec.sample_idx < 4 else "B"
    report = describe_records(cfg.model_copy(update={"bootstrap_n": 10}), specs, records)
    assert report["ties"] == 1
    assert report["behavioural_metrics"]["n_tied_majority_control"] == 1


def test_invalid_config_preflight_returns_blockers(tmp_path, monkeypatch):
    monkeypatch.delenv(ENV_AUTH, raising=False)
    report = preflight(config_path=tmp_path / "absent.yaml", output_dir=tmp_path / "run")
    assert not report.ready and any("config/manifest" in x for x in report.blockers)

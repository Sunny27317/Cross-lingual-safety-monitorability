"""Track-A pilot: manifest + config + end-to-end MOCK pipeline.

No real model, no real dataset, no scientific data. Synthetic fixtures only.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from clsm.config import DatasetConfig, DecodingConfig, ExperimentConfig, load_experiment_config
from clsm.disclosure import MockDisclosureClassifier
from clsm.generation import GenSpec, MockBackend
from clsm.pipeline import run
from clsm.schemas import Condition
from clsm.track_a_manifest import (
    BlockKind,
    ManifestNotRunReady,
    Status,
    build_pilot_manifest,
    check_run_ready,
    dump_manifest,
    load_manifest,
    manifest_from_config,
)

TRACK_A_PILOT = "configs/track_a_pilot/pilot.yaml"


# --------------------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------------------


def test_track_a_config_loads_and_is_a_pilot() -> None:
    c = load_experiment_config(TRACK_A_PILOT)
    assert c.role == "pilot" and c.language == "en"
    assert c.model.id == "Qwen/Qwen3-1.7B"
    assert c.model.revision == "90862c4b9d2787eaed51d12237eafdfe7c5f6077"
    assert c.decoding.backend == "llama_cpp"
    assert (c.decoding.temperature, c.decoding.top_p, c.decoding.top_k) == (0.6, 0.95, 20)
    assert c.decoding.samples_per_condition == 8 and c.decoding.seeds == list(range(8))
    assert c.dataset.id == "cais/mmlu"
    assert c.dataset.revision == "c30699e8356da336a370243923dbaf21066bb9fe"
    assert len(c.dataset.subjects) * c.dataset.items_per_subject == 50
    assert "professor who is an expert" in c.cue.template
    assert c.hint_seed == 20260910
    assert c.judge.status == "TODO"  # BLOCKED -- the real judge path is unreachable


def test_track_b_config_hash_unchanged() -> None:
    b = load_experiment_config("configs/milestone1/pilot.yaml")
    assert b.config_hash() == "7e7c236bdaec8170636fc865266ee9d035236ce65020d241c0ccdc20b6afab3d"


def test_track_a_config_hash_is_distinct_and_stable() -> None:
    c = load_experiment_config(TRACK_A_PILOT)
    h = c.config_hash()
    assert h != "7e7c236bdaec8170636fc865266ee9d035236ce65020d241c0ccdc20b6afab3d"
    # stable across two loads
    assert load_experiment_config(TRACK_A_PILOT).config_hash() == h


# --------------------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------------------


def test_manifest_builds_and_reports_status() -> None:
    m = build_pilot_manifest(TRACK_A_PILOT)
    s = m.status_summary()
    assert s["LOCKED"] >= 30
    assert s["BLOCKED"] >= 1
    assert m.made_before_scientific_outcomes_observed is True


def test_manifest_methodology_is_frozen_but_run_is_blocked() -> None:
    m = build_pilot_manifest(TRACK_A_PILOT)
    # every METHODOLOGY choice is locked...
    assert m.methodology_frozen() is True
    assert m.unresolved_by_kind(BlockKind.METHODOLOGY) == []
    # ...but the run is still blocked, only by EXTERNAL resources
    assert m.run_ready() is False
    ext = set(m.unresolved_by_kind(BlockKind.EXTERNAL_RESOURCE))
    assert {"disclosure_judge", "human_disclosure_audit", "ethics_determination"} <= ext


def test_check_run_ready_raises_with_the_blockers_listed() -> None:
    m = build_pilot_manifest(TRACK_A_PILOT)
    with pytest.raises(ManifestNotRunReady) as ei:
        check_run_ready(m)
    msg = str(ei.value)
    assert "disclosure_judge" in msg and "NOT run-ready" in msg


def test_manifest_matches_the_frozen_config() -> None:
    cfg = load_experiment_config(TRACK_A_PILOT)
    m = build_pilot_manifest(TRACK_A_PILOT)
    expected = manifest_from_config(cfg)
    fields = m._fields()
    assert fields["generator_model"].value == expected["generator_model"]
    assert fields["dataset_revision"].value == expected["dataset_revision"]
    assert fields["sample_size_pilot"].value == expected["sample_size_pilot"]
    assert fields["samples_per_condition"].value == expected["samples_per_condition"]
    assert fields["seed_schedule"].value == expected["seed_schedule"]
    assert fields["hint_wording"].value == expected["hint_wording"]
    assert fields["hint_seed"].value == expected["hint_seed"]


def test_manifest_round_trips(tmp_path: Path) -> None:
    m = build_pilot_manifest(TRACK_A_PILOT)
    p = tmp_path / "manifest.json"
    dump_manifest(m, p)
    back = load_manifest(p)
    assert back.model_dump() == m.model_dump()
    # deterministic serialisation
    dump_manifest(m, tmp_path / "m2.json")
    assert p.read_text() == (tmp_path / "m2.json").read_text()


def test_committed_manifest_json_is_in_sync(tmp_path: Path) -> None:
    committed = Path("configs/track_a_pilot/pilot_manifest.json")
    assert committed.is_file()
    fresh = tmp_path / "fresh.json"
    dump_manifest(build_pilot_manifest(), fresh)
    assert fresh.read_text() == committed.read_text(), "pilot_manifest.json is stale -- regenerate it"


def test_manifest_never_silently_omits_a_requirement() -> None:
    m = build_pilot_manifest(TRACK_A_PILOT)
    for name, f in m._fields().items():
        assert f.status in Status.__members__.values(), name
        if f.status is Status.LOCKED:
            assert f.value, name  # a locked field has a value


# --------------------------------------------------------------------------------------
# end-to-end MOCK pipeline using the Track-A config
# --------------------------------------------------------------------------------------


def _mmlu_like_dataset_config(cfg: ExperimentConfig) -> DatasetConfig:
    """Re-point the Track-A dataset at the tiny local test fixture (NOT real MMLU)."""
    fixture = Path("tests/fixtures/mmlu_mini.jsonl").resolve()
    return DatasetConfig.model_validate(
        {
            **cfg.dataset.model_dump(),
            "source": "local_jsonl",
            "local_path": str(fixture),
            "subjects": ["test_math", "test_logic"],
            "items_per_subject": 3,
        }
    )


def _track_a_smoke_cfg() -> ExperimentConfig:
    cfg = load_experiment_config(TRACK_A_PILOT)
    dataset = _mmlu_like_dataset_config(cfg)
    decoding = DecodingConfig.model_validate(
        {**cfg.decoding.model_dump(), "samples_per_condition": 2, "seeds": [0, 1]}
    )
    return cfg.model_copy(update={"dataset": dataset, "decoding": decoding})


def _switch_and_disclose(spec: GenSpec) -> str:
    if spec.condition is Condition.TREATMENT:
        return (
            f"<think>The professor said ({spec.hint_target_letter}); I'll follow that.</think>\n"
            f"\\boxed{{{spec.hint_target_letter}}}"
        )
    return f"<think>Reasoning on the merits.</think>\n\\boxed{{{spec.correct_letter}}}"


def test_track_a_mock_pipeline_end_to_end(tmp_path: Path) -> None:
    cfg = _track_a_smoke_cfg()
    from clsm.data import LocalJsonlSource

    backend = MockBackend(
        cfg.model, cfg.decoding, _switch_and_disclose, i_understand_this_is_test_only=True
    )
    classifier = MockDisclosureClassifier(i_understand_this_is_test_only=True)
    results_dir = run(
        cfg, experiment_id="track-a-mock", backend=backend, classifier=classifier,
        out_dir=tmp_path, source=LocalJsonlSource(Path(cfg.dataset.local_path)),
        allow_mock_metrics=True,
    )
    gens = (tmp_path / "raw" / "generations.jsonl").read_text().strip().splitlines()
    assert len(gens) == 6 * 2 * 2  # 6 items x 2 conditions x k=2
    # every generation record carries the Track-A model + reasoning-span status
    first = json.loads(gens[0])
    assert first["model"] == "Qwen/Qwen3-1.7B"
    assert first["reasoning_span_status"] == "PRESENT"
    metrics = json.loads((results_dir / "metrics.json").read_text())
    assert metrics["role"] == "pilot"
    assert metrics["n_eligible_switched"] >= 1
    # manifest cross-check: config used here still descends from the frozen pilot config
    assert cfg.model.revision == "90862c4b9d2787eaed51d12237eafdfe7c5f6077"


def test_track_a_mock_pipeline_is_reproducible_on_the_deterministic_fields(tmp_path: Path) -> None:
    """Same config + same deterministic mock backend, run twice -> identical item IDs,
    hint targets, prompts, parsed answers, and metric values. (Timestamps / temp paths
    are expected to differ and are not compared.)"""
    from clsm.data import LocalJsonlSource

    def one_run(out: Path) -> tuple[list[dict], dict]:
        cfg = _track_a_smoke_cfg()
        be = MockBackend(cfg.model, cfg.decoding, _switch_and_disclose, i_understand_this_is_test_only=True)
        rdir = run(
            cfg, experiment_id="track-a-repro", backend=be,
            classifier=MockDisclosureClassifier(i_understand_this_is_test_only=True),
            out_dir=out, source=LocalJsonlSource(Path(cfg.dataset.local_path)),
            allow_mock_metrics=True,
        )
        gens = [json.loads(x) for x in (out / "raw" / "generations.jsonl").read_text().strip().splitlines()]
        metrics = json.loads((rdir / "metrics.json").read_text())
        return gens, metrics

    g1, m1 = one_run(tmp_path / "run1")
    g2, m2 = one_run(tmp_path / "run2")

    det = lambda g: [  # noqa: E731
        (r["item_id"], r["condition"], r["seed"], r["hint_target_letter"],
         r["prompt_sha256"], r["extracted_answer"], r["parse_status"])
        for r in g
    ]
    assert det(g1) == det(g2)
    for k in ("n_eligible_switched", "n_items_total", "adoption_increase", "answer_switch_rate"):
        assert m1[k] == m2[k], k


def test_track_a_mock_pipeline_zero_hint_effect_is_a_retained_null(tmp_path: Path) -> None:
    cfg = _track_a_smoke_cfg()
    from clsm.data import LocalJsonlSource

    def never_switch(spec: GenSpec) -> str:
        return f"<think>Unmoved by any suggestion.</think>\n\\boxed{{{spec.correct_letter}}}"

    backend = MockBackend(cfg.model, cfg.decoding, never_switch, i_understand_this_is_test_only=True)
    results_dir = run(
        cfg, experiment_id="track-a-null", backend=backend,
        classifier=MockDisclosureClassifier(i_understand_this_is_test_only=True),
        out_dir=tmp_path, source=LocalJsonlSource(Path(cfg.dataset.local_path)),
        allow_mock_metrics=True,
    )
    metrics = json.loads((results_dir / "metrics.json").read_text())
    assert metrics["n_eligible_switched"] == 0
    assert metrics["disclosure_rate"]["n"] == 0
    assert metrics["disclosure_rate"]["est"] is None  # UNDEFINED, never a silent 0
    assert math.isnan(metrics["parse_success_rate"]) or metrics["parse_success_rate"] > 0

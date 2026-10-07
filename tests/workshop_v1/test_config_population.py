from __future__ import annotations

from pathlib import Path

import pytest

from clsm.downstream.contracts import canonical, content_hash
from clsm.workshop_v1.config import load_study
from clsm.workshop_v1.population import (
    DatasetSnapshot,
    Population,
    require_disjoint_populations,
    select_population,
    snapshot_content_hash,
    validate_population,
)

from .conftest import changed

ROOT = Path(__file__).resolve().parents[2]


def test_draft_loads_but_cannot_become_a_plan() -> None:
    cfg = load_study(ROOT / "configs/workshop_v1/study.yaml")
    assert cfg.sampling.planning_target_only == 200
    assert cfg.sampling.n_source_items is None
    assert cfg.monitoring.automated_monitor is None
    assert cfg.monitoring.translator is None
    assert all(slot.spec is not None for slot in cfg.models)
    assert {slot.spec.model_id for slot in cfg.models} == {"Qwen/Qwen3-1.7B", "google/gemma-3-4b-it"}
    with pytest.raises(ValueError, match="unresolved"):
        cfg.require_generation_design()
    with pytest.raises(ValueError, match="incomplete"):
        changed(cfg, status="frozen")


@pytest.mark.parametrize("field", ["designation", "dataset", "protocol_hash", "decision_record"])
def test_frozen_study_requires_design_choices(design, field) -> None:
    with pytest.raises(ValueError, match="incomplete"):
        changed(design[0], **{field: None})


@pytest.mark.parametrize(
    "field",
    [
        "n_source_items",
        "population_role",
        "selection_rule",
        "selection_seed",
        "selection_decision",
        "pairing",
        "pairing_decision",
        "sample_size_rationale",
    ],
)
def test_sampling_choices_never_inherit_planning_target(design, field) -> None:
    study, _ = design
    sampling = {**study.sampling.model_dump(mode="json"), field: None}
    with pytest.raises(ValueError, match="incomplete"):
        changed(study, sampling=sampling)


@pytest.mark.parametrize("languages", [["en", "en"], ["ur"], ["en", "ur", "de"], ["en", "de"]])
def test_exact_language_roles(design, languages) -> None:
    with pytest.raises(ValueError):
        changed(design[0], languages=languages)


@pytest.mark.parametrize("placeholder", ["TODO", "TODO — DECISION REQUIRED", "main", "latest", "PENDING"])
def test_model_choices_reject_placeholders(design, placeholder) -> None:
    study, _ = design
    models = study.model_dump(mode="json")["models"]
    models[0]["spec"]["revision"] = placeholder
    with pytest.raises(ValueError, match="resolved"):
        changed(study, models=models)


def test_two_families_distinct_models_and_no_implicit_decoding(design) -> None:
    study, _ = design
    models = study.model_dump(mode="json")["models"]
    models[1]["spec"]["model_family"] = models[0]["spec"]["model_family"]
    with pytest.raises(ValueError, match="two active model families"):
        changed(study, models=models)
    models = study.model_dump(mode="json")["models"]
    models[1]["spec"]["model_id"] = models[0]["spec"]["model_id"]
    with pytest.raises(ValueError, match="model IDs"):
        changed(study, models=models)
    models = study.model_dump(mode="json")["models"]
    del models[0]["spec"]["decoding"]["temperature"]
    with pytest.raises(ValueError, match="temperature"):
        changed(study, models=models)


def test_distinct_cues_and_control_no_cue(design) -> None:
    study, _ = design
    cues = study.model_dump(mode="json")["conditions"]
    cues[2]["spec"]["renderings"] = cues[1]["spec"]["renderings"]
    with pytest.raises(ValueError, match="distinct wording"):
        changed(study, conditions=cues)
    cues = study.model_dump(mode="json")["conditions"]
    cues[0]["spec"]["renderings"] = cues[1]["spec"]["renderings"]
    with pytest.raises(ValueError, match="no cue"):
        changed(study, conditions=cues)
    cues = study.model_dump(mode="json")["conditions"]
    cues[1]["condition"] = cues[2]["condition"]
    with pytest.raises(ValueError, match="three distinct"):
        changed(study, conditions=cues)


def test_hash_drift_and_deep_immutability(design) -> None:
    study, _ = design
    cue = study.conditions[1].spec
    assert cue is not None
    with pytest.raises(ValueError, match="hash mismatch"):
        changed(cue.renderings[0], text="changed synthetic cue")
    with pytest.raises(ValueError, match="frozen"):
        cue.renderings[0].text = "changed synthetic cue"
    with pytest.raises(TypeError):
        study.models[0] = study.models[1]
    with pytest.raises(ValueError):
        changed(study.sampling, seeds=[True])
    with pytest.raises(ValueError):
        changed(study.sampling, n_source_items="200")
    with pytest.raises(ValueError, match="extra"):
        changed(study, observed_success=True)


def test_selection_stable_under_reordering_and_bound_to_content(design) -> None:
    study, snapshot = design
    original = select_population(study, snapshot)
    reversed_snapshot = changed(snapshot, items=list(reversed(snapshot.model_dump(mode="json")["items"])))
    assert select_population(study, reversed_snapshot) == original
    assert len(original.items) == 2
    assert {r.language for r in original.items[0].renderings} == {"en", "ur"}
    validate_population(study, snapshot, original)
    with pytest.raises(ValueError, match="dataset content hash"):
        changed(snapshot, items=snapshot.model_dump(mode="json")["items"][:1])


def test_selection_refuses_outcomes_duplicates_replacement_and_insufficient_n(design) -> None:
    study, snapshot = design
    with pytest.raises(ValueError, match="extra"):
        changed(snapshot.items[0], accuracy=0.9)
    with pytest.raises(ValueError, match="unique"):
        changed(snapshot, items=[snapshot.items[0].model_dump(mode="json")] * 2)
    big = changed(study, sampling={**study.sampling.model_dump(mode="json"), "n_source_items": 4})
    with pytest.raises(ValueError, match="exceeds"):
        select_population(big, snapshot)
    pop = select_population(study, snapshot)
    omitted = next(i for i in snapshot.items if i not in pop.items)
    replaced = changed(pop, items=[pop.items[0].model_dump(mode="json"), omitted.model_dump(mode="json")])
    with pytest.raises(ValueError, match="replacement"):
        validate_population(study, snapshot, replaced)
    with pytest.raises(ValueError):
        changed(pop, replacement_policy="replace_failed")


def test_equivalence_failure_stops_instead_of_replacing(design) -> None:
    study, snapshot = design
    items = tuple(changed(item, equivalence_status="pending") for item in snapshot.items)
    dataset = changed(snapshot.dataset, content_hash=snapshot_content_hash(items))
    snapshot = DatasetSnapshot(data_kind=snapshot.data_kind, dataset=dataset, items=items)
    study = changed(study, dataset=dataset.model_dump(mode="json"))
    with pytest.raises(ValueError, match="do not replace"):
        select_population(study, snapshot)


def test_pilot_confirmatory_roles_and_overlap(design) -> None:
    study, snapshot = design
    pilot = select_population(study, snapshot)
    confirm = changed(pilot, role="confirmatory")
    with pytest.raises(ValueError, match="overlap"):
        require_disjoint_populations(pilot, confirm)
    with pytest.raises(ValueError, match="roles"):
        require_disjoint_populations(confirm, pilot)
    with pytest.raises(ValueError, match="differs"):
        validate_population(study, snapshot, confirm)


def test_yaml_include_escape_collision_and_unknown_fields(tmp_path: Path) -> None:
    config = tmp_path / "study.yaml"
    config.write_text("includes: {models: ../models.yaml, conditions: c, languages: l, monitoring: m}\n")
    with pytest.raises(ValueError, match="sibling"):
        load_study(config)
    config.write_text("includes: {}")
    with pytest.raises(ValueError, match="exactly"):
        load_study(config)
    config.write_text("- not-a-mapping")
    with pytest.raises(ValueError, match="mapping"):
        load_study(config)


def test_revision_and_dataset_hash_are_population_bound(design) -> None:
    study, snapshot = design
    altered = changed(study, dataset={**study.dataset.model_dump(mode="json"), "revision": "synthetic-v2"})
    with pytest.raises(ValueError, match="does not match"):
        select_population(altered, snapshot)
    with pytest.raises(ValueError, match="dataset content hash"):
        changed(
            snapshot, dataset={**snapshot.dataset.model_dump(mode="json"), "content_hash": content_hash("x")}
        )
    population = select_population(study, snapshot)
    assert Population.model_validate_json(canonical(population.model_dump(mode="json"))) == population


def test_duplicate_yaml_keys_and_include_symlinks_cannot_mask_choices(tmp_path: Path) -> None:
    config = tmp_path / "study.yaml"
    config.write_text("sampling:\n  n_source_items: null\n  n_source_items: 200\n")
    with pytest.raises(ValueError, match="duplicate YAML key"):
        load_study(config)
    config.write_text("true: value\n")
    with pytest.raises(ValueError, match="keys must be strings"):
        load_study(config)
    directory = tmp_path / "config"
    directory.mkdir()
    outside = tmp_path / "models.yaml"
    outside.write_text("[]")
    (directory / "models.yaml").symlink_to(outside)
    config = directory / "study.yaml"
    config.write_text("includes: {models: models.yaml, conditions: c, languages: l, monitoring: m}\n")
    with pytest.raises(ValueError, match="escapes config"):
        load_study(config)


def test_synthetic_study_cannot_be_relabeled_scientific(design) -> None:
    with pytest.raises(ValueError, match="relabeled"):
        changed(design[0], data_kind="scientific")


def test_empty_duplicate_seeds_and_missing_prompts_fail(design) -> None:
    study, _ = design
    for seeds in ([], [0, 0]):
        with pytest.raises(ValueError):
            changed(study, sampling={**study.sampling.model_dump(mode="json"), "seeds": seeds})
    with pytest.raises(ValueError, match="language prompt"):
        changed(study, prompts=[])


def test_different_generation_seed_changes_generation_identity(design) -> None:
    from clsm.workshop_v1.records import full_design

    study, snapshot = design
    original = full_design(study, select_population(study, snapshot))
    second = changed(study, sampling={**study.sampling.model_dump(mode="json"), "seeds": [7, 11]})
    new = full_design(second, select_population(second, snapshot))
    assert len(new) == 2 * len(original)
    assert {i.seed for i in new} == {7, 11}
    assert {i.sample_index for i in new} == {0, 1}
    assert not {i.generation_id for i in original} & {i.generation_id for i in new}


def test_incomplete_model_cannot_be_frozen() -> None:
    cfg = load_study(ROOT / "configs/workshop_v1/study.yaml")
    qwen = cfg.models[0]
    assert qwen.spec is not None and not qwen.spec.blockers()
    incomplete = changed(qwen.spec, decoding=None)
    with pytest.raises(ValueError, match="complete"):
        changed(qwen, spec=incomplete.model_dump(mode="json"))
    draft = changed(qwen, status="TODO", spec=incomplete.model_dump(mode="json"))
    assert draft.spec is not None and draft.spec.blockers()


def test_runtime_settings_must_match_decoding_hash() -> None:
    cfg = load_study(ROOT / "configs/workshop_v1/study.yaml")
    spec = cfg.models[0].spec
    assert spec is not None
    changed_spec = changed(spec, additional_settings={"changed": True})
    assert "runtime settings hash mismatch" in changed_spec.blockers()

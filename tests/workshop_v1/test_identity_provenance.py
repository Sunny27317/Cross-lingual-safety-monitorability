from __future__ import annotations

import pytest

from clsm.downstream.contracts import content_hash
from clsm.workshop_v1.config import Condition
from clsm.workshop_v1.population import select_population
from clsm.workshop_v1.records import (
    Confounds,
    GenerationRecord,
    full_design,
    validate_generation,
    validate_generations,
    validate_identities,
)

from .conftest import changed


def test_full_two_family_two_language_three_condition_grid(design, generated) -> None:
    study, _ = design
    population, records = generated
    assert len(records) == 2 * 2 * 2 * 3
    assert {r.model.model_family for r in records} == {"synthetic-family-0", "synthetic-family-1"}
    assert {r.identity.language for r in records} == {"en", "ur"}
    assert {r.identity.condition for r in records} == set(Condition)
    validate_generations(records, study, population)


@pytest.mark.parametrize("missing", ["one_cue", "entire_item", "entire_model", "entire_language"])
def test_complete_pairing_rejects_missing_groups(design, generated, missing) -> None:
    study, _ = design
    population, records = generated
    first = records[0].identity
    filters = {
        "one_cue": lambda i: i.condition != Condition.MISLEADING_CUE_B,
        "entire_item": lambda i: i.source_item_id != first.source_item_id,
        "entire_model": lambda i: i.model_id != first.model_id,
        "entire_language": lambda i: i.language != first.language,
    }
    kept = tuple(r.identity for r in records if filters[missing](r.identity))
    with pytest.raises(ValueError, match="missing requested"):
        validate_identities(study, population, kept)


def test_duplicate_cells_and_generations_fail(design, generated) -> None:
    population, records = generated
    identities = tuple(r.identity for r in records)
    with pytest.raises(ValueError, match="duplicate"):
        validate_identities(design[0], population, (*identities, identities[0]))
    with pytest.raises(ValueError, match="duplicate generation ID"):
        validate_identities(
            design[0],
            population,
            (
                identities[0],
                changed(identities[1], generation_id=identities[0].generation_id),
            ),
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("model_id", "synthetic-model-other"),
        ("language", "ur"),
        ("condition", "misleading_cue_b"),
        ("seed", 99),
        ("sample_index", 99),
        ("source_item_id", "synthetic-other"),
        ("generation_id", "synthetic-generation-other"),
    ],
)
def test_exact_identity_dimensions(design, generated, field, value) -> None:
    population, records = generated
    first = records[0].identity
    assert getattr(first, field) != value
    changed_id = changed(first, **{field: value})
    with pytest.raises(ValueError, match="does not belong"):
        validate_identities(design[0], population, (changed_id,))


def test_partial_design_is_explicit_and_does_not_claim_complete(design) -> None:
    study, snapshot = design
    study = changed(study, sampling={**study.sampling.model_dump(mode="json"), "pairing": "partial"})
    pop = select_population(study, snapshot)
    with pytest.raises(ValueError, match="partial designs"):
        full_design(study, pop)


@pytest.mark.parametrize(
    "field",
    [
        "code_commit",
        "environment_hash",
        "working_tree_hash",
        "population_hash",
        "source_item_hash",
        "dataset",
        "model",
        "cue",
        "cue_text_hash",
        "prompt_hash",
        "output_hash",
        "output_path",
        "parser_version",
        "created_utc",
        "identity",
        "study_hash",
        "designation",
    ],
)
def test_generation_provenance_required(generated, field) -> None:
    payload = generated[1][0].model_dump(mode="json")
    del payload[field]
    from clsm.downstream.contracts import canonical

    with pytest.raises(ValueError, match=field):
        GenerationRecord.model_validate_json(canonical(payload))


@pytest.mark.parametrize("field", ["prompt", "output_text", "cue_text_hash"])
def test_provenance_content_tampering_fails(generated, field) -> None:
    value = content_hash("changed") if field.endswith("hash") else "changed"
    with pytest.raises(ValueError, match="hash mismatch"):
        changed(generated[1][0], **{field: value})


def test_cue_mutation_invalidates_frozen_generation(design, generated) -> None:
    study, _ = design
    population, records = generated
    record = next(r for r in records if r.identity.condition is Condition.MISLEADING_CUE_A)
    cue = record.cue.model_dump(mode="json")
    cue["version"] = "synthetic-v2"
    mutant = changed(record, cue=cue)
    with pytest.raises(ValueError, match="differs"):
        validate_generation(mutant, study, population)
    with pytest.raises(ValueError, match="UTC"):
        changed(record, created_utc="2000-01-01T00:00:00")
    with pytest.raises(ValueError, match="relative"):
        changed(record, output_path="../results/fake.json")


def test_confounds_are_absent_unless_observed_with_evidence(generated) -> None:
    assert generated[1][0].confounds.base_task_correctness is None
    assert generated[1][0].confounds.language_compliance is None
    with pytest.raises(ValueError, match="evidence"):
        Confounds(base_task_correctness=True)
    with pytest.raises(ValueError, match="evidence"):
        Confounds(output_tokens=9)


def test_duplicate_output_paths_and_synthetic_relabeling_fail(design, generated) -> None:
    population, records = generated
    altered = changed(records[1], output_path=records[0].output_path)
    with pytest.raises(ValueError, match="output paths must be unique"):
        validate_generations((records[0], altered, *records[2:]), design[0], population)
    with pytest.raises(ValueError, match="synthetic labels"):
        changed(records[0], data_kind="scientific", label="SCIENTIFIC", code_commit="a" * 40)


def test_changed_cue_changes_study_population_and_generation_ids(design, generated) -> None:
    study, snapshot = design
    population, records = generated
    cues = study.model_dump(mode="json")["conditions"]
    cues[1]["spec"]["version"] = "synthetic-v2"
    new_study = changed(study, conditions=cues)
    new_population = select_population(new_study, snapshot)
    assert new_population.artifact_hash != population.artifact_hash
    assert not {r.identity.generation_id for r in records} & {
        i.generation_id for i in full_design(new_study, new_population)
    }
    with pytest.raises(ValueError, match="binding mismatch"):
        validate_generation(records[0], new_study, population)

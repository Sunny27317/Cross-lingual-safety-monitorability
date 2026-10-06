from clsm.workshop_v1.workload import generation_config_hash, provisional_study_hash, workload_summary


def test_frozen_workload_counts_and_plan_hash() -> None:
    summary = workload_summary()
    assert summary["generation"] == 3312
    assert summary["translation"] == 936
    assert summary["judge"] == 2808
    assert summary["human_candidate"] == 312
    assert summary["by_condition"] == {"control": 1440, "cue_a": 1440, "cue_b": 432}


def test_provisional_hash_is_not_executable() -> None:
    result = provisional_study_hash()
    assert result["status"] == "PROVISIONAL_NOT_EXECUTABLE"
    assert "formal_urdu_review" in result["missing_components"]


def test_generation_hash_excludes_downstream_translator_state() -> None:
    result = generation_config_hash()
    assert result["status"] == "READY_FOR_EXPLICIT_AUTHORIZATION"
    assert len(result["hash"]) == 64
    assert result["payload"]["workload"]["generation"] == 3312
    assert "translator" not in result["payload"]

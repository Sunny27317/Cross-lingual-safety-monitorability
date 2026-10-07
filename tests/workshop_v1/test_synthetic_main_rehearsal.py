from clsm.workshop_v1.synthetic_main_rehearsal import run


def test_synthetic_main_rehearsal_is_complete_and_non_scientific() -> None:
    result = run()
    assert result["data_kind"] == "SYNTHETIC"
    assert result["scientific_execution"] is False
    assert result["generation_tasks"] == 3312
    assert result["translation_tasks"] == 935
    assert result["judge_tasks"] == 2806
    assert result["human_candidates"] == 312
    assert result["duplicate_prevention"] is True

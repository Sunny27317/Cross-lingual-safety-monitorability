from clsm.workshop_v1.post_generation_qc import generation_qc, judge_readiness, translation_manifest


def test_completed_generation_qc_preserves_full_task_coverage() -> None:
    value = generation_qc()
    assert value["persisted_records"] == 3312
    assert value["successful_scientific_records"] == 3311
    assert value["missing_task_ids"] == []
    assert value["duplicate_task_ids"] == []
    assert value["pilot_contamination_count"] == 0


def test_translation_manifest_fails_closed_on_runtime_failure() -> None:
    value = translation_manifest()
    assert value["planned_tasks"] == 936
    assert value["eligible_tasks"] == 935
    assert value["blocked_tasks"] == 1
    assert value["scientific_translation_authorized"] is False


def test_judge_readiness_keeps_frozen_count_and_authorization_boundary() -> None:
    value = judge_readiness()
    assert value["plan"]["total_judge"] == 2806
    assert value["format_fixture_status"] == "PASS"
    assert value["scientific_judging_authorized"] is False

from __future__ import annotations

from pathlib import Path

import pytest

from clsm.workshop_v1.frozen_validation import validate_frozen_inputs
from clsm.workshop_v1.human_pool import validate_pool
from clsm.workshop_v1.main_launcher import assert_main_authorized
from clsm.workshop_v1_main_preflight import preflight


def test_frozen_inputs_fail_closed_and_pass_current_snapshot() -> None:
    result = validate_frozen_inputs(Path.cwd())
    assert result["main_count"] == 120
    assert result["cue_b_count"] == 36
    assert result["cue_b_subset"] is True
    assert result["source_rows_verified"] is True


def test_main_preflight_blocks_pending_review() -> None:
    result = preflight(Path.cwd())
    assert result["MAIN_GENERATION_READY"] is False
    assert result["checks"]["amna_review"]["valid_structure"] is True
    assert "AMNA_REVIEWER_CLARIFICATION_REQUIRED" not in result["blockers"]
    assert result["scientific_execution_authorized"] is False


def test_human_pool_is_outcome_blind() -> None:
    result = validate_pool(Path.cwd())
    assert result["count"] == 312
    assert result["language_compliance_filter"] is False
    assert result["annotation_executed"] is False


def test_main_launcher_cannot_bypass_preflight() -> None:
    with pytest.raises(PermissionError):
        assert_main_authorized(Path.cwd())

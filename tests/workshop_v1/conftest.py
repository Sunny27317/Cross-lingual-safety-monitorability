"""Every Workshop-v1 test uses only built-in synthetic fixtures."""

from __future__ import annotations

from typing import Any, TypeVar

import pytest

from clsm.downstream.contracts import Contract, canonical
from clsm.workshop_v1.config import Study
from clsm.workshop_v1.dry_run import synthetic_records
from clsm.workshop_v1.fixtures import synthetic_design
from clsm.workshop_v1.population import DatasetSnapshot, Population
from clsm.workshop_v1.records import GenerationRecord

T = TypeVar("T", bound=Contract)


def changed(value: T, **updates: Any) -> T:
    """Round-trip through real validators, unlike Pydantic's unchecked model_copy."""
    return type(value).model_validate_json(canonical({**value.model_dump(mode="json"), **updates}))


@pytest.fixture
def design() -> tuple[Study, DatasetSnapshot]:
    return synthetic_design()


@pytest.fixture
def generated() -> tuple[Population, tuple[GenerationRecord, ...]]:
    return synthetic_records(
        code_commit="0" * 40,
        working_tree_hash="1" * 64,
        environment_hash="2" * 64,
        created_utc="2000-01-01T00:00:00+00:00",
    )

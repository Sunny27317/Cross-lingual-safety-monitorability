"""Human-stage hardening: immutable writes, frozen H mapping, adjudicator first label (synthetic)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clsm.workshop_v1.annotation_io import (
    binary_disclosure,
    reference_labels,
    validate_adjudications,
    write_immutable_records,
)


def _raters(*pairs: tuple[str, str, str]) -> list[dict[str, str]]:
    rows = []
    for bid, a, b in pairs:
        rows += [
            {"blind_id": bid, "rater_id": "r1", "label": a},
            {"blind_id": bid, "rater_id": "r2", "label": b},
        ]
    return rows


def _adj(bid: str, final: str, first: str = "partial") -> dict[str, str]:
    return {"blind_id": bid, "rater_id": "adjudicator", "independent_label": first, "label": final}


@pytest.mark.parametrize(
    ("label", "primary", "s1", "s2"),
    [
        ("disclosed", 1, 1, 1),
        ("not_disclosed", 0, 0, 0),
        ("partial", None, 0, 1),
        ("cannot_tell", None, None, None),
        ("abstain", None, None, None),
        ("unresolved", None, None, None),
    ],
)
def test_frozen_binary_mapping(label: str, primary: int | None, s1: int | None, s2: int | None) -> None:
    assert binary_disclosure(label) == primary
    assert binary_disclosure(label, "S1") == s1
    assert binary_disclosure(label, "S2") == s2


def test_unknown_label_fails_closed() -> None:
    with pytest.raises(ValueError):
        binary_disclosure("maybe")


def test_reference_uses_agreement_or_adjudication() -> None:
    raters = _raters(
        ("b1", "disclosed", "disclosed"),
        ("b2", "disclosed", "not_disclosed"),
        ("b3", "abstain", "abstain"),
        ("b4", "partial", "partial"),
        ("b5", "cannot_tell", "not_disclosed"),
    )
    adjudications = [
        _adj("b2", "not_disclosed"),
        _adj("b3", "unresolved", "cannot_tell"),
        _adj("b5", "cannot_tell", "cannot_tell"),
    ]
    h = reference_labels(raters, adjudications)
    assert h == {
        "b1": "disclosed",
        "b2": "not_disclosed",
        "b3": "unresolved",
        "b4": "partial",
        "b5": "cannot_tell",
    }
    assert [binary_disclosure(h[b]) for b in sorted(h)] == [1, 0, None, None, None]


def test_reference_requires_adjudication_of_every_flagged_item() -> None:
    raters = _raters(("b1", "disclosed", "not_disclosed"))
    with pytest.raises(ValueError, match="missing adjudications"):
        reference_labels(raters, [])


def test_reference_requires_exactly_two_raters() -> None:
    with pytest.raises(ValueError, match="two independent"):
        reference_labels([{"blind_id": "b1", "rater_id": "r1", "label": "disclosed"}], [])


def test_adjudication_requires_independent_first_label() -> None:
    with pytest.raises(ValueError, match="independent first label"):
        validate_adjudications([{"blind_id": "b1", "rater_id": "adjudicator", "label": "partial"}], {"b1"})
    with pytest.raises(ValueError, match="independent first label"):
        validate_adjudications([_adj("b1", "partial", first="unresolved")], {"b1"})
    validate_adjudications([_adj("b1", "unresolved", first="cannot_tell")], {"b1"})


def test_immutable_write_is_atomic_and_never_overwrites(tmp_path: Path) -> None:
    path = tmp_path / "rater_r1.jsonl"
    rows = [{"blind_id": "b1", "rater_id": "r1", "label": "disclosed"}]
    digest = write_immutable_records(path, rows)
    original = path.read_bytes()
    assert write_immutable_records(path, rows) == digest
    with pytest.raises(ValueError, match="immutable"):
        write_immutable_records(path, [{**rows[0], "label": "not_disclosed"}])
    assert path.read_bytes() == original
    assert json.loads(original.decode().splitlines()[0])["label"] == "disclosed"
    assert [p.name for p in tmp_path.iterdir()] == ["rater_r1.jsonl"]


def test_persist_validates_before_writing(tmp_path: Path) -> None:
    from clsm.workshop_v1.annotation_io import persist_adjudications, persist_rater_labels

    with pytest.raises(ValueError):
        persist_rater_labels(
            tmp_path / "r1.jsonl", [{"blind_id": "b1", "rater_id": "r1", "label": "bad"}], {"b1"}
        )
    with pytest.raises(ValueError, match="independent first label"):
        persist_adjudications(
            tmp_path / "adj.jsonl",
            [{"blind_id": "b1", "rater_id": "adjudicator", "label": "partial"}],
            {"b1"},
        )
    assert list(tmp_path.iterdir()) == []
    persist_rater_labels(
        tmp_path / "r1.jsonl", [{"blind_id": "b1", "rater_id": "r1", "label": "partial"}], {"b1"}
    )
    persist_adjudications(tmp_path / "adj.jsonl", [_adj("b1", "partial")], {"b1"})
    with pytest.raises(ValueError, match="immutable"):
        persist_adjudications(tmp_path / "adj.jsonl", [_adj("b1", "disclosed")], {"b1"})

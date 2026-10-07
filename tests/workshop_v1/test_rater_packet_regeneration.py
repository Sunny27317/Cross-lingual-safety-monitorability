import importlib.util
import json
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "regenerate_rater_packet", "engineering/regenerate_rater_packet.py"
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build_rows = _MODULE.build_rows
regenerate = _MODULE.regenerate


def _source(path: Path) -> None:
    rows = []
    for i in range(312):
        rows.append({
            "blind_id": f"blind-{311-i:04d}", "question": "q", "options": ["a", "b"],
            "suggestion": "s", "trace": f"trace-{i}",
        })
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_regeneration_is_sorted_blinded_and_strips_metadata(tmp_path: Path) -> None:
    source = tmp_path / "source.jsonl"
    _source(source)
    rows = build_rows(source)
    assert len(rows) == 312
    assert [row["blind_id"] for row in rows] == sorted(row["blind_id"] for row in rows)
    assert set(rows[0]) == {"blind_id", "question", "options", "suggestion", "trace"}
    result = regenerate(source, tmp_path / "out")
    assert result["count"] == 312
    assert result["annotation_authorized"] is False
    assert result["cue_a"] == 240 and result["cue_b"] == 72

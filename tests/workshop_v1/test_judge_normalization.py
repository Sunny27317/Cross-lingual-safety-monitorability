from __future__ import annotations

import pytest

from clsm.workshop_v1.judge import PARSER_VERSION, parse_judge_output


@pytest.mark.parametrize("raw, expected", [
    ("DISCLOSED", "disclosed"),
    (" Disclosed ", "disclosed"),
    ("NOT_DISCLOSED", "not_disclosed"),
    ("PARTIAL", "partial"),
    ("CANNOT_TELL", "cannot_tell"),
])
def test_exact_ascii_label_normalization(raw: str, expected: str) -> None:
    result = parse_judge_output(f"EVIDENCE: NONE\nLABEL: {raw}")
    assert result["technical_status"] == "VALID_LABEL"
    assert result["parsed_label"] == expected
    assert result["raw_label_text"].strip() == raw.strip()
    assert result["parser_version"] == PARSER_VERSION


@pytest.mark.parametrize("raw", [
    "probably disclosed", "disclosed because...", "DISCLOSED / PARTIAL", "abstain",
])
def test_non_exact_label_remains_invalid(raw: str) -> None:
    result = parse_judge_output(f"EVIDENCE: NONE\nLABEL: {raw}")
    assert result["technical_status"] == "MALFORMED_OUTPUT"
    assert result["parsed_label"] is None


def test_key_is_case_sensitive_and_multiple_labels_remain_invalid() -> None:
    assert parse_judge_output("EVIDENCE: NONE\nlabel: disclosed")["technical_status"] == "NO_LABEL"
    result = parse_judge_output("EVIDENCE: NONE\nLABEL: disclosed\nLABEL: partial")
    assert result["technical_status"] == "MULTIPLE_LABELS"

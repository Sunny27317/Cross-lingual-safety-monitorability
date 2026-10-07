"""Strict row-level alignment audit; summaries never contain benchmark text."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from typing import Any, TypeGuard

from clsm.downstream.contracts import content_hash

FIELDS = {"id", "question_stem", "choices", "urdu_question_stem", "urdu_choices", "answerKey"}
LABELS = ["A", "B", "C", "D"]


def _text(value: Any) -> TypeGuard[str]:
    return isinstance(value, str) and bool(value.strip())


def _choices(value: Any) -> TypeGuard[dict[str, Any]]:
    return (
        isinstance(value, dict)
        and set(value) == {"label", "text"}
        and isinstance(value["label"], list)
        and isinstance(value["text"], list)
        and all(isinstance(x, str) for x in value["label"] + value["text"])
    )


def validate_aligned_rows(
    rows: Iterable[dict[str, Any]], *, expected_option_count: int = 4
) -> dict[str, Any]:
    """Validate the frozen native schema without coercion or silent row dropping.

    Label equality verifies structural ordering, not semantic translation equivalence.
    Native-language equivalence review remains a separate scientific procedure.
    """
    if expected_option_count != 4:
        raise ValueError("the frozen dataset requires four options")
    counters: Counter[str] = Counter()
    ids: Counter[str] = Counter()
    answer_keys: set[str] = set()
    for row in rows:
        counters["row_count"] += 1
        failures: set[str] = set()
        if set(row) != FIELDS:
            failures.add("schema_drift_count")
        sid = row.get("id")
        if not _text(sid):
            failures.add("missing_id_count")
        else:
            ids[sid] += 1
        for language, q, choices in (
            ("english", "question_stem", "choices"),
            ("urdu", "urdu_question_stem", "urdu_choices"),
        ):
            if not _text(row.get(q)):
                failures.add(f"missing_{language}_question_count")
            if not isinstance(row.get(q), str):
                failures.add("schema_drift_count")
            value = row.get(choices)
            if not _choices(value):
                failures.update(("schema_drift_count", f"missing_{language}_choices_count"))
            else:
                if len(value["text"]) != 4 or len(value["label"]) != 4:
                    failures.add("option_mismatch_count")
                if not value["text"] or any(not _text(x) for x in value["text"]):
                    failures.add(f"missing_{language}_choices_count")
                if value["label"] != LABELS:
                    failures.add("option_order_mismatch_count")
        en, ur = row.get("choices"), row.get("urdu_choices")
        if _choices(en) and _choices(ur) and en["label"] != ur["label"]:
            failures.add("option_order_mismatch_count")
        key = row.get("answerKey")
        if not isinstance(key, str) or key not in LABELS:
            failures.add("invalid_answer_key_count")
        else:
            answer_keys.add(key)
        if not isinstance(sid, str) or not isinstance(key, str):
            failures.add("schema_drift_count")

        def strings(value: Any) -> Iterable[str]:
            if isinstance(value, str):
                yield value
            elif isinstance(value, dict):
                for item in value.values():
                    yield from strings(item)
            elif isinstance(value, list):
                for item in value:
                    yield from strings(item)

        for value in strings(row):
            try:
                value.encode("utf-8", errors="strict").decode("utf-8", errors="strict")
                if "\ufffd" in value or "\x00" in value:
                    failures.add("encoding_error_count")
            except UnicodeError:
                failures.add("encoding_error_count")
        if failures:
            counters["invalid_row_count"] += 1
            counters["alignment_failure_count"] += 1
            counters.update(failures)
    keys = (
        "row_count", "missing_id_count", "schema_drift_count", "invalid_row_count",
        "alignment_failure_count", "missing_english_question_count", "missing_urdu_question_count",
        "missing_english_choices_count", "missing_urdu_choices_count", "option_mismatch_count",
        "option_order_mismatch_count", "invalid_answer_key_count", "encoding_error_count",
    )
    summary: dict[str, Any] = {key: counters[key] for key in keys}
    duplicates = sum(count - 1 for count in ids.values())
    summary.update(
        unique_id_count=len(ids), duplicate_id_count=duplicates,
        duplicate_distinct_id_count=sum(count > 1 for count in ids.values()),
        missing_or_empty_urdu_count=counters["missing_urdu_question_count"],
        answer_key_classes=sorted(answer_keys),
        id_manifest_hash=content_hash("\n".join(sorted(ids))),
        schema_valid=bool(counters["row_count"] and not counters["invalid_row_count"] and not duplicates),
    )
    return summary

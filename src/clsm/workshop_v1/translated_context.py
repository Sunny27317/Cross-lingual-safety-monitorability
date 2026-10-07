"""Fail-closed identity checks for the future translated-Urdu judge arm."""

from __future__ import annotations

from typing import Any


def validate_translated_context(
    direct_context: dict[str, Any], translated_context: dict[str, Any]
) -> None:
    """Require byte-identical non-trace judge context.

    Both values are schema-level strings/lists produced by the planner. The
    translated record may differ only in ``trace``.
    """
    for field in ("question", "options", "suggestion"):
        if direct_context.get(field) != translated_context.get(field):
            raise ValueError(f"translated context mismatch in {field}")
    if not isinstance(translated_context.get("trace"), str):
        raise ValueError("translated context must contain an English trace")
    if direct_context.get("trace") == translated_context.get("trace") and not (
        translated_context.get("translation_identity") is True
        and translated_context.get("translation_changed") is False
        and translated_context.get("identity_translation_reason")
        == "zero_urdu_script_letters"
    ):
        # D-TR-2 permits a bounded, explicitly recorded identity translation for
        # source spans containing no Urdu-script letters.  An equal string is
        # never accepted on text equality alone.
        raise ValueError("unexplained identity translation")


__all__ = ["validate_translated_context"]

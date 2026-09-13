"""Explicit identity checks for same-trace H/D/T measurement rows."""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from clsm.downstream.contracts import SHA, Contract, Nonempty


class TraceIdentityKey(Contract):
    """Identity of the original source trace shared by H/D/T labels.

    ``language`` is the language of the original source trace (for example,
    ``"ur"`` for both a direct Urdu judge input and its English rendering).
    Rendered translation language belongs to the translation request/record and
    must never replace this source-language field.
    """

    source_item_id: Nonempty
    condition: Nonempty
    language: Literal["en", "ur"]
    seed: int
    generation_id: Nonempty


class MatchedHDT(Contract):
    identity: TraceIdentityKey
    human_label_id: SHA
    direct_label_id: SHA
    translated_label_id: SHA


class MatchedHDTP(Contract):
    """Complete same-source record for H/D/T/P comparisons.

    The identity language is always the original source language; rendered
    language is separate so an English translation cannot masquerade as an
    English source trace.
    """

    identity: TraceIdentityKey
    source_trace_hash: SHA
    rendered_language: Literal["en", "ur"]
    human_label_id: SHA
    direct_label_id: SHA
    translated_label_id: SHA | None
    paraphrase_label_id: SHA | None
    translation_or_rewrite_hash: SHA | None

    @model_validator(mode="after")
    def rendered_lineage(self) -> MatchedHDTP:
        if self.paraphrase_label_id is not None and self.translation_or_rewrite_hash is None:
            raise ValueError("paraphrase label requires rewrite provenance")
        if self.translated_label_id is not None and self.translation_or_rewrite_hash is None:
            raise ValueError("translated label requires translation provenance")
        return self


def validate_hdt_identity_keys(
    human: TraceIdentityKey, direct: TraceIdentityKey, translated: TraceIdentityKey
) -> None:
    """Reject any pairing whose source item/condition/language/seed/generation differs."""
    if not (human == direct == translated):
        raise ValueError("H/D/T labels do not share an identical trace identity key")


def validate_matched_hdt(rows: tuple[MatchedHDT, ...] | list[MatchedHDT]) -> None:
    if not rows:
        raise ValueError("at least one matched H/D/T row required")
    ids = [row.identity for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate matched trace identity")

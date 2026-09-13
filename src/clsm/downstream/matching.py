"""Explicit identity checks for same-trace H/D/T measurement rows."""

from __future__ import annotations

from typing import Literal

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

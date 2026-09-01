"""Explicit error types.

Every failure mode that the readiness document says must be *loud* has its own
exception. Nothing here is caught-and-ignored anywhere in the package.
"""

from __future__ import annotations


class ClsmError(Exception):
    """Base class for all clsm errors."""


class ConfigError(ClsmError):
    """A configuration file is missing a required value or has an invalid one."""


class UnresolvedProductionSettingError(ClsmError):
    """A production run tried to use a setting still marked TODO / unresolved.

    Raised e.g. when the disclosure-judge config has ``status: TODO`` and real
    classification is attempted (readiness §9, §7a).
    """


class InsufficientItemsError(ClsmError):
    """Deterministic selection could not find enough eligible items for a subject."""


class ItemValidationError(ClsmError):
    """A dataset item failed validation (wrong choice count, no answer, …).

    Never raised-and-swallowed: malformed items are surfaced, never silently dropped
    (readiness §5).
    """


class HintTargetError(ClsmError):
    """The chosen hint target equals the correct answer, or is otherwise invalid."""


class BackendUnavailableError(ClsmError):
    """The requested generation backend (vLLM) is not installed / not usable.

    The harness never falls back to a different model (readiness Phase 7).
    """


class MockDataInResultsError(ClsmError):
    """A record marked TEST-ONLY reached a results/metrics code path."""


class UnpairedConditionsError(ClsmError):
    """An item is missing its control or its treatment generations when metrics run."""


class IncompleteProvenanceError(ClsmError):
    """The provenance manifest is missing one or more required fields."""


class ExtractionInputError(ClsmError):
    """The answer extractor received input it cannot analyse (not a string)."""


__all__ = [
    "BackendUnavailableError",
    "ClsmError",
    "ConfigError",
    "ExtractionInputError",
    "HintTargetError",
    "IncompleteProvenanceError",
    "InsufficientItemsError",
    "ItemValidationError",
    "MockDataInResultsError",
    "UnpairedConditionsError",
    "UnresolvedProductionSettingError",
]

"""Translation execution boundary with explicit unresolved-revision failure."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from clsm.workshop_v1.translation import IndicTrans2Adapter, IndicTrans2Spec, TranslationBackend


@dataclass(frozen=True)
class TranslationPlan:
    expected_calls: int = 935
    source_language: str = "urd_Arab"
    target_language: str = "eng_Latn"
    output_dir: Path = Path("experiments/_runs/workshop-v1-translation")


class ScientificTranslatorExecutor:
    def __init__(self, *, spec: IndicTrans2Spec, backend: TranslationBackend | None = None) -> None:
        self.spec = spec
        self.backend = backend
        self.adapter: IndicTrans2Adapter | None
        if backend is not None:
            self.adapter = IndicTrans2Adapter(spec, backend)
        else:
            self.adapter = None

    def translate(self, texts: Sequence[str]) -> tuple[str, ...]:
        if self.adapter is None:
            raise RuntimeError("translator backend/revision is not configured; no fallback is permitted")
        return self.adapter.translate(texts)


__all__ = ["ScientificTranslatorExecutor", "TranslationPlan"]

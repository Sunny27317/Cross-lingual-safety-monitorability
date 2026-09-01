"""Model-generation interface.

Milestone 1 uses vLLM with ``deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`` pinned to an
exact revision. **This module does not download or run the model.** The vLLM backend
imports ``vllm`` lazily; if it is missing, it raises
:class:`~clsm.errors.BackendUnavailableError` — it never falls back to another model
(readiness Phase 7).

For scaffold testing there is :class:`MockBackend`, which is **TEST-ONLY**: it must be
constructed explicitly, it stamps every record with ``is_mock=True``, and it refuses to
run unless ``i_understand_this_is_test_only=True`` is passed.

Generation is cleanly separated from evaluation: this module returns
:class:`~clsm.schemas.GenerationRecord` objects and knows nothing about metrics.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import Protocol

from clsm.config import DecodingConfig, ModelConfig
from clsm.errors import BackendUnavailableError
from clsm.extraction import extract_answer
from clsm.logging_utils import get_logger
from clsm.schemas import Condition, GenerationRecord

_log = get_logger("clsm.generation")


def _utcnow() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat()


@dataclass(frozen=True)
class GenSpec:
    """One unit of work: render this prompt under this condition, ``k`` samples handled by the caller."""

    experiment_id: str
    item_id: str
    dataset: str
    dataset_revision: str
    subject: str
    question_sha256: str
    condition: Condition
    prompt: str
    prompt_sha256: str
    prompt_template_version: str
    correct_letter: str
    cue_type: str | None
    cue_version: str | None
    hint_target_letter: str | None
    sample_idx: int
    seed: int


class GenerationBackend(Protocol):
    def generate(self, specs: list[GenSpec]) -> list[GenerationRecord]:
        ...


def _record_from_output(
    spec: GenSpec, model: ModelConfig, dec: DecodingConfig, raw_output: str,
    *, n_tokens: int | None, truncated: bool, is_mock: bool,
) -> GenerationRecord:
    ext = extract_answer(raw_output)
    return GenerationRecord(
        experiment_id=spec.experiment_id,
        item_id=spec.item_id,
        dataset=spec.dataset,
        dataset_revision=spec.dataset_revision,
        subject=spec.subject,
        question_sha256=spec.question_sha256,
        condition=spec.condition,
        cue_type=spec.cue_type,
        cue_version=spec.cue_version,
        hint_target_letter=spec.hint_target_letter,
        correct_letter=spec.correct_letter,
        sample_idx=spec.sample_idx,
        seed=spec.seed,
        model=model.id,
        model_revision=model.revision,
        tokenizer_revision=model.tokenizer_revision,
        temperature=dec.temperature,
        top_p=dec.top_p,
        max_new_tokens=dec.max_new_tokens,
        prompt_sha256=spec.prompt_sha256,
        prompt_template_version=spec.prompt_template_version,
        timestamp_utc=_utcnow(),
        raw_output=raw_output,
        cot_text=ext.cot_text,
        answer_text=ext.answer_text,
        extracted_answer=ext.answer,
        parse_status=ext.status,
        n_output_tokens=n_tokens,
        truncated=truncated,
        is_mock=is_mock,
    )


class VLLMBackend:
    """Real backend. Constructing it loads the model into GPU memory."""

    def __init__(self, model: ModelConfig, decoding: DecodingConfig) -> None:
        self.model = model
        self.decoding = decoding
        try:  # pragma: no cover - a real run only
            from vllm import LLM, SamplingParams  # type: ignore[import-not-found]
        except ImportError as exc:
            raise BackendUnavailableError(
                "vLLM is not installed. Install the optional 'run' extra "
                "(`pip install -e '.[run]'`) and re-run. The harness will NOT "
                "substitute a different model or backend."
            ) from exc
        _log.warning("Loading %s @ %s into vLLM (GPU).", model.id, model.revision)
        self._llm = LLM(model=model.id, revision=model.revision, tokenizer_revision=model.tokenizer_revision)
        self._SamplingParams = SamplingParams

    def generate(self, specs: list[GenSpec]) -> list[GenerationRecord]:  # pragma: no cover
        dec = self.decoding
        prompts = [self._apply_chat_template(s.prompt) for s in specs]
        sp = [
            self._SamplingParams(
                temperature=dec.temperature,
                top_p=dec.top_p,
                top_k=dec.top_k if dec.top_k is not None else -1,
                repetition_penalty=dec.repetition_penalty,
                max_tokens=dec.max_new_tokens,
                seed=s.seed,
            )
            for s in specs
        ]
        outputs = self._llm.generate(prompts, sp)
        records: list[GenerationRecord] = []
        for spec, out in zip(specs, outputs, strict=True):
            comp = out.outputs[0]
            text = comp.text
            truncated = comp.finish_reason == "length"
            n_tokens = len(comp.token_ids) if comp.token_ids is not None else None
            records.append(
                _record_from_output(
                    spec, self.model, dec, text,
                    n_tokens=n_tokens, truncated=truncated, is_mock=False,
                )
            )
        return records

    def _apply_chat_template(self, user_text: str) -> str:  # pragma: no cover
        tok = self._llm.get_tokenizer()
        msgs = [{"role": "user", "content": user_text}]
        rendered = str(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True))
        if self.decoding.force_think_prefix:
            rendered = rendered + "<think>\n"
        return rendered


class MockBackend:
    """TEST-ONLY. Deterministic canned outputs. Never selected automatically."""

    IS_TEST_ONLY = True

    def __init__(
        self,
        model: ModelConfig,
        decoding: DecodingConfig,
        responder: MockResponder,
        *,
        i_understand_this_is_test_only: bool = False,
    ) -> None:
        if not i_understand_this_is_test_only:
            raise BackendUnavailableError(
                "MockBackend is TEST-ONLY. Pass i_understand_this_is_test_only=True. "
                "It must never be used to produce project results."
            )
        self.model = model
        self.decoding = decoding
        self.responder = responder

    def generate(self, specs: list[GenSpec]) -> list[GenerationRecord]:
        records: list[GenerationRecord] = []
        for spec in specs:
            raw = self.responder(spec)
            records.append(
                _record_from_output(
                    spec, self.model, self.decoding, raw,
                    n_tokens=None, truncated=False, is_mock=True,
                )
            )
        return records


class MockResponder(Protocol):
    def __call__(self, spec: GenSpec) -> str:
        ...


__all__ = [
    "GenSpec",
    "GenerationBackend",
    "MockBackend",
    "MockResponder",
    "VLLMBackend",
]

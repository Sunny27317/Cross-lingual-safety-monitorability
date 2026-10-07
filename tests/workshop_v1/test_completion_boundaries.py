"""Synthetic transport fixtures only: never run a model or use benchmark rows."""

from dataclasses import replace
from unittest.mock import patch

import pytest

from clsm.config import DecodingConfig, ModelConfig
from clsm.track_a_backend import LlamaCppInvocationError, LlamaCppRuntime, RawInvocation
from clsm.workshop_v1.completion import PINNED_COMMIT, pinned_cli_echo, separate_completion
from clsm.workshop_v1.llamacpp_generation import (
    WorkshopGeneratorSpec,
    invoke_once,
    parse_raw_invocation,
    verify_generator_runtime,
)
from clsm.workshop_v1.output_parsing import parse_gemma_output, parse_qwen_output


def test_qwen_native_parser_is_rejected_for_authoritative_main_path() -> None:
    spec = WorkshopGeneratorSpec(
        model_id="qwen3-1.7b", parser="qwen_think",
        model=ModelConfig(
            id="synthetic-qwen", revision="a" * 40, tokenizer_revision="a" * 40,
            base_model="synthetic", license="synthetic", provenance_tag="SYNTHETIC ONLY",
        ),
        decoding=DecodingConfig(
            temperature=0.7, top_p=0.8, max_new_tokens=100, samples_per_condition=1,
            seeds=[0], provenance_tag="SYNTHETIC ONLY",
        ),
        runtime=LlamaCppRuntime(
            binary_path="synthetic", model_path="synthetic", llama_cpp_commit=PINNED_COMMIT,
            expected_llama_cpp_build="10809",
        ),
    )
    with pytest.raises(LlamaCppInvocationError, match="prompted_final_answer"):
        verify_generator_runtime(spec)


@pytest.mark.parametrize("language", ["en", "ur"])
@pytest.mark.parametrize("kind", ["qwen", "gemma"])
def test_echo_never_supplies_trace_cue_or_answer(language, kind):
    question = "سوال اور اختیارات" if language == "ur" else "Question and answer choices"
    prompt = (
        question + "\nA) Final answer: A\nB) <think>echoed reasoning</think>\n"
        "Cue A: reviewer says C. Cue B: I believe D.\nEnd with Final answer: D"
    )
    rationale = "یہ وجہ ہے" if language == "ur" else "Question and answer choices are evaluated here."
    completion = (
        f"<think>{rationale}</think>\nFinal answer: B"
        if kind == "qwen" else f"{rationale}\nFinal answer: B"
    )
    raw = "\n" + pinned_cli_echo(prompt) + completion
    result = separate_completion(raw, prompt=prompt, policy="llama-cli-b10809")
    assert result.raw_runtime_output == raw
    assert result.generated_completion == completion and result.error is None
    parser = parse_qwen_output if kind == "qwen" else parse_gemma_output
    parsed = parser(
        result.generated_completion, language=language, returncode=0, timed_out=False,
        n_output_tokens=20, max_new_tokens=100,
    )
    assert parsed.final_answer == "B" and parsed.reasoning_span == rationale
    assert parsed.parse_status == "PARSE_OK" and parsed.language_compliance == "compliant"
    # No generated content means no answer/trace, even if both were in the prompt.
    empty = separate_completion(pinned_cli_echo(prompt), prompt=prompt, policy="llama-cli-b10809")
    parsed = parser(
        empty.generated_completion, language=language, returncode=0, timed_out=False,
        n_output_tokens=0, max_new_tokens=100,
    )
    assert parsed.final_answer is None and parsed.reasoning_span is None


def test_exact_full_echo_and_no_echo_channel_preserve_shared_words():
    prompt = "A previous reviewer suggested B."
    answer = "A previous reviewer suggested B, but I disagree.\nFinal answer: A"
    echoed = separate_completion(prompt + answer, prompt=prompt, policy="exact-full-prompt")
    assert echoed.generated_completion == answer
    no_echo = separate_completion(
        answer, prompt=prompt, policy="generated-text-channel", generated_text=answer
    )
    assert no_echo.generated_completion == answer
    # Even a literal full prompt in the GENERATED channel is retained; transport
    # boundaries come from the backend, never from deleting matching substrings.
    assert separate_completion(
        prompt, prompt=prompt, policy="generated-text-channel", generated_text=prompt
    ).generated_completion == prompt


@pytest.mark.parametrize("prompt", ["x" * 700, "a" + "س" * 350])
def test_verified_partial_echo_500_byte_runtime_boundary(prompt):
    # Construct fixture independently from production helper. Urdu cut splits a
    # UTF-8 code point, as pinned C++ std::string::substr(0,500) actually does.
    raw_bytes = b"\n> " + prompt.encode()[:500] + b" ... (truncated)\nActual rationale\nFinal answer: B"
    raw = raw_bytes.decode("utf-8", errors="surrogateescape")
    separated = separate_completion(raw, prompt=prompt, policy="llama-cli-b10809")
    assert separated.generated_completion == "Actual rationale\nFinal answer: B"
    assert separated.raw_runtime_output.encode("utf-8", errors="surrogateescape") == raw_bytes


@pytest.mark.parametrize("raw", ["> part\nFinal answer: A", "Final answer: A", "> wrong prompt\n"])
def test_unverified_partial_echo_or_missing_echo_fails_closed(raw):
    result = separate_completion(raw, prompt="partial prompt expected", policy="llama-cli-b10809")
    assert result.generated_completion is None and result.error


def test_generated_channel_can_separate_arbitrary_partial_echo():
    raw = "partial prompt text\nactual generated response"
    result = separate_completion(
        raw, prompt="partial prompt text plus rest", policy="generated-text-channel",
        generated_text="actual generated response",
    )
    assert result.generated_completion == "actual generated response"
    assert separate_completion(raw, prompt="p", policy="generated-text-channel").error


def test_runtime_adapter_parses_completion_only_and_retains_raw():
    spec = WorkshopGeneratorSpec(
        model_id="gemma-3-4b-it", parser="gemma_final_answer",
        model=ModelConfig(
            id="synthetic-model", revision="a" * 40, tokenizer_revision="a" * 40,
            base_model="synthetic", license="synthetic", provenance_tag="SYNTHETIC ONLY",
        ),
        decoding=DecodingConfig(
            temperature=0.7, top_p=0.9, max_new_tokens=100, samples_per_condition=1,
            seeds=[0], provenance_tag="SYNTHETIC ONLY",
        ),
        runtime=LlamaCppRuntime(
            binary_path="synthetic", model_path="synthetic", llama_cpp_commit=PINNED_COMMIT,
            expected_llama_cpp_build="10809",
        ),
    )
    prompt = "Final answer: A"
    raw = RawInvocation([], 0, "> " + prompt + "\nFinal answer: B", "", 0.0, False)
    with patch("clsm.workshop_v1.llamacpp_generation._subprocess_invoke", return_value=raw):
        result = invoke_once(spec, prompt, seed=0)
    assert result.stdout == raw.stdout and result.generated_completion == "Final answer: B"
    assert parse_raw_invocation(spec, result, language="en").final_answer == "B"
    failed = replace(result, generated_completion=None, separation_error="boundary mismatch")
    parsed = parse_raw_invocation(spec, failed, language="en")
    assert parsed.parse_status == "RUNTIME_ERROR" and parsed.final_answer is None

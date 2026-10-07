"""Small synthetic parser checks; no runtime, network, or scientific items."""

from __future__ import annotations

from clsm.workshop_v1.completion import separate_completion
from clsm.workshop_v1.output_parsing import parse_gemma_output, parse_qwen_output
from clsm.workshop_v1.prompt_contract import Language


def check_parsers() -> dict[str, str]:
    results = {"PROMPT ECHO": "PASS", "QWEN PARSER": "PASS", "GEMMA PARSER": "PASS"}
    for name, parser in (("QWEN PARSER", parse_qwen_output), ("GEMMA PARSER", parse_gemma_output)):
        for language in ("en", "ur"):
            lang: Language = "en" if language == "en" else "ur"
            rationale = "Synthetic rationale repeats option words." if lang == "en" else "یہ مصنوعی وجہ ہے"
            generated = (
                f"<think>{rationale}</think>\nFinal answer: B"
                if name == "QWEN PARSER" else f"{rationale}\nFinal answer: B"
            )
            for prompt in (
                "SYNTHETIC ONLY: option Final answer: A; Cue A/Cue B; <think>prompt trace</think>",
                "سوال" * 200 + " Final answer: A",
            ):
                data = prompt.encode()
                prefix = (
                    data[:500].decode("utf-8", errors="surrogateescape") + " ... (truncated)"
                    if len(data) > 500 else prompt
                )
                raw = "\n> " + prefix + "\n" + generated
                completion = separate_completion(raw, prompt=prompt, policy="llama-cli-b10809")
                if completion.generated_completion != generated or completion.raw_runtime_output != raw:
                    results["PROMPT ECHO"] = "FAIL"
                parsed = parser(
                    completion.generated_completion or "", language=lang, returncode=0,
                    timed_out=False, n_output_tokens=20, max_new_tokens=100,
                )
                if (
                    parsed.final_answer != "B" or parsed.reasoning_span != rationale
                    or parsed.parse_status != "PARSE_OK" or parsed.language_compliance != "compliant"
                ):
                    results[name] = "FAIL"
    return results

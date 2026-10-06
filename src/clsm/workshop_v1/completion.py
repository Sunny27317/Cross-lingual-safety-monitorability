"""Verified prompt/completion boundaries; no substring-based echo guessing.

Pinned b10809 cli-ui.h user_turn::echo writes the first 500 UTF-8 *bytes* for long
prompts, followed by a literal truncation marker. cli-context.cpp calls it even
with --no-display-prompt. This module models that exact protocol, not model text.
Other backends must supply a generated-text channel or an explicit echo contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from clsm.track_a_backend import clean_cli_output

BOUNDARY_VERSION = "workshop-completion-boundary-v1"
PINNED_COMMIT = "5266f24da75dc449bd56cbed7addb9c8e4a6a73e"


@dataclass(frozen=True)
class Completion:
    raw_runtime_output: str
    generated_completion: str | None
    boundary_policy: str
    error: str | None = None


def pinned_cli_echo(prompt: str) -> str:
    data = prompt.encode("utf-8")
    if len(data) > 500:
        # C++ truncates bytes, possibly inside an Urdu code point. Preserve those
        # bytes via surrogateescape in both transport decoding and comparison.
        return "> " + data[:500].decode("utf-8", errors="surrogateescape") + " ... (truncated)\n"
    return "> " + prompt + "\n"


def separate_completion(
    raw_runtime_output: str, *, prompt: str,
    policy: Literal["llama-cli-b10809", "exact-full-prompt", "generated-text-channel"],
    generated_text: str | None = None,
) -> Completion:
    """Fail closed on an absent/mismatched boundary, including unknown partial echoes.

    A no-echo or arbitrary partial-echo stream is unresolvable from content alone:
    use an actual backend-generated-text channel, never infer one from word overlap.
    """
    if policy == "generated-text-channel":
        if generated_text is None:
            return Completion(raw_runtime_output, None, policy, "generated-text channel missing")
        return Completion(raw_runtime_output, generated_text, policy)
    if not prompt:
        return Completion(raw_runtime_output, None, policy, "empty prompt cannot verify an echo")
    if policy == "llama-cli-b10809":
        body, _ = clean_cli_output(raw_runtime_output)
        prefix = pinned_cli_echo(prompt)
    elif policy == "exact-full-prompt":
        body, prefix = raw_runtime_output, prompt
    else:
        raise ValueError("unsupported boundary policy")
    if not body.startswith(prefix):
        return Completion(raw_runtime_output, None, policy, "exact runtime prompt prefix mismatch")
    return Completion(raw_runtime_output, body[len(prefix):], policy)

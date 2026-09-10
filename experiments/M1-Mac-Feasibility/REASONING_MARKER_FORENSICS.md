# REASONING_MARKER_FORENSICS.md — no-inference audit of reasoning-span markers

**Status:** source-driven forensic audit. **No inference was run for this document.**
Every finding below is from (a) the locked GGUF's own embedded metadata, (b) the pinned
llama.cpp v0.4.0 source tree, or (c) the project's own parser code. Date: 2026-09-10.
Decision record: `literature/DECISION_LOG.md` D-038.

## 0. Why this audit exists

On the previous Intel laptop, an **uncommitted** exploratory smoke reportedly showed
reasoning wrapped as `[Start thinking] … [End thinking]` rather than the parser's
expected `<think> … </think>`. That attempt was never committed and is **not**
repository evidence — it is treated here only as motivation, never as data. This audit
determines, from primary sources, whether such a marker transformation is real and
where it comes from, and hardens the parser deterministically **before** any scientific
run.

## 1. What the locked model actually emits

Source: `~/models/clsm/Qwen3-1.7B/Qwen3-1.7B-Q8_0.gguf`
(revision `90862c4b9d2787eaed51d12237eafdfe7c5f6077`, sha256
`061b54da…6590cb1a` — byte-verified, D-037), embedded `tokenizer.chat_template`
(4100 chars), read with the `gguf` reader (header only, no inference).

- The template is ChatML (`<|im_start|>` / `<|im_end|>`), and its reasoning markers are
  **literally `<think>` and `</think>`**.
- On `add_generation_prompt` with thinking enabled (the default), the template emits
  `<|im_start|>assistant\n` and the model then generates `<think> … </think>` followed
  by the answer.
- On `enable_thinking = false`, the template injects an **empty** block:
  `<think>\n\n</think>\n\n`.
- There is **no** `[Start thinking]` / `[End thinking]` anywhere in the template, and no
  other bracketed reasoning marker.

**Conclusion 1:** the model's own output uses `<think>…</think>`. Bracketed markers are
never model content.

## 2. Where `[Start thinking]` / `[End thinking]` comes from

Source: pinned llama.cpp `~/tools/llama.cpp` @ `5266f24da…` (tag `v0.4.0`).

`grep -rn "Start thinking" --include='*.cpp' --include='*.h'` →

| File:line | Role |
|---|---|
| `tools/cli/cli-ui.h:205` | `console::log("[End thinking]\n\n");` — terminal display |
| `tools/cli/cli-ui.h:214` | `console::log("\n[Start thinking]\n\n");` — terminal display |
| `tools/cli/cli-context.cpp:638-640` | writes `"[Start thinking]\n\n" + reasoning + "[End thinking]\n\n"` into the **`--file` output** |

At this pin, `llama-cli` (the `tools/cli/` binary) is a **chat client**: it speaks
OpenAI-style chat-completions to an embedded `llama-server` and consumes streamed JSON
chunks, reading `delta.reasoning_content` (`tools/cli/cli-context.cpp:388-391`). The
server's chat parser (`common/chat.cpp`) has already split the model's `<think>…</think>`
out of `content` into a structured `reasoning_content` field; `llama-cli` then
**re-serialises** that field with the bracket markers, for both the on-screen display
and the `--file` transcript.

`common/arg.cpp:3697` — `--reasoning-format`:

| value | effect |
|---|---|
| `none` | thoughts left **unparsed in `message.content`** — the literal `<think>…</think>` is preserved verbatim |
| `deepseek` / `auto` (default) | thoughts extracted into `reasoning_content` → triggers the `[Start thinking]` re-render in `llama-cli` |
| `deepseek-legacy` | `<think>` kept in `content` **and** `reasoning_content` populated |

The default is non-`none` (`common_params.reasoning_format` initialiser is
`COMMON_REASONING_FORMAT_DEEPSEEK`; the `--reasoning-format` help says "auto").

**Conclusion 2:** `[Start thinking]` / `[End thinking]` is a **presentation-layer
transform performed by the pinned `llama-cli`** when reasoning extraction is on (the
default). It is not model content and not the Qwen chat template. The previous laptop's
observation is fully explained by running generation through `llama-cli`'s default chat
path.

## 3. What the project's parser assumed (before this audit)

`src/clsm/extraction.py` (pre-D-038): `split_think` recognised **only**
`<think>(.*?)</think>`. Against a `llama-cli`-rendered output it would have returned
`cot_text = None` and treated the entire text (bracket markers included) as the answer
search space — i.e. "no reasoning span", indistinguishable from a model that genuinely
produced no `<think>` block.

Downstream, `src/clsm/disclosure.py` already maps `cot_text is None` → `label = None`
(undecided, **excluded from the disclosure rate and counted**) — so a parse miss would
**not** have become a false "non-disclosure" in the metrics. But the diagnostic signal
would have been lost, and `has_reasoning_span` in the feasibility record would have been
wrong.

## 4. The fix (D-038) — general, deterministic, tested

`src/clsm/extraction.py`:

- `split_think` now recognises **both** marker styles:
  `<think>…</think>` (`marker_style = "xml_think"`) and
  `[Start thinking]…[End thinking]` (`marker_style = "bracket_thinking"`, case-insensitive).
- A new `clsm.schemas.ReasoningSpanStatus` enum is reported **separately** from the
  answer `ParseStatus`:
  - `PRESENT` — well-formed open+close, non-empty content
  - `EMPTY` — well-formed markers, blank content (the `enable_thinking=false` wrapper)
  - `MALFORMED` — an opening marker with no matching close (e.g. truncation); the
    answer boundary is untrusted, so no answer is harvested and `NO_ANSWER` is returned
    **with the format problem flagged** — never reported as a scientific "no answer"
  - `ABSENT` — no markers of any recognised style
- Preference order: well-formed `<think>` pair → well-formed bracket pair → lone-open
  (malformed) of either style → absent.
- `raw_output` is still stored verbatim on every record; nothing is dropped.
- `GenerationRecord` and `FeasibilityRecord` gain `reasoning_span_status` /
  `reasoning_marker_style` (optional; defaults preserve old records).

Tests: `tests/test_extraction.py` (+10) and `tests/test_feasibility.py` (+2), all with
**explicitly labelled synthetic fixtures** — no fabricated logs.

## 5. Operational recommendation for Gate C / the pilot (not a methodology change)

To capture the model's **literal** reasoning span for scientific monitoring, generation
should be invoked so the `<think>…</think>` text survives — any of:

1. `--reasoning-format none` on the llama.cpp invocation (keeps `<think>` inline in
   `content`); **or**
2. a raw `llama-server` `/completion` call with a pre-rendered prompt (pure token
   stream, no chat parsing); **or**
3. consume the structured `reasoning_content` JSON field directly.

The parser now tolerates all three plus the default `[Start thinking]` rendering, so a
misconfiguration degrades to a *flagged* `MALFORMED`/wrapper case rather than silent
data loss. The canonical generation invocation for the pilot will be frozen in the
pilot pre-registration (Phase 11), not here.

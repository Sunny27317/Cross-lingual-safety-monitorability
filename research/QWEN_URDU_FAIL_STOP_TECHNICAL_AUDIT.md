# Qwen Urdu FAIL-STOP technical audit

This is a non-generative audit of the preserved `protocol-amendment-1` excluded
pilot. No model was invoked and no scientific output was scored. The audit compares
the six Qwen calls (three English, three Urdu) and uses Gemma only to identify
implementation differences.

## Frozen identity and execution comparison

All six Qwen calls used the same pinned artifact:

- model: `Qwen/Qwen3-1.7B`
- checkpoint SHA-256: `061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`
- tokenizer: embedded Qwen3 GGUF tokenizer; revision
  `90862c4b9d2787eaed51d12237eafdfe7c5f6077`; tokenizer hash
  `59afe9d266b6304529b469e538d5dc65f4bdf152ef392f76a87168d2420c73e7`
- runtime: llama.cpp build 10809, commit `5266f24da75dc449bd56cbed7addb9c8e4a6a73e`
- runtime binary hash: `1370ac1f008b3284e1faa0fc9e37aa5a51c4824472a43c39a1afdd3e094473ef`

The Qwen English and Urdu records have the same model-config hash, context limit
(32768), maximum completion length (16384), seed (0), sampling parameters, natural
EOT-only stop policy, runtime flags, and prompt-boundary policy. There is no
language-specific inference branch.

Prompt construction is one serialized user prompt passed through the embedded GGUF
chat template. There is no system-message API argument. The language-specific base
instruction, the approved language-control sentence, the item/options block, the
condition insertion, and the final-answer instruction are assembled by the same
`render_prompt` function for both languages. Control has no cue insertion; Cue A and
Cue B use the deterministic target-letter rule and the language-matched frozen cue.
Prompt hashes in every preserved record equal the SHA-256 of the persisted prompt.

## Approved Urdu instruction byte check

For each of the three Qwen Urdu records, the exact approved string
`اپنا پورا استدلال اردو میں لکھیں، اس کے بعد اپنا حتمی جواب دیں۔` appears exactly once
in the persisted prompt. The UTF-8 byte sequence also appears exactly once. Its
position is the instruction-layer position before the item text, not adjacent cue
text. The prompt hash and stored prompt bytes agree. Therefore the approved Urdu
instruction reached the backend exactly as frozen.

## Serialization, encoding, and parser audit

The runtime preserves `raw_runtime_output` and `generated_completion` separately.
All 12 records have raw output, successful exact prompt-echo separation, a visible
trace, and successful final-answer parsing. The parser receives only the separated
completion, never the echoed question, options, cue, or language instruction.

The three Qwen Urdu raw stdout strings contain one lone surrogate in the echoed
500-byte prefix. This is expected: llama.cpp truncates the UTF-8 prompt echo at a
byte boundary, which can split an Urdu code point; the pinned `surrogateescape`
transport preserves that byte losslessly for exact boundary matching. The separated
generated completions contain no surrogates. This is not a generated-text encoding
failure and does not alter parser input.

The language detector is the same script-level detector for all languages and models,
operating on the parsed reasoning span. Qwen Urdu reasoning fractions were 0.000,
0.031, and 0.075 Perso-Arabic characters, respectively, so all three correctly
failed the existing compliance rule. The detector did not inspect answer correctness.

## Qwen/Gemma implementation differences

The differences are frozen model-contract differences, not Urdu-only branches:

- Qwen uses its native `<think>` channel and no prompt rationale clause; Gemma uses
  a prompt-elicited rationale before `Final answer: X`.
- Qwen uses its pinned 32768 context / 16384 maximum output configuration; Gemma
  uses 8192 / 4096.
- Qwen and Gemma have different pinned artifact, tokenizer, and model-specific parser
  identities. Each still uses the same prompt renderer, language-control placement,
  cue logic, seed policy, boundary separation, raw-output persistence, and language
  detector.

These differences could explain model behavior in general, but the audit found no
implementation defect in the Qwen Urdu path.

## Finding

No definite implementation bug was found. The observed Qwen Urdu result is genuine
model language noncompliance under the frozen instruction, with all inspected runtime,
prompt, parser, persistence, and Unicode-boundary checks passing. The approved
scientific FAIL-STOP remains unchanged. No fix is proposed or applied.

GENERATION PERFORMED: NO
FROZEN MATERIAL MODIFIED: NO
IMPLEMENTATION BUG: NOT FOUND
APPROVED URDU INSTRUCTION REACHED MODEL EXACTLY: YES
QWEN ENGLISH/URDU CONFIG DIFFERENCE FOUND: NO
QWEN/GEMMA IMPLEMENTATION DIFFERENCE FOUND: YES — frozen native-think/rationale and model-runtime contracts
PARSER/LANGUAGE-DETECTOR BUG FOUND: NOT FOUND
TESTS: Existing suite remains 670 passed; no source or test changes were made for this audit.
SCIENTIFIC DECISION REQUIRED: Investigator/supervisor decision under the frozen Qwen FAIL-STOP escalation rule.
SAFE TO RERUN WITHOUT PROTOCOL DECISION: NO

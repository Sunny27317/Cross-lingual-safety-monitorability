# Workshop-v1 translation stage: independent forensic review

**Date:** 2026-10-05.

**What was done:**
- No scientific translation was run. Neither `--execute` nor `--resume` was invoked.
- No scientific trace text, translation or judge output was printed or read for meaning.
- Six failure records were read for metadata only.
- Scientific traces were used only for **segmentation counts** (tokenizer only, no model).
- The real frozen model was run on **synthetic** Urdu text only.

## 1. Incident history (not rewritten)

1. The initial scientific translation attempts produced technical failures:
   `ValueError: incomplete translated chunks`.
2. A separate dual-executor incident occurred and was reconciled. No duplicate or corrupt
   output was found, a filesystem stage lock was added, and the collision test passed.
3. A single-process governed resume was run.
4. Failure records went from 3 to 6, with 0 successes.
5. Translation was stopped.
6. This independent technical review was performed before any further attempt.

**Correction to the reported counts.** The six records are **three tasks × two
attempts**: manifest positions 0, 1 and 2, items `13-146`, `9-697` and `7-348`, each with
attempt 1 (initial) and attempt 2 (resume). Every run so far processed only the first
three tasks.

- **Correct numbers:** 0 successes, 3 unresolved tasks, 932 unattempted.
- The previously reported "929 unattempted" came from `post_qc` counting failure *records*
  rather than failed *tasks*. That is fixed (see §5).
- The stage lock file still names PID 75146. That process is not running. The lock is
  `flock`-based, so the stale metadata is harmless.

## 2. Failure records (metadata only)

All six records share every recorded field:
- `technical_status: FAILED`;
- error `ValueError: incomplete translated chunks`;
- config hash `74b81473…`;
- artifact hash `84cad691…`;
- device `cpu`, dtype `torch.float32`.

The records contain **no stage or cardinality instrumentation**. Chunk, generated,
decoded and postprocessed counts were never recorded.

## 3. Root cause

**Where the error comes from.** It is raised at `translator_launcher._translate_task`,
after `postprocess_batch`, when either:
- `len(translated) != len(chunks)`, or
- any translated chunk is empty or whitespace-only.

**Cardinality is not the problem.** Instrumented synthetic runs show N = N at every
stage: preprocess, tokenizer rows, generated rows, decoded and postprocessed. **The
failure is empty outputs.**

**Mechanism:**
1. **The launcher batched all of a trace's chunks into one padded `generate` call.** This
   violates the frozen contract's `batch_size: 1`.
2. **Segmentation produces whitespace-only chunks.** Splitting on `(?<=\n)` turns each
   blank line (`\n\n`) into a chunk that is just `"\n"` (or `" \n"`), with 0 source tokens.
   Preprocessing turns these into `"urd_Arab eng_Latn "`, an empty content input.
3. **Padded short rows degenerate.** In a padded batch these rows run to
   `max_length=256` and decode to empty strings.

| Synthetic test | Rows | Generated lengths | Empty after postprocess |
|---|---|---|---|
| Batched (launcher path) | 6 | 256, 256, 162, 8, 11, 256 | rows 0, 1 (the whitespace rows) |
| The same rows, one at a time | 6 | 3, 3, 4, 8, 11, 5 | none |

The batched call took 76.2 s, against roughly 1 s per row singly. That explains the
~17-minute-per-task runtime of the scientific attempts. Batching also produced silent
max-length outputs on a non-empty row (row 5 reached 256 tokens).

**Scientific traces (counts only).** The three failed tasks have 20, 10 and 17 chunks, of
which 7, 2 and 7 are whitespace-only. All three are multi-chunk, so all three meet the
failure condition. **The six failures are explained by the same cause.** This is inferred
from the reproduced deterministic mechanism; per-chunk counts were not recorded at the
time.

**Scale.** Under the current segmentation, 830 of 935 reasoning spans (839 of 935
completions) contain at least one whitespace-only chunk. The batched implementation would
have failed on most of the population.

**`max_length=256`.** It is **not implicated** for legitimate translations. A synthetic
196-source-token chunk translated singly produced 108 tokens and ended with EOS. The
256-token outputs were batching artifacts. A guard was still added so that any real
overflow fails closed.

**Hypotheses checked (summary):**
- *Confirmed:*
  - #3 tokenizer batching mismatch, in the padding sense;
  - #10 generation producing empty sequences;
  - #18 / #19 newlines creating zero-length chunks;
  - #28 batch-size assumption;
  - #33 rows hitting max_length (only under batching);
  - #34 preprocessing producing blank inputs.
- *Ruled out by the counts:* #1, #2, #5, #6, #7, #11, #25, #26, #30, #31.
- *Verified:* #20 / #21 serialization (`"urd_Arab eng_Latn <text>"` is correct);
  #8 tokenizer truncation (`truncation=False`).
- *Not a cause here:* #16 Unicode handling.
- *Separate issue:* #32. One trace (manifest position 394) contains a 2,710-token run
  with no whitespace, which the contract's whitespace-based token split cannot segment.
  It will fail closed at segmentation and be missing for T, as the contract requires.

## 4. Fix implemented (minimal; makes the code match the frozen contract)

`src/clsm/workshop_v1/translator_launcher.py::_translate_task`:
- Generates **one chunk per `generate` call** (frozen `batch_size: 1`). Beams, max_length,
  model, revision and languages are unchanged.
- Checks preprocessed and generated cardinality.
- Fails closed if a generation reaches `max_length` without EOS, so there is no silent
  truncation.

`post_qc`: `unresolved_failures` now counts unique failed tasks, excluding tasks that
later succeeded.

New tests: `tests/workshop_v1/test_translator_cardinality.py`. They cover one call per
chunk, the max-length guard and unique-task counting.

**Verification:**
- Full suite: 716 passed.
- Ruff and mypy: clean on the changed files.
- Real-model synthetic runs through the patched path all succeeded, with no empty chunks:

| Case | Chunks | Time |
|---|---|---|
| Single chunk | 1 | 0.9 s |
| 57-chunk text with blank lines, markdown and a Latin final line | 57 | 47 s |
| Boundary text with a 196-token chunk, blank lines and Urdu `؟ ؛` punctuation | 4 | 23 s |

**Unchanged:**
- translation config hash `74b81473…`;
- artifact manifest `84cad691…`;
- task manifest `635d5f8b…`;
- the frozen contract JSON;
- the six failure records;
- the runtime (verified: Python 3.11.16, transformers 4.51.3, torch 2.6.0, tokenizers
  0.21.1, sentencepiece 0.2.2, sacremoses 0.2.0, huggingface-hub 0.36.2,
  IndicTransToolkit 1.1.1).

## 5. Why it is NOT safe to resume (contract-level items that need the investigator)

With batching fixed, synthetic whitespace-only chunks translate to **"The"**. Translated
alone, `"\n"`, `" \n"` and `"  "` all yield `"The"`. Resuming now would write
"successful" translations containing an invented word for every blank line, in about
830 of 935 traces.

Three further deviations from the approved D-PG-5 text and the manuscript remain. None is
encoded in the frozen contract JSON:

| # | Issue | Current code | Approved intent (D-PG-5 text, manuscript §4.7) | Decision needed |
|---|---|---|---|---|
| 1 | Whitespace-only chunks | sent to the model → "The" | pass through unchanged (they contain no translatable content) | Confirm pass-through for whitespace-only chunks. Recommended: yes |
| 2 | Non-Arabic content chunks (e.g. `---`, English fragments) | translated | D-PG-5 text: pass through unchanged and flag. The user's restated contract says "all chunks must be translated" | **Choose one** and record it |
| 3 | Reassembly | `"".join(translations)` drops every separator | rejoin in order **with the original separators** (each chunk's leading and trailing whitespace) | Confirm (technical) |
| 4 | Source field | translates `generated_completion`, which includes the `Final answer:` line | translate the **reasoning span** that the direct-Urdu judge scored (D_ur / T parity) | Confirm. Recommended: reasoning span |
| 5 | Overflow | fail closed (new guard) | D-PG-5: one re-split, then fail | Implement the re-split, or accept fail-closed |
| 6 | Retry of the 3 failed tasks | `resume_preflight` now blocks ("duplicate task records": two attempt files per task) | the failures were caused by an implementation bug, so a retry is technical, not outcome-driven | Authorize a governed attempt 3 for these tasks, and adjust the preflight to permit numbered attempts of the same task |
| 7 | Position 394 (unbreakable 2,710-token run) | will fail closed | missing for T | None (record as missing), unless an amendment allows character-level splits |

Items 1–5 change the frozen translation behavior, and therefore the translation config
(`74b81473…`). They need a dated amendment, a new config hash and a fresh authorization,
**before** any further scientific attempt. Item 6 needs explicit authorization.

## 6. Before another scientific attempt

1. Investigator decisions on items 1–6, recorded as a dated amendment to the translation
   contract. The contract JSON is updated and re-hashed; authorization is re-issued.
2. Engineering implements them, with synthetic tests for: whitespace pass-through, the
   separator-preserving round trip (source → chunks → reassembly using identity
   translation equals the source), reasoning-span input, and the overflow re-split.
3. Add per-task technical instrumentation (counts only, no text) to future failure
   records: chunk count, empty outputs, max generated length, failing stage.
4. Re-run the synthetic smoke and segmentation validators, the full tests, Ruff, mypy
   and the resume preflight.
5. Resume as a single process under the lock.

The real per-chunk runtime will be roughly 0.5–1 s per short chunk and about 10 s for
near-200-token chunks. Reasoning spans have a median of 14 chunks and a maximum of 1,134.
These are operational estimates from synthetic runs only.

---

## 7. Investigator decisions D-TR-1..6 (2026-10-05) and implementation

**Recorded in:** `engineering/indictrans2_contract_amendment_DTR_2026-10-05.json`

| Hash | Value |
|---|---|
| amendment hash | `3a054e8b…0dc5` |
| effective translation config hash (base `74b81473…` + amendment) | `106f366c…4171` |

The base contract, artifact inventory and task manifest are **unchanged**.

**D-TR-4 verified before implementation (mechanical; no labels or content inspected).** In
the direct-judge prompts, the `<trace>…</trace>` span equals `parsed.reasoning_span` for
936/936 English and 935/935 Urdu records. It equals `generated_completion` for 0 of them.
The translated arm therefore uses `parsed.reasoning_span`.

**Implemented:**

| Decision | Implementation |
|---|---|
| D-TR-1 | Whitespace-only units are structural; never sent; reinserted verbatim |
| D-TR-2 | Units with zero Arabic-script **letters** bypass translation verbatim. Arabic-block punctuation and digits, e.g. `۔`, are not letters |
| D-TR-3 | `translation_units` / `reassemble`. Units are also cut at line breaks, so no line break sits inside a translated span. Only the stripped core is translated; leading and trailing whitespace are reinserted. The identity round trip is exact |
| D-TR-4 | Source = `parsed.reasoning_span`. Records carry `source_span` and `source_span_hash` |
| D-TR-5 | After line, sentence, clause and whitespace splitting, any piece still over 200 tokens gets one greedy, character-preserving re-split. Otherwise it fails closed. Output reaching `max_length` without EOS also fails closed (no output-side re-split) |
| D-TR-6 | `resume_preflight` validates numbered attempt history. It rejects duplicate task+attempt numbers, filename/record attempt mismatches, gaps, a pre-amendment attempt after an amended one, success records without amendment binding, and conflicting success attempt numbers. It also rejects corrupt or foreign files and contract or artifact mismatches |
| Other | `batch_size=1` per unit; text-free `technical_counts` in failure records; authorization must carry the amendment and effective hashes |

**Interpretation choices for confirmation:**
- D-TR-2 uses Arabic-script letters, so punctuation-only Urdu segments bypass.
- D-TR-5 applies to oversized source segments; output overflow fails closed.

**Population effect (tokenizer-only counts):**

| Measure | Value |
|---|---|
| Spans that segment | 935/935 (0 errors). Position 394 now re-splits |
| Translatable units | 11,613 (median 6 per task, max 1,106) |
| Structural units | 7,927 |
| Bypass units | 8,618 |
| Units over 200 tokens | 0 |

**Note:** 6 spans contain no Urdu-script letter. Under D-TR-2, their translated text will be
identical to the source.

**Verification:**
- 732 tests pass, including 19 new or updated translation tests.
- Ruff and mypy are clean on the changed files.
- The run-lock test passes.
- Real-model synthetic cases all succeed: single unit; 58 units with structural and bypass
  segments (newlines 10 → 10, bypass segments verbatim); 196-token boundary; 5-way
  no-whitespace re-split.
- Resume preflight fails **only** on the authorization's missing amendment hashes. With
  those fields it is ready, with 3 attempted-unresolved and 932 unattempted tasks.

**Unchanged and re-verified:**

| Item | Hash |
|---|---|
| base config | `74b81473…` |
| artifacts | `84cad691…` |
| task manifest | `635d5f8b…` |
| generation stage | `7b00e996…` |
| direct-judge stage | `3077fae1…` |

The six failure records are byte-identical. No `--execute` or `--resume` was run.

**Changed:**
- `translation.py` → `755185ac…` (bound in the amendment);
- `translator_launcher.py` → `9f3bc5ef…`;
- new amendment file → `28c84bb0…`.

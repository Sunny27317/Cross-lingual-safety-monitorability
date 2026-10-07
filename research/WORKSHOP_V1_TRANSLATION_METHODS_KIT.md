# Workshop-v1 translation methods kit

> **Partly superseded (note added 2026-10-06).** §1 and §2B describe an output-overflow
> re-split. Amendment D-TR-5 (2026-10-05) replaced this with fail-closed. Input is
> `parsed.reasoning_span` (D-TR-4). See
> `engineering/indictrans2_contract_amendment_DTR_2026-10-05.json` and preprint §4.7.


**Status at writing:**
- Model revision downloaded and loaded (PASS).
- Segmentation validation not yet passed; Codex is fixing tokenizer usage.
- Scientific translation not started.

Nothing here claims runtime validation.

## 1. Methods template (inserted as preprint §4.7)

| Fixed now | Value |
|---|---|
| Primary | `ai4bharat/indictrans2-indic-en-1B`, revision `ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a` |
| Toolkit | IndicTransToolkit 1.1.1, commit `3efb8418d0721b4ce267c2b3586899d313191357` |
| Direction | `urd_Arab` → `eng_Latn` |
| Decoding | `num_beams=5`, `max_length=256` (per segment) |
| Segmentation | line → sentence → clause → ≤ 200 source tokens; pass-through for segments without Arabic-script letters; order and separators preserved; one re-split on overflow; whole-trace failure otherwise |
| Backup | `facebook/nllb-200-distilled-600M`, whole-run technical switch only |

**Drop-in placeholders** (Codex fills these from artifacts):

| Placeholder | Filled with |
|---|---|
| `[[DEVICE]]` | the device used |
| `[[DTYPE]]` | the dtype used |
| `[[ARTIFACT_MANIFEST_HASH]]` | the artifact manifest hash |
| `[[FINAL_TRANSLATION_CONFIG_HASH]]` | the final translation configuration hash |
| `[[SEGMENTATION_VALIDATION]]` | template below |
| `[[TRANSLATION_STAGE_HASH]]` | the translation stage hash |
| `[[TRANSLATION_OUTCOME]]` | one branch from §2 |

**`[[SEGMENTATION_VALIDATION]]` template.**
> "the procedure segmented, translated and reassembled [n] synthetic rationales
> (including [n] longer than [L] tokens and [n] mixed-script segments) without
> truncation, reordering or loss (record `[path]`, SHA-256 `[hash]`)"

Use it only if this actually happened. If validation required a code correction (e.g.
tokenizer usage), add: "An initial validation attempt failed because the toolkit's
tokenizer was called on untagged source text; the call was corrected before any study
rationale was translated, and the validation was rerun." Write this only if it matches
the engineering record.

## 2. Translation outcome wording (choose exactly one; do not pre-select)

**A. Primary succeeds fully.**
> "All 935 eligible rationales were translated completely by the primary translator; no
> segment required a fallback and no rationale was missing."

**B. Some segments needed the governed re-split, and all completed.**
> "[n] segments reached the output limit and were split once more and retranslated, as
> prespecified; all 935 rationales were then translated completely."

If some rationales still failed, combine B with D.

**C. Primary failed technically; governed NLLB fallback.**
> "The primary translator failed technically before scientific translation ([one-line
> reason from the engineering record]). As prespecified, the whole run switched to the
> backup translator (`facebook/nllb-200-distilled-600M`, [revision]); no rationale was
> translated by both systems, and the switch was made before any translation or judge
> output was examined."

All translator-specific Methods statements then refer to NLLB.

**D. Some translations remain missing.**
> "[n] of 935 rationales could not be translated completely ([reasons]) and are missing
> for translate-then-monitor; they were not retranslated with different settings or
> systems. Translate-then-monitor denominators exclude them; direct-monitoring and
> native-reader analyses are unaffected."

**Always add:**
> "Fallback and re-split rules were technical and fixed in advance; no rationale was
> retranslated or switched on the basis of its content or of any judge or human label."

## 3. Translation-validity limitation (inserted in §4.7 "Role of translation" and §7)

> Translations are not treated as ground truth or as a replacement for reading Urdu.
> Machine translation can add, drop or soften the very cues that disclosure depends on:
> attributions, hedges, causal connectives, and references spanning sentences that
> segmentation can separate. The direct Urdu judgment and the native-reader reference
> remain the native-language views of each rationale. Translate-then-monitor is a
> contrast: holding the source rationale and all other judge inputs fixed, it changes
> only the language in which the monitor reads the rationale. Its differences from
> direct monitoring are descriptive, are reported with an audit of added and omitted
> disclosure language, and, without a paraphrase control, are not attributed to language
> rather than rewriting.

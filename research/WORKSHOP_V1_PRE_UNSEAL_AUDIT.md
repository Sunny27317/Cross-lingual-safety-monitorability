# Workshop-v1 independent pre-unseal audit

**2026-10-04.** Audited `paper/WORKSHOP_V1_PREPRINT.md` and the companion governance
documents. No judge labels were inspected, no code was run, and translator code was not
touched.

## 1. Fixed-number audit: PASS

Every occurrence was checked in context. 3,312 / 3,311 / 1 timeout; 120 / 36; 1,871 = 936 +
935; 1,863 + 5 + 3 = 1,871; 935 translations and 935 translated-judge tasks; 312 = 240 +
72 (120 + 36 per model); 2 raters + 1 adjudicator; B = 10,000; seed 0.

All values are consistent. Also verified: 900 s timeout; 294 prompt instances; 20/20
fixtures per language; 16 Urdu training sentences within 17 synthetic examples; 200
source tokens; seed 20260921.

One non-mismatch clarified in text: "valid label" (1,863) includes `partial` and
`cannot_tell`. §5.6 now says so, and that the binary denominators are smaller.

## 2. Provenance-language audit: ISSUES, all fixed

| Risk | Finding | Action |
|---|---|---|
| Generation code committed at run time | Not implied ("uncommitted working tree based on `e764072`") | — |
| Analysis code committed when frozen | Not implied ("frozen by content hash … from an uncommitted working tree") | — |
| D-PG-6 before judging began | Not implied. The text says "before any judge output was examined" (D-PG-6 19:10Z follows the judge authorization ≈18:16Z) | — |
| Native review written or signed | Verbal wording throughout | — |
| ORPI determination issued | Not implied ("requested … none is claimed") | — |
| Translated judging happened | **Abstract used the past tense** ("re-scored after translation"; "labelled a fixed 312-rationale subset") | Added an HTML guard: do not post until these are true. Methods §4.7 carries a status comment |
| Translation contract frozen | Methods says "decoding settings as frozen" only inside a placeholder | — |
| All judge outputs valid | §5.6 previously risked conflating valid with binary | Clarified |
| Raters "native" | The abstract said "native Urdu readers", but qualification admits near-native | Fixed: "native or near-native". §4.8 defines the "native readers" shorthand |

## 3. Date / timeline audit: ISSUES, documented and not rewritten

- The governance timeline now carries a **Date discrepancy register**. It covers:
  - `models.yaml` "2026-10-05";
  - the Claude-side nominal session dates and future-dated headers;
  - the D-PG-1..5 midnight `recorded_utc`;
  - the duplicate verbal-review records.
- Two early timeline rows that inferred dates from the seed value `20260921` are
  corrected to evidence-based bounds (after the base commit of 2026-09-13; before the
  2026-09-24 pilot).

## 4. Construct terminology: PASS

- "Chain-of-thought" is used only for the research field and cited work. Our object is
  the "rationale".
- "Faithfulness" and "monitorability" appear only in attributed background or explicit
  negation.
- "Transparency", "deception" and "hidden" do not appear as claims.
- "Internal" appears only in negations.
- "Disclosure" and "non-disclosure" are used as defined in Table A1.

## 5. Result-shell consistency: ISSUES, fixed

| Finding | Action |
|---|---|
| The abstract now uses named slots (`[PRIMARY_…]`), but other docs referenced R-ABS-1..6 | `WORKSHOP_V1_SLOT_REGISTRY.md` maps each named slot to one §5 source. R-ABS-1 (cue effect) is dropped from the abstract |
| `R-MON-0` (technical-state breakdown) existed only in the preprint | Registered → Table 2a |
| Matrix R-QC-4, R-COMP-3, R-CUE-SW had no prose destination | Registered as table-only (T1, Fig. S1, T4) |
| Conflicting table/figure numbering (old plan vs new shells and captions) | §5 renumbered to the shells and captions. Older docs carry supersession notes |

## 6. Technical-missingness wording: PASS

5 malformed + 3 no-label are described as technical missingness, retained and not rerun.
No substantive label is implied. Denominators are stated as binary-labelled traces. 1,871
is never treated as "all valid". The cell breakdown is a slot (R-MON-0), not inferred.

## 7. Human-validation logic: PASS

- Two fixed raters → Cohen's κ (not Fleiss), reported on raw labels.
- Adjudication is reported separately and never as reliability.
- `cannot_tell`, `abstain` and `unresolved` are missing from binary H.
- The four labels are identical to the judge's, with `abstain` human-only.
- Inputs are identical to the judge's.
- No κ adjectives.
- Qualification, compensation and ORPI remain placeholders.
- Annotation is gated on the ORPI reply.

## 8. Translation claim boundaries: PASS (after the abstract guard)

No runtime, device, dtype, completed translation, frozen translation hash or translated
judging is claimed. The placeholders are `[[TRANSLATOR_RUNTIME]]`,
`[[TRANSLATION_CONFIG_HASH]]` and `[[TRANSLATED_JUDGE_STAGE_HASH]]`.

## 9. Release / licensing language: PASS (now Version 3 by default)

| Item | Final language |
|---|---|
| Repository | "Code, configurations, prompt and cue templates, rubrics, synthetic training material and provenance records are available at [URL] ([DOI])." Only once these exist |
| Dataset IDs | "We release item identifiers with row hashes for `large-traversaal/openbookqa_urdu_final` at revision `e4186f6b`." |
| Hashes | "Configuration, artifact, stage and output SHA-256 hashes are published so that any later release can be verified." |
| Code | "All generation, judging, translation, segmentation, human-packet and analysis code." |
| Prompts | "Prompt and cue templates (EN/UR) are released. Rendered prompts containing item text are not." |
| Model outputs | "Retained with published hashes; [release route]. Not redistributed while they quote item text under an unstated licence." |
| Restricted source text | "Item text is not redistributed. Obtain it from the source dataset at the stated revision." |

## 10. Archival-commit wording (use only if the commit is made before results are inspected)

> **Generation code provenance.** Main generation (2026-10-02 to 2026-10-04) was run from
> an uncommitted working tree based on commit `e764072`. The executed code is identified
> by the generation configuration hash (`7b00e996…`) and by the implementation hashes of
> the serialization fix recorded during the run.
>
> **Analysis code provenance.** The analysis code was frozen by content hash
> (`1671bc3c…`) at 2026-10-04 19:15 UTC, before any monitor or human label was examined.
>
> **Archival snapshot.** On [DATE] (UTC), before any monitor or human label was examined,
> the repository state, including the executed generation code and the frozen analysis
> code, was committed as `[COMMIT]` for archiving. We verified that the archived files
> reproduce the recorded hashes ([list of hashes checked]). This commit is a later
> snapshot. It is not the commit from which generation was run.

If the hash check cannot be completed, replace the last two sentences with: "The
archived files have not been verified against every recorded hash." Never write "code
was committed at `[COMMIT]` and executed".

## 11. Mock review (no results filled; design and method only)

> **Summary.** A same-trace measurement study of whether an LLM disclosure monitor's
> Urdu labels match native readers', with a translation contrast. Two small models; 120
> items; descriptive intervals.
>
> **Strengths.** Clear construct. Input parity between judge and raters. Prespecified
> rules with dated records. Honest provenance (uncommitted code is disclosed; failures
> are retained). Conservative novelty and release language.

| Concern | Status |
|---|---|
| Construct drift toward faithfulness or monitorability | **FIXED** (terminology table; wording audit) |
| Prompt not monolingual (English elicitation sentence) | **FIXED** (disclosed); the design choice is an **INHERENT LIMITATION** |
| Abstract states completed stages | **FIXED** (posting guard) |
| Analysis freeze without a commit | **FIXED** (hash-based wording); archival commit pending (§10) |
| Translation details missing; paraphrase control absent | **WAITING ON TRANSLATION** / **INHERENT LIMITATION** |
| Translated-arm input identity not yet enforced in the executing path | **WAITING ON TRANSLATION** (engineering) |
| Human reference not yet collected; rater details unknown | **WAITING ON HUMAN DATA** |
| Precision of G with 36-item Cue-B and complete-case restriction | **WAITING ON RESULTS** |
| One language, two small models, one judge, one translator, translated items | **INHERENT LIMITATION** |
| No English human reference | **INHERENT LIMITATION** |

> **Verdict (internal diagnostic only):** methodologically sound and honestly scoped. Its
> value hinges on the human reference and on G's precision.

## 12. Result-unseal rule sheet

1. Populate raw denominators for every cell and arm first (planned → eligible → valid →
   complete).
2. Record technical missingness by state and cell (generation, judge, translation,
   human).
3. Compute the locked estimates with the frozen analysis code (hash `1671bc3c…`), once.
4. Compute the locked intervals: item-cluster percentile, B = 10,000, seed 0, paired
   within replicate.
5. Fill the tables (T1–T8, S1–S13) from that output only.
6. Only then activate Discussion branches (`WORKSHOP_V1_DISCUSSION_DECISION_TREE_V2.md`).
7. Run the claim ledger and the tripwire phrase scan.
8. No post-hoc thresholds: no κ bands, no compliance cutoffs other than ≥ 0.50
   (exploratory), and no new "meaningful" sizes.
9. Mark anything not in the frozen plan as **exploratory**, or **post-hoc** with its
   date.
10. Report null and mixed outcomes with the same prominence as resolved differences.

## Top 5 things that must be true before the preprint

1. The human reference exists: ORPI reply on file, two raters and an adjudicator,
   all 312 double-labelled and adjudicated, κ computed per spec.
2. Translation and translated judging are complete, under a frozen contract and stage
   hashes, with the input-identity check enforced in the executing path.
3. The frozen analysis has been run once and every result slot filled from it. The
   abstract's past-tense statements are then true and its posting guard can be removed.
4. Provenance is closed:
   - archival commit described as in §10;
   - date-discrepancy register in the appendix;
   - pause note written;
   - duplicate verbal-review records reconciled.
5. Author, acknowledgment (consent), compensation, funding and release decisions are
   made, and the final claim, citation and overclaim scans pass.

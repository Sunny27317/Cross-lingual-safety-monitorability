# Workshop-v1: citations, placeholder audit, acknowledgment options

**2026-10-04, pre-results.** No bibliographic detail is supplied from memory. Placeholder
tags refer to `paper/WORKSHOP_V1_PREPRINT.md`. Search for the tag text, because line
numbers drift.

## A. HIGH-priority citations: the claim each supports, and the fallback

| # | Citation to verify | Exact claim it supports (where) | Essential? | If it stays unavailable |
|---|---|---|---|---|
| H1 | Gemma 3 technical report | "Gemma-3-4B-it" model identity (Methods §4.4) | No. Identity is already fixed by repository, revision and SHA-256 | Cite the official model card/repository at the stated revision |
| H2 | Falcon-H1 report / model card | (a) judge identity; (b) **"chosen on … reported Urdu capability"** (Methods §4.9) | (a) No. (b) **Yes, if (b) is kept** | Remove "reported Urdu capability". Write: "selected before any study data existed, from a model family not shared with either generator, and not selected by agreement with our human labels" |
| H3 | IndicTrans2 paper | translator identity; Urdu→English support (Methods §4.10) | Conventional | Cite the official model card/repository at revision `ac3daf0e` |
| H4 | OpenBookQA paper | origin of the items (Methods §4.2) | **Yes.** Dataset creators must be credited | No weakening possible. Must be verified |
| H5 | Cohen (1960) | definition of κ (Methods §4.11) | Conventional (verification is trivial) | Name the statistic without a citation |
| H6 | DialectShift-Monitor | "translate-then-monitor has been explored in a dialect setting" (Related Work, positioning) | **Yes, for honest positioning** | Drop the specific sentence, but **keep** the disclaimer "we do not claim translate-then-monitor is new". Do not imply we are first |
| H7 | arXiv:2603.20172 | "judge-dependent conclusions in CoT-faithfulness evaluation" (Related Work) | No, but it **must be read** (possible close prior work) | Remove the citation. The general point stays supported by the VERIFIED multilingual-judge papers |
| H8 (placeholder) | Dataset card / provenance of `large-traversaal/openbookqa_urdu_final`, and its licence | "item-aligned English–Urdu release"; any UrduBench link (Methods §4.2) | **Yes** | Describe it only as "the Hugging Face dataset `large-traversaal/openbookqa_urdu_final` at revision `e4186f6b`", with **no** UrduBench attribution |

## B. Placeholder audit (all non-result, non-citation-key placeholders)

**Closed this pass (2):**
- **Cue/instruction sign-off.** Now reads: approval "given verbally and recorded by the
  investigator on 2026-09-29. No separate written sign-off was obtained."
- **AI-assistance disclosure.** Text inserted. Re-check the chosen server's policy
  before upload.

Also added to Methods §4.11 and the Ethics statement, though neither was a placeholder:
the human-validation text is final, and the synthetic training review is recorded with
verbal-only wording.

| Tag (search text) | Type | Closable now? | Who supplies / exact replacement |
|---|---|---|---|
| `[[AUTHOR_INFO: names and affiliations…` | AUTHOR_INFO | No | Investigator: "[MY NAME]¹ — ¹[DEPARTMENT/PROGRAM], [INSTITUTION]. Correspondence: [EMAIL]." |
| `[[AUTHOR_INFO: per author — Conceptualization…` | AUTHOR_INFO | Yes, if single-author. Investigator to confirm | "[MY NAME]: Conceptualization, Methodology, Software, Investigation, Data curation, Formal analysis, Visualization, Writing – original draft, Writing – review & editing." |
| `[[AUTHOR_INFO: funding…` | AUTHOR_INFO | Yes, if true | "This work received no specific funding." |
| `[[HUMAN_INPUT: rater and adjudicator qualification summary…` | HUMAN_INPUT | No (after recruitment) | "Raters were two [native/near-native] Urdu readers with strong written English who passed a reading screen on synthetic text; the adjudicator met the same criteria and did not rate. [No author served as a rater. / One author served as a rater and did not adjudicate.]" |
| `[[HUMAN_INPUT: compensation]]` | HUMAN_INPUT | No (decide before recruiting) | "Raters were compensated at [RATE]." or "Raters volunteered without payment." |
| `[[HUMAN_INPUT: auditor role; executed scope]]` | HUMAN_INPUT | No | "A bilingual reviewer who did not serve as a rater audited the [n] translations entering the human-anchored comparison." |
| `[[HUMAN_INPUT: insert acknowledgment option A … or option B…` | HUMAN_INPUT | No (consent) | §C below |
| `[[HUMAN_INPUT: raters/adjudicator, named only with consent]]` | HUMAN_INPUT | No | "We also thank [NAMES] for annotation and [NAME] for adjudication." / "We also thank the two raters and the adjudicator." |
| `[[HUMAN_INPUT: confirm release scope…` and `[[HUMAN_INPUT: per consent]]` | HUMAN_INPUT | No | Release scope per licence and consent |
| `[[ORPI: determination text and date]]` (Methods) and `[[ORPI: "UNC Charlotte's Office…` (Ethics) | ORPI | No | Verbatim from ORPI's reply |
| `[[ORPI: consent and compensation statement.]]` | ORPI | No | Per ORPI's guidance |
| `[[PROVENANCE: archived commit of the executed generation code…` | PROVENANCE | No (needs an approved commit) | "The code executed during generation was not committed at run time. It was archived after the run at commit `[HASH]` ([URL]); its correspondence to the executed code is supported by the implementation hashes recorded in the resume-provenance file." |
| `[[PROVENANCE: implementation confirmation for the translated arm]]` | PROVENANCE | **No.** `translated_context.validate_translated_context` exists and is tested, but `translated_judge_launcher.py` is preflight-only and does not yet call it | Close once the executing path calls the validator: "Question, options and suggestion were verified byte-identical between direct and translated inputs before scoring." |
| `[[PROVENANCE: completion date, technical-state counts, stage hash]]` | PROVENANCE | No (direct run active) | From direct-judge post-QC |
| `[[PROVENANCE: authorization date, stage hash]]` | PROVENANCE | No | From translated-judge authorization and run |
| `[[PROVENANCE: analysis code commit and hash]]` / `[[PROVENANCE: analysis code commit]]` | PROVENANCE | No (needs an approved commit before unsealing) | "Analysis code was frozen at commit `[HASH]` on [DATE] (UTC), before any judge or human output was unsealed." |
| `[[PROVENANCE: archive URL/DOI.]]`, `[[PROVENANCE: repository URL and archived commit.]]` | PROVENANCE | No | "Code and data: [URL]; archived at [DOI] (commit `[HASH]`)." |
| `[[TRANSLATOR_RUNTIME: device, dtype, …` and `[[TRANSLATOR_RUNTIME: translation contract and stage hashes]]` | TRANSLATOR_RUNTIME | No | From the frozen translator contract and run |
| `[[CITATION: compile from …` | CITATION | No | §A plus the VERIFIED list |

**Counts:**

| Type | Count |
|---|---|
| SCIENTIFIC_RESULT | 42 (28 `[[R-…]]` + 14 `[[R-DISC: …]]`) |
| HUMAN_INPUT | 7 |
| PROVENANCE | 8 |
| ORPI | 3 |
| AUTHOR_INFO | 3 |
| TRANSLATOR_RUNTIME | 2 |
| CITATION | 1 reference-list compile, plus 42 inline `[[CITE…]]` keys (resolved through §A and the audit) |

## C. Acknowledgment options for the native reviewer

Choose one. Option A requires her consent to being named.

- **A (named):** "We thank Amna Anwar Riaz for reviewing the Urdu item translations, the
  Urdu cue and instruction wording, and the Urdu rater-training examples."
- **B (anonymous):** "We thank a native Urdu reviewer for reviewing the Urdu item
  translations, the Urdu cue and instruction wording, and the Urdu rater-training
  examples."

Neither option claims a signed or written review. If you choose A, record her consent
(date and how it was given) in `engineering/provenance/`.

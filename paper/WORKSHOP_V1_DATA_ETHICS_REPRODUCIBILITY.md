<!-- Drop-in back-matter sections for paper/WORKSHOP_V1_PREPRINT.md. Outcome-blind; 2026-10-06.
PRECONDITION for the Data Availability text: the public repository must not contain item
text. Currently it does: engineering/provenance/URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.pdf
(commit 08db78d). Remediate it, or rewrite this section to state what is public. -->

## Data availability

**Released:**
- the code for generation, monitoring, translation and analysis;
- the configuration files;
- the frozen item manifests (source identifiers and row hashes, not item text);
- the SHA-256 hashes of every persisted generation, monitor and translation record;
- the stage seals;
- the analysis implementation;
- the synthetic test suites.

**Item text.** Items come from `large-traversaal/openbookqa_urdu_final` (revision
`e4186f6b`), an Urdu translation of OpenBookQA (Mihaylov et al., 2018) from the UrduBench
project (Shafique et al., 2026). That release states no licence of its own and defers to
the original dataset's terms, so we do not redistribute item text. Anyone with access to
the dataset can reconstruct the items from the released identifiers.

**Model outputs and labels.** Rationales, monitor outputs and translations contain item
text, so they are `[[HUMAN_INPUT: release route, e.g. "available for verification on
request" or "released after licence clarification"]]`.

**Native-reader labels** will be released only under pseudonyms, and only as the
institutional determination and rater consent permit.

**Repository:** `[[PROVENANCE: repository URL and archival snapshot DOI/commit]]`.

## Ethics statement

**What has happened.**
- Generation, monitoring and translation used only openly available models and a public
  dataset. These stages involved no human participants.
- One native Urdu reader reviewed the item translations (written, item-by-item) and the
  cue and instruction wordings (verbal). The reviewer judged materials only and saw no
  model output.
- The reviewer is acknowledged `[[HUMAN_INPUT: anonymously, or by name only with recorded
  consent]]`.

**What has not happened yet.**
- The native-reader annotation (two raters and an adjudicator, labelling model-written
  rationales about science questions) requires a determination from UNC Charlotte's Office
  of Research Protections and Integrity.
- That determination was requested on or before 2026-10-04.
- `[[ORPI: verbatim determination and date — if none at posting: "No determination had
  been received at the time of writing; no annotation has been conducted."]]`
- No human annotation has taken place and no human outcome data exist.

**Annotation conditions.**
- Raters will see no personal data and may skip any item.
- Compensation: `[[HUMAN_INPUT: compensation statement]]`.

## Reproducibility statement

**Stages.** Every stage is identified by content hashes:
- **Inputs:** the dataset revision; the item manifests (`576a991f…`, `e18b48b6…`); the model
  and monitor artifacts; the prompt and cue templates.
- **Configurations:** generation (`7b00e996…`); judge specification (`a8cb84c1…`, prompt
  `050ed492…`); translation (base `74b81473…`, amendment D-TR-1–6 `3a054e8b…`, effective
  `106f366c…`).
- **Stage seals:** direct monitoring (`3077fae1…`), translation (`14175ab5…`) and
  translated monitoring (`[[TRANSLATED_JUDGE_STAGE_HASH]]`).

**Failures and amendments.**
- Failed, timed-out and superseded records are retained and never overwritten.
- Every amendment is dated and recorded with what it changed and why (Appendix J).

**Executed code.**
- Generation ran from an uncommitted working tree based on commit `e764072`; translation ran
  from launcher code with hash `8f7c241a…`.
- Both are identified by content hash and archived in later commits; we do not claim that
  the archival commits are the executed commits.

**Analysis.**
- The analysis uses a deterministic item-cluster bootstrap (10,000 replicates, seed 0) and
  was frozen by content hash `[[PROVENANCE: final analysis freeze hash and commit]]`,
  after synthetic-only validation and before any result was unsealed.
- Generation on the Metal backend is not bitwise reproducible, so regenerated text may
  differ. Every reported number can be recomputed exactly from the hashed persisted
  records.

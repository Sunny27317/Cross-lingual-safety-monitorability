# Workshop-v1 preprint: completion map and outcome-blind drafts

**Written 2026-10-06, before any result.** These are drop-in texts for
`paper/WORKSHOP_V1_PREPRINT.md`, which itself is **not edited here** so the investigator
can review each insertion. No result is stated or implied.

## 1. Completion map

**Status codes:**
- **C**: complete now.
- **R**: needs results.
- **H**: needs human data.
- **O**: needs ORPI.
- **Cit**: needs citation work.
- **S**: needs a supervisor or investigator decision.
- **St**: stale (must be updated).

| Section | Status | Notes |
|---|---|---|
| Front matter (authors) | S | Author name, affiliation, CRediT, funding |
| Abstract | R | Template with branch versions; filled only after the single unseal |
| 1 Introduction | C, plus one R slot | One forward reference to results |
| 2 Related work | C / Cit | Re-check all citations on the upload date; 1 of 8 high-priority items still unverified |
| 3 Research questions | C | — |
| 4.1–4.4 | C | — |
| 4.5 Generation provenance | St → C | Fill the archival-commit slot: generation code archived in commit `08db78d` (a later snapshot, not the executed commit) |
| 4.6 Automated monitor | C | — |
| 4.7 Translation | St → C | Four slots can be filled now (§2.1 below). One HUMAN_INPUT (translation auditor) remains |
| 4.8 Native-reader reference | H, O, S | Rater qualifications, compensation, ORPI text |
| 4.9 Analysis | **St** | The "Freeze" paragraph presents `1671bc3c…` as the complete implementation. Replace with §2.2 below |
| 4.10 Changes to the plan | St → C | Add the post-translation and implementation addenda (§2.3) |
| 5.1–5.11 Results | R (5.7–5.9 also H) | Slots only |
| 6 Discussion | R | 22 result slots; branch rules fixed |
| 7 Limitations | C, plus one addition | Add the precision note (§2.4) |
| 8 Conclusion | R | — |
| Back matter: Ethics | O | Quote the determination verbatim |
| Back matter: acknowledgments / release | S | Consent-based naming; release route. The public-item-text issue (audit R1) must be resolved |
| Back matter: stage hashes | St → partly C | Translation stage `14175ab5…`. Translated-judge stage is pending (U-3) |
| Appendix J (provenance and errata) | C (drafts in §2.5) | — |
| References | Cit | Re-verify |

## 2. Drafts that can be completed outcome-blind

### 2.1 §4.7 slot fills (technical facts only)

- **`[[SEGMENTATION_VALIDATION]]`:**
  > A non-model validation of the amended segmentation and reassembly path loaded only the pinned tokenizer. It checked six synthetic edge cases and replayed all 935 completed records structurally, recomputing every unit and comparing unit metadata, hashes and exact reassembly. All checks passed, with 0 failing records (`engineering/indictrans2_amended_path_validation_2026-10-06.json`, SHA-256 `22372034…`).
- **`[[TRANSLATION_OUTCOME]]`** (branch A of the methods kit; true as a technical fact):
  > All 935 eligible rationales were translated completely by the primary translator; no segment required a fallback and no rationale was missing.

  The three rationales that failed under the superseded batching implementation succeeded on their governed third attempt; this is already described in the incident paragraph.
- **`[[TRANSLATION_STAGE_HASH]]`:**
  > `14175ab596e667684352d7326824979212634f7bf5dfd583c271231ea34a65ce` (seal schema `workshop-v1-translation-seal/2`; executed translation launcher `8f7c241a…`; effective configuration `106f366c…`)
- **`[[PROVENANCE: byte-identical non-rationale inputs]]`:**
  > The executing translated-judge path recovers the question, options and suggestion from the source Urdu generation exactly as the direct arm does. It refuses any task whose non-rationale inputs differ from the direct arm's. Before any judge call it verifies the translation seal from disk and requires an authorization bound to the sealed stage hash.

  Add one sentence on the six identity translations:
  > Six rationales contained no Arabic-script letter, so their translation equals the source. By a decision recorded before translated judging, they remain in the translated arm, are judged as-is with an explicit identity flag, and are excluded only in a pre-specified secondary robustness analysis.

### 2.2 Replacement §4.9 "Freeze" paragraph

> **Freeze.** The analysis primitives were validated on synthetic data and frozen by content hash (`1671bc3c…f3db`) at 2026-10-04 19:15 UTC, before any monitor or human label was examined. A pre-result audit on 2026-10-06 found that these primitives did not yet implement several planned quantities: paired contrasts within a bootstrap replicate, the cue-sensitivity measure, the sensitivity analyses, the confusion matrices and the record join. These were implemented without changing any definition, validated on synthetic data with hand-computed oracle tests, and frozen by a pre-result addendum (`[[PROVENANCE: implementation hash and commit]]`) before any judge or human label was examined. The plan itself (estimands, conventions, sensitivity analyses) did not change.

### 2.3 §4.10 additions

> After translation, and before translated judging, we recorded:
> - a segmentation amendment (D-TR-1 to D-TR-6), made before any successful translation;
> - a decision to keep the six identity translations in the primary translated arm, with an exclude-six robustness analysis;
> - an analysis-input builder that yields one analysis row per judge task.
>
> Before examining any result, we completed the analysis implementation (§4.9). Analyses not listed in the plan are labelled exploratory or post hoc.

### 2.4 §7 Limitations: precision sentence

> **Precision.** The design fixes the sample sizes. For Cue A, each monitor-validity estimate rests on at most 120 rationales per model. Under plausible disagreement rates, the 95% intervals span roughly ±6 to ±14 percentage points. For Cue B (36 items), they span roughly ±10 to ±21 points, and percentile intervals with this few clusters may under-cover. Intervals that include zero are therefore compatible with practically relevant gaps, and are reported as unresolved, not as evidence of equivalence.

(These widths are design-based planning values, not observed results. Replace them with the actual interval widths only if the text is rewritten after unsealing.)

### 2.5 Appendix J entries (outcome-blind)

- **Date labels.** Several planning documents carry "session N, date" labels that are sequence counters, not calendar dates. Their actual authoring times come from file and session-log timestamps; the analysis plan was final by 2026-10-01 (`research/frozen_sources/PROVENANCE.json`).
- **D-PG-2 arithmetic.** The approval text's "2,807/2,808 judge calls eligible" should read 2,806 eligible (936 English + 935 Urdu direct + 935 translated) of 2,808 planned.
- **C9.** An early governance note said the judge would see the English canonical question. The implemented judge uses the question as in the generation prompt (Urdu for Urdu rationales).
- **Translation incident and amendment.** As in §4.7.
- **Analysis implementation addendum.** As in §4.9.
- **Recovered test files.** Three test files were reconstructed after an accidental truncation. Reconstruction was verified against cached bytecode, apart from comment text. This concerns tests only, not data or analysis code.

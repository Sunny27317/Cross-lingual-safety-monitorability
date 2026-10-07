# 02–03 — Manuscript map (Methods and skeleton)

The canonical manuscript is `paper/WORKSHOP_V1_PREPRINT.md`. It already contains every
skeleton section requested, written from verified project facts. This map shows where each
section lives and what is still open. It contains **no results**.

| Skeleton section | Location in preprint | Status (2026-10-06) | Open placeholders |
|---|---|---|---|
| Title candidates | Front matter (top 3); full list of 15 in `research/WORKSHOP_V1_PUBLICATION_STRATEGY.md` §2 | ready; choose after results | — |
| Abstract template | Abstract (master); four branches in `research/WORKSHOP_V1_ABSTRACT_MASTER.md` | ready; posting guard present | `[PRIMARY_LANGUAGE_DIFFERENCE]`, `[MAIN_INTERVAL]`, `[HUMAN_JUDGE_AGREEMENT]`, `[DIRECT_VS_TRANSLATED_DIFFERENCE]`, `[IMPLICATION]` |
| Introduction | §1 | ready | `[[R-INTRO-1]]` |
| Related work | §2 (verified citations only) | ready | — |
| Research questions | §3 | ready | — |
| Methods: design | §4.1 | ready | — |
| Methods: dataset and item selection | §4.2 | ready | — |
| Methods: conditions, Cue-B design | §4.3 | ready | — |
| Methods: models, language conditions, prompts, item review | §4.4 | ready | — |
| Methods: generation provenance and QC | §4.5 | ready | `[[PROVENANCE: archival commit]]` |
| Methods: judge procedure, direct evaluation | §4.6 | ready (direct stage sealed) | — |
| Methods: translation pipeline, translated evaluation | §4.7 (**updated 2026-10-06** with verified runtime, D-TR-1–6 and the incident) | translation in progress | `[[SEGMENTATION_VALIDATION]]`, `[[TRANSLATION_OUTCOME]]`, `[[TRANSLATION_STAGE_HASH]]`, translated-arm confirmation, `[[TRANSLATED_JUDGE_STAGE_HASH]]`, auditor |
| Methods: human annotation | §4.8 | ready | rater qualifications, compensation, ORPI |
| Methods: statistical analysis | §4.9 | ready (D-PG-6) | `[[PROVENANCE: analysis archive commit]]` |
| Methods: changes to the plan | §4.10 + Appendix J | ready | — |
| Results | §5 (slot registry: `research/WORKSHOP_V1_SLOT_REGISTRY.md`) | shell ready | 45 result slots |
| Discussion | §6 (paragraph bank; tree V2) | ready | `[[R-DISC]]` slots |
| Limitations | §7 | ready | — |
| Conclusion | §8 | template | `[[R-CONC]]` |
| Ethical considerations | Back matter: Ethics | ready pending ORPI | `[[ORPI]]` ×3 |
| Reproducibility, data and code | Back matter | ready (conservative release by default) | URLs, DOI, commit |
| References | References (28 verified) | ready; re-check on the upload date | — |

**Placeholder census (2026-10-06):**

| Type | Count |
|---|---|
| Results | 45 |
| Human input | 8 |
| Provenance | 6 |
| Author info | 3 |
| ORPI | 3 |
| Translator stage hash | 2 |
| Translated-judge stage hash | 2 |
| Segmentation validation | 1 |
| Translation outcome | 1 |

The **Quality control** subsection requested in the brief is spread across §4.5 (generation
QC), §4.6 (judge technical states), §4.7 (translation failures) and §4.8 (agreement and
adjudication). The checklist is in `05_HUMAN_ANNOTATION_PROTOCOL.md` §11 and
`08_SUBMISSION_READINESS_CHECKLIST.md`.

# Workshop-v1 figure/table master plan and supplement plan

> **Superseded in part (2026-10-04):** slot IDs and table/figure numbers are governed by
> `research/WORKSHOP_V1_SLOT_REGISTRY.md` and `WORKSHOP_V1_TABLE_SHELLS_AND_CAPTIONS.md`;
> abstract slots by `WORKSHOP_V1_ABSTRACT_MASTER.md`. The content definitions here remain valid.


**No plots exist yet.** Everything below is a specification, rendered later only from the
frozen analysis output.

**Global rules:**
- Every figure shows 95% item-cluster intervals.
- No figure pools models.
- Every caption states the denominator, the interval method and the fact that intervals
  are descriptive.

## Main paper (minimum strong set)

| Item | Content and axes / rows | Denominator | Uncertainty | Caption must state | Misleading visualization to avoid |
|---|---|---|---|---|---|
| **Figure 1** Design | Schematic: items → 2 models × 2 languages × {Control, Cue A, Cue B(36)} × 3 samples → D_en / D_ur / translation → T; 312-trace H subset; identical judge/human inputs | counts in boxes: 3,312; 1,871 + 935; 312 | none | the counts; that H and the judge share inputs; that T uses the same judge spec | implying a causal flow from language to disclosure |
| **Figure 2** Cue sensitivity | x: language (EN, UR) within panels for model × cue; y: target-match rate under Control vs cue (paired dots) or ΔTM | parsed traces per cell (Cue B on the 36) | 95% CI bars | Cue B on its 36-item subset; Control baseline uses the same item-specific target | truncated y-axis exaggerating ΔTM; comparing Cue-B panels with full-120 Cue A |
| **Figure 3** Disclosure by reader | rows: model × cue; points: D_en, D_ur, T (all-k automated) and, on the 312 subset, H and D_ur (paired) | binary-labelled traces per arm (stated per point) | 95% CI | that the H/D_ur comparison is on the 312 subset; that partial/cannot_tell are excluded from the binary rates and shown in Table 5 | mixing all-k automated rates with subset human rates on one axis without a visual separation; bars without denominators |
| **Table 1** Design and counts | per cell: planned, completed, parseable, visible trace, compliant-flag rate (EN/UR) | 3,312 / per cell | CI for rates | that the timeout is retained as missing | — |
| **Table 2** Primary estimates | rows: model × cue. Columns: Acc(Control), ΔTM (EN, UR), D_en, D_ur, AG, G, R_full, R, each "estimate [CI] (n)" | as per matrix | CI | descriptive intervals; number of intervals in the table; R descriptive only | bold or star marking "significant" cells |
| **Table 3** Human validation | the Table 6 shell in `WORKSHOP_V1_RESULT_BRANCHES.md` §4 | 312 / binary subset | κ CIs | Cohen's κ; no verbal bands; adjudicated labels are the reference | colour scales implying good/bad |

If space allows, add **Table 4**, the confusion matrix (judge × human, 4×5) for D_ur. The
main text should show at least the pooled-over-cue version per model.

## Supplement tables

| Table | Content |
|---|---|
| S1–S5 | sensitivity variants |
| S6 | exploratory compliance-restricted recomputation |
| S7 | missingness cascade with worst-case bounds |
| S8 | judge technical states by arm × language × model × cue |
| S9 | translation failures and audit findings |
| S10 | Cue B vs Cue A(36) paired contrasts |
| S11 | full rater 5×5 contingency |
| S12 | raw count tables for every proportion |
| S13 | per-item distribution of disclosed traces (0–3), descriptive |

## Supplement / appendix plan

**Public redistribution:** "public" means it can be redistributed; "restricted" means it
cannot be redistributed and is referenced or reconstructed instead.

| Section | Content | Public? |
|---|---|---|
| A. Prompts and cues | Prompt templates (EN/UR), cue texts, language instruction, elicitation sentence, with hashes | **Public** (project-authored text) |
| — | Rendered prompts containing item text | **Restricted.** Item text is under the dataset's unstated licence; give IDs and a reconstruction script instead |
| B. Generation settings | Model IDs, revisions, SHA-256, decoding, runtime build, seeds, timeout | Public |
| C. Dataset provenance | Dataset ID, revision, ID manifests and hashes, selection algorithm and seed, licence note | Public (IDs and hashes only) |
| D. Native-review procedures | Item-equivalence procedure and outcome; verbal cue-instruction approval; verbal training-example confirmation, worded as such | Public (procedure and outcomes). Reviewer name only with consent |
| E. Judge V2 | Verbatim prompt, label definitions, parser precedence, decoding, fixture check | Public |
| F. Translation pipeline | Translator ID and revision, toolkit, decoding, runtime | Public |
| G. Segmentation algorithm | Rules, S_max = 200, pass-through, overflow handling, failure policy | Public |
| H. Human rubric | Rater instructions, decision tree, synthetic training tutorial, adjudicator instructions, agreement-reporting spec | Public (all synthetic) |
| I. Governance decisions | D5, language instruction, D-PG-1..6 with dates; approval records | Public |
| J. Missingness | Cascade, reasons, worst-case bounds | Public |
| K. Technical incidents | Attempt-1 port failure; serialization incident and outcome-independence evidence; resume; timeout; code-provenance note | Public |
| L. Reproducibility hashes | Per-stage hashes, analysis commit, archive DOI | Public |
| M. Analysis specification | Estimands, D-PG-6, S1–S5, exploratory list, interval method | Public |
| N. Additional tables | S1–S13 | Public (aggregates) |
| — | Model rationales, judge outputs, human labels | **Release decision pending** (licence and consent). Rationales may quote item text; consider redacting the question/options |

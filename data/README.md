# data/

Holds task items, generated reasoning traces, translations, and human/native
annotations.

## Rules

- Contents are **real** data only: real task items, real model generations, real
  collected annotations. Never simulated, model-filled, or hand-fabricated
  annotations (see `CLAUDE.md` §2.1–2.2).
- Every dataset records its provenance: source, version/revision, split,
  language, retrieval date, and any processing applied.
- Large or license-restricted data is not committed; instead a manifest here
  documents exactly how to retrieve/regenerate it.
- Raw annotator data is stored so every reported number can be recomputed.

Empty until Milestone 1.

Item sources (from the Run-2 blueprint, see `../experiments/EXPERIMENT_SPEC.md` §4):
MGSM, GPQA/GPQA-Diamond, CommonSenseQA / OpenBookQA, BBH/BBQ-style items, plus a
to-be-authored ~50-item safety-relevant decision set. MGSM, CommonSenseQA and OpenBookQA
already have Urdu translations in UrduBench (arXiv:2601.21000 — VERIFIED). The Urdu
subset is built by machine translation → native correction → back-translation audit →
≥90% native-agreement acceptance. Which single dataset seeds the ~50 Milestone-1 items
is `TODO — DECISION REQUIRED` (U6; recommendation: MGSM).

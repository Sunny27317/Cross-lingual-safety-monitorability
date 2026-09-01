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

Empty until Milestone 1. Item source for the Urdu pilot is
`TODO — import/verify from Run-2 blueprint`.

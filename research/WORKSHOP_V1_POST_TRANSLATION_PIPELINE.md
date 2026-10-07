# Workshop-v1 post-translation pipeline

## Architecture and constraints

The frozen path is generation records -> 935-task translation manifest ->
IndicTrans2 translation records -> translated Urdu Judge V2 records -> the
frozen analysis table/statistics scaffolding. Direct English and direct Urdu
judge records are separate upstream routes. Cue-A and Cue-B remain separate;
Cue-B comparisons use the frozen shared subset. Translation, translated judging,
human annotation, and analysis have separate authorization boundaries.

The active translation run is not touched by this preparation. No translation,
judging, label inspection, or analysis was performed here.

## Implemented downstream controls

`post_translation_pipeline.py` provides manifest/hash/count validation for all
935 translation records, technical failure accounting, immutable stage sealing,
and provenance-complete analysis-table construction. It never summarizes labels
or silently drops malformed rows.

`translated_judge_launcher.py` now requires translation QC before preflight,
retains deterministic task IDs, uses atomic immutable writes, supports explicit
resume, and exposes technical post-QC/progress output. Existing translated-arm
context parity remains enforced before prompt construction.

`run_workshop_v1_post_translation.sh` and
`WORKSHOP_V1_POST_TRANSLATION_COMMANDS.md` provide the fail-closed sequence.
Translated judging still requires separate investigator authorization.

## Remaining gates

The translation launcher must reach zero remaining tasks and pass its own stage
QC/seal. A separate translated-judge authorization is required before any
translated judging. Human annotation, final analysis, and publication claims
remain separately governed. Current active translation outputs were not read or
modified by this preparation.

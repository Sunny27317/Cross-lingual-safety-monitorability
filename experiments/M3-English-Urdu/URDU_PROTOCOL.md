# Urdu protocol — prospective, no run

## Scope and frozen boundaries

The primary research question, Track-A English generator/model/runtime/config/selection/
intervention/estimands and Track B remain unchanged. This package adds schemas and
prospective analysis, not a new generator or generation credential. The singular
`authorize_track_a_run()` boundary remains untouched; its English token does not
constitute authorization for Urdu, judge, human, translation or confirmatory stages.

MMLU is primary. Before Urdu collection, reviewers must specify the exact aligned Urdu
material, source and language provenance, translation/adaptation procedure, revision,
content hashes, split, item IDs and compatibility/inclusion criteria. UrduBench
OpenBookQA can be secondary robustness only where the four-choice task and label mapping
are compatible. UrduMMLU is a candidate, not an approved source; provenance/license/
schema evidence must be verified before adoption. This task downloaded no dataset.

## Conditions and measurement controls

Preserve the paired hinted/unhinted intervention logic and model-versus-monitor
separation. Do not infer language effects by pooling different subject distributions,
models, interventions or evaluation populations. Human review must freeze Urdu prompt
and cue equivalence, target rule, sample counts/seeds/decoding, answer instruction,
missingness handling and aligned comparison population before Urdu outputs are inspected.
Nothing here authorizes changing the frozen English generator experiment.

Use source-item IDs to cluster repeated traces, language variants and conditions. The
same source item must not span calibration and heldout partitions. A trace manifest is
locked by exact identity/hash, not filename order. Outcome-based trace selection is not
implemented. If the existing behavioural eligibility definition defines a later target
population, apply that **predeclared** rule consistently, preserve all denominator and
exclusion evidence, and do not choose it based on pilot effect magnitude. Reuse existing
`clsm.metrics` for behavioural quantities; disclosure labels alone cannot establish
causal hidden influence.

## Dataset adapter contract

`DatasetSpec`, `SourceRow`, `adapt_item`, and `validate_items` are offline. They require
explicit language, immutable revision, source item/subject, repository/config/split,
licensing/provenance evidence and compatibility decision. Choice order is preserved
byte-for-byte in JSON strings. Answers require an explicit zero-based integer or exact
Latin-letter mapping; no guessed one-based, translated or rearranged answer mapping.
Stable identity binds source ID to the dataset spec; content SHA includes question,
all four ordered choices, correct index, subject and language. Duplicate IDs, incomplete
choices, hash/revision/language mismatches and invalid answer indices are refused.
Text normalization is not applied silently. Human evidence fields are attestations,
not a license or linguistic-equivalence verification service.

The primary answer extraction calls the existing `clsm.extraction.extract_answer`
unchanged. It uses Latin A–D and existing final-span/ambiguity rules in both languages.
`extract_strategies` exposes the primary answer/status separately from an exploratory
boxed Perso-Arabic mapping (الف/ب/ج/د). Exploratory markers are searched only in the final
answer span; they cannot repair or replace a missing/ambiguous primary parse. Publish
separate denominators and label this exploratory. Do not pool extraction strategies.

## Stage gates and stop

Required before Urdu execution: approved dataset/content provenance and aligned design,
validated direct judge on the relevant population, native reviewer protocol/resources,
governance determination, frozen Urdu config and independent human stage authorization.
The English pilot can inform documented feasibility/deviation review later, but it has
not been inspected by this package's author and must not retroactively justify these
prospective selection choices. Any future design change must be recorded before the
corresponding downstream outcomes are seen.

**STOP:** no Urdu generator executor is added or run by this package. Its contracts,
validation and synthetic analysis are available for human review. They are not permission
to begin Urdu scientific collection.

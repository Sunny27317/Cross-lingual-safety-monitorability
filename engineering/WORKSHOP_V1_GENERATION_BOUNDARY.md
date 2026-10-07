# Workshop-v1 generation boundary

This is an engineering classification, not authorization. The whole-study
provisional hash remains preserved in `workshop_v1_main_launch_manifest.json`.
The raw-generation-only configuration is separately hashed as
`7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec` in
`engineering/workshop_v1_generation_config.json`.

## Critical path

The following must pass before raw generation: frozen dataset/manifests and
source rows; closed Urdu item-equivalence review; approved cues and language
instruction; D5 Qwen and Gemma artifact/configuration checks; exact workload
and pilot exclusion; generation configuration hash; a new empty output
directory; the fail-closed scientific executor; and explicit investigator
authorization tied to the generation hash. These checks do not authorize a
run by themselves.

The translator is not part of the raw 3,312-call generation input. The frozen
design's IndicTrans2 path consumes completed Urdu cued traces for a later
translation-monitoring stage. Its exact checkpoint/backend/procedure must be
frozen before the first scientific translation, not before raw generation.

## Stage classification

| Gate | Stage |
|---|---|
| IndicTrans2 checkpoint/backend/provenance | MUST_BEFORE_TRANSLATION |
| Translator preprocessing/postprocessing/decoding/fallback | MUST_BEFORE_TRANSLATION |
| Falcon technical format fixture and judge contract | MUST_BEFORE_JUDGING |
| ORPI/institutional determination, rater recruitment, compensation | MUST_BEFORE_HUMAN_ANNOTATION |
| Compliance-floor analysis rule | MUST_BEFORE_ANALYSIS |
| Scientific executor, generation hash, empty output, authorization | MUST_BEFORE_GENERATION |
| Final whole-study hash and downstream analysis lock | MUST_BEFORE_ANALYSIS |
| Publication wording and claims | PUBLICATION_ONLY |

The judge format contract is technically ready; scientific judging remains a
later-stage operation. No translator, judge, human, or model call was made in
this boundary sprint.

## Authorization text prepared, not recorded

The investigator must explicitly approve the following exact statement after
reviewing the generation preflight:

> I authorize Workshop-v1 scientific main generation under generation
> configuration hash `7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec`,
> comprising exactly 3,312 calls: Qwen3-1.7B and Gemma-3-4B-it, English and
> Urdu, Control/Cue-A/Cue-B, three samples per frozen main item, written only
> to `experiments/_runs/workshop-v1-main`. This authorization begins scientific
> main generation; it does not authorize translation, judging, human annotation,
> or any downstream stage.

This statement is not an authorization record and has not been supplied to the
executor.

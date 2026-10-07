# Workshop-v1 publication artifact inventory

This inventory distinguishes private scientific provenance from material safe
to publish. Hashes and IDs can be released where licenses permit; item text,
review packets, reviewer identities and contact details remain private pending
license/privacy review.

| Artifact | Internal location | Purpose | Recommendation |
|---|---|---|---|
| Main generation manifest/config | `engineering/workshop_v1_main_manifest.json`, `engineering/*generation*` | Frozen task identity/config | Release metadata/hash only |
| Judge V2 prompt/spec | `engineering/workshop_v1_judge_prompt_v2.json`, `configs/workshop_v1/judge_model.yaml` | Judge construct provenance | Release if license permits |
| Translation contract/amendment | `engineering/indictrans2_final_contract.json`, `engineering/provenance/*D-TR*` | Translator provenance | Release config and hashes |
| Translation stage seal | `experiments/_runs/workshop-v1-translation/translation_stage_seal.json` | Stage integrity | Private full copy; publish hash |
| Direct judge seal | `engineering/workshop_v1_direct_judge_stage_seal_v2.json` | Stage integrity | Publish hash/metadata |
| Translated judge QC/seal | Created after live run and QC | Downstream integrity | Publish hash/metadata only until policy review |
| Analysis freeze | `engineering/provenance/ANALYSIS_CODE_FREEZE_2026-10-04.json` and Claude worktree | Frozen analysis | Publish code/hash, preserve provenance |
| Rater package/forms | `docs/rater_package/`, `engineering/provenance/` | Human validation | Private; anonymized excerpts only |
| Dataset/item manifests | `engineering/workshop_v1_*manifest.json` | Reconstruct task IDs | Release IDs/hashes, not item text if license unclear |
| Raw run outputs | `experiments/_runs/**` | Scientific records | Private encrypted archive; publish only governed derivatives |

No scientific result values were inspected while preparing this inventory.

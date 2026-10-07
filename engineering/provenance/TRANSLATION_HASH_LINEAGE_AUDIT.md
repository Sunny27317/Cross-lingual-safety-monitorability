# Translation hash lineage audit

| Hash | Object | Status | Execution relevance |
|---|---|---|---|
| `4ef0a4de36c7ce4b58a4fda1877be30c9755d526e7e82340b8dc784edccfeaf2` | Older `workshop_v1_translation_config_hash.json` | Historical/stale | Not the operative authorized contract. |
| `74b81473f4c714e8146c352c6c351772ea995b3dff6f37c8a4af06ca311f99bc` | Base IndicTrans2 contract | Canonical base | Original authorization reference. |
| `3a054e8bac831a1cbbfd25b545c15562bbc76b82824266ba707798e104720dc5` | D-TR-1..6 amendment | Canonical amendment | Binds amended execution rules. |
| `106f366c7a0010dab11849150e48b2fb88cb3a4d23260a9abdd750760e6b4171` | Effective base+amendment contract | Canonical effective | Operative amended translation provenance. |
| `14175ab596e667684352d7326824979212634f7bf5dfd583c271231ea34a65ce` | Translation stage seal | Canonical stage | Binds the completed translation stage. |

Conclusion: the discrepancy is stale metadata confusing an earlier config
object with later base/effective lineage, not evidence of a model revision
change. Historical files remain untouched; future manifests must expose base,
amendment, effective, and stage hashes separately.

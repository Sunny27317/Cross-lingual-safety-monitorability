# 06 — Discussion framework (conditional; no results claimed)

Paragraph activation is mechanical: see `research/WORKSHOP_V1_DISCUSSION_DECISION_TREE_V2.md`
and the paragraph bank in preprint §6. This page gives the conditional framing for each
interpretation category the brief asks for.

- **Intervals.** "Resolved" means the 95% D-PG-6 interval excludes 0.
- **Replication.** "Replicated" means the same direction holds in both models.
- **Thresholds.** No numeric thresholds are used.

| Category | If the observed pattern shows… | …this would suggest | It would not show |
|---|---|---|---|
| Cross-lingual consistency | AG and G intervals both contain 0 in both models | within the stated bounds, this monitor's Urdu labels track native readers, and automated EN/UR rates do not resolvably differ | language-robust monitoring in general; "equivalence" |
| Model variation | the cross-model flag is "differs" for AG, G or ΔTM | monitor validity depends on the generating model's rationale style; validate per deployment | effects of size, family or training (these are confounded) |
| Language effects (behavior) | the L_ΔTM interval excludes 0 | cue sensitivity differs between the English and Urdu versions of the same items | an effect of the Urdu language as such (items are translations) |
| Language effects (monitoring) | AG excludes 0 | automated disclosure rates differ by language. Read it through G, never on its own | a model-transparency difference |
| Monitor validity | G > 0 (or < 0) | the direct monitor under- (or over-) labels disclosure relative to native readers on identical text | monitors in general fail in Urdu |
| Translation-mediated effects | R / R_full excludes 0 | translating before monitoring changes automated labels. If the exploratory agreement diagnostic is > 0, labels move toward native readers | mitigation, or a language-specific mechanism (no paraphrase control) |
| Monitorability implications | any G ≠ 0 | cross-lingual monitoring rates need a native reference before they are read as model behavior | that chain-of-thought monitoring is (un)reliable in general |
| Validity threats | high `cannot_tell` or technical failures in one arm (P-CT, P-MISS) | coverage, not only accuracy, differs across languages; binary estimates describe the decidable subset | — |
| Generalizability | (always) | results hold for two small models, one monitor, one translator, one task, two cue wordings and one language | other languages, scales, tasks |
| Measurement and judge limits | low κ, or disagreement concentrated at `partial` | the construct has boundary ambiguity; read G with the measured agreement in view | an invalid reference |
| Translation limits | translation failures, or audit-flagged additions or omissions | the T arm describes the translatable, audited subset; sentence-level units can break references that span sentences | translator-independent conclusions |
| Small-model / local-inference limits | (always) | prompted rationales from 1.7B/4B quantized models on CPU/Metal; outputs are not bitwise reproducible; a 7B quantized judge | frontier-model or native-reasoning-channel behavior |

**Reporting rule.** Null and mixed outcomes get the same prominence as resolved
differences. See `research/WORKSHOP_V1_NULL_AND_MIXED_RESULT_PLANS.md`.

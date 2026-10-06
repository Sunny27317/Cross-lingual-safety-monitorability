# Workshop-v1 post-translation reconciliation

This record is an engineering pointer created after the independent paper-readiness
audit. It does not replace or rewrite the historical forensics, translation failures,
or scientific outputs.

The C1 identity-translation decision is implemented at the translated-context boundary:
an equal trace is accepted only when the immutable translation record explicitly carries
`translation_identity=true`, `translation_changed=false`, and the D-TR-2 reason
`zero_urdu_script_letters`. Unexplained equality remains a hard failure; the technical
QC bounds this authorized edge case to six records.

Translated judging is blocked until a complete translation QC pass and immutable stage
seal bind the task, configuration, artifact, and stage hashes with zero unresolved
technical failures. Human adjudication triggers on either disagreement or abstention,
including both raters abstaining, and permits the protocol's `unresolved` final state.

The prior segmentation-validation JSON and older forensic documents remain historical.
After the active translation process ends, refresh the segmentation artifact using the
recorded synthetic-only command before sealing the translation stage. No active output
was inspected or modified for this reconciliation.

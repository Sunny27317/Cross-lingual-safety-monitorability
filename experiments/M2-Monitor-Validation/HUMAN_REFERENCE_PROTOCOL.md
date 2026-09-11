# Human reference protocol — human approval required

Purpose: create a locked, auditable disclosure reference, including native Urdu
judgments for Urdu traces. No human labels are created by this package. Synthetic labels
are software fixtures and are tagged `data_kind=synthetic` at every boundary.

## Prospective decisions still required

Investigator and institutional reviewers must approve recruitment, language competence
assessment, independent rater count, overlap allocation, training materials, sample size,
compensation/consent, content exposure safeguards, conflict handling, and adjudication
roles. No heuristic kappa/alpha cutoff or fixed rater-count sufficiency rule is adopted.
Training/calibration/heldout items must be separated at source-item level. Training
examples must not disclose heldout outcomes. The steward documents the qualifications
of native/bilingual reviewers without publishing personal identities.

The draft [annotation rubric](ANNOTATION_GUIDE.md) must be reviewed by humans, including
native Urdu reviewers before Urdu use. Freeze its version, exact wording in each language,
partial-label policy and uncertainty treatment before scientific annotations. Human
review is not replaceable by machine translation or a synthetic consistency test.

## Collection and lock

1. Steward locks the prospective population, exact text hashes, item clusters and
   inclusion policy. Existing parser diagnostics remain linked but are not turned
   into negative labels. Full preserved reasoning spans are used; no favourable
   fragment selection. Record whether the rubric needs additional cue context; changing
   input content requires a new prospectively reviewed contract/version.
2. `blind_packet` uses a private steward-held HMAC secret to create anonymous IDs and
   a recorded seed to randomize presentation order. Export `AnnotationPacket` only.
   Store `PrivateAssignment`, secret and identity mapping separately with restricted
   access. Independent raters can receive different presentation seeds; preserve each
   packet/assignment and reconcile by opaque ID, never row position.
3. Raters independently submit `Annotation` records with category, confidence (or
   missing), uncertainty flag, rationale, pseudonym, round, rubric version, status,
   UTC timestamp and provenance. Do not show model/condition/automated labels. Textual
   cues may be unavoidable; disclose rather than silently edit them away.
4. Validate duplicates, assignment/hash/rubric consistency and schema. Preserve original
   annotations unchanged. Distinguish missing submission, cannot-tell and abstention.
5. Apply the approved [adjudication protocol](ADJUDICATION_PROTOCOL.md). Every final
   `ReferenceLabel` links the exact original annotation hashes and an adjudicator
   pseudonym/record. Do not silently manufacture consensus or majority-tie resolutions.
6. `LockedReference` binds the packet, protocol decision, steward and timestamp.
   `validate_reference` requires matching raw source records. Archive originals,
   adjudication evidence and lock hash before showing judge outputs to reference raters.
   The lock is an attestation with an audit trail; a hash does not prove human competence
   or historical timing. Missing reference entries remain explicit in analysis.

## Agreement and audit

`inter_rater_report` compares two identified pseudonyms in one round on the declared
packet, with explicit partial policy and item-cluster resampling if prospectively chosen.
It reports the same confusion/prevalence/agreement diagnostics as judge comparison.
Keep directional sensitivity/specificity distinct from symmetric agreement: neither rater
is automatically truth. Retain raw multicategory labels even when binarizing for an
approved estimand. For more raters, predeclare pairwise summaries and multiplicity;
no automatic aggregation or cutoff is implemented.

Report raw disagreement before adjudication separately from final judge-reference
agreement. An adjudicated reference remains fallible. Sensitivity analyses should vary
only preregistered ambiguity treatments and propagate reference uncertainty; they must
not choose the treatment with the largest scientific effect.

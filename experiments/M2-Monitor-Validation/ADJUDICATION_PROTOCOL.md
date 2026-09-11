# Prospective adjudication protocol

Status: mechanism implemented; staffing, quorum, tie/ambiguity and escalation rules
**HUMAN REQUIRED**. No automatic majority vote, arbitrary agreement cutoff, or synthetic
replacement for a missing human judgment is permitted.

- Preserve each independent annotation with an immutable hash, pseudonym, round, rubric
  and timestamp. Subsequent edits are new records linked to originals, not overwrites.
- Report independent agreement before adjudication. Independent raters do not see one
  another's responses or judge outputs while producing their initial records.
- A steward identifies conflicts under an approved rule. An authorized adjudicator
  reviews the source text, original rationales and frozen rubric. Keep generator,
  condition and automated outcomes blinded. Adjudication access differs from initial
  rating access and is logged.
- The adjudication record names the original hashes, adjudicator pseudonym, rubric
  rationale, final category or unresolved status, timestamp, and deviation record if
  the frozen rubric does not address the case. Do not resolve ambiguity by desired effect.
- An unresolved case remains cannot-tell/abstain or absent under the preregistered policy.
  Partial-label binarization is supplied independently through `LabelPolicy`, never
  inferred from observed agreement.
- `ReferenceLabel.source_annotation_hashes` and `LockedReference` preserve lineage.
  `validate_reference` rejects nonexistent/foreign source records. It does not decide
  whether an adjudication was scientifically justified; named humans attest this.
- Lock the reference before candidate comparison/heldout access. Any later correction
  invalidates the old lock for a new analysis and requires a visible deviation and
  sensitivity report. Never silently replace the reference and retain an old hash.

Required approval record: investigator, native-language reviewer where relevant,
independence/conflict-of-interest safeguards, role allocation, unresolved-case rule,
release policy, and institutional/ethics determination. All remain pending here.

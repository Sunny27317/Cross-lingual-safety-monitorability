# Workshop-v1 overnight engineering package

This package is prepared without reading scientific labels or translated
content and without touching the live translated-judge process.

## Safe post-run sequence

After the translated-judge process exits, first confirm it is gone and take a
read-only technical snapshot. Then run the structural QC tool below. It does
not print label values or label counts:

```bash
cd /path/to/Cross-lingual-safety-monitorability
PYTHONPATH=src python -m engineering.workshop_v1_translated_judge_post_qc \
  --output experiments/_runs/workshop-v1-translated-urdu-judge \
  --manifest engineering/workshop_v1_translated_urdu_judge_manifest.json \
  --translation-stage-hash 14175ab596e667684352d7326824979212634f7bf5dfd583c271231ea34a65ce \
  --effective-config-hash 106f366c7a0010dab11849150e48b2fb88cb3a4d23260a9abdd750760e6b4171 \
  --prompt-hash 050ed49289b435ed84ab565dcca000cafd4554de3c11230edc2fe56d29844984 \
  --judge-spec-hash a8cb84c12821a2352442a25589bf88834b8c87744350ea45c0af0db8f7dfb419 \
  > /tmp/workshop-v1-translated-judge-qc.json
```

The report must be reviewed mechanically before any seal is considered. A
seal is immutable and must be written only after QC PASS and investigator
authorization under the applicable governance record.

## Readiness separation

`engineering/workshop_v1_pre_unseal_validator.py` reports automated-pipeline
readiness separately from full human-validated paper readiness. The latter is
blocked until ORPI/institutional determination and human labels exist.

## Reproducibility and portability

The current branch contains recovery notes, model-artifact recovery metadata,
bootstrap instructions, archive/bundle procedures, privacy-remediation plans,
and translation hash lineage records. Scientific run directories, downloaded
model binaries and local dataset copies remain local-only/backup assets and
must not be deleted while any stage is live.

## Privacy and release boundary

The Urdu review PDF, reviewer identity, contact identifiers, and item text are
not publication-safe. Preserve a private archival copy and perform a reviewed
history-remediation operation before public release. Do not rewrite history
during a live scientific stage.

## Known blockers

1. The live translated-judge stage must finish and pass structural QC.
2. A translated-judge stage seal must be created and independently verified.
3. ORPI/institutional determination still blocks human annotation.
4. The Claude analysis worktree remains independent and must not be edited or
   merged by this package.

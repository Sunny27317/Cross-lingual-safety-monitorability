# Execution gates added by the scientific freeze

The downstream code now has four outcome-independent safeguards.

* `clsm.downstream.partitions.assign_source_items` creates a deterministic,
  hashable, item-disjoint assignment to rubric-training, calibration, heldout,
  and confirmatory partitions. Assignment uses only source IDs and a recorded
  seed; observed labels cannot affect it.
* `JudgeAcceptanceCriteria` is a signed, hash-bound contract. Candidate scoring
  rejects missing criteria, criteria for another plan, unsigned timestamps, or
  criteria signed after the first candidate output. Threshold values remain
  investigator supplied; the code does not select a judge.
* `clsm.downstream.matching` validates the exact
  `(source_item_id, condition, language, seed, generation_id)` identity key for
  matched human/direct/translated labels and rejects duplicate identities.
* A mechanism claim in `measurement_report(..., mechanism_claim=True)` requires
  a usable English-to-English paraphrase control for every English source trace.
  The control is optional for descriptive contrasts where the language-mechanism
  claim is explicitly withdrawn.

`validate_cluster_method` provides an ADEMP-style synthetic check of the
source-item clustered percentile bootstrap. It has no model, judge, translation,
or project-data input and does not freeze confirmatory design choices.

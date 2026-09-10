# English Track-A pilot report — PRE-FROZEN TEMPLATE

**PENDING RUN. All values below are intentionally unfilled.** DESCRIPTIVE pipeline and
instrument validation; n=50 design, not confirmatory evidence. Do not fill from fixtures.

## 1. Run identity

PENDING RUN: experiment ID, scientific hash, exact commit, clean-tree evidence, reviewed
stage authorization, start/end UTC, deviation record and completion manifest location.

## 2. Hardware/software

PENDING RUN: hardware, OS, architecture, Python/library versions, memory conditions.
Document Metal nondeterminism: identical seeds do not promise byte-identical outputs.

## 3. Model/runtime provenance

PENDING RUN: model/revision, GGUF file/size/SHA verification, llama.cpp commit/build/version,
command surface, decoding/timeout and provenance references. No alternative generator.

## 4. Dataset pin

PENDING RUN: repository/config/split/requested and resolved revision, library version,
source hashes, selected content hash, exact IDs, subject counts, exclusions and schema/order/label checks.

## 5. Completion counts

PENDING RUN: planned/present/missing records, distinct item-condition-seed identities,
raw artifact count/hash verification. Design maximum is 800 calls, not an observed count.
If incomplete, report diagnostics and withhold behavioural estimates.

## 6. Parsing diagnostics

PENDING RUN: VALID, AMBIGUOUS, NO_ANSWER, PARSE_ERROR, success denominator; reasoning
PRESENT/EMPTY/ABSENT/MALFORMED, marker styles and multiple-span diagnostics where available.
Missing/empty reasoning is not evidence of absent disclosure.

## 7. Truncation/failure diagnostics

PENDING RUN: EOS, LENGTH, TIMEOUT, NONZERO_EXIT, UNKNOWN; requested caps, token-count
availability, partial timeout output, missing samples and infrastructure interruptions.

## 8. Baseline accuracy

PENDING RUN: unhinted majority accuracy, denominator and descriptive item-cluster CI;
valid-sample majority rule, tied/undefined conditions. Discuss contamination limitations.

## 9. Hint adoption

PENDING RUN: control and treatment adoption, paired adoption increase, denominators and
descriptive CIs. Do not call these monitor-validity estimates.

## 10. Answer switching

PENDING RUN: eligible items (control majority correct and wrong hint), eligible switched
items, majority-treatment-observed denominator, answer-switch rate and descriptive CI.

## 11. Missingness/ties

PENDING RUN: missing specifications, tie counts by condition, all-invalid conditions,
undefined denominators and paired availability. Never silently exclude or break ties.

## 12. Deviations

PENDING RUN: every interruption/change, date, reason, whether known before outcomes,
affected artifacts and human review. Never overwrite the planned protocol.

## 13. Limitations

Small locked model, one quantization/runtime, English only, n=50, contamination,
stochastic generation, paired-sample dependence and unavailable validated disclosure labels.
Report null/negative observations with the same prominence as positive ones.

## 14. What the pilot does NOT show

This pilot CANNOT establish the **Monitor-Validity Gap**, cross-lingual degradation,
Urdu monitor failure, translate-then-monitor recovery or frontier-model generalization.
Those require later native reference, validated monitors, language/translation design
and separately powered confirmatory evidence. No p-value or effect-size success claim.

## 15. Is the measurement instrumentation usable?

PENDING HUMAN REVIEW: assess completion, parsing, provenance, reproducibility and failure
visibility using the frozen infrastructure policies. Record usability limitations and
required repairs. Do not use favourable effect magnitude/direction to select models or
thresholds. Any policy amendment requires a dated decision before a new run.

## 16. Next stage

**STOP.** PENDING HUMAN REVIEW of judge calibration/human-reference design and ethics.
No automated judge, annotation, Urdu, translation or confirmatory work follows automatically.

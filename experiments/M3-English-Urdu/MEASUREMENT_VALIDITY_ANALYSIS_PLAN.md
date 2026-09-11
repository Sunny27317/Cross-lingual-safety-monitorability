# Measurement-validity analysis — prospective contracts

Engineering implementation: `clsm.downstream.analysis`, version downstream/1. Existing
behavioural metrics and generator design are unchanged. This document fixes implementation
semantics of recorded estimands; it does not choose final confirmatory populations,
thresholds, SESOI, N, acceptance rules or outcomes.

## Paired quantities and signs

For a trace i in the prospectively declared Urdu population, let Hᵢ be native-human
binary disclosure under an explicitly approved `LabelPolicy`, Dᵢ the direct English-centric
monitor on Urdu, and Tᵢ the **same judge specification** on its English translation.

- Primary Monitor-Validity Gap: mean(Hᵢ − Dᵢ) on complete native/direct pairs.
  Positive means lower automated positive detection than human positive detection;
  negative means more automated positives. It is a marginal detection gap, **not**
  disagreement: false positives and false negatives can cancel. Always report the
  confusion matrix, sensitivity/specificity, prevalence, agreement and missingness.
- Secondary translation recovery: mean(Tᵢ − Dᵢ) on the **same complete H/D/T triple set**.
  Equivalently mean(Hᵢ − Dᵢ) − mean(Hᵢ − Tᵢ), computed on that common set. Do not subtract
  gaps calculated from different available-case populations.
- Separate agreement recovery diagnostic: mean(1[Hᵢ = Tᵢ] − 1[Hᵢ = Dᵢ]) on those triples.
  This distinguishes increasing positive labels from improving human-reference agreement.
- English direct/paraphrase comparisons are separate controls, not pooled into Urdu
  recovery. Backtranslation and in-language judge comparisons are separately registered
  diagnostics, not replacement primary estimands.

These signs preserve D-059 and the M1 protocol's M3−M1 and M4−M1 notation. The historic
in-language arm M2 is not the primary direct comparator. Translation is not called a
mitigation before evidence supports it. A zero detection gap does not mean agreement;
a lack of recovery does not establish a generation-side information deficit.

## Population, pairing and missingness

Before scientific use, lock `TraceSet`, source-item clusters, inclusion rules, human
reference/annotation hashes, label policy, judge spec and translation specs. The implementation
aligns opaque IDs **and** text hashes, not row order. Duplicate, foreign or misaligned
traces, wrong judge/translator versions, mismatched rubric, invalid source lineage and
labels for unusable translations cause explicit refusal.

Missing source records and abstentions are not zero labels. Report absent reference,
direct and translated outputs, raw categories, pair/triple completeness, unavailable
translation IDs and denominators. Partial-label treatment is investigator-supplied;
cannot-tell/abstain remain missing. Report complete-pair gap and complete-triple recovery
populations separately. Missingness may be informative; complete-case estimates alone
do not establish unbiased population effects. Predeclare sensitivity/bounds procedures
before real label outcomes; none is selected automatically here.

This package analyzes disclosure measurement. A native-negative/monitor-negative trace
is agreement on nondisclosure, not proof of model unfaithfulness. Relating disclosure to
behavioural hint influence requires the existing frozen eligibility/switch definitions,
paired task evidence and their scientific limitations. Do not infer causal faithfulness
from textual labels alone or alter eligibility to increase the observed gap.

## Uncertainty and prospective confirmatory work

Optional `ResamplingPlan` resamples source **items**, retaining all traces/arms in each
cluster. The same cluster draw is used across paired contrasts. Alpha, replicates, seed
and decision record are required; intervals are absent otherwise. Report undefined
replicates and small/sparse-cluster limitations. Stratification/weighting/generalization
requires additional prospective design review; pooled trace-level intervals are not a
substitute for it. Exact independent-pair McNemar power is inappropriate for repeated
correlated traces; use explicitly justified cluster scenarios in the power tooling.

No p-value success criterion, automatic effect threshold or model/translator selection
uses these reports. Confirmatory N/SESOI, multiplicity, analysis population and hypothesis
test remain investigator decisions in M4. Pilot instrumentation success cannot establish
Monitor-Validity Gap, Urdu failure, translation recovery or frontier-model generalization.

## Reproducibility and output

`MeasurementBundle` includes original traces, private mapping, packet, raw annotations,
locked reference, judge spec/outputs and translation requests/records/specs. Preserve this
restricted bundle as immutable evidence. `measurement_envelope` validates it and binds
its hash plus all component hashes, policy, optional resampling plan and report provenance.
`deterministic_report` yields canonical JSON with an artifact hash. `write_new_report`
refuses existing destinations. Raw inputs are retained separately; a report hash is not
an access-control mechanism or permission to publish private annotations.

Synthetic tests cover perfect agreement, language-dependent misses, nondisclosure with
a correct monitor, recovery, degradation, missing labels, abstentions, corrupted lineage
and extraction separation. These tests demonstrate arithmetic/integrity, not scientific
instrument validity. **STOP before scientific analysis until the stage is authorized.**

# Separating reasoning disclosure from language-dependent monitoring failure in Urdu

**Paper scaffold — prospective methods; results pending.** No English pilot results
were inspected by the author of this scaffold. This text does not assert that a
scientific stage has or has not been executed elsewhere. It contains no generated
scientific findings, invented labels, selected judge/translator, or confirmatory claim.

## Abstract [RESULTS PENDING]

Reasoning traces can expose information useful to safety monitoring, but a monitor's
failure to detect explicit disclosure can arise from limitations of the monitor as well
as from the trace itself. We introduce a native-human-validated framework for separating
reasoning unfaithfulness from language-dependent monitor failure in Urdu, including a
same-trace translate-then-monitor diagnostic. Here, “native-human-validated” describes
the framework's required validation design, not a completed validation result. The
framework compares automated disclosure judgments with native human reference labels,
retains paired trace identity across translation, and reports translation-induced changes
alongside semantic-preservation audits. An English feasibility stage is separated from
monitor validation, Urdu collection and confirmatory inference. **Methods requiring
human decisions remain unresolved; results and conclusions will be written only after
authorized scientific stages and their evidence are available.**

## Introduction

An interpretable-looking explanation is not necessarily a faithful account of how an
answer was produced. Biasing interventions and reasoning-trace interventions motivate
empirical distinctions between textual explanation, behavioural influence and causal
faithfulness (Turpin et al., 2023; Lanham et al., 2023). Hint-based studies make a related
measurement question concrete: when an external suggestion influences the answer,
does the trace acknowledge it (Chen et al., 2025)?

Automating that judgment introduces another instrument whose validity must be assessed.
In cross-lingual work, lower observed disclosure may reflect differences in generation,
language access by the monitor, translation, or annotation rather than one mechanism
alone. We focus on Urdu and use native human judgments and paired measurement controls
to make these explanations distinguishable where the eventual evidence permits.
We make no priority claim and do not assume translation will improve measurement.

## Related Work

Turpin et al. study biasing features and unfaithful explanations in chain-of-thought
prompting. Lanham et al. investigate faithfulness through interventions on reasoning
traces. Chen et al. study acknowledgment of answer hints in paired hinted/unhinted
settings. Xiong et al. distinguish intra-draft and draft-to-answer faithfulness through
counterfactual interventions. Emmons et al. distinguish monitorability and faithfulness
in studying reasoning and monitoring. These works motivate careful operationalization;
none substitutes for native-language validation of the instrument used here.

This scaffold uses only citations verified in
[`literature/CITATION_VERIFICATION.md`](../literature/CITATION_VERIFICATION.md), sections
A.4–A.8. It does not add an outcome-dependent literature search or unverified numerical
comparison. The eventual manuscript must distinguish source-reported claims from this
study's results and audit citations again before publication if their use changes.

## Research Questions

The primary question is whether apparent automated monitoring failure on Urdu reasoning
traces reflects reasoning disclosure differences or language-dependent monitor limitations.
The primary estimand is the Urdu Monitor-Validity Gap: native-human positive disclosure
rate minus direct automated positive disclosure rate on the same traces. The secondary
same-trace diagnostic is translated-to-English automated detection minus direct automated
detection, with native-reference agreement recovery reported separately.

Positive, negative and null values all require interpretation alongside confusion matrices,
missingness and semantic-equivalence evidence. A zero marginal gap can hide opposing
false-positive and false-negative errors. Translation recovery is not assumed to be a
mitigation, and lack of recovery is not sufficient evidence of a generation-side deficit.

## Methods

MMLU remains the primary multiple-choice benchmark. Compatible UrduBench OpenBookQA
is a separately reported secondary robustness source; any UrduMMLU use remains contingent
on source, licensing and schema verification. The frozen English Track-A generator
configuration and authorization mechanism are preserved. Future aligned Urdu materials,
measurement specifications and confirmatory choices require separate prospective review.

The infrastructure binds repository/config/dataset/trace identities to raw human-label
provenance, judge and translator versions, rubric and analysis versions, seeds and artifact
hashes. Metadata-blinded packets use opaque trace IDs and seeded presentation order.
Strict Latin A–D answer extraction remains primary across languages; an exploratory
Perso-Arabic mapping is never used to repair primary extraction. Source-item clustering
preserves dependence across repeated samples and paired measurement arms.

## English Feasibility Pilot

The English stage is descriptive pipeline/instrument validation under its frozen protocol.
It does not establish Urdu monitor failure, a Monitor-Validity Gap, translation recovery,
or frontier-model generalization. **Pilot counts, diagnostics, accuracy, switching and
all outcomes are pending incorporation by an authorized researcher; none was read to
write this scaffold.** Any future feasibility-driven amendment must preserve its access
history and be separated from confirmatory decisions about scientific effects.

## Monitor Validation

Candidate judges are registered by exact provider/model/version, prompt, decoding and
rubric. A locked human reference and disjoint calibration/heldout source items support
candidate comparison. Confusion matrices, sensitivity/specificity, precision/recall/F1,
balanced accuracy, agreement, prevalence and defined uncertainty summaries are reported.
Kappa is diagnostic where appropriate; PABAK is optional. No model-size heuristic or
arbitrary acceptance cutoff is adopted. Candidate selection, reference staffing and
acceptance rules are **HUMAN REQUIRED** before scientific use.

## Urdu Study

Native-human validation is central, with language competence, rubric wording, blinding,
independent rating and adjudication documented prospectively. Direct automated and native
judgments remain aligned to the same exact trace. Nondisclosure is not automatically
causal unfaithfulness; behavioural influence evidence and established eligibility criteria
are necessary context. **Urdu population/config approval and scientific data are pending.**

## Translate-Then-Monitor

A translator-independent contract records full source/output hashes, language direction,
exact settings, errors and truncation. Urdu-to-English, English paraphrase, backtranslation
and native/bilingual equivalence audits address different measurement concerns. Direct
and translated monitoring use the same judge specification within a recovery comparison.
Disclosure omission, addition/explicitation and option changes are recorded, not assumed
absent. **Translator selection and all scientific translation results are pending.**

## Confirmatory Analysis

SESOI, sample size, nuisance assumptions, alpha, target power, multiplicity and the final
statistical procedure require investigator justification before confirmatory outcomes.
Prospective exact independent paired-binary calculations and explicitly assumed item-cluster
simulations support sensitivity analysis; they do not select N or SESOI automatically.
The confirmatory preregistration is an unfilled template, not a registered or approved
scientific design. **No confirmatory result exists in this scaffold.**

## Limitations

Human references are fallible and may be affected by language/register, ambiguity and
adjudication. Metadata blinding cannot conceal all cues present in the text. Translation
may change precisely the disclosure construct being measured. Missingness and abstention
may be informative. Version pinning cannot alone establish provider stability or semantic
equivalence. Controlled benchmark cues and textual acknowledgment do not reveal hidden
cognition or establish universal safety-monitor validity. Model/task/language scope limits
generalization, especially to frontier systems. Synthetic tests validate software, not
these scientific assumptions.

## Ethics

Institutional determination, consent/compensation, harmful-content exposure, privacy,
retention and release policy require human review. Public benchmark status does not by
itself resolve these obligations. Pseudonymization and hashes do not remove personal
information from free text. See the [governance checklist](../docs/ETHICS_AND_DATA_GOVERNANCE_CHECKLIST.md).
No legal or IRB finding is asserted.

## Reproducibility

The [downstream API guide](../docs/DOWNSTREAM_INFRASTRUCTURE.md) describes strict contracts,
canonical hashing, blinded assignments, reference lineage, paired analysis and exclusive
report publication. The synthetic end-to-end pipeline can be run without model access,
datasets, scientific results or human annotations. Future scientific artifact access and
release require separate governance and authorization. A paper release must include exact
run identifiers and approved evidence, not substitute fixture hashes for scientific ones.

## Results [PENDING]

**No results written.** Planned tables and figures are in their respective directories.
Do not insert invented estimates, representative-looking outputs or synthetic labels.

## Discussion [PENDING]

Interpretation must follow validated evidence, including alternative mechanisms,
measurement error, missingness and negative findings. No success claim is prewritten.

## Conclusion [PENDING]

No empirical conclusion is available in this scaffold.

## References

- Turpin, M., Michael, J., Perez, E., & Bowman, S. R. (2023).
  [Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting](https://arxiv.org/abs/2305.04388). NeurIPS 2023.
- Lanham, T., et al. (2023).
  [Measuring Faithfulness in Chain-of-Thought Reasoning](https://arxiv.org/abs/2307.13702).
- Chen, Y., et al. (2025).
  [Reasoning Models Don't Always Say What They Think](https://arxiv.org/abs/2505.05410).
- Xiong, Z., Chen, S., Qi, Z., & Lakkaraju, H. (2025).
  [Measuring the Faithfulness of Thinking Drafts in Large Reasoning Models](https://arxiv.org/abs/2505.13774). NeurIPS 2025.
- Emmons, S., et al. (2025).
  [When Chain of Thought is Necessary, Language Models Struggle to Evade Monitors](https://arxiv.org/abs/2507.05246).

# Post-English pilot execution plan

Status: **PROSPECTIVE, OUTCOME-BLIND AUDIT.** This plan was prepared from the merged
main tree (`9ce491f7b6fb4dd4426168499a09b3c0b7e6f758`) in a separate worktree. It does
not inspect the active PR #19 checkout, `generations.jsonl`, raw outputs, intermediate
outcomes, or the active process. It is a dependency plan, not permission to start any
downstream scientific stage.

## Dependency chain

```text
English pilot integrity review
        ↓
instrumentation/eligibility decision
        ↓
judge selection freeze
        ↓
human-reference protocol freeze
        ↓
judge calibration
        ↓
Urdu dataset/native validation
        ↓
Urdu inference
        ↓
translation diagnostic
        ↓
Monitor-Validity Gap + recovery analysis
        ↓
confirmatory design freeze
        ↓
confirmatory experiment
        ↓
paper results/discussion
```

The arrows are gates. Later stages must not be started because an earlier stage produced
a convenient result. Every scientific artifact must bind the relevant repository/config,
dataset, trace, rubric, judge/translator, provenance and analysis hashes.

## Stage gates

| Stage | Status | What is ready | Required decision or blocker |
|---|---|---|---|
| English pilot integrity review | **PARTIALLY READY** | Frozen Track-A executor, plan, pin schema, completion-manifest validator, descriptive analyzer, and report template | The authorized run must finish or be explicitly documented as incomplete. Independently verify 800 unique spec identities, raw-artifact inventory, completion manifest, commit/config/dataset hashes, dirty state, timeout/parse/UNKNOWN accounting, and no duplicate/missing records. Do not select later scientific instruments from effect direction or magnitude. |
| Instrumentation/eligibility decision | **PARTIALLY READY** | Existing Track-A parser, behavioral metric definitions, zero-retry policy, collision policy, and descriptive report structure | Investigator decides whether completion, parsing, stop-reason visibility, provenance, and eligibility rules are usable. Preserve all failures and missingness. A pilot can inform feasibility/deviation documentation; it cannot silently redefine metrics, eligibility, or the primary question after outcomes are seen. |
| Judge selection freeze | **BLOCKED** | `JudgeSpec`, strict `JudgeInput`/`JudgeOutput`, label normalization, candidate comparison, common-coverage reporting, and calibration/heldout templates | Register candidates with immutable provider/model/version, prompt, decoding, rubric and identity evidence. Investigator must approve construct, calibration/heldout item-level split, missingness/abstention policy, uncertainty method, error tradeoffs, and any acceptance rule before judge outputs are observed. No model-size, BA/F1/PABAK/kappa threshold or automatic winner is implemented. |
| Human-reference protocol freeze | **BLOCKED** | Blinded packet generation, randomized seeded order, annotation schema, provenance validation, adjudication lineage, and inter-rater metrics | Human reviewers must approve rubric wording (including Urdu), partial/cannot-tell/abstain policy, rater competence, overlap/counts, adjudicator roles, consent/compensation, exposure safeguards, governance, and release/storage. Codex/Claude cannot fabricate labels, competence, consensus, or ethics approval. |
| Judge calibration | **BLOCKED** | Offline `candidate_comparison` and agreement metrics: confusion matrix, sensitivity/recall, specificity, precision, F1, balanced accuracy, raw agreement, prevalence, kappa where defined, optional PABAK diagnostic, and explicit intervals | Lock a human reference and disjoint calibration/heldout source-item sets first. Run only after the candidate plan and acceptance decision are frozen. Review all candidate coverage, abstentions and common complete-set metrics; freeze one candidate or select none before heldout evaluation. |
| Urdu dataset/native validation | **BLOCKED** | Generic four-choice adapter validates exact choice order, answer mapping, language, immutable revision, provenance, stable IDs and content hash. MMLU remains primary; UrduBench OpenBookQA is secondary only if compatible; UrduMMLU is unverified. Latin A–D extraction is primary and Perso-Arabic mapping is exploratory/separate. | Verify source/license/schema, exact English-item relationship or predeclared Urdu population, prompt/cue equivalence, language/register policy, item IDs and content pin. Native/bilingual reviewers must approve the rubric and validation plan. No Urdu model/language suitability choice is frozen by this code. |
| Urdu inference | **BLOCKED** | Protocol and data contracts exist; no Urdu executor is provided | Requires approved dataset/design, validated direct judge, native reviewers, governance determination, frozen Urdu config/seed/decoding, and separately scoped human authorization. English generator authorization does not authorize Urdu. |
| Translation diagnostic | **BLOCKED** | Translator-agnostic `TranslatorSpec`/`TranslationRecord`, source/output/parent hashes, truncation/error checks, Urdu→English, English paraphrase, backtranslation and equivalence-audit structures | Select translator prospectively using immutable identity, complete-input capacity/context accounting, deterministic settings, semantic/disclosure preservation controls and human review. NLLB, a context threshold, or a favorable recovery result is not selected. Native/bilingual equivalence audit and governance are required before translation. |
| Monitor-Validity Gap + recovery analysis | **PARTIALLY READY** | `measurement_report` preserves same-trace pairing and common triples. Primary gap is native-human detection minus direct automated detection; recovery is translated-minus-direct detection. Agreement recovery, missingness and controls are separate. | Requires completed native reference, validated judge, aligned Urdu traces, usable translations, and the same judge spec for direct/translated labels. Report confusion and agreement, not just marginal rates. A zero marginal gap can hide opposing errors; recovery is not called mitigation without evidence. |
| Confirmatory design freeze | **BLOCKED** | Power utilities accept investigator-supplied SESOI, alpha, target power, joint paired probabilities, missingness, ICC, clustering and seeds; exact paired and cluster-simulation sensitivity are available | Investigator/statistical reviewer must choose estimand/test, SESOI, independent-item N, nuisance/ICC/missingness assumptions, alpha, target power, multiplicity, robustness and preregistration. Pilot effect magnitude must not choose SESOI or N automatically. |
| Confirmatory experiment | **BLOCKED** | Templates and robustness inventory exist | Requires registered, approved design, frozen judge/reference/translation procedures, governance, resources, and fresh stage-specific authorization. No confirmatory execution is in this package. |
| Paper methods/governance | **PARTIALLY READY** | Paper scaffold, verified repository citations, methods/provenance/governance text, figure/table plans and pending-result markers | Methods can be finalized from frozen protocols and verified literature. Ethics claims, model/provider choices and language equivalence remain conditional on review. |
| Paper Results/Discussion/Conclusion | **BLOCKED** | Section placeholders explicitly remain pending | Must use only verified artifacts and approved analysis. Do not write monitor-failure, recovery, causal-faithfulness, or confirmatory conclusions from the English pilot alone. |

## Judge stage audit

The implemented interfaces are data contracts, not judge executors. `JudgeSpec` requires
provider, model, immutable version, prompt, rubric version, decoding and identity evidence.
`JudgeInput` allows only an opaque ID, language, exact text/hash and rubric version; it
does not expose model, condition, correctness, human labels, other judge outputs or
outcome fields. `JudgeOutput` binds input hash, judge-spec hash, rubric, normalized label,
confidence, raw-response hash, error and provenance. Candidate comparison rejects unknown
versions, duplicate/unassigned outputs, item/text leakage between calibration and heldout
sets, and mismatched reference/policy hashes. Reports retain abstention and coverage and
return `selected_candidate: null`.

Before any output is observed, freeze the construct wording, registered candidate list,
human-reference protocol, item-cluster split, label policy, missingness, uncertainty and
acceptance decision record. The code has no unsupported fixed threshold; kappa and PABAK
are diagnostics, not gates. Human reviewers decide the error tradeoff and whether the
instrument is fit for the intended population.

## Human validation audit

Annotation records require opaque ID, text hash, annotator pseudonym, round and rubric
versions, disclosure category, confidence, uncertainty, rationale, adjudication status,
and provenance. Packets are HMAC-blinded and seeded-randomized; the steward-only mapping
keeps trace IDs/item IDs separate from the annotator export. The guide says not to show
model, condition, correctness, automated labels, other annotations, or desired outcomes.
Textual cues cannot always be hidden and must be recorded as limitations.

Independent annotations remain immutable. Adjudication references source annotation hashes,
adjudicator pseudonym and decision record; unresolved cases remain explicit. Inter-rater
reports use the approved label policy and item-cluster pairing, with no arbitrary agreement
cutoff. Native Urdu speakers or qualified bilingual reviewers are required for Urdu
disclosure judgments and equivalence work; their qualification, recruitment, compensation,
consent, safety and institutional determination cannot be automated by this repository.

## Urdu and extraction audit

MMLU remains the primary benchmark; UrduBench OpenBookQA is only a compatible secondary
robustness source, and UrduMMLU remains a candidate pending provenance/license/schema review.
The adapter preserves four choices in exact order and requires an explicit answer mapping.
The primary Latin A–D parser remains unchanged. Perso-Arabic markers are exploratory and
must be published with separate denominators; they cannot repair an ambiguous primary
parse. Freeze the Urdu source relation, revision/content hash, prompt/cue equivalence,
source-item clusters, language/register policy, native rubric and missingness before Urdu
outputs are available.

## Translation and estimand audit

Translator selection remains unresolved. `TranslatorSpec` records provider/model/version,
context limit and accounting, direction, decoding, prompt, determinism and evidence.
`TranslationRecord` binds root/source/request/output hashes, settings, truncation/errors
and provenance; backtranslation binds parent lineage. Urdu→English, English→English
paraphrase, backtranslation and native/bilingual audit are separate controls. A failed or
truncated translation is preserved but unusable for the paired primary comparison.

The committed downstream analysis agrees with D-059: primary Monitor-Validity Gap is
native-human disclosure detection minus direct automated detection on matched traces;
secondary recovery is translated-to-English automated detection minus direct automated
detection on the same complete triples. Behavioral hint adoption/answer switching are
supporting Track-A quantities; parsing, stop reasons, truncation, ties and missingness are
diagnostics. A historical M1 protocol shorthand uses M3−M1 and M4−M1; the downstream
analysis makes the common-triple denominator and agreement-recovery distinction explicit.
This is a documentation clarification, not a redefinition based on pilot outcomes.

## Confirmatory design audit

Legitimate pilot inputs are limited to predeclared feasibility quantities or explicitly
approved nuisance ranges (for example, completion/missingness and cluster structure), and
only if the investigator decides in advance how they inform planning. An observed effect,
direction, switch rate, accuracy, parse rate, or favorable gap cannot automatically choose
SESOI, N, a threshold, a judge, or a translator. SESOI requires independent substantive
justification. N must be frozen from the approved estimand/test, alpha, target power,
independent-item clustering, missingness, nuisance/reference-error assumptions and
statistical review. Multiplicity and robustness analyses must be written in the
preregistration; the existing robustness template does not silently select them.

## What can be written now

Methods, data/provenance contracts, stage boundaries, governance requirements, the
validated literature framing, and the exact non-outcome estimand definitions can be
written now. Results, outcome-dependent Discussion, claims that a monitor fails in Urdu,
claims that translation recovers safety signal, causal-faithfulness claims, and the
Conclusion must remain blank until the relevant authorized stages are complete and
reviewed. The English pilot alone cannot establish the Monitor-Validity Gap or recovery.

## Required handoff order

1. Complete an outcome-blind integrity review of the English run and separately decide
   instrumentation/eligibility usability.
2. Freeze judge candidates, human rubric/reference procedure, acceptance policy and
   calibration/heldout manifests before candidate outputs.
3. Lock human reference and calibrate/validate the judge; select none if the policy is
   not met.
4. Verify the Urdu dataset relationship, source/license/content pin, native protocol and
   governance; authorize Urdu separately.
5. Register translator/control/equivalence criteria, select only after review, and run
   the translation diagnostic only after Urdu traces and human reference are available.
6. Compute the frozen Gap/recovery estimands with paired denominators and diagnostics.
7. Freeze confirmatory design and preregister it independently of observed effect size.
8. Run confirmatory work only under new stage-specific authorization, then populate the
   paper's Results/Discussion/Conclusion.

At each gate, preserve failures, abstentions, missingness and deviations. No stage in this
document launches another stage automatically.

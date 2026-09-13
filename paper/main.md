# Monitor or Model? A Native-Urdu-Anchored Test of Automated Chain-of-Thought Monitoring Validity

**Paper scaffold — pre-results scientific draft.** The English feasibility pilot
(PR #19, not yet merged) is complete and its descriptive numbers are reported below
accurately, exactly as published in its own integrity-reviewed report. No Urdu, judge,
translation, human-annotation, or confirmatory result exists anywhere in this document.
This text does not assert that any of those stages have or have not begun elsewhere.

## Title options

**Recommended:** *Monitor or Model? A Native-Urdu-Anchored Test of Automated
Chain-of-Thought Monitoring Validity.* States the actual question (is it the monitor or
the model's behavior?), names the method (native-Urdu-anchored), and names the object
(automated CoT monitoring validity) without asserting a direction or a "first" claim.

**Alternative 1:** *Separating Reasoning Disclosure from Language-Dependent Monitor
Failure: A Native-Urdu Validation Study.* Closer to the original working title; slightly
more technical, foregrounds the measurement-validity framing over the question framing.

**Alternative 2:** *Same Trace, Different Language: Testing Automated Safety-Monitor
Validity Against Native Urdu Judgments.* Emphasizes the same-trace design most directly;
reads less like a question, more like a method label.

All three avoid "first," avoid asserting monitors fail in Urdu, and avoid implying
access to private cognition. Final choice should wait until Results exist, since a
title implying a direction would itself be a premature claim.

## Abstract [structured pre-results draft]

**Problem.** Automated monitors are increasingly used to check whether a model's
visible reasoning discloses reliance on information it should not use unquestioningly —
here, an explicit answer hint. A monitor that reports low disclosure on a reasoning
trace could be right about the model, or could itself be failing to read the trace,
especially when the trace is in a language the monitor handles less well than English.
**Gap.** Prior multilingual chain-of-thought work documents that monitoring quality and
faithfulness measurements vary across languages, and at least one adjacent system
already tests translate-then-monitor recovery in a different language pair; none of the
inspected prior work combines a native-human-anchored reference, a same-trace
translate-then-monitor diagnostic, and explicit rewriting-artifact controls for Urdu
specifically [PLACEHOLDER: recheck at submission time against `literature/
CITATION_VERIFICATION.md` and `research/POST_PILOT_METHODS_DECISIONS.md` §I for any
newly published closer work]. **Method.** We separate an English feasibility stage from
a native-Urdu measurement stage. In the English stage — complete — 50 MMLU items were
generated under a misleading-hint paradigm (control vs. treatment, 8 samples each, 800
generations total) to validate the pipeline's parsing, provenance, and behavioral
instrumentation. In the (not yet executed) Urdu stage, native Urdu speakers will provide
a blinded disclosure reference on Urdu reasoning traces; an automated monitor will score
the same traces directly and after locked translation to English, using one shared judge
specification; English-original and English-paraphrase control arms bound
rewriting-only effects. **Contribution.** [PLACEHOLDER: fill only from executed
stages] a controlled, source-trace-matched measurement of automated-monitor detection
relative to a native-human reference, and of whether that detection changes after
translation, with the translation's own semantic and disclosure preservation audited
rather than assumed. **English feasibility result (observed, descriptive only).** All
800 planned generations completed with 787/800 (98.4%) validly parsed; the pipeline's
behavioral instrumentation (answer-switch rate 6/35 = 0.1714, 95% descriptive interval
[0.057, 0.314]) is reported for pipeline-validation purposes only and is not evidence
about Urdu, monitor validity, or translation recovery. **Limitations.** One quantized
1.7B-parameter open-weight model, one benchmark family, one hint design, one language
pair; disclosure is a textual, not causal-cognition, construct; human and automated
references are both fallible. [PLACEHOLDER: Urdu-stage limitations once executed.]

## Introduction

Chain-of-thought output is often used as if it were a window onto a model's actual
decision process, including for safety-relevant oversight: if a model relied on
something it should disclose — an unearned hint, a leaked answer, a biased cue — an
observer hopes the visible reasoning will say so. This hope is only as good as two
separate things holding at once: that the model's visible text actually reflects what
influenced it (a faithfulness question), and that whatever automated system reads that
text can correctly recognize disclosure when it is present (a monitor-validity
question). Prior work has shown the first can fail even in English (Turpin et al., 2023;
Lanham et al., 2023; Chen et al., 2025). This project is about the second question, and
about a case where the two are easy to conflate: **when an automated monitor reports low
disclosure on a non-English reasoning trace, is that because the model did not disclose,
or because the monitor could not read the disclosure that was there?**

**Why this matters for safety monitoring.** An oversight pipeline that silently degrades
outside English would create a false sense of security precisely where verification is
hardest to double-check locally. If the degradation is in the monitor, the fix is a
better or better-calibrated monitor; if it is in the model's behavior, the fix is
elsewhere entirely. Treating the two as interchangeable risks either over-trusting a
broken monitor or over-concluding that a model behaves worse in other languages than it
actually does.

**Why language shift specifically.** Multilingual evaluation work increasingly shows
that LLM judges and multilingual reasoning quality do not transfer uniformly across
languages even when the underlying task is held fixed (see Related Work). That
literature motivates treating "the monitor's own competence in this language" as a
variable to be measured, not assumed away.

**Why native-human validation.** An automated judge cannot certify its own validity.
The only direct way to know whether a monitor's disclosure label is right is to compare
it against a reference produced by someone who can actually read the trace natively —
not a back-translation, not the same automated system in a different guise, and not the
investigators' own guess at what the text says.

**Why Urdu.** Urdu is written in a distinct (Perso-Arabic, right-to-left) script,
supports substantial English code-switching in technical registers, has enough existing
model support to produce reasoning traces worth evaluating at all, and — unlike several
higher-resource languages — has not yet been the subject of a native-anchored,
same-trace translate-then-monitor study in this literature as of the last review
(`research/POST_PILOT_METHODS_DECISIONS.md` §I). It is a genuinely useful test case for
the monitor-vs-model question, not chosen because it is expected to show a larger or
more publishable gap; the design and its acceptance criteria are frozen before any Urdu
output is observed (`research/FINAL_PROTOCOL.md`).

This paper's research questions, contributions, and estimands are stated precisely in
Research Questions, below; the short version is: we ask whether a Monitor-Validity Gap
exists between native-human and direct-automated Urdu disclosure detection, and whether
translating the trace to English before monitoring changes that detection, while
explicitly auditing translation as a candidate confound rather than assuming it is a fix.

## Related Work

**CoT faithfulness.** Turpin et al. (2023) and Lanham et al. (2023) establish that
visible reasoning can misrepresent what actually drove a model's answer. Chen et al.
(2025) operationalize disclosure of an external hint as a measurable behavior in paired
hinted/unhinted settings — the paradigm this project's English pilot and Urdu design
both use. Xiong et al. (2025) and Emmons et al. (2025) further separate distinct notions
of faithfulness and monitorability from one another. None of this work asks whether an
*automated reader* of the reasoning trace is itself a valid instrument outside English;
that is this project's specific gap, not a claim that faithfulness itself is unstudied.

**Multilingual reasoning and multilingual LLM-as-judge validity.** Independently
verified prior work (`literature/CITATION_VERIFICATION.md`) documents that multilingual
chain-of-thought performance, consistency, and monitoring degrade unevenly across
languages (Zhao et al., 2026; Yang et al., 2026), and that LLM-judge reliability
established in one language does not transfer automatically to another (Doğruöz et al.,
2026). Onyame et al. (2026) report large-scale evidence of CoT monitoring fragility
across typologically diverse languages using manual inspection, without a native-human
reference, a translate-then-monitor diagnostic, or Urdu. **We do not claim multilingual
monitoring degradation is a new finding** — Onyame et al. and the broader multilingual
CoT-faithfulness literature already establish that. What is not yet established is
whether, for a specific language and monitor, an apparent gap is a monitor-competence
problem, a translation problem, or a genuine behavioral difference, tested on the same
traces with a native reference.

**Translation-based monitoring.** Ercolano's *DialectShift-Monitor* is the closest
adjacent system: it already implements translate-then-monitor recovery (for
Spanish/Spanglish dialect shift, not Urdu) with crowdsourced human semantic-adequacy
validation. **We do not claim translate-then-monitor itself is novel** — this prior
system already does it, for a different language pair and with a different human
validation design (crowdsourced adequacy rating rather than adjudicated
native-competent disclosure labeling). Alfano et al. (2026) similarly use translation
baselines for multilingual faithfulness evaluation, without the same-trace disclosure
construct used here.

**What this leaves as the contribution.** Combining, for Urdu specifically: (1) a
native-human-anchored disclosure reference produced by qualified, adjudicated raters
rather than crowdsourced adequacy scoring; (2) a same-trace translate-then-monitor
diagnostic using one fixed judge specification for both direct and translated scoring;
(3) an explicit English-original anchor and English-to-English paraphrase control
separating "translation changed the language" from "rewriting changed the text." No
single inspected prior source combines all three for this language. This is a
**measurement-validity contribution**, not a claim of discovering monitor failure, and
the novelty status is **YELLOW**: adjacent, materially overlapping work exists, and this
project's claim is narrowed accordingly (full citation-by-citation positioning in
`research/POST_PILOT_METHODS_DECISIONS.md` §I and `research/
SCIENTIFIC_LEAD_FINAL_AUDIT.md` §5; both reaffirmed unchanged here).

This section uses only citations verified in
[`literature/CITATION_VERIFICATION.md`](../literature/CITATION_VERIFICATION.md). The
eventual manuscript must re-audit any citation whose use changes before submission.

## Research Questions

Full formal definitions live in `research/FINAL_PROTOCOL.md` §4 (statistical plan) and
`research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` (D-073); this section is the canonical
paper-facing statement, consistent with both, introducing no new estimand.

### Primary RQ

**Question:** Does automated direct disclosure detection on Urdu reasoning traces match
a native-human disclosure reference?
**Construct:** Explicit textual acknowledgment of reliance on an external answer hint
(the frozen five-category rubric: `disclosed`/`not_disclosed`/`partial`/`cannot_tell`/
`abstain`; binary mapping `disclosed=1`, `not_disclosed=0`, `partial` excluded,
`cannot_tell`/`abstain` missing).
**Estimand:** `G = mean(H − D)` over complete native-human/direct-automated pairs on
matched Urdu traces.
**Evidence required:** a locked native-human reference; a calibrated, accepted
automated judge scoring the identical traces; the full confusion matrix (not just the
marginal `G`), reported alongside missingness.
**Would count as support (for a Monitor-Validity Gap claim):** a confirmatory-sample
estimate of `G` with an interval excluding the investigator's independently justified
SESOI, interpreted jointly with the confusion matrix — not a bare nonzero point estimate.
**Would NOT count as support:** a nonzero `G` from an unvalidated or uncalibrated judge;
a gap computed on a different population than the one used for `R`; a gap attributed to
"the model" without confusion-matrix evidence that the errors are asymmetric rather than
cancelling.

### Secondary RQ

**Question:** Does scoring the same Urdu trace's locked English translation, with the
same judge specification, change automated detection?
**Construct:** identical disclosure construct as the primary RQ, applied to a rendered
(translated) text rather than the original.
**Estimand:** `R = mean(T − D)` over the common complete native/direct/translated (H/D/T)
triple population; a separate agreement-recovery diagnostic
`mean(1[T=H] − 1[D=H])` is exploratory, not a replacement for `R`.
**Evidence required:** everything the primary RQ requires, plus a locked translator
specification, a bilingual/native translation-adequacy and disclosure-preservation
audit, and — for any interpretation of `R` as evidence of a *language-specific*
mechanism — an English-original human anchor and an English-to-English paraphrase
control on matched items (MUST HAVE per `research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` item
15; enforced in code per `research/FINAL_PROTOCOL.md` §1).
**Would count as support (for "language limitation, not just rewriting"):** `R`
materially nonzero in the direction of improved detection, **and** improved agreement
with the native reference (not just more positive labels), **and** the paraphrase
control on the English anchor showing a materially smaller effect than `R` itself, **and**
the translation-artifact audit not attributing the change to added/omitted disclosure.
**Would NOT count as support:** `R` nonzero without an improvement in native-reference
agreement (more false positives, not better detection); an English paraphrase control
showing a similar-sized effect (generic rewriting, not language); an unaudited or
partially-audited translation population.

### Exploratory RQ

**Question:** Where the automated monitor and the native-human reference disagree,
does translation change *which* traces they agree on (not just the marginal rate)?
**Construct:** same disclosure construct, analyzed as a match/mismatch indicator per
trace rather than a rate.
**Estimand:** the agreement-recovery diagnostic `mean(1[T=H] − 1[D=H])` on H/D/T triples.
**Evidence required:** the same H/D/T triples as the secondary RQ.
**Would count as informative (this RQ is diagnostic, not confirmatory — it does not
"support" or "fail to support" a hypothesis in the primary/secondary sense):** a
pattern distinguishing which specific traces flip agreement, cross-referenced against
the translation-artifact audit's per-trace findings.
**Would NOT count as support for anything on its own:** this diagnostic is never
reported as if it were `R`, and never used to select which traces belong in the primary
or secondary populations.

**No new primary outcome is introduced by this section.** `G`, `R`, and the agreement
diagnostic are exactly as frozen in D-073/D-059/D-070; this section only adds the
construct/evidence/support structure the completion-phase task requested.

## Methods

**Study overview.** Two stages, gated in sequence: (1) an English feasibility pilot
validating the shared generation pipeline (complete); (2) a Urdu measurement stage
(not yet authorized) collecting native-human reference labels, automated direct and
translated monitor labels, and translation-artifact audits on the same traces. Stage 2
does not begin until the human-only decisions in `research/
SUPERVISOR_DECISION_PACKET.md` are resolved.

**Source items.** 50 items drawn from `cais/mmlu` (revision
`c30699e8356da336a370243923dbaf21066bb9fe`), 10 subjects × 5 items, frozen dataset
content hash `db93be51bc72ea852d50a816f835d5822e4241ddb5039102fa46e91a5c98d399`. MMLU is
the primary benchmark; compatible UrduBench OpenBookQA items are a secondary,
separately reported robustness source; UrduMMLU remains an unverified candidate.

**Misleading-hint paradigm.** Each item is generated under two conditions: an unhinted
control and a treatment condition carrying an explicit, misleading answer hint
attributed to an external authority. The behavioral quantities (answer-switch rate,
hint adoption) follow Chen et al.'s (2025) paired hinted/unhinted design; the disclosure
construct (does the trace *say* it used the hint) is separate from whether the trace's
*answer* changed.

**Generation design.** `Qwen/Qwen3-1.7B` (GGUF `Qwen3-1.7B-Q8_0.gguf`, SHA-256
`061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`) via llama.cpp
(commit `5266f24da75dc449bd56cbed7addb9c8e4a6a73e`, build 10809); temperature 0.6,
top-p 0.95, top-k 20, 8 samples per condition per item, seeds 0–7, max 16,384 new
tokens, 900 s timeout, zero-retry policy. 50 items × 2 conditions × 8 samples = 800
generations for the English stage. Any Urdu generation stage uses a structurally
identical, separately authorized configuration — English authorization does not extend
to Urdu.

**Urdu equivalence process.** Forward translation of each matched item and the shared
hint by a competent translator, followed by independent bilingual review of every item
and the shared prompt/cue, discrepancy classification, and adjudication before content
lock (`docs/URDU_ITEM_EQUIVALENCE_FORM.md`; procedure in `experiments/M3-English-Urdu/
URDU_PROTOCOL.md`). No item is used until its form is complete.

**Human annotation.** Two independent native/near-native Urdu readers with strong
written English, plus an independent adjudicator, label the complete reasoning trace
under the frozen five-category rubric, blinded to condition, generator, answer key, and
automated labels, with randomized presentation order and preserved original labels
(`docs/HUMAN_URDU_VALIDATION_PACKAGE.md`; operational packet in `docs/rater_package/`).

**Automated monitor.** One judge specification (candidate shortlist: GPT-5.4 primary,
Claude Sonnet 4.6 backup — closed shortlist, final selection pending calibration),
scoring one trace per request under the identical English-language rubric construct,
calibrated against the locked human reference on an item-disjoint calibration split
before heldout evaluation (`experiments/M2-Monitor-Validation/
JUDGE_VALIDATION_PROTOCOL.md`; rubric package in `experiments/M2-Monitor-Validation/
JUDGE_RUBRIC_PACKAGE.md`).

**Translation diagnostic.** The same locked Urdu trace is translated once to English by
one locked translator specification and scored by the identical judge specification
used directly, producing `T`. A bilingual/native audit checks semantic adequacy,
disclosure preservation, omission, addition/explicitation, polarity, option
preservation, and truncation on every translated trace in the declared primary sample.

**English paraphrase control.** For every English-original anchor trace, an
independently specified English-to-English rewrite is produced and scored identically,
bounding generic-rewriting sensitivity separately from translation/language effects
(MUST HAVE for any language-mechanism interpretation of `R`; `research/
FINAL_PROTOCOL.md` §1).

**Matching rules.** A trace's identity key is `(source_item_id, condition, language,
seed, generation_id)`; `H`, `D`, and `T` share this key with `language="ur"` throughout
(identifying the same source trace; a separate `judge_input_language` field records
what was actually scored). The paraphrase record `P` matches its anchor by
`(source_item_id, condition, seed)` only, since it is a deliberate rewrite
(`research/FINAL_PROTOCOL.md` §§1–2).

**Missingness.** Every stage reports planned, evaluable, complete, and missing counts by
reason (`cannot_tell`, `abstain`, translation failure, judge error). Complete-case
estimates are labeled as targeting the available, not planned, population; missing
values are never imputed as zero or negative disclosure.

**Statistical analysis.** Source-item is the clustering unit; `G` and `R` use
trace-weighted item-cluster percentile bootstrap intervals descriptively; the
confirmatory test/interval requires the simulation validation in `research/
FINAL_PROTOCOL.md` §3 before use. Full plan in `research/FINAL_PROTOCOL.md` §4.

**Confirmatory separation.** Descriptive reporting (coverage, calibration, audits,
bootstrap intervals) is distinguished throughout from the single preregistered
confirmatory test, which runs once against a preregistered N, SESOI, alpha, and
multiplicity rule, none of which is chosen from pilot or pre-preregistration Urdu data
(`experiments/M4-Confirmatory/CONFIRMATORY_PREREG_TEMPLATE.md`).

**Reproducibility.** Every artifact binds git commit, config hash, dataset content hash,
judge/translator spec hash, rubric version, and seeds (`docs/
DOWNSTREAM_INFRASTRUCTURE.md`). The synthetic end-to-end pipeline runs without model
access, real datasets, or human data, for engineering validation only.

**Ethics.** See Ethics, below.

## English Feasibility Pilot (observed, descriptive; complete)

**Status.** The frozen English pilot (`experiments/M1-Mac-Feasibility/PILOT_REPORT.md`,
committed on PR #19, which remains open and unmerged) reports complete: 800/800
generations present, 0 missing/duplicate/extra, integrity verdict **PASS WITH
DOCUMENTED LIMITATIONS**. The numbers below are transcribed exactly from that
integrity-reviewed report — not recomputed, not inspected from raw output by the author
of this paper draft, and not evidence for any Urdu, monitor-validity, or translation
claim. They validate the shared pipeline's parsing, provenance, and behavioral
instrumentation only.

| Quantity | Value | 95% descriptive interval |
|---|---:|---:|
| Valid parsed generations | 787 / 800 (98.375%) | — |
| Parse-invalid (5 `AMBIGUOUS`, 8 `NO_ANSWER`, 0 `PARSE_ERROR`) | 13 / 800 | — |
| Unhinted accuracy | 36 / 50 = 0.7200 | [0.600, 0.840] |
| Hinted accuracy | 29 / 49 = 0.5918 | [0.449, 0.735] |
| Control adoption | 5 / 50 = 0.1000 | [0.020, 0.180] |
| Hinted adoption | 13 / 49 = 0.2653 | [0.143, 0.388] |
| Adoption increase | 8 / 49 = 0.1633 | [0.061, 0.265] |
| **Answer-switch rate** | **6 / 35 = 0.1714** | **[0.057, 0.314]** |

Stop reasons were `UNKNOWN` for all 800 generations — a documented, honest limitation of
the pinned llama.cpp build's default stderr signal, not evidence of truncation
(`literature/DECISION_LOG.md`, PR #19's entry, pending merge-time renumbering). The
three disclosure-dependent quantities (`disclosure_rate`, `hidden_influence_rate`,
`conditional_hidden_influence_rate`) are correctly **not estimable** at this stage: they
require judge or human labels that do not yet exist. English feasibility gate: **PASS
WITH LIMITATIONS**. This is a pipeline/behavior feasibility conclusion, not evidence for
the Urdu hypothesis, monitor validity, or translation recovery.

## Monitor Validation

Candidate judges are registered by exact provider/model/version, prompt, decoding and
rubric. A locked human reference and disjoint calibration/heldout source items support
candidate comparison. Confusion matrices, sensitivity/specificity, precision/recall/F1,
balanced accuracy, MCC, agreement, prevalence and defined uncertainty summaries are
reported. Kappa is diagnostic where appropriate; PABAK is optional. No model-size
heuristic or arbitrary acceptance cutoff is adopted; the numeric acceptance criteria are
signed by the investigator before any candidate output exists
(`experiments/M2-Monitor-Validation/JUDGE_SELECTION_RECORD_TEMPLATE.md`). **Candidate
selection, reference staffing and acceptance rules are HUMAN REQUIRED before scientific
use.**

## Urdu Study

Native-human validation is central, with language competence, rubric wording, blinding,
independent rating and adjudication documented prospectively and packaged for real
raters (`docs/rater_package/`). Direct automated and native judgments remain aligned to
the same exact trace. Nondisclosure is not automatically causal unfaithfulness;
behavioural influence evidence and established eligibility criteria are necessary
context. **Urdu population/config approval and scientific data are pending.**

## Translate-Then-Monitor

A translator-independent contract records full source/output hashes, language
direction, exact settings, errors and truncation. Urdu-to-English, English paraphrase,
backtranslation and native/bilingual equivalence audits address different measurement
concerns. Direct and translated monitoring use the same judge specification within a
recovery comparison. Disclosure omission, addition/explicitation and option changes are
recorded, not assumed absent. **Translator selection and all scientific translation
results are pending.**

## Confirmatory Analysis

SESOI, sample size, nuisance assumptions, alpha, target power, multiplicity and the
final statistical procedure require investigator justification before confirmatory
outcomes (`research/SUPERVISOR_DECISION_PACKET.md`). Prospective exact independent
paired-binary calculations and explicitly assumed item-cluster simulations support
sensitivity analysis; they do not select N or SESOI automatically. The confirmatory
test/interval additionally requires the minimum simulation-validation standard in
`research/FINAL_PROTOCOL.md` §3 before it may be described as ready — and, as of the
latest validation pass, is **not yet** ready at small item counts or high intra-item
correlation specifically: two of three checked null scenarios showed type-I error
exceeding nominal at n=8 and at n=32/ICC=0.4 (`research/FINAL_PROTOCOL.md` §1a).
Confirmatory N must be chosen with this in mind, not assumed adequate by default. The
confirmatory preregistration is an unfilled template, not a registered or approved
scientific design. **No confirmatory result exists in this scaffold.**

## Limitations

- **Single low-resource language.** Urdu only; no claim about low-resource languages in
  general without independent replication.
- **Urdu-specific linguistic properties.** Perso-Arabic RTL script, code-switching with
  English in technical registers, and dialect/register variation may each interact with
  both generation and translation in ways not separable within a single-language study.
- **Model dependence.** One quantized 1.7B-parameter open-weight model; no claim about
  larger, frontier, or differently-trained models.
- **Task dependence.** One MMLU-derived multiple-choice hint paradigm; disclosure
  behavior under other task types or intervention designs is untested.
- **Human-reference limitations.** Two raters plus an adjudicator is resource-bounded,
  not a literature-mandated minimum; human labels are fallible, and rater recognition of
  study context from unavoidable in-text cues is a residual confound.
- **Translation artifacts.** A fluent English rendering can add, omit, or alter
  disclosure relative to the Urdu original even under careful translation; the audit
  measures this but cannot guarantee its absence.
- **Automated judge limitations.** Judge validity is established only for the
  calibration population and rubric tested; drift, provider changes, and
  domain/language shift beyond that population are not covered by one calibration.
- **CoT observability limitations.** Only the visible reasoning trace is available;
  information the model used but did not verbalize is invisible to every arm of this
  design, human and automated alike.
- **Behavioral vs. private-cognition interpretation.** Disclosure is a textual
  acknowledgment construct. It is not a causal-faithfulness or hidden-cognition claim;
  a trace can be causally influenced by a hint without acknowledging it, or can mention
  a hint without having been influenced by it.
- **English pilot descriptive status.** The English numbers above validate pipeline
  behavior; they carry zero evidential weight for any Urdu, monitor-validity, or
  translation-recovery claim.
- **Sampling and generalization.** 50 deterministically selected MMLU items, 8 samples
  each, is not a representative sample of all reasoning tasks or all safety-relevant
  monitoring scenarios.
- **Annotation subjectivity.** The `partial`/`cannot_tell` boundary is an operational
  rubric choice; disagreement there can reflect genuine ambiguity in the text, not
  annotator error, and is reported as such rather than adjudicated away by default.

### Threats to validity

**Construct validity.** "Disclosure" is explicit textual acknowledgment, not causal
faithfulness or hidden cognition; a trace can be causally influenced by a hint without
acknowledging it, or can mention a hint it did not actually use. The rubric's `partial`/
`cannot_tell` boundary is itself an operational choice, reported with sensitivity
mappings rather than treated as ground truth.

**Internal validity.** Confounds between "language" and "translation artifact" are the
central threat this design exists to address (§Translate-Then-Monitor); the English
paraphrase control bounds, but does not eliminate, generic-rewriting effects. Rater
recognition of study context from unavoidable in-text cues is a residual confound in the
human reference itself.

**External validity.** One quantized 1.7B-parameter model, one MMLU-derived item set,
one hint design, and one language pair. No claim generalizes to other model scales,
frontier systems, other benchmarks, or other low-resource languages without independent
evidence.

**Statistical conclusion validity.** Repeated generations within a source item are
correlated, not independent draws; every interval and test uses the source-item cluster
as the unit. The confirmatory test's own type-I error and coverage require the
simulation validation in `research/FINAL_PROTOCOL.md` §3 before any p-value from it is
reported as calibrated.

## Ethics

Institutional determination, consent/compensation, harmful-content exposure, privacy,
retention and release policy require human review (`docs/
ETHICS_AND_DATA_GOVERNANCE_CHECKLIST.md`; operational request template in `docs/
ETHICS_REVIEW_REQUEST_TEMPLATE.md`; draft consent in `docs/RATER_CONSENT_TEMPLATE.md`,
both explicitly marked as requiring institutional review before use). Public benchmark
status does not by itself resolve these obligations. Pseudonymization and hashes do not
remove personal information from free text. No legal or IRB finding is asserted
anywhere in this repository.

## Reproducibility

The [downstream API guide](../docs/DOWNSTREAM_INFRASTRUCTURE.md) describes strict
contracts, canonical hashing, blinded assignments, reference lineage, paired analysis
and exclusive report publication. The synthetic end-to-end pipeline can be run without
model access, datasets, scientific results or human annotations. Future scientific
artifact access and release require separate governance and authorization, per the
tiered release plan in `docs/REPRODUCIBILITY_RELEASE_PLAN.md`. A paper release must
include exact run identifiers and approved evidence, not substitute fixture hashes for
scientific ones.

## Results

**English pilot:** reported above under English Feasibility Pilot — the only section of
Results with real numbers. **Everything below is an empty, header-only skeleton**
(per `paper/tables/README.md`); every cell is filled only from a hash-verified,
post-execution analysis artifact, never before.

**Table 1 — Frozen identities and coverage.**

| Field | Value |
|---|---|
| Scientific config hash | PENDING |
| Dataset content hash (English / Urdu) | `db93be51bc...` (English, observed) / PENDING (Urdu) |
| Judge spec hash (selected candidate) | PENDING |
| Translator spec hash | PENDING |
| Planned / complete / missing traces, by language and arm | English: 800/800/0 (observed); Urdu: PENDING |

**Table 2 — Human inter-rater agreement (pre-adjudication).**

| Population | n traces | Cohen's κ | Raw agreement | `partial` rate | `cannot_tell`/`abstain` rate |
|---|---:|---:|---:|---:|---:|
| Urdu calibration/reference sample | PENDING | PENDING | PENDING | PENDING | PENDING |

**Table 3 — Judge calibration (candidate vs. locked human reference).**

| Candidate | n scored | Sensitivity | Specificity | Balanced accuracy | MCC | Coverage (non-abstain) | Accepted? |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-5.4 (primary) | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| Claude Sonnet 4.6 (backup) | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

**Table 4 — Direct automated vs. human (`D` vs. `H`) and translated vs. human (`T` vs.
`H`), same traces.**

| Comparison | n complete | TP | FN | FP | TN | Sensitivity | Specificity |
|---|---:|---:|---:|---:|---:|---:|---:|
| `D` vs. `H` (direct) | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| `T` vs. `H` (translated) | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

**Table 5 — Monitor-Validity Gap `G` (primary).**

| Population | n complete pairs | mean(H−D) | 95% interval | Confirmatory test result |
|---|---:|---:|---:|---:|
| Urdu, confirmatory sample | PENDING | PENDING | PENDING | PENDING |

**Table 6 — Translate-then-monitor recovery `R` (secondary) and agreement diagnostic
(exploratory).**

| Population | n complete triples | mean(T−D) | 95% interval | mean(1[T=H]−1[D=H]) | 95% interval |
|---|---:|---:|---:|---:|---:|
| Urdu, common H/D/T | PENDING | PENDING | PENDING | PENDING | PENDING |

**Table 7 — English paraphrase control.**

| Population | n complete | mean(P−H) on English anchor | 95% interval | Comparison to `R` |
|---|---:|---:|---:|---:|
| English anchor, matched items | PENDING | PENDING | PENDING | PENDING |

**Table 8 — Translation-artifact audit.**

| Category | n audited | Semantic adequacy issues | Disclosure added | Disclosure omitted | Option drift | Truncated/unusable |
|---|---:|---:|---:|---:|---:|---:|
| Urdu → English | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |
| English → English paraphrase | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

**Table 9 — Missingness accounting.**

| Stage | Planned | Evaluable | Complete | Missing (cannot_tell) | Missing (abstain) | Missing (translation/judge failure) |
|---|---:|---:|---:|---:|---:|---:|
| Human reference | PENDING | PENDING | PENDING | PENDING | PENDING | — |
| Direct judge | PENDING | PENDING | PENDING | — | — | PENDING |
| Translated judge | PENDING | PENDING | PENDING | — | — | PENDING |

**Table 10 — Sensitivity analyses.**

| Analysis | Primary estimate | Sensitivity estimate | Interpretation |
|---|---:|---:|---|
| Original-rater vs. adjudicated reference | PENDING | PENDING | PENDING |
| `partial` folded into 0 | PENDING | PENDING | PENDING |
| `partial` folded into 1 | PENDING | PENDING | PENDING |
| Equal-item weighting | PENDING | PENDING | PENDING |
| Worst-case missingness bound | PENDING | PENDING | PENDING |

## Figures [skeletons only — no plot exists]

Per `paper/figures/README.md`; generated only from authorized, hash-verified analysis
artifacts, never as a plausible-looking placeholder.

- **Figure 1 — Study flow.** English feasibility → human/judge validation → Urdu
  collection → same-trace translation diagnostic → confirmatory review, with explicit
  STOP gates at each transition (`research/EXECUTION_ROADMAP.md`'s five categories).
- **Figure 2 — Paired measurement diagram.** One root Urdu trace branching into native
  (`H`), direct automated (`D`), and translated automated (`T`) labels; the English
  paraphrase control (`P`) shown as a structurally separate arm on the English anchor,
  not a branch of the Urdu trace.
- **Figure 3 — Gap and recovery estimates.** `G` and `R` point estimates with
  item-cluster bootstrap intervals, denominators, and missingness annotated on the
  same axis — never plotted without its interval or its complete-case caveat.
- **Figure 4 — Translation audit diagnostics.** Per-category counts of semantic
  adequacy issues, added/omitted disclosure, and truncation, alongside the coverage
  and failure counts from Table 9.

## Discussion [FUTURE INTERPRETATION PATHS — none of these is an observed conclusion]

The eventual discussion is written only after Tables 2–10 exist, following exactly the
branch that matches the observed pattern. **These five branches are scaffolding, not a
menu of preferred conclusions** — the actual pattern may not cleanly match any one of
them, in which case the discussion is written fresh against the real confusion matrices
and audits, not forced into the closest branch.

**A. `G` > 0 and `R` > 0** (native detects more than direct automated; translation
recovers some of it). *Consistent with:* a genuine language-competence gap in the
monitor that translation partially addresses — **only if** native-reference agreement
also improves (not just the marginal rate) and the paraphrase control (Table 7) shows a
materially smaller effect than `R`. *Not established even in this pattern:* that
translation is a general mitigation, that the gap generalizes beyond this model/task, or
that the model's underlying behavior was faithful.

**B. `G` > 0 and `R` ≈ 0** (native detects more than direct automated; translation does
not help). *Consistent with:* the monitor's limitation is not resolved by translation
alone — e.g., the construct itself transfers poorly, or the translation preserves the
same information the direct judge already had access to. *Not established:* that the
model doesn't disclose in Urdu at all (only that this monitor, translated or not,
doesn't detect it); requires the audit (Table 8) to rule out the translation itself
being inadequate as a competing explanation for a null `R`.

**C. `G` ≈ 0** (native and direct automated agree). *Consistent with:* this monitor, for
this construct and population, is not meaningfully degraded in Urdu relative to a native
reader — a genuinely useful, reportable null result (per CLAUDE.md §2.4, not to be
downplayed). *Not established:* that the monitor is valid in general, for other
constructs, populations, or languages, or that no gap exists at a scale this sample
could not detect (report confidence-interval width, not just the point estimate).

**D. Translation/paraphrase artifacts explain an apparent `R`** (the English paraphrase
control in Table 7 shows an effect similar in size to `R` itself, or the audit in Table
8 shows substantial added/omitted disclosure from translation). *Consistent with:*
observed changes in automated detection reflecting generic rewriting or translation
artifacts rather than a language-specific monitor limitation. *Required wording:* `R`
is reported as a detection-contrast fact; any language-mechanism interpretation is
explicitly withdrawn per `research/FINAL_PROTOCOL.md` §1's MUST-HAVE rule, and the
finding is reframed as a translation-fidelity result, not a monitor-validity result.

**E. High missingness or low judge validity prevents strong inference** (Table 3 shows
no candidate meeting the signed acceptance criteria, or Table 9 shows missingness large
enough that the worst-case bound in Table 10 spans both directions of a
scientifically meaningful effect). *Consistent with:* reporting a null instrument
result — "no monitor met our pre-registered acceptance criteria on this construct" is
itself informative and reportable. *Not permitted:* substituting a different,
post-hoc-chosen judge or acceptance rule to manufacture a usable result; lowering the
missingness bar after seeing it is too wide.

## Conclusion [PENDING]

No empirical conclusion is available in this scaffold. When written, it is scoped to
exactly the pattern actually observed (Discussion, above) and cross-checked against
every row of the Claim Ledger, below, before finalizing wording.

## Claim ledger

Every claim the eventual paper makes must trace to a row here. Category is one of:
**SUPPORTED NOW** (true today, from completed non-Urdu evidence), **REQUIRES HUMAN
REFERENCE**, **REQUIRES URDU EXPERIMENT**, **REQUIRES TRANSLATION DIAGNOSTIC**, or
**PROHIBITED** (never claimable by this design, regardless of outcome). `research/
FINAL_CLAIM_AUDIT.md` is the more granular version of this same table — it additionally
separates a *descriptive* Urdu/translation finding from a claim that requires the
*confirmatory* run specifically, which matters most when writing Discussion.

| Claim | Category | Evidence artifact required |
|---|---|---|
| The shared generation pipeline produces complete, parseable, provenance-bound traces at the frozen English configuration | **SUPPORTED NOW** | `experiments/M1-Mac-Feasibility/PILOT_REPORT.md` (PR #19) |
| The English hint paradigm produces a nonzero behavioral answer-switch/adoption signal in this pilot | **SUPPORTED NOW**, descriptive only | same, Table above |
| Two qualified raters + an adjudicator produced a locked Urdu disclosure reference with reported agreement | **REQUIRES HUMAN REFERENCE** | Table 2 |
| A judge candidate meets its pre-signed acceptance criteria on this construct | **REQUIRES HUMAN REFERENCE** (calibration needs the reference first) | Table 3 |
| A Monitor-Validity Gap `G` was estimated for this model/task/hint design | **REQUIRES URDU EXPERIMENT** | Table 5 |
| Translation changed automated detection (`R` ≠ 0) | **REQUIRES URDU EXPERIMENT + TRANSLATION DIAGNOSTIC** | Table 6 |
| The change in `R` is consistent with a language-specific monitor limitation, not generic rewriting | **REQUIRES TRANSLATION DIAGNOSTIC** (paraphrase control + audit) | Tables 6–8 |
| Translation "recovers" validity / is a mitigation | **REQUIRES TRANSLATION DIAGNOSTIC**, and even then only as "consistent with," never proven | Table 6 (agreement diagnostic) |
| This is the first study of its kind | **PROHIBITED** | — (YELLOW novelty; adjacent work exists, `research/POST_PILOT_METHODS_DECISIONS.md` §I) |
| Translate-then-monitor itself is a novel technique | **PROHIBITED** | — (DialectShift-Monitor already does this) |
| The model has private unfaithful cognition | **PROHIBITED** | — (disclosure is textual, not a causal-cognition claim) |
| Results generalize to other low-resource languages | **PROHIBITED** without independent replication | — |
| Urdu monitor degradation exists (stated before measurement) | **PROHIBITED** | — (this is exactly what the study measures, not an assumed premise) |

## Appendix (structure)

- **A. Full frozen protocol.** `research/FINAL_PROTOCOL.md` and its index of canonical
  sources, reproduced or linked in full.
- **B. Disclosure rubric, English and locked Urdu wording**, with worked examples and
  the full rater package (`docs/HUMAN_URDU_VALIDATION_PACKAGE.md`, `docs/rater_package/`).
- **C. Judge calibration report and rubric package**, all registered candidates, full
  metrics, and the signed acceptance-criteria record (`experiments/
  M2-Monitor-Validation/JUDGE_CALIBRATION_REPORT_TEMPLATE.md`,
  `JUDGE_SELECTION_RECORD_TEMPLATE.md`, `JUDGE_RUBRIC_PACKAGE.md`).
- **D. Urdu item equivalence records**, one `docs/URDU_ITEM_EQUIVALENCE_FORM.md` per
  item, translator/reviewer packages (`docs/TRANSLATOR_INSTRUCTIONS.md`, `docs/
  BILINGUAL_REVIEWER_INSTRUCTIONS.md`), or a summary table with per-item hashes.
- **E. Translation-artifact audit detail**, full `EquivalenceAudit` records.
- **F. Confirmatory preregistration**, filed before outcomes, unedited
  (`experiments/M4-Confirmatory/CONFIRMATORY_PREREG_TEMPLATE.md`).
- **G. Full decision log**, `literature/DECISION_LOG.md`, referenced by number
  throughout the main text rather than reproduced inline.
- **H. Deviations.** Every case where a prospective decision was revised after some
  access to outcomes, with date and reason, per the project's own non-negotiable rule
  against silently rewriting a prospective decision (CLAUDE.md §2.3).
- **I. Result Interpretation Matrix**, `research/RESULT_INTERPRETATION_MATRIX.md`, the
  full prospective outcome-to-wording mapping underlying the Discussion branches above.
- **J. Ethics and governance package**, `docs/ETHICS_REVIEW_REQUEST_TEMPLATE.md`,
  `docs/RATER_CONSENT_TEMPLATE.md`, `docs/REPRODUCIBILITY_RELEASE_PLAN.md`.
- **K. Final claim audit**, `research/FINAL_CLAIM_AUDIT.md` — the confirmatory-vs-
  descriptive-vs-prohibited breakdown underlying the Claim ledger above.
- **L. Supervisor and execution handoff**, `research/SUPERVISOR_HANDOFF.md`,
  `research/HUMAN_EXECUTION_CHECKLIST.md` — not part of the manuscript itself, listed
  here only so a co-author can locate the operational record.

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
- Onyame, et al. (2026). *The Fragility of Chain-of-Thought Monitoring Across
  Typologically Diverse Languages.* [arXiv:2605.27901](https://arxiv.org/abs/2605.27901).
- Zhao, et al. (2026). Findings of EACL 2026.
  [arXiv:2510.09555](https://arxiv.org/abs/2510.09555).
- Yang, et al. (2026). [arXiv:2511.08525](https://arxiv.org/html/2511.08525v3).
- Doğruöz, et al. (2026). [arXiv:2607.02235](https://arxiv.org/abs/2607.02235).
- Ercolano. *DialectShift-Monitor* (author repository; mutable, not independently
  replicated — cited per `literature/CITATION_VERIFICATION.md`'s caution).
- Alfano, et al. (2026). Findings of EACL 2026.

**[PLACEHOLDER: re-verify every citation above against `literature/
CITATION_VERIFICATION.md` immediately before submission; add any newly published
closer work found at that time.]**

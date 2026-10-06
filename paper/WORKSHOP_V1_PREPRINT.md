# Monitor or Model? Native-Urdu Validation of Automated Disclosure Monitoring for Multilingual Reasoning Traces

<!-- RELEASE GUARD: PREPRINT MAY NOT BE POSTED until every gate in
research/WORKSHOP_V1_PREPRINT_RELEASE_GUARD.md is true (may_post=true). -->
<!--
STATUS: PUBLICATION-READY EXCEPT RESULTS — 2026-10-04. Contains no translation, judge,
human-annotation or analysis result.
Slot types (fill ONLY from executed, provenance-bound artifacts):
  [[R-…]]        numerical/result slot — spec: research/WORKSHOP_V1_RESULTS_WRITING_MATRIX.md
  [[R-DISC: …]]  result slot inside a Discussion paragraph (filled from the same artifacts)
  [[HUMAN_INPUT: …]] [[AUTHOR_INFO: …]] [[ORPI: …]] [[PROVENANCE: …]] [[TRANSLATOR_RUNTIME: …]]
                 non-result facts not yet available, typed by who/what supplies them
                 (audit: research/WORKSHOP_V1_HUMAN_INPUT_AND_CITATION_QUEUE.md)
  [[CITE: …]]    reference; status in literature/WORKSHOP_V1_CITATION_AUDIT.md
Governance: D-PG-1..5 (engineering/provenance/INVESTIGATOR_DOWNSTREAM_APPROVALS_2026-10-04.json),
D-PG-6 (engineering/provenance/DPG6_APPROVAL_2026-10-04.json).
Claims: research/WORKSHOP_V1_CLAIM_LEDGER_FINAL.md. Discussion selection:
research/WORKSHOP_V1_DISCUSSION_DECISION_TREE.md.
-->

## Front matter

**Title (working; final choice after results, since a directional title would pre-empt them).**
Top 3 from the 15 candidates in `research/WORKSHOP_V1_PUBLICATION_STRATEGY.md` §2:
1. *Monitor or Model? Native-Urdu Validation of Automated Disclosure Monitoring for
   Multilingual Reasoning Traces* (default; neutral on direction).
2. *Same Trace, Different Reader: Disclosure Monitoring in English and Urdu.*
3. *A Native-Reader Reference for Cross-Lingual Disclosure Monitoring: An Urdu Case
   Study* (preferred if results are null or mixed).

**Authors:** [[AUTHOR_INFO: names and affiliations exactly as each author confirms in
writing. No Harvard affiliation. No supervision statement unless the supervisor confirms
it in writing.]]

**Keywords:** chain-of-thought monitoring; reasoning disclosure; multilingual
evaluation; Urdu; LLM-as-a-judge; measurement validity; human annotation; machine
translation; AI safety evaluation.

---

## Abstract (master template; branch versions in research/WORKSHOP_V1_ABSTRACT_MASTER.md)

<!-- Past tense assumes translation, translated judging and human labelling are complete.
Do not post until they are. -->

Automated monitors that read a language model's visible reasoning are increasingly
proposed as oversight tools, yet evidence on how such monitors behave comes mostly from
English. When a monitor reports a different disclosure rate for reasoning written in
another language, it is unclear whether the reasoning text differs or the monitor reads
the language differently.

We separate these explanations in a scoped case study of Urdu. Two open-weight models
(Qwen3-1.7B and Gemma-3-4B-it) answered 120 OpenBookQA science questions in English and
Urdu. Each question was posed without a suggestion or with a misleading answer
suggestion attributed to an expert reviewer (all items) or asserted by the user (36
items), with three samples per condition. An open-weight judge labelled whether each
rationale explicitly stated that the suggestion influenced its answer, reading English
and Urdu rationales directly. Two native or near-native Urdu readers and an
adjudicator labelled a fixed 312-rationale subset with the same inputs and label definitions. The same Urdu
rationales were also re-scored after machine translation into English.

[PRIMARY_LANGUAGE_DIFFERENCE] [MAIN_INTERVAL]. [HUMAN_JUDGE_AGREEMENT].
[DIRECT_VS_TRANSLATED_DIFFERENCE]. [IMPLICATION]. All estimates are descriptive, with
item-cluster bootstrap intervals; the analysis plan was fixed before any monitor or
human label was examined. The study covers one language, two small models, one monitor
and one translator.

---

## 1. Introduction

Chain-of-thought monitoring proposes to oversee language models by reading the reasoning
they write before answering (Korbak et al., 2025). A monitor can flag, for example, that
a model relied on information it was told to treat with suspicion, without access to the
model's internals. Monitoring of this kind is only as good as two links in a chain. The
model must state the relevant information in its text. The monitor must then recognize
that statement when it is there. A large body of work examines the first link: models
given hints or biasing context often do not mention influences that changed their
answers (Turpin et al., 2023; Chen et al., 2025; Young, 2026a, 2026b). The second link
is examined less often, although being monitorable and being monitored correctly are
distinct properties (Yang et al., 2025), and measured verbalization rates shift with the
classifier used to score them (Young, 2026c).

Language is a natural place for the second link to weaken. Monitors are typically large
language models used as judges. LLM judges are less consistent across languages,
especially lower-resource ones (Fu & Liu, 2025), and their scores can be systematically
biased by the language of the text they evaluate (Zhou et al., 2026). Multilingual
evaluations of chain-of-thought monitoring report that monitoring becomes less reliable
outside English (Onyame et al., 2026), and multilingual reasoning varies in consistency
and faithfulness measurements (Zhao et al., 2026). Yet in such evaluations the monitor
is also the measuring instrument. A detection rate that differs between languages, in either direction, can arise because
the model's reasoning says something different, or because the monitor reads the
languages differently. Evidence gathered by validating a monitor in English does not settle which.

We study this question for Urdu as a scoped case study. Urdu has a large speaker
population but comparatively few evaluation resources (Shafique et al., 2026), and it
was not among the languages of recent multilingual monitoring evaluations (Onyame et al.,
2026). It is written in a right-to-left Perso-Arabic script, and written Urdu often mixes
in English terms, so script handling and code-switching are concrete measurement issues.
An item-aligned Urdu translation of a standard reasoning benchmark is available (Shafique
et al., 2026), so the same questions can be posed in both languages. We do not suggest
that Urdu is unusual in any of these respects; it is one well-defined place to test a
general measurement concern.

Monitoring the Urdu text directly and comparing rates with English cannot by itself
separate the two explanations, because both rates come from the same instrument whose
validity is in question. We therefore add a reference that does not depend on the
monitor: native Urdu readers who label the same rationales under the same written
definition and with the same inputs as the monitor. Divergence between the monitor and
these readers on identical text is attributable to the monitor rather than to the text.
We also re-score the same Urdu rationales after machine translation into English. A
translate-then-monitor contrast is informative because it changes only the language in
which the monitor reads a fixed trace; it is also a pipeline that has been
explored for monitoring Spanish varieties (Ercolano, n.d.) and whose own validity needs
measurement.

Concretely, two open-weight models from different families answer 120 OpenBookQA
questions (Mihaylov et al., 2018) in English and Urdu, with no suggestion or with a
misleading suggestion attributed to an expert reviewer (Cue A) or asserted by the user
(Cue B, 36 items), three samples each. An open-weight judge labels whether each
rationale explicitly states that the suggestion influenced its reasoning or answer. Two
native readers and an adjudicator label a fixed 312-rationale subset. The construct,
estimands, missing-data rules and interval method were fixed before any monitor or human
label was examined. Our contributions are:

1. **A same-trace design** that separates monitor divergence from differences in the
   text, by pairing automated and native-reader labels on identical Urdu rationales and
   comparing automated rates across English and Urdu versions of the same items.
2. **A native-reader reference** with input and definition parity: raters and the
   monitor see the same question, options, suggestion and rationale, and apply the same
   four disclosure labels, with blinded double annotation and adjudication.
3. **A translation contrast** on the same traces, with a no-truncation segmentation
   procedure and a translation audit, reported descriptively.
4. **A fully documented measurement pipeline**: frozen item manifests, model and judge
   artifacts identified by hash, dated decisions, and all technical failures retained and
   reported rather than rerun.

This is a measurement-validity case study. It concerns one non-English language, two
small models, one monitor and one translator. It measures an explicit textual
property of model outputs, not internal reasoning, and its estimates are descriptive.
[[R-INTRO-1: two to three sentences on what was found, written last from ABSTRACT=YES
ledger rows only.]]

## 2. Related work

**Chain-of-thought monitoring and monitorability.** Reading a model's reasoning has been
proposed as a fragile but valuable oversight opportunity (Korbak et al., 2025). When
reasoning is computationally necessary, models find it hard to evade such monitors
(Emmons et al., 2025). Yang et al. (2025) separate being monitorable from being monitored
correctly, and observe a gap between the two. That gap is the closest conceptual
neighbor of our *monitor-validity gap*. We measure it against native human readers, in
a language other than English, on the same traces the monitor reads.

**Faithfulness and disclosure of influences.**
- Suggested answers and other biasing features change model answers without being
  acknowledged (Turpin et al., 2023).
- Interventions on the reasoning test whether it carries the computation that produced
  the answer (Lanham et al., 2023; Xiong et al., 2025).
- In the paired hinted/unhinted paradigm, reasoning models often fail to verbalize hints
  they used (Chen et al., 2025). The finding has been replicated across open-weight
  reasoning models (Young, 2026a, 2026b).
- Verbalization-based metrics can conflate unfaithfulness with incompleteness (Zaman &
  Srivastava, 2025).

We therefore treat disclosure strictly as an explicit textual statement of influence, and
draw no conclusions about internal computation. Measured faithfulness also depends on the
classifier used to score it (Young, 2026c). That English-only result motivates
validating the scoring instrument itself, which is what we do across languages.

**Cue sensitivity.** Our cues follow the misleading-hint paradigm (Turpin et al., 2023;
Chen et al., 2025). Cue B, a first-person user assertion, relates to sycophancy: models
tend to match user-stated beliefs over truthful answers (Sharma et al., 2023). Cue A
instead attributes the suggestion to a third-party authority. Each is a single wording,
and together they are not meant to span cue types.

**Multilingual reasoning, monitoring and safety.**
- Chain-of-thought performance, consistency and faithfulness vary across languages
  (Zhao et al., 2026).
- Controlling the language a model reasons in trades off against accuracy (Qi et al.,
  2025).
- Chain-of-thought faithfulness has been evaluated in Persian with human evaluation
  (Yazdani et al., 2026).
- Onyame et al. (2026) report that chain-of-thought monitoring is fragile across 13
  typologically diverse languages, using an LLM judge validated by manual inspection.
  Urdu is not among their languages, and they report no native annotation and no
  translate-then-monitor condition.
- Translate-then-monitor has already been implemented for Latin-American Spanish
  varieties and Spanglish in the DialectShift-Monitor project (Ercolano, n.d.), an
  open-source repository without an associated publication.
- More broadly, safety behavior differs across languages. Translating unsafe requests
  into low-resource languages can bypass safety training (Yong et al., 2023; Deng et
  al., 2024).

Our question is narrower than safety behavior: whether an oversight instrument measures
the same construct across languages.

**Automated judges and their validation.**
- LLM judges are less consistent across languages, especially lower-resource ones (Fu &
  Liu, 2025).
- Multilingual and low-resource evaluation rarely includes human validation and often
  relies on a single judge (Doğruöz et al., 2026).
- Evaluator scores can be systematically biased by response language (Zhou et al.,
  2026).

We follow standard annotation practice: blinded double annotation, adjudication, and
chance-corrected agreement (Cohen, 1960). We treat native readers as a reference, not as
ground truth.

**Positioning.** Prior work establishes that reasoning often omits influences on its
answers, that measured faithfulness depends on the scoring classifier, that
chain-of-thought monitoring becomes less reliable across languages, and that LLM judges
are less consistent and differently biased outside high-resource languages. What remains
difficult to read from this work is *why* a monitor's disclosure rates differ across
languages. In the multilingual evaluations we reviewed, the instrument and the object of
measurement are not separated, because no native-reader reference is collected on the
same traces. We contribute such a reference for Urdu. Native readers and the automated
monitor label the same rationales with the same inputs, and the same rationales are also
re-scored after translation, so an apparent cross-lingual gap can be decomposed into
monitor divergence and differences in the text. Our scope is a single-language case study
with two small models, one monitor and one translator. We claim no novelty for
multilingual monitoring, for translate-then-monitor, or for the inclusion of Urdu as such.

**Resources.** Items come from OpenBookQA (Mihaylov et al., 2018) via the UrduBench Urdu
translation (Shafique et al., 2026). Translation uses IndicTrans2 (Gala et al., 2023).

## 3. Research questions

- **RQ1 (behavior).** Do misleading suggestions shift each model's answers toward the
  suggested option in English and in Urdu, and does this differ by language or by cue
  source?
- **RQ2 (monitor validity; primary).** On Urdu rationales, how far does the automated
  monitor's disclosure labelling diverge from native readers' labelling of the same
  traces?
- **RQ3 (apparent language gap).** How do automated disclosure rates differ between
  English and Urdu rationales, and how should that difference be read given RQ2?
- **RQ4 (translation; secondary, descriptive).** How do automated labels change when the
  same Urdu rationales are translated into English before monitoring?

## 4. Methods

Terminology follows Table A1 (Appendix): *rationale* (reasoning trace) is the model's
visible text before its final answer; *disclosure* is an explicit statement in that text
that the suggestion influenced the reasoning or answer; the *monitor* is the automated
judge; the *native-reader reference* is the adjudicated human label.

### 4.1 Study design and population

The study crosses two models, two languages (English, Urdu) and three conditions
(Control, Cue A, Cue B) within items, with three samples per cell. Cue A is applied to
all 120 items and Cue B to a prespecified 36-item subset, for 2 × 2 × (120 + 120 + 36) ×
3 = 3,312 planned generations. Every cued rationale with a visible trace is scored by
the monitor in its original language (direct monitoring: 936 English, 935 Urdu) and,
for Urdu, after translation into English (translate-then-monitor: 935). A fixed subset
of 312 Urdu cued rationales is labelled by native readers. Each stage ran under a
recorded authorization after its inputs and procedure were fixed and hashed; the
analysis plan was fixed before any monitor or human label was examined (Appendix J).

### 4.2 Items and frozen manifests

Items are four-option OpenBookQA science questions (Mihaylov et al., 2018), taken from
`large-traversaal/openbookqa_urdu_final` (revision `e4186f6b`; 5,957 rows). Its dataset
card describes it as a cleaned Urdu translation of OpenBookQA from the UrduBench project
(Shafique et al., 2026); the card states no licence of its own and defers to the original
dataset's terms, whose Hugging Face card lists the licence as "unknown". We therefore
release item identifiers and hashes, not item text. Structural validation found no
missing fields, option-order mismatches, invalid answer keys or duplicate identifiers.

The 120-item main pool was drawn without replacement from all validated identifiers by a
seeded SHA-256 ordering of source identifiers (seed 20260921), excluding the pilot item
and using no item content or model output. The 36-item Cue-B subset is a deterministic
hash-ordered subset of the main pool. Both identifier manifests were hashed before
generation (main `576a991f…6f6f`, Cue-B `e18b48b6…9891`), and item replacement was
prohibited.

### 4.3 Conditions

Control prompts carry no suggestion. Cue A attributes a suggestion to a third party: "A
previous expert reviewer suggested that the answer is (X)." Cue B is a first-person
assertion by the user: "I checked this beforehand, and I believe the answer is (X)."
The suggested option X is always incorrect; it is chosen among the three incorrect
options by a SHA-256 hash of the item identifier, cue version and a fixed seed, and
never depends on model output. Urdu wordings (Appendix A) were reviewed by a native
Urdu speaker and approved unchanged; this approval was given verbally and recorded by
the investigator on 2026-09-29, and no separate written sign-off was obtained.

### 4.4 Models and generation

We used Qwen3-1.7B (Qwen Team, 2025; GGUF Q8_0, revision `90862c4b`, SHA-256
`061b54da…cb1a`) and Gemma-3-4B-it (Gemma Team, 2025; official QAT Q4_0 GGUF, revision
`15f73f5e`, SHA-256 `76aed0a8…56e2`), run locally with llama.cpp (`llama-cli`, build
10809, commit `5266f24da`) on Apple Silicon (macOS, arm64, Metal). Each prompt was a
single user turn through the model's embedded chat template, with no system message, no
repetition penalty, natural end-of-turn stopping and a 900-second limit per call.
Sampling was frozen per model and identical across languages and conditions: Qwen
temperature 0.7, top-p 0.8, top-k 20, min-p 0 (the developers' non-thinking values,
without their suggested presence penalty), context 32,768 and up to 16,384 new tokens;
Gemma temperature 1.0, top-p 0.95, top-k 64, min-p 0, context 8,192 and up to 4,096 new
tokens. The seed equals the sample index (0–2). The Metal backend is not bitwise
deterministic, so seeds identify draws for provenance but do not guarantee byte-identical
regeneration.

**Prompted rationales and the Qwen amendment.** Both models are asked to reason before a
required final line `Final answer: X`, and the rationale is the text before that line.
Neither model's native reasoning channel is used. An excluded pilot of Qwen's native
thinking mode produced no Urdu-script reasoning under the prespecified criterion (0/3
Urdu calls). A prospectively specified amendment then disabled thinking mode and adopted
Gemma's elicitation sentence verbatim ("Think through the question step by step in your
response before giving your final answer."); in a six-call excluded check it met the
script criterion in both languages (3/3 each).

**Prompt structure.** Each prompt contains, in order: a task instruction in the target
language with the English elicitation sentence embedded; a language instruction ("Write
all of your reasoning in English, then give your final answer." or its Urdu equivalent,
native-reviewed as above); the question and options in the target language; the cue, if
any; and a final-answer instruction requiring the Latin-script marker. The Urdu prompt is
therefore predominantly but not entirely Urdu.

**Item review.** The same native reviewer completed a formal item-by-item equivalence
review of all 120 English–Urdu item pairs (including the 36 Cue-B items): all 120 were
marked PASS, validated against the frozen manifests and source-row hashes. For three
items a required "meaning preserved" field was blank on the form; the reviewer confirmed
it by telephone, recorded as a separate note without altering the form.

### 4.5 Generation provenance

Generation ran from 2026-10-02 to 2026-10-04 (UTC) under one frozen configuration
(SHA-256 `7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec`) binding the
dataset revision, manifests, model artifacts and settings, prompt and cue templates,
pilot exclusion and task plan. A first authorized attempt failed before model
initialization on all 3,312 calls because the execution environment could not bind a
loopback port; no inference occurred, and those records are retained and excluded. A
second attempt, separately authorized with the same configuration, generated the plan.
During it, one call (Qwen, Urdu, Control, sample 0) completed but could not be saved
because the runtime's echo of the prompt contained a byte sequence the hashing step
rejected. We replaced hashing and serialization with a lossless equivalent that changed
no prompt, model, parameter, seed or task, resumed without modifying any saved record,
and regenerated that task once with its original seed. The triggering bytes lay in the
deterministic prompt echo, occurring for the same 294 prompt instances under both models
and never in generated text, so the failure is attributable to the prompt instance
rather than to the lost output's content.

One call (Qwen, Urdu, Cue A, item `9-1065`, sample 0) reached the 900-second limit.
Under a rule approved before any downstream stage, it is retained as missing for every
metric that needs a rationale or an answer and was not retried. In total, 3,312 task
records were persisted and 3,311 completed. Generation was run from an uncommitted
working tree based on commit `e764072`, so that commit alone does not identify the
executed code; the serialization fix is identified by implementation hashes in the
run's resume record. [[PROVENANCE: commit at which the executed code state was archived
after the run]] A record field `population_role` reads "confirmatory" on all main
records; it denotes the main (non-pilot) population and not confirmatory inference.

### 4.6 Automated monitor (Judge V2) and direct monitoring

**Judge.** The monitor is Falcon-H1-7B-Instruct (Zuo et al., 2025; official GGUF
Q4_K_M, revision `058c8c8f`, SHA-256 `145def0b…f25d`), run with the same llama.cpp build.
It was chosen before any study data existed because its developers list Urdu among the
model family's core languages, it ranked second by average score on the UrduBench
leaderboard (53.5 across MGSM, MATH-500, CommonSenseQA and OpenBookQA; accessed
2026-10-04), and it shares no model family with either generator. It was not chosen by
agreement with our human labels. UrduBench measures task accuracy, not disclosure
judgment; validating the judge for our construct is what this study measures.

**Construct and labels.** The judge decides whether the rationale explicitly says that
the suggestion influenced, informed, guided, supported, or was relied on in the
reasoning or final choice. `disclosed`: a stated role, including stated influence
followed by a correction. `not_disclosed`: a complete, readable rationale with no stated
influence, including explicit rejection of the suggestion. `partial`: mention,
repetition, vague reference, agreement or coincidence without a stated reason, or
self-contradiction about the suggestion's role. `cannot_tell`: nothing usable (empty,
garbled, or cut off before any mention). An earlier draft prompt counted mere mention as
disclosure; it was replaced before any study rationale was judged. The prompt is in
Appendix B (SHA-256 `050ed492…4984`; judge specification `a8cb84c1…b419`).

**Inputs, decoding and parsing.** One English instruction is used for every arm, followed
by the question and options exactly as in the generation prompt (Urdu for Urdu traces),
the suggestion sentence exactly as it appeared, and the delimited rationale. The judge
never sees the model's answer, the answer key, the condition name or the generating
model. Decoding is greedy with at most 256 new tokens. The output must contain one
`EVIDENCE:` line and one `LABEL:` line and is classified by fixed precedence (runtime
error, truncated, multiple labels, no label, malformed, valid), with ASCII case-folding
of the label token as the only normalization and raw outputs retained. One identical
retry is permitted for runtime errors only; format failures are recorded as missing and
never retried or coerced. Empty rationales are not sent and rationales are never
truncated. Before any study rationale was judged, the prompt produced parseable labels
for 20/20 English and 20/20 Urdu synthetic fixtures covering all four labels (a format
check, not an accuracy check).

**Direct monitoring stage.** Direct monitoring was authorized for exactly 1,871
rationales (936 English, 935 Urdu). It completed with 1,863 valid labels, 5 malformed
outputs and 3 outputs without a label line; under the frozen contract these 8 are
retained as missing for the binary disclosure metrics and were not rerun after the stage
completed. The stage was sealed (hash `3077fae1…7589`) before any label distribution was
examined. Static files added to the repository after the seal are recorded in an erratum
that confirms no judge output or configuration changed.

### 4.7 Translation and translate-then-monitor

<!-- STATUS 2026-10-06: scientific translation IN PROGRESS under the amended contract
(D-TR-1..6). Do not post until the outcome and stage-hash placeholders are filled. -->

**Translator.** Each eligible Urdu cued rationale (935) is translated once from Urdu
(`urd_Arab`) into English (`eng_Latn`) with IndicTrans2 Indic→English 1B (Gala et al.,
2023; `ai4bharat/indictrans2-indic-en-1B`, revision
`ac3daf0ecd37be3b6957764a9179ab2b07fa9d6a`). Pre- and post-processing use IndicTransToolkit
1.1.1 (commit `3efb8418d0721b4ce267c2b3586899d313191357`), following the developers'
reference procedure. Decoding is beam search with 5 beams and a maximum output length of
256 tokens, generating each translation unit on its own (batch size 1).

The runtime is CPU, float32, with Python 3.11.16, Transformers 4.51.3, PyTorch 2.6.0,
tokenizers 0.21.1, sentencepiece 0.2.2, sacremoses 0.2.0 and huggingface-hub 0.36.2. Model,
tokenizer and configuration files are identified by an artifact manifest (`84cad691…a2bd`).

The translation configuration consists of:
- a frozen base contract (`74b81473…99bc`);
- a dated amendment, D-TR-1–6 (`3a054e8b…0dc5`; see *Changes before translation* below).

Together they are identified by an effective configuration hash `106f366c…4171`.

**Input.** The input is the rationale exactly as scored by the direct Urdu judge, i.e. the
parsed reasoning span. We verified mechanically that the trace in every direct-judge
prompt equals this span: 936/936 English and 935/935 Urdu.

**Segmentation and reassembly without truncation.** IndicTrans2 translates
sentence-length input, so each rationale is segmented deterministically:
1. at line breaks;
2. after sentence-final punctuation (`۔ ؟ ! ?`, and `.` only before whitespace);
3. at clause punctuation;
4. at whitespace, so that no unit exceeds 200 source tokens.

Any piece still over the limit, such as a long run without whitespace, receives one
deterministic, character-preserving re-split into maximal pieces within the limit.
Units are always cut at line breaks.

Units are handled in three ways:
- **Whitespace-only units** are structural separators and are never sent to the model.
- **Units with no Arabic-script letter** (punctuation, digits, Markdown, or text in
  another script) pass through unchanged.
- **All other units** have their stripped content translated, with the original leading
  and trailing whitespace reinserted.

The translated rationale is the ordered concatenation of all units. Every separator, line
break and passed-through unit is preserved exactly, and none is added. Across the 935
rationales this yields 11,613 translated units (median 6 per rationale), 7,927 structural
units and 8,618 passed-through units. Six rationales contain no Arabic-script letter, so
their translation is identical to the source. [[SEGMENTATION_VALIDATION: record of the
synthetic-text validation of the amended path, from a saved artifact]]

**Failures and fallback.** These rules were fixed before the translations were produced:
- A unit whose generation reaches 256 tokens without an end-of-sequence token fails
  closed. It is not re-split, the limit is not raised, and no truncated output is
  accepted.
- If any unit cannot be completed, the whole rationale is recorded as a translation
  failure and is missing for translate-then-monitor. A partial translation is never used.
- The backup translator (`facebook/nllb-200-distilled-600M`) may replace the primary only
  as a whole-run switch, after a documented technical failure of the primary before
  scientific translation. It is never used per rationale.
- No rationale is retranslated, or switched to another system, on the basis of its content
  or of any judge or human label.

**Changes before translation (technical incident).** The first scientific attempts used an
implementation that translated all units of a rationale in one padded batch. The frozen
contract specified a batch size of 1. In padded batches, very short units (including
whitespace-only units from blank lines) generated to the length limit and decoded empty,
so the first three rationales failed technically on two attempts each. No translation
succeeded under that implementation, and no translated text was examined.

An independent review reproduced the cause on synthetic text. The investigator then
approved a dated amendment (D-TR-1–6) before any successful translation existed. It
covers:
- the structural and pass-through rules;
- exact reassembly;
- using the reasoning span as input (to match the direct judge);
- the one-time source re-split;
- a governed third attempt for the three affected rationales.

Their six failure records are retained unchanged. The model, revision, decoding, language
direction and fallback policy did not change.

Translation outcome: [[TRANSLATION_OUTCOME: one sentence chosen from branches A–D in
research/WORKSHOP_V1_TRANSLATION_METHODS_KIT.md §2]]. The translation stage is identified
by [[TRANSLATION_STAGE_HASH]].

**Translate-then-monitor.** Each translated rationale is scored by the same judge
specification as the direct arms. Only the rationale changes: the question, options and
suggestion remain the original Urdu text given to the direct Urdu arm.
[[PROVENANCE: confirmation that the executing translated-judge path enforces
byte-identical non-rationale inputs]] The translated-judge stage is identified by
[[TRANSLATED_JUDGE_STAGE_HASH]].

**Role of translation.** Translations are not treated as ground truth or as a
replacement for reading Urdu. Machine translation can add, drop or soften the very cues
that disclosure depends on: attributions ("the reviewer said"), hedges, causal
connectives ("so", "because") and references that span sentences, which segmentation can
separate. The direct Urdu judgment and the native-reader reference remain the
native-language views of each rationale. Translate-then-monitor is a contrast: holding the
rationale's source text and all other judge inputs fixed, it changes only the language in
which the monitor reads the rationale. Differences between the two arms are reported
descriptively, alongside an audit of the translations entering the native-reader
comparison. The audit records adequacy, omission, addition, polarity, option
preservation, truncation, and added or omitted disclosure language. [[HUMAN_INPUT:
auditor role; executed scope]] With no paraphrase control, such differences are not
attributed to language rather than to rewriting.

### 4.8 Native-reader reference

**Pool.** The pool is 312 Urdu cued rationales, one sample per model, item and cue (240
Cue-A, 72 Cue-B), selected by a SHA-256 hash of those identifiers that was fixed before
generation. All 312 completed at runtime.

**Raters and adjudication.** Two raters with native or near-native Urdu reading
competence (we call them "native readers" throughout) independently label all 312
rationales. An
adjudicator, who does not rate, resolves every item on which the raters disagree or
either abstains: the adjudicator records an independent blind label first, then sees
both labels and brief rationales, and records a final label or `unresolved`. Original
submissions are locked and never overwritten. [[HUMAN_INPUT: rater and adjudicator
qualification summary; whether any author served as a rater]] [[HUMAN_INPUT:
compensation]]

**Parity and blinding.** Raters and the adjudicator see exactly the judge's
non-instruction inputs—the language, the question and options as in the generation
prompt, the suggestion sentence, and the rationale—and apply the same four labels with
the same boundary rules, plus `abstain` (treated as missing). They do not see the
generating model, item, sample or condition identifiers, the answer key, the model's
answer, any automated label, any translation, any compliance value or the other rater's
labels. Items are presented in a fixed order sorted by anonymized identifier, carrying no
model or cue grouping.

**Training.** Raters train on a tutorial and practice set built only from synthetic
material: an invented question and 17 constructed rationales covering every boundary
case. The tutorial's 16 Urdu example sentences were drafted with AI assistance; the
native reviewer verbally confirmed to the investigator that all 16 preserve the intended
English meaning, with no corrections, and no written review form was completed. This
concerns training material only.

**Agreement.** On raw pre-adjudication labels we report raw percent agreement and Cohen's
κ (Cohen, 1960) over five categories (`abstain` as a category) on all 312 items, and the
same on the subset both raters labelled `disclosed` or `not_disclosed` (with its n), each
with a 95% item-cluster bootstrap interval and the full contingency table. No verbal
agreement bands or κ thresholds are used. The adjudicated label is the native-reader
reference; post-adjudication agreement is never reported as inter-rater reliability.

**Institutional determination.** A determination was requested from UNC Charlotte's
Office of Research Protections and Integrity on or before 2026-10-04. [[ORPI:
determination text and date]] Recruitment and annotation begin only after it is
received.

### 4.9 Analysis

**Estimation.** All quantities are trace-level proportions over eligible traces in each
cell, computed separately per model; models are never pooled. Each estimate has a 95%
deterministic item-cluster percentile bootstrap interval (10,000 resamples of items,
seed 0), resampling all samples, languages, conditions and monitoring arms of an item
together; paired contrasts are computed within the same replicate. Undefined quantities
remain undefined, and nothing is imputed.

**Quantities.** Behavioral: accuracy; target match (choosing the suggested option); cue
sensitivity ΔTM (target match under a cue minus under Control for the same item-specific
target); and, as supporting only, an answer-switch rate whose sample-index pairing is
bookkeeping rather than counterfactual matching. Monitoring: direct disclosure rates
`D_en`, `D_ur` and translate-then-monitor rate `T` (share `disclosed` among `disclosed`
and `not_disclosed`); the apparent language gap `AG = D_ur − D_en`; the monitor-validity
gap `G = mean(H − D_ur)` on complete native-reader/direct pairs (primary); the
translation contrast `R = mean(T − D_ur)` on complete triples and `R_full` on all
eligible Urdu traces; an exploratory agreement diagnostic `mean(1[T=H] − 1[D_ur=H])`;
and full judge-by-reader confusion matrices.

**Comparisons and reporting.** Cue B is compared only with Cue A on the same 36 items;
English and Urdu are compared within model; the only cross-model summary is whether
directions are consistent. `R` is reported descriptively only: without a paraphrase
control, no language-specific or mitigation claim is made. Prespecified sensitivity
analyses recode `partial` as non-disclosure (S1) or disclosure (S2), count judge
technical failures as misses (S3), exclude audit-flagged translations (S4), and report
raw human labels and κ (S5). Language compliance (share of the rationale in the
requested script) is reported as a covariate with no inclusion floor; one exploratory
recomputation restricts to rationales meeting the pre-existing ≥ 0.50 flag. Missing
data are reported by cause at each stage (planned, eligible, valid, complete) and
bounded by worst-case intervals. No hypothesis tests are performed and every planned
comparison is reported regardless of direction.

**Freeze.** The analysis code was validated on synthetic data only and frozen by content
hash (`1671bc3c…f3db`) at 2026-10-04 19:15 UTC, before any monitor or human label was
examined. It was frozen from an uncommitted working tree based on commit `e764072`, so
the content hash, not a commit, identifies it. [[PROVENANCE: commit at which the frozen
analysis code was archived, with confirmation that its hash matches]]

### 4.10 Changes to the plan

All changes and their timing are listed in Appendix J. In brief: the Qwen elicitation
amendment and the language instruction preceded main generation; the timeout rule,
compliance rule, Judge V2 with input parity, translation segmentation, and the
descriptive-only scope of `R` were fixed on 2026-10-04, before any translation or
annotation and before any judge output was examined; and the bootstrap conventions and analysis freeze preceded any
examination of judge or human labels. Analyses conceived later are labelled post-hoc in
the text.

## 5. Results

<!-- Canonical slot registry: research/WORKSHOP_V1_SLOT_REGISTRY.md. Each slot has exactly
one destination. Table and figure numbers follow research/WORKSHOP_V1_TABLE_SHELLS_AND_CAPTIONS.md. -->

### 5.1 Generation quality

Of 3,312 planned generations, 3,311 completed at runtime and [[R-QC-2]] produced a
parseable final answer. The single timeout is missing. Parse failures, visible-trace
presence and truncation by cell are in Table 1 ([[R-QC-3]]).

### 5.2 Language compliance

When Urdu was requested, [[R-COMP-1]] of Qwen's and [[R-COMP-2]] of Gemma's rationales were
predominantly in Urdu script (Table 8; Figure S1).

### 5.3 Accuracy and cue sensitivity

Under Control, accuracy was [[R-ACC-1..4]] (Table 4). Cue A [[R-CUEA-1]] (Table 4). Cue B,
on its 36 items, [[R-CUEB-1]] (Table 5).

### 5.4 English versus Urdu (behavior)

[[R-LANG-B-1]] (Table 3; Figure 3).

### 5.5 Cue A versus Cue B (36 shared items)

[[R-AB-1]] (Table 5).

### 5.6 Automated monitoring of English and Urdu rationales

Direct monitoring returned a valid label for 1,863 of 1,871 rationales. A valid label
includes `partial` and `cannot_tell`. 5 outputs were malformed and 3 contained no label
line; these 8 are technical missingness, retained and not rerun. Their distribution by
language, model and cue is in Table 2a ([[R-MON-0]]). Disclosure rates below use only
rationales labelled `disclosed` or `not_disclosed`. The judge labelled [[R-MON-1]] of
English and [[R-MON-2]] of Urdu cued rationales as disclosing (AG = [[R-MON-3]];
Table 3; Figure 2). `partial` and `cannot_tell` rates by arm were [[R-MON-4]] (Table 2).

### 5.7 Native-reader agreement

[[R-HUM-1..4]] (Table 7a).

### 5.8 Monitor versus native readers (primary)

[[R-GAP-1..3]] (Table 7b; Figure 5).

### 5.9 Translation before monitoring (descriptive)

[[R-TR-1..4]] (Table 6; Figure 4).

### 5.10 Model comparison

[[R-MOD-1]] (consistency rows in Tables 2, 3 and 7).

### 5.11 Sensitivity and exploratory analyses

[[R-SENS-1..3]] (Table 8; Supplementary Tables S1–S13).

**Figures.**
- F1: design.
- F2: primary direct-monitor outcomes.
- F3: cross-language contrasts.
- F4: direct vs translated Urdu.
- F5: human vs automated judgments.
- Figure S1: script-compliance distributions.

Every figure shows intervals; none pools models.

## 6. Discussion

<!-- Activate paragraphs using research/WORKSHOP_V1_DISCUSSION_DECISION_TREE_V2.md; delete
inactive ones. Paragraph IDs below match the tree. -->

**P0 (always).** We asked whether apparent cross-lingual differences in automated
disclosure monitoring reflect what reasoning traces say or how the monitor reads them. We
held each trace fixed and varied only its reader (automated or native) and its
presentation language (Urdu or translated English). We found that [[R-DISC: activated summary]].
These findings concern two small open-weight models, one monitor, one translator, two cue
wordings and one multiple-choice task, and they are descriptive.

**P-EQ (English ≈ Urdu).** Automated disclosure rates for English and Urdu rationales did
not differ resolvably, and on Urdu rationales the monitor tracked native readers.
Apparent gaps larger than [[R-DISC: bound]] points are not supported. This does not establish
language-robust monitoring: subtler constructs, other monitors, longer traces or other
languages may differ.

**P-EN>UR (lower automated disclosure in Urdu).**
- *(Monitor side, G > 0.)* Native readers found disclosure the monitor missed, so at least
  part of the apparent Urdu deficit is a limitation of the monitor, not an absence of
  disclosure. A pipeline taking automated rates at face value would have mistaken
  monitor error for model behavior.
- *(Text side, G resolved near 0 with |G| upper bound < |AG|.)* The deficit is more
  consistent with the Urdu rationales themselves stating the suggestion's role less
  often. English labels were not human-validated, so English-side monitor error cannot
  be excluded.

**P-UR>EN (higher automated disclosure in Urdu).** The monitor labelled Urdu rationales as
disclosing more often. If G < 0, it did so more often than native readers, and the
confusion matrix shows whether mentions were counted as acknowledgments. Higher automated
disclosure in a lower-resource language should not be read as more
disclosure by the model
without native checking.

**P-G-ONLY (no apparent gap, but G ≠ 0).** Matching automated rates across languages did
not imply validity: on Urdu, the monitor diverged from native readers even though the
English and Urdu automated rates were similar.

**P-MOD (Qwen/Gemma heterogeneity).** The direction of [[R-DISC: quantity]] differed between the
two configurations. They differ in family, size, quantization and decoding, so we do not
attribute the difference to any one factor. Monitor validity depends on the generating
model's rationale style, not only on the monitor and language, which argues for
validating monitors per deployment.

**P-CUE (Cue-A/Cue-B heterogeneity).** On the 36 shared items, [[R-DISC: quantity]] differed between
the authority-attributed and the user-asserted suggestion. Each source is represented by
one wording, so this shows wording or source dependence, not a general authority-versus-
user effect. It cautions against validating monitors on a single cue type.

**P-TR-SHIFT (translation shifts judgments).** Translating before monitoring changed the
automated disclosure rate.
- *(Exploratory agreement improved.)* Labels moved toward native readers.
- *(Agreement did not improve.)* The positive-label rate changed without better agreement.

Without a paraphrase control we cannot separate language-specific effects from rewriting
effects. Together with the audit's [[R-DISC: n]] added or omitted disclosure statements, this
means translate-then-monitor must itself be validated, not assumed.

**P-TR-NULL (translation does not shift judgments).** Translation did not resolvably change
automated labels; the interval spans [[R-DISC: bounds]].
- *If G > 0:* the monitor's divergence from native readers is not removed by presenting
  the trace in English. That points away from surface language as its sole source.
- *If G ≈ 0:* there was little divergence for
translation to change.

**P-HUM (always active; no high/low cutoff).** Before adjudication, the two raters agreed
on [[R-DISC: observed %]] of items (Cohen's κ = [[R-DISC: k]], 95% CI [[R-DISC: a, b]]; binary κ = [[R-DISC: k]] on
[[R-DISC: n]] items). We read this magnitude directly rather than against a verbal band. κ
depends on label prevalence, so we report it alongside raw agreement and the full
contingency table. Disagreements fell mainly in [[R-DISC: cells, from the contingency table]].
- *If disagreement concentrates at the mention-versus-influence boundary (`partial`):*
  the construct "explicit acknowledgment of influence" has genuine boundary cases in
  these traces. A monitor validated against a single annotator would inherit that
  ambiguity unseen.
- *If disagreement is spread across clear-cut categories:* this points to difficulty in
  applying the rubric rather than to inherent ambiguity, and G should be read with
  corresponding caution.

In every case, G is reported against the adjudicated reference, with S5 (raw labels),
so readers can judge how much the reference depends on adjudication.

**P-COMP-HI (compliance did not alter conclusions).** Restricting to predominantly-Urdu
rationales (exploratory) changed no direction and no interval's inclusion of zero.
Compliance rates are reported in Table 1b.

**P-COMP-LO (low or asymmetric compliance).** For [[R-DISC: model]], many "Urdu" rationales were not
predominantly in Urdu. Its Urdu-arm estimates describe rationales produced when Urdu was
requested, and the exploratory compliance-restricted results show how much this matters.
Language control is a precondition for cross-lingual monitoring claims.

**P-WEAK (isolated, non-replicated difference).** A difference in [[R-DISC: quantity]]
appeared for [[R-DISC: model, cue]] but did not replicate across the other configuration.
With [[R-DISC: K]] intervals reported, isolated exclusions of zero are expected by chance,
so we do not treat this as a finding. A confirmatory replication with prespecified tests
would establish whether it is stable.

**P-TR-WORSE (translation moves labels away from native readers; exploratory).**
Translated traces were labelled further from native readers than the direct Urdu traces
([[R-DISC: R / agreement diagnostic]]). We used one translator with sentence-level
segmentation, which can break references that span sentences, such as a later sentence
that points back to the suggestion. The audit found [[R-DISC: n]] omissions of disclosure
language. Translate-then-monitor pipelines can lose the very statements a disclosure
monitor looks for. This must be checked per translator rather than assumed.

**P-CT (the monitor often declined to decide).** The judge returned `cannot_tell` or a
technical failure for [[R-DISC: rate]] of [[R-DISC: arm]] traces, more often than for
[[R-DISC: comparison arm]]. Binary disclosure rates therefore describe the decidable
subset. S1–S3 and the worst-case bounds show how far this could move G. For a deployed
monitor, coverage loss of this kind is a validity problem in its own right, separate from
accuracy on the cases it does decide.

**P-MISS (missingness, non-decisions, failures).** Missingness was concentrated in
[[R-DISC: arm/model/language]]. Binary estimates describe the decidable subset; the worst-case
bounds show how far conclusions could move. A differential rate of judge non-decisions or
translation failures is itself a validity finding: coverage, not only accuracy, can
differ across languages.

**P-END (always).** Before differences in automated disclosure rates across languages are
read as differences in what
models disclose, they need a native reference on the same
traces. Natural extensions:
- an English native reference and a paraphrase control;
- more languages, monitors and translators;
- larger and natively reasoning models;
- open-ended tasks.

## 7. Limitations

**Models.** We studied two small, quantized open-weight models (1.7B and 4B parameters)
from different families. Two configurations can show whether a pattern holds for more
than one model, but cannot separate family, size, quantization or decoding, and they are
far from the frontier systems where monitoring is most often proposed.

**Languages.** Urdu is the only non-English language. Our results are a case study of
one under-resourced, Perso-Arabic-script language and do not establish behavior for
other languages, scripts or resource levels.

**Task, items and cues.**
- The task is one four-option science QA benchmark.
- The Urdu items come from an existing translation (UrduBench). A native reviewer judged
  all 120 used items equivalent, but language and item translation remain confounded.
- The Urdu prompts keep the elicitation sentence and the `Final answer:` marker in
  English.
- The cues are low-stakes misleading suggestions of a single answer letter, with one
  wording per source (authority, user). They are a controlled probe chosen for
  measurement clarity, not a model of real-world manipulation.

**What is measured.** Both models produced prompted rationales. Qwen's native thinking
mode was disabled after an excluded pilot showed it did not reason in Urdu in our setup.
The rationale is model-generated output, not a privileged view of internal state.
"Disclosure" is an explicit textual statement of a suggestion's influence. We make no
claim about faithfulness, intent or internal computation, and we study one narrow
construct among the many that monitors target.

**Monitor and translator.**
- All automated results concern one quantized open-weight judge under one prompt, whose
  instructions are in English for all traces. LLM judges can be biased by the language of
  the text they score, and this is exactly what G is designed to detect. It is not
  separately characterized for English, because there is no English human reference.
- The translator is one system (IndicTrans2) used with sentence-level segmentation,
  which can lose references that span sentences.
- Translated-trace results are properties of this translator–judge pair.
- No English-to-English paraphrase control was run, so changes after translation are not
  attributed to language rather than rewriting.

**Human reference.**
- The native-reader reference rests on two raters and an adjudicator labelling 312
  traces: 120 Cue-A and 36 Cue-B per model, before missingness.
- The construct has acknowledged boundary cases.
- There is no English human reference, so English automated labels are not validated
  and the English side of any apparent gap rests on the monitor.

**Statistics.** Analyses are descriptive. Many intervals are reported without error
control, so some will exclude zero by chance, and we give weight only to patterns that
replicate across models. Percentile bootstrap intervals over 36 items (Cue B) may be
anti-conservative. Binary estimates exclude `partial` and `cannot_tell`; sensitivity
analyses bound this.

**Provenance.**
- One generation call timed out and is retained as missing. Eight of 1,871 direct-judge
  outputs (5 malformed, 3 without a label) are retained as missing, not rerun.
  The first translation implementation violated the frozen batch-size rule. Six
  failure records for three rationales are retained, and the contract was amended
  (D-TR-1–6) before any translation succeeded.
- Generation code ran from an uncommitted working tree, identified by recorded
  implementation hashes and archived afterwards. The analysis code was likewise frozen by
  content hash rather than by commit.
- Sampling on the hardware used is not bitwise reproducible.
- The Urdu dataset states no licence of its own, so item text is not redistributed.

**Generalization.** All conclusions are conditional on these models, this monitor, this
translator, these cues, this task and Urdu. They are best read as a tested procedure plus
one measurement, which motivates broader replication.

## 8. Conclusion (template)

An automated monitor's disclosure rates for Urdu and English reasoning need not describe
the model. On the same Urdu rationales, the monitor we studied [[R-CONC-1: G, per model]].
Translating the rationales before monitoring [[R-CONC-2: R, descriptive]].
[[R-CONC-3: activated implication]]. For monitors intended for multilingual use, checking
them against native readers on the same traces is a practical prerequisite for
interpreting cross-lingual differences.

---

## Back matter

**Author contributions (CRediT template).** [[AUTHOR_INFO: per author — Conceptualization;
Methodology; Software; Validation; Formal analysis; Investigation; Data curation; Writing
— original draft; Writing — review & editing; Supervision (only if confirmed); Project
administration.]] AI assistants (Claude Code and Codex) were used to draft documentation and manuscript
text and to write and review code. All scientific decisions and approvals were made by
the author, who checked the final text and is responsible for it.
<!-- Check the chosen server's AI-disclosure policy before upload. -->

**Acknowledgments.** [[HUMAN_INPUT: insert acknowledgment option A (named, only with Amna Anwar
Riaz's consent) or option B (anonymous) from research/WORKSHOP_V1_HUMAN_INPUT_AND_CITATION_QUEUE.md §C]] We also thank
[[HUMAN_INPUT: raters/adjudicator, named only with consent]]. [[AUTHOR_INFO: funding, or "This work
received no specific funding."]]

**Ethics statement.** The study analyzes text generated by AI models in response to
public multiple-choice science questions. No personal or sensitive data are processed,
and no intervention is directed at any person.

**Human involvement:**
1. A native Urdu speaker reviewed the Urdu item translations, cue wording and language
   instruction (completed).
2. The same reviewer verbally confirmed the meaning of 16 synthetic Urdu rater-training
   sentences (completed; no written form).
3. Two raters and an adjudicator are to label 312 model-generated rationales with a
   written rubric (planned).

All involved act as reviewers of text. No data are collected about them beyond
qualification and administrative records, and rater labels are stored under pseudonyms.
An institutional determination was requested from UNC Charlotte's Office of Research
Protections and Integrity (ORPI) on or before 2026-10-04. No determination had been
received at the time of writing, and none is claimed. [[ORPI: "ORPI determined on [date]
that [verbatim determination]." Annotation began only after it was received.]] The two
completed reviews took place before the request and were described in it.

**Raters and compensation.** [[ORPI: consent / information-sheet statement as required by
the determination]] [[HUMAN_INPUT: compensation statement]].

**Release.** We release prompts, cues, rubrics, synthetic training material, code and
provenance records. Model outputs and labels are released under anonymized identifiers,
subject to the dataset's licence terms and rater consent. Because the dataset states no
licence of its own, item text is not redistributed. The task content is general
science. Released outputs will be screened before release [[HUMAN_INPUT: confirm the
screen was done]].

**Data availability.** <!-- Default = Version 3 (research/WORKSHOP_V1_DATA_AVAILABILITY_OPTIONS.md). Upgrade only after licence clarification. -->
Items are from OpenBookQA (Mihaylov et al., 2018), via the Urdu release
`large-traversaal/openbookqa_urdu_final` (revision `e4186f6b`) from the UrduBench project
(Shafique et al., 2026). That release states no licence of its own and defers to the
original dataset's terms. We therefore do not redistribute item text or outputs that quote
it.

We release:
- item identifiers with row hashes;
- prompt and cue templates;
- judge and rater rubrics;
- synthetic training material;
- per-stage provenance records (configuration, artifact and stage hashes; authorizations;
  incident records).

Model rationales, judge outputs, translations and adjudicated labels are retained with
published SHA-256 hashes. [[HUMAN_INPUT: release route for these, e.g. "available for
verification on request" or "released after licence clarification"; individual rater
labels only under pseudonyms and only as consent permits]] [[PROVENANCE: repository URL
and archive DOI, once they exist]].

**Code availability.** Generation, judging, translation, segmentation, human-packet and
analysis code, with all configuration files, [[PROVENANCE: repository URL; archival
snapshot commit, described as in research/WORKSHOP_V1_PRE_UNSEAL_AUDIT.md §10]].

**Reproducibility statement.** Every stage is bound to recorded hashes:
- generation configuration `7b00e996…0fec`;
- dataset revision and manifests;
- model, judge and translator artifacts;
- Judge V2 prompt `050ed492…` and specification `a8cb84c1…`;
- direct-judge stage `3077fae1…7589`;
- translation artifacts `84cad691…a2bd`, effective configuration `106f366c…4171` (base
  `74b81473…99bc` plus amendment D-TR-1–6 `3a054e8b…0dc5`), and stage
  [[TRANSLATION_STAGE_HASH]];
- translated-judge stage [[TRANSLATED_JUDGE_STAGE_HASH]];
- analysis code, by content hash `1671bc3c…f3db` [[PROVENANCE: archive commit of the
  frozen analysis code]].

Raw outputs and per-stage provenance records, including the infrastructure-failure,
serialization-fix and resume records, are retained unmodified. Sampling is not bitwise
deterministic on the hardware used, so regenerated outputs will differ byte-for-byte.
Every reported statistic is deterministically reproducible from the stored records with
the archived analysis code (B = 10,000, seed 0).

## Appendices

- **A.** Verbatim prompts, cues and instructions (EN/UR).
- **B.** Judge V2 prompt, verbatim.
- **C.** Rater instructions, decision tree and synthetic training examples.
- **D.** Hash and provenance table, by stage.
- **E.** Missingness cascade (planned → eligible → valid → complete).
- **F.** Judge × human confusion matrices.
- **G.** Sensitivity analyses S1–S5 and the exploratory compliance analysis.
- **H.** Data dictionary, including the `population_role` note.
- **I.** Segmentation algorithm, translation failure counts, translation audit protocol.
- **J.** Dated decision record (D5, language instruction, D-PG-1..6).
- **K.** Generation incident record (Attempt 1; serialization fix; resume; timeout).

## References

<!-- Every entry below is recorded as VERIFIED in literature/CITATION_VERIFICATION.md
(§A, §D, §G, §H). Re-check arXiv versions and venues on the upload date. -->

- Chen, Y., Benton, J., Radhakrishnan, A., Uesato, J., Denison, C., Schulman, J., et al.
  (2025). Reasoning models don't always say what they think. arXiv:2505.05410.
- Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and
  Psychological Measurement*, 20(1), 37–46. https://doi.org/10.1177/001316446002000104
- Deng, Y., Zhang, W., Pan, S. J., & Bing, L. (2024). Multilingual jailbreak challenges
  in large language models. ICLR 2024. arXiv:2310.06474.
- Doğruöz, A. S., Liao, X., Blaschke, V., Prange, J., Li, S., & Adelani, D. I. (2026).
  Challenges and recommendations for LLM-as-a-judge in multilingual settings and for
  low-resource languages. arXiv:2607.02235 (Findings of EMNLP 2026, per arXiv comment).
- Emmons, S., Jenner, E., Elson, D. K., Saurous, R. A., Rajamanoharan, S., Chen, H.,
  Shafkat, I., & Shah, R. (2025). When chain of thought is necessary, language models
  struggle to evade monitors. arXiv:2507.05246.
- Ercolano, L. (n.d.). *DialectShift-Monitor* [Software repository].
  https://github.com/LucasErcolano/DialectShift-Monitor (accessed 2026-10-04).
- Fu, X., & Liu, W. (2025). How reliable is multilingual LLM-as-a-judge? Findings of
  EMNLP 2025. arXiv:2505.12201.
- Gala, J., Chitale, P. A., AK, R., Gumma, V., Doddapaneni, S., et al. (2023).
  IndicTrans2: Towards high-quality and accessible machine translation models for all 22
  scheduled Indian languages. *Transactions on Machine Learning Research*.
  arXiv:2305.16307.
- Gemma Team (Kamath, A., Ferret, J., Pathak, S., et al.) (2025). Gemma 3 technical
  report. arXiv:2503.19786.
- Korbak, T., Balesni, M., Barnes, E., Bengio, Y., et al. (2025). Chain of thought
  monitorability: A new and fragile opportunity for AI safety. arXiv:2507.11473.
- Lanham, T., Chen, A., Radhakrishnan, A., et al. (2023). Measuring faithfulness in
  chain-of-thought reasoning. arXiv:2307.13702.
- Mihaylov, T., Clark, P., Khot, T., & Sabharwal, A. (2018). Can a suit of armor conduct
  electricity? A new dataset for open book question answering. In *Proceedings of
  EMNLP 2018*, 2381–2391. https://doi.org/10.18653/v1/D18-1260
- Onyame, E., Zhou, R., Thopalli, K., Kailkhura, B., & Agarwal, C. (2026). The fragility
  of chain-of-thought monitoring across typologically diverse languages.
  arXiv:2605.27901.
- Qi, J., Chen, S., Xiong, Z., Fernández, R., Bitterman, D. S., & Bisazza, A. (2025).
  When models reason in your language: Controlling thinking language comes at the cost
  of accuracy. arXiv:2505.22888.
- Qwen Team (Yang, A., et al.) (2025). Qwen3 technical report. arXiv:2505.09388.
- Shafique, M. A., Mehboob, A., Fiaz, L., Qadeer, M. U., & Farooq, H. (2026). UrduBench:
  An Urdu reasoning benchmark using contextually ensembled translations with
  human-in-the-loop. arXiv:2601.21000. Leaderboard:
  https://github.com/traversaal-ai/urdubench_leaderboard (accessed 2026-10-04).
- Sharma, M., Tong, M., Korbak, T., Duvenaud, D., Askell, A., et al. (2023). Towards
  understanding sycophancy in language models. arXiv:2310.13548.
- Turpin, M., Michael, J., Perez, E., & Bowman, S. R. (2023). Language models don't always
  say what they think: Unfaithful explanations in chain-of-thought prompting. NeurIPS
  2023. arXiv:2305.04388.
- Xiong, Z., Chen, S., Qi, Z., & Lakkaraju, H. (2025). Measuring the faithfulness of
  thinking drafts in large reasoning models. NeurIPS 2025. arXiv:2505.13774.
- Yang, S., et al. (2025). Investigating CoT monitorability in large reasoning models.
  arXiv:2511.08525.
- Yazdani, S., España-Bonet, C., Avramidis, E., Hamidullah, Y., & van Genabith, J.
  (2026). A comprehensive evaluation of chain-of-thought faithfulness in Persian
  classification tasks. In *Proceedings of LoResLM 2026* (co-located with EACL 2026).
  ACL Anthology 2026.loreslm-1.27.
- Yong, Z.-X., Menghini, C., & Bach, S. H. (2023). Low-resource languages jailbreak
  GPT-4. NeurIPS 2023 Workshop on Socially Responsible Language Modelling Research
  (SoLaR). arXiv:2310.02446.
- Young, R. J. (2026a). Why models know but don't say: CoT faithfulness divergence
  between thinking tokens and answers in open-weight reasoning models.
  arXiv:2603.26410.
- Young, R. J. (2026b). Lie to me: How faithful is chain-of-thought reasoning in
  reasoning models? arXiv:2603.22582.
- Young, R. J. (2026c). Measuring faithfulness depends on how you measure: Classifier
  sensitivity in LLM chain-of-thought evaluation. arXiv:2603.20172.
- Zaman, K., & Srivastava, S. (2025). Is chain-of-thought really not explainability?
  Chain-of-thought can be faithful without hint verbalization. arXiv:2512.23032.
- Zhao, R., Liu, Y., Schütze, H., & Hedderich, M. A. (2026). A comprehensive evaluation
  of multilingual chain-of-thought reasoning: Performance, consistency, and faithfulness
  across languages. Findings of EACL 2026, 5223–5247. arXiv:2510.09555.
- Zhou, E., Resck, L., Hui, Z., & Korhonen, A. (2026). Lower-resource, higher scores:
  Language bias in LLM evaluators. arXiv:2607.14480.
- Zuo, J., et al. (2025). Falcon-H1: A family of hybrid-head language models redefining
  efficiency and performance. arXiv:2507.22448.

# Workshop-v1: PhD application pack and publication positioning

## M. PhD application pack

**CV entries.** Use exactly one, matching the true state. Never upgrade a state.

| State | CV wording |
|---|---|
| In preparation | "[Name]. *[Title].* Manuscript in preparation." |
| Preprint | "[Name]. *[Title].* arXiv:[ID], [year]. Preprint; not peer reviewed." |
| Submitted | "[Name]. *[Title].* Submitted, [year]." (Name the venue only if its anonymity policy allows) |
| Under review | "[Name]. *[Title].* Under review at [venue], [year]." (Only while a review is actually in progress) |
| Accepted | "[Name]. *[Title].* [Workshop name] at [Conference] [year] ([archival/non-archival])", or "*Findings of [Conference] [year]*", or "*Proceedings of [Conference] [year]*". Use exactly the track that accepted it |

**SOP paragraph.**
> AI oversight increasingly relies on automated monitors that read a model's written
> reasoning, but most evidence that such monitors work comes from English. In my recent
> project I asked a measurement question: when a monitor reports a different result for
> reasoning written in Urdu, is that a property of the model or of the monitor? I built a
> same-trace design in which an automated monitor and native Urdu readers label identical
> model rationales with identical inputs, and the same rationales are re-scored after
> translation. I implemented it as a fully provenance-tracked pipeline, with prespecified
> analysis, documented decisions and every failure retained. The project taught me to
> treat evaluation instruments as objects of study in their own right. In graduate
> school I want to extend this toward validated, multilingual oversight methods.

Use "built", "implemented" and "ran" only for stages that are complete when the statement
is written. Do not state findings until they exist.

**Professor outreach (2 sentences).**
> I recently designed and ran a prespecified study comparing an automated chain-of-thought
> disclosure monitor with native Urdu readers on the same model rationales, to separate
> monitor error from model behavior across languages. I'm interested in how your group's
> work on [topic] could inform validating AI oversight tools beyond English.

**LinkedIn / project description.**
> **Cross-lingual validation of automated reasoning monitors (independent research).**
> Designed a same-trace study testing whether an LLM-based monitor of model reasoning
> reads Urdu as reliably as native readers do. Built a fully local, hash-tracked pipeline
> covering:
> - 3,312 generations from two open-weight models in English and Urdu;
> - direct and translate-then-monitor judging;
> - a blinded, double-annotated native-reader reference;
> - a prespecified descriptive analysis.
>
> [Status: manuscript in preparation / preprint at link.]

## N. Publication positioning

**Workshop.**
- *Offers:* a careful, single-language measurement-validity case study, with a
  native-reader reference, input parity, a translation contrast and transparent
  governance.
- *Would weaken acceptance:* overclaiming generality, vague construct language, or
  intervals too wide to say anything.
- *Extension that helps most:* clear qualitative examples and a crisp statement of the
  decomposition logic.
- *Must not claim:* novelty from Urdu, monitorability or faithfulness in general, or
  mitigation by translation.

**Findings / main track.**
- *Offers:* the same design, plus release.
- *Would weaken acceptance:* one language, two small models, one judge, no paraphrase
  control or English reference. Reviewers will see it as a case study.
- *Extension that helps most:* at least two more languages (one in a different script or
  resource tier), a reasoning model with native thinking, a second judge, and an English
  human reference.
- *Must not claim:* cross-language or cross-model generality from the current data.

**TMLR-style extended study.**
- *Offers:* thoroughness and reproducibility, which suit a venue that values correctness
  over novelty.
- *Would weaken acceptance:* an extension without the same governance discipline.
- *Extension that helps most:* multi-language and multi-monitor replication, a paraphrase
  control, a coverage check of the interval method at the realized cluster counts, and a
  full data release once licensing allows.
- *Must not claim:* confirmatory results unless a separately preregistered confirmatory
  study is run.

No deadlines are asserted. Verify each venue's call and preprint policy before choosing.

# Translate-then-monitor protocol — translator unresolved

This is a same-trace measurement diagnostic, not an established mitigation. No translator
model/provider or minimum context-size heuristic is selected. Complete input preservation
is required by the scientific comparison; that requirement does not imply a universal
numeric context threshold. No real translation was performed to develop this package.

## Prospective registration

Before outputs, approve candidate-selection criteria independent of scientific effects:
language competence, measured semantic/disclosure preservation on a separate calibration
set, complete-input capacity, version stability, cost/resources and governance. Register
`TranslatorSpec`: provider/model, immutable version, exact context limit/unit and accounting
method (including tokenizer/version and prompt overhead), decoding/output budget, prompt
or explicit inapplicability, source/target language, determinism settings/limitations,
identity evidence and provenance. Mutable aliases are rejected. Hosted version claims
must be supported by provider evidence; software cannot guarantee that a service is stable.

Freeze translator calibration versus heldout evaluation sets, human adequacy rubric,
acceptance procedure, reviewer qualifications/counts and sampling before scientific
translation selection. No fixed NLLB choice, model scale, context minimum, adequacy
threshold or favourable recovery score is adopted. Selection remains HUMAN REQUIRED.

## Four controls

| Control | Input and comparison | What it can diagnose |
|---|---|---|
| Urdu → English | Same Urdu trace, translated once, judged by the **same** English-centric judge spec used directly | Change attributable to the translation/monitor-input pathway, conditional on equivalence |
| English → English paraphrase | Original English trace versus independently registered paraphrase control | Sensitivity to rewriting rather than language alone |
| Backtranslation | English translation → Urdu, linked to the parent translation | Possible drift; not proof of equivalence |
| Native/bilingual equivalence audit | Source and output reviewed under a frozen rubric | Adequacy, disclosure changes, omission/addition and preservation errors |

Monitor-arm notation is D-059/M1 protocol: native M3 minus direct M1 is the gap;
translated M4 minus direct M1 is recovery. An in-language M2 judge is a separate diagnostic,
not a silent replacement for the direct comparator. The same `JudgeSpec` hash is required
for direct and translated labels in one recovery report. Register different-arm comparisons
separately. English controls are reported separately from Urdu traces.

## Integrity and failures

`TranslationRequest` contains only opaque ID, text/hash, languages/control and lineage.
It contains no human labels, model/condition identity, answers or desired outcomes.
`TranslationRecord` binds request/root/source hashes, source language, translated text/
output hash, complete translator spec/settings, input/output-budget accounting, truncation,
errors and provenance. `validate_translation` checks these against the expected spec.
Backtranslation must bind the parent output hash and original root hash; a foreign,
truncated or failed parent is refused. Preserve the exact text and error evidence.

No content-based retry, favourable output selection, concatenation, or silent segmentation
is specified. Future executor/retry/segmentation policies require prospective approval.
Context overflow, truncation or translation errors make a record unusable for the paired
primary comparison. Preserve the failed record and denominator. A translated judge label
without a usable matching translation is rejected. No translation adapter performs model
execution in this package.

## Native audit

`EquivalenceAudit` stores an independent reviewer pseudonym, versioned rubric, source/
output/record hashes, provenance, rationale, semantic adequacy, disclosure preservation,
omission, addition/explicitation, answer-option preservation and truncation observations.
Unknown/abstain categories remain explicit. Multiple reviews retain distinct identities;
no automatic consensus or acceptance rule is implied. `audit_summary` reports all category
counts and unaudited records; it **never certifies equivalence**.

A fluent English output can omit Urdu disclosure, add an acknowledgment, or alter option
references. Increased positive detection alone may reflect these artifacts. Report native
reference agreement, both discordance directions and audit findings with recovery. A
failure to recover does not prove information was absent at generation: translator quality,
monitor limitations and uncertainty can also explain it. The older research-plan hypothesis
table's shorthand must not be read as that causal implication.

**STOP** until translator selection, bilingual/native audit, governance, exact settings and
separate authorization are approved. English generator authorization covers none of these.

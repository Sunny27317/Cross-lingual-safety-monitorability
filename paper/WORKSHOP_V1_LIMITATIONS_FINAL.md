<!-- Drop-in for §7 of paper/WORKSHOP_V1_PREPRINT.md. Outcome-blind; written 2026-10-06. -->

# 7 Limitations

**Scope.** This is a case study of one language, two small models, one monitor and one
translator. Its contribution is a measurement design and its result for these
configurations, not a general statement about multilingual monitoring.

**One non-English language.** Urdu was chosen because it is a widely spoken, lower-resource
language for these models, written in a right-to-left Perso-Arabic script, with
frequent English code-mixing in technical writing. These properties may matter for
monitoring, and they also limit transfer: other scripts, morphologies and
code-switching norms may behave differently. The Urdu items are translations of the
English ones, so every English–Urdu contrast compares the two versions of the same items,
not the two languages as such.

**Two small model configurations.** Qwen3-1.7B (Q8_0) and Gemma-3-4B-it (QAT Q4_0) differ in
family, size, quantization, tokenizer and decoding. We never pool them, and we attribute
differences only to "the model configuration as deployed". Larger and frontier models may
reason, code-switch and disclose differently.

**Prompted rationales, not native reasoning channels.** Both models wrote rationales
because the prompt asked for them, and native thinking was disabled for Qwen. Disclosure
here is a property of visible prompted text. It does not show how internal computation
used the suggestion, and it may differ from disclosure in native reasoning traces.

**One monitor.** All automated labels come from one quantized monitor (Falcon-H1-7B) with one
prompt. Other monitors, prompts or larger judges could disagree with native readers
differently. G characterizes this monitor.

**The monitor sees the suggestion.** For parity with human readers, the monitor is given the
suggestion sentence, so it could partly match keywords. The `partial` label, the
judge-`disclosed` × reader-`partial` confusion cell, and the identical inputs for native
readers bound this, but do not remove it.

**Translation dependence and no paraphrase control.** Translate-then-monitor uses one
sentence-level translator, which can add, drop or soften disclosure language and break
references that span sentences. With no paraphrase control, a difference between direct
and translated monitoring cannot be attributed to language rather than to rewriting. R
and R_full are therefore descriptive. A translation audit (S4) qualifies them, and its
completion is reported.

**Identity translations.** Six rationales contain no Arabic-script letter, so their
"translation" equals the source. They stay in the primary translated arm with an
explicit flag, and a secondary analysis excludes them.

**Native-reader reference.** H comes from two raters and an adjudicator, and it is a
reference, not ground truth. Agreement is reported continuously (κ with intervals,
raw agreement, the full contingency table), and `abstain`/`unresolved` items are
missing, never imputed. Native readers can share the monitor's ambiguities at the
`partial` boundary. There is no English human reference, so no human-validated
English–Urdu disclosure comparison is possible. AG remains an automated measurement.

**Precision and few clusters.** Each G cell rests on at most 120 (Cue A) or 36 (Cue B)
rationales per model, before exclusions. Planning calculations from the design alone
suggest interval half-widths of roughly 6–14 percentage points for Cue A and 10–21 for
Cue B. Percentile bootstrap intervals may under-cover with 36 clusters. Intervals that
include zero are compatible with practically relevant gaps.

**No multiplicity correction.** Many intervals are reported, and some will exclude 0 by
chance. We report every planned interval, state family sizes, and give weight only to
patterns that replicate in sign across both models. We perform no hypothesis tests.

**Post-generation decisions.** Several analysis decisions (compliance reporting, timeout
handling, the scope of R, Judge V2, translation segmentation, bootstrap conventions) and
the interpretation framework were fixed **after** generation. All were fixed before any
monitor or human label was examined. The framework's author saw only provenance fields
and overall parse counts. We call these choices frozen relative to result inspection, not
preregistered.

**Technical failures and amendments.** One generation timed out (retained as missing). Eight
direct-monitor outputs were malformed or unlabeled (retained as missing). A batching defect
in the first translation implementation caused three rationales to fail, before any
translation succeeded. A dated amendment then fixed the procedure, and all 935 rationales
were translated. Executed code ran from uncommitted working trees and is identified by
content hash. Appendix J lists every event.

**Dataset domain and licensing.** Items are grade-school science questions, so other
domains and safety-relevant tasks may differ. The Urdu dataset states no licence of its
own, so we release identifiers and hashes rather than item text.

**Causal interpretation.** G compares two readings of the same text. It can show that the
monitor and native readers diverge, but not why. A positive G does not show that models
are unfaithful, and a null G does not show that the monitor is reliable in general.

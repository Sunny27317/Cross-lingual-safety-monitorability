# Workshop-v1: final contributions (result-independent)

These four bullets appear at the end of Introduction §1. Each is a design or method claim.
None depends on any result.

1. **Empirical design.** A same-trace design that separates monitor divergence from
   differences in the text. Automated and native-reader disclosure labels are paired on
   identical Urdu rationales, and automated rates are compared across the English and Urdu
   versions of the same 120 items, for two model families and two cue sources (third-party
   authority; user assertion).
2. **Methodological contribution: native-reader validation with parity.** A blinded,
   double-annotated, adjudicated native-Urdu reference on 312 rationales. Raters and the
   automated monitor receive identical inputs (question, options, suggestion, rationale)
   and identical label definitions (`disclosed`, `not_disclosed`, `partial`,
   `cannot_tell`). Agreement is reported continuously, without verbal bands.
3. **Translation contrast.** A translate-then-monitor arm on the same rationales. It
   changes only the language in which the monitor reads a fixed text, uses a
   deterministic no-truncation segmentation procedure, and includes a translation audit.
   It is reported descriptively, with no mechanism claim.
4. **Reproducibility and governance.** Frozen, hashed item manifests and model, judge and
   analysis artifacts. A dated decision record that separates prospective,
   post-generation and engineering decisions. All technical failures (one generation
   timeout; eight non-valid judge outputs) retained and reported rather than rerun. Code,
   identifiers, prompts, rubrics and provenance released.

**Not a contribution:** novelty of multilingual monitoring, of translate-then-monitor, or of
including Urdu. Also not a contribution: any result about faithfulness or internal
reasoning.

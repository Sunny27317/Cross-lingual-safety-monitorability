# English–Urdu measurement validity — prospective infrastructure

**ENGINEERING READY; scientific collection/monitoring/translation NOT AUTHORIZED.**
No English pilot outputs were inspected to construct this package. No Urdu inference,
scientific judge, human annotation or real translation was run here.

The question is whether apparent monitoring failure on Urdu traces reflects differences
in reasoning disclosure or limitations of the monitor's language access. The study
preserves native-human validation, same-trace translate-then-monitor, model/monitor
separation, controlled measurement validity and an Urdu focus. This framework has not
yet demonstrated that any of those mechanisms occurs in scientific data.

Read in order:

1. [Urdu protocol](URDU_PROTOCOL.md): population and design boundaries.
2. [Native validation](NATIVE_VALIDATION_PROTOCOL.md): human-required reference.
3. [Translation protocol](TRANSLATION_PROTOCOL.md): provider-independent controls.
4. [Analysis plan](MEASUREMENT_VALIDITY_ANALYSIS_PLAN.md): signs, pairing and interpretation.
5. [Report template](REPORT_TEMPLATE.md): prewritten output structure.

MMLU remains primary; UrduBench OpenBookQA is a secondary robustness candidate only
where compatible. UrduMMLU remains unverified pending provenance, licensing and schema
review. No dataset or translator is substituted/approved by an adapter's existence.

Safe engineering check: `python3.11 -m clsm.downstream fixture-check`.
It runs a fixed in-memory synthetic English/Urdu comparison, not the Urdu experiment.
External and human blockers are in the [master matrix](../../docs/DOWNSTREAM_BLOCKER_MATRIX.md).

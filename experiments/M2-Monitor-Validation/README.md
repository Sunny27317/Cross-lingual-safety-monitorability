# Downstream monitor validation — prospective infrastructure

**ENGINEERING READY; SCIENTIFIC EXECUTION NOT AUTHORIZED.** This package was developed
independently of the English pilot. Its author did not inspect that pilot's results,
execution branch, traces, accuracy, parsing diagnostics, or effects. This is not a claim
about whether another researcher has collected data elsewhere.

Start with the [master blocker matrix](../../docs/DOWNSTREAM_BLOCKER_MATRIX.md).
The current generator design and authorization boundary are unchanged. The M1 pilot
can eventually supply provenance-bound English traces and feasibility diagnostics;
it cannot select a judge, establish Urdu validity, or fix confirmatory effect assumptions.

The directory names M2/M3/M4 name **project stages**. Historical monitor arms M1–M4
mean English-centric direct, in-language direct, native human, and translate-then-English
monitor respectively. They are distinct naming systems.

| Canonical resource | Purpose |
|---|---|
| [Judge protocol](JUDGE_VALIDATION_PROTOCOL.md) | Candidate registration, calibration, heldout comparison |
| [Human reference](HUMAN_REFERENCE_PROTOCOL.md) | Locked reference and independent adjudication |
| [Annotation guide](ANNOTATION_GUIDE.md) | Versioned draft rubric and blinding |
| [Form schema](ANNOTATION_FORM_SCHEMA.json) | Generated strict annotation JSON Schema |
| [Adjudication](ADJUDICATION_PROTOCOL.md) | Preserve originals; resolve disagreements prospectively |
| [Selection record](JUDGE_SELECTION_RECORD_TEMPLATE.md) | Human decisions, no automatic winner |
| [Calibration report](JUDGE_CALIBRATION_REPORT_TEMPLATE.md) | Prewritten results structure |
| [API and reproducibility](../../docs/DOWNSTREAM_INFRASTRUCTURE.md) | Contracts, validation, safe commands |

Safe offline smoke check (Python 3.11, core/dev environment):

```sh
python3.11 -m clsm.downstream fixture-check
python3.11 -m pytest tests/downstream
```

The CLI accepts **no scientific input path**, makes no network/model calls, and writes
only stdout. Synthetic identity placeholders and labels are visibly marked. They must
never be promoted to a scientific reference or treated as translator/judge choices.

No model-size requirement, BA/F1/PABAK/kappa cutoff, annotator-count threshold, or
translator context minimum is selected here. D-061's retractions remain in effect.
Existing `M1-Mac-Feasibility/MONITOR_VALIDATION_PROTOCOL.md` and the decision log retain
their history; these documents specify the new infrastructure and remaining decisions.

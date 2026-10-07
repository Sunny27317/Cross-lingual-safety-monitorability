# Workshop-v1 preprint release guard

**PREPRINT MAY NOT BE POSTED UNTIL every gate below is `true`, with its evidence path
filled.** The machine-readable block is the record. Update it only with evidence, never
by assertion.

```json
{
  "schema": "workshop-v1-preprint-release-guard/1",
  "updated_utc": "2026-10-04",
  "may_post": false,
  "gates": {
    "translation_stage_complete":        {"value": false, "evidence": null, "note": "translation stage hash recorded; failures by reason recorded"},
    "translated_judge_complete":         {"value": false, "evidence": null, "note": "translated-judge stage hash; byte-identical non-rationale inputs enforced in the executing path"},
    "orpi_determination_on_file":        {"value": false, "evidence": null, "note": "verbatim reply saved in engineering/provenance with SHA-256"},
    "human_annotation_complete":         {"value": false, "evidence": null, "note": "312 double-labelled, adjudicated, locked; kappa computed per AGREEMENT_REPORTING.md"},
    "final_analysis_complete":           {"value": false, "evidence": null, "note": "frozen analysis (hash 1671bc3c...) run once; immutable result artifact hashed"},
    "result_slots_filled":               {"value": false, "evidence": null, "note": "zero [[...]] and zero [UPPER_SNAKE] slots in the manuscript"},
    "abstract_tense_guard_removed":      {"value": false, "evidence": null, "note": "only after the four stages above are true"},
    "provenance_reconciled":             {"value": false, "evidence": null, "note": "date-discrepancy register in appendix; pause note; duplicate verbal-review records reconciled"},
    "archival_snapshot_described":       {"value": false, "evidence": null, "note": "wording per PRE_UNSEAL_AUDIT.md section 10; hashes verified or caveat stated"},
    "citations_claims_final_scan":       {"value": false, "evidence": null, "note": "citations re-checked; claim ledger mapped; tripwire scan clean"},
    "author_ack_release_decisions":      {"value": false, "evidence": null, "note": "author/affiliation, consent-based acknowledgments, funding, release route"}
  }
}
```

**Human-readable rule.** `may_post` becomes `true` only when all eleven gates are `true`.
The investigator flips it after reading the final PDF end to end. The HTML comment at the
top of the preprint repeats this rule.

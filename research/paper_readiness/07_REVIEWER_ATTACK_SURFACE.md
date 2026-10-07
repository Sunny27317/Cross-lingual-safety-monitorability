# 07 — Reviewer attack surface

**Classes:**
- **AA:** already addressed.
- **AB:** addressable before submission, without changing the locked experiment.
- **UL:** unavoidable limitation.
- **SD:** requires a supervisor or investigator decision.

| # | Criticism | Class | Concrete fix / response (no retrospective design change) |
|---|---|---|---|
| 1 | One non-English language; no generalization | UL | Framed as a case study (title option 3, scope statements, tier-3 ban) |
| 2 | Two small quantized models | UL | Stated; models never pooled; cross-model flag only |
| 3 | Prompted rationales ≠ native reasoning traces | UL / AA | §4.4 explains D5; claims restricted to visible text |
| 4 | Disclosure ≠ faithfulness / monitorability | AA | Terminology table A1; construct defined; banned terms |
| 5 | LLM judge validity | AA | This is what G measures, against native readers with identical inputs |
| 6 | Judge sees the suggestion (keyword matching) | AA / AB | Parity with raters; `partial` captures mention-only. **AB:** highlight the judge `disclosed` × human `partial` cell in T7b |
| 7 | Translation artifacts; one sentence-level translator | UL / AB | **AB:** complete the translation audit on the H/D/T subset and report added/omitted counts beside R; S4 |
| 8 | Translation implementation incident | AA / AB | Disclosed in §4.7 and Limitations. **AB:** save the amended-path synthetic validation as an artifact (C6) |
| 9 | No paraphrase control or English human anchor | UL | R descriptive only (D-PG-3); stated |
| 10 | Many intervals, no error control | AA | Multiplicity statement; replication rule; all planned comparisons reported |
| 11 | Few clusters (36 Cue-B items) → under-coverage | UL / AB | **AB:** add one Limitations sentence (present); report counts with every rate |
| 12 | Complete-case G/R | AA | S1–S3, cascade, worst-case bounds |
| 13 | Human reference thin (two raters); author as rater? | SD | **SD:** prefer that the investigator does not rate. If they do, disclose it and they do not adjudicate |
| 14 | Adjudication-code mismatch (abstain trigger, `unresolved`) | AB | Engineering fix before annotation (C3) |
| 15 | Six identity "translations" | SD | **SD:** judge them flagged, or treat them as missing for T; decide before translated judging (C1) |
| 16 | Uncommitted executed code | AB / SD | **SD:** approve the pre-result archival commit; Methods §4.5 wording is already honest |
| 17 | Dated decisions after generation (D-PG, D-TR) | AA | Timeline in Appendix J; all before any result was examined |
| 18 | D-PG-6 approved after direct-judge authorization | AA | Stated as "before any judge output was examined"; labels were sealed |
| 19 | Dataset licence unstated | AA | IDs and hashes only (Version 3 release) |
| 20 | Item translation confounds language | UL | 120/120 native equivalence review; wording "English and Urdu versions of the items" |
| 21 | Mixed-language Urdu prompt | UL / AA | Disclosed in §4.4 |
| 22 | Single cue wording per source | UL | Stated; "wording/source-dependent" phrasing only |
| 23 | Missing timeout and 8 judge non-valid outputs | AA | Retained, not rerun; reported by cell (T2a) |
| 24 | Ethics: reviews done before an ORPI request | AA / SD | Disclosed in the request and Ethics. **SD:** follow the ORPI reply |
| 25 | Translated-judge executor does not check the amendment or the seal | AB | Engineering fix before translated judging (C2) |

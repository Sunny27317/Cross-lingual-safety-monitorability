# Translation audit (S4): canonical protocol (2026-10-07; not performed)

**Sources.**
- Plan §2 (S4: "R recomputed excluding audit-flagged translations").
- D-PG-3 ("report R together with the translation-artifact audit").
- `research/POST_PILOT_METHODS_DECISIONS.md` (audit every translation in the declared
  primary measurement sample, locked before monitor outcomes).
- The frozen audit contract `src/clsm/downstream/translation.py::EquivalenceAudit`.

## 1. Frozen sample

The **312 translations of the human-pool rationales**: the declared primary measurement
sample, i.e. the H/D/T triples. That is every translated record whose `generation_id` is
in `human_pool.candidate_pool()`. **All 312 are audited**, including unchanged and the
(at most six) identity translations. No sampling.

## 2. Auditor

- One bilingual Urdu–English auditor with native or near-native Urdu reading and strong
  English.
- **Not** one of the two primary raters. If the auditor is a rater, the audit happens only
  after that rater has locked their labels.
- Never the adjudicator during adjudication.
- Pseudonym: AUD.

## 3. What the auditor sees, and does not see

- **Sees:** the Urdu source rationale and its English translation, side by side; the
  suggestion sentence; the question and options (to recognize references to them).
- **Never sees:** any judge label (direct or translated), any rater label, the model,
  the condition, the answer key, or the study's results.
- **Procedure:** to reduce anchoring, the auditor first marks disclosure in the source and
  the target separately (randomized order across items), then compares them.

## 4. Taxonomy (the frozen `EquivalenceAudit` fields)

| Field | Values | Meaning |
|---|---|---|
| `semantic_adequacy` | adequate / inadequate / uncertain / abstain | Overall meaning preserved |
| `disclosure_preservation` | preserved / changed / uncertain / abstain | Any statement of the suggestion's influence, or its absence, is preserved. Covers **cue preservation**: references to "the reviewer", "you said" or the suggested option |
| `omission` | present / absent / uncertain | Source content missing from the translation |
| `addition_or_explicitation` | present / absent / uncertain | Content, inference or explicitness added |
| `answer_option_preservation` | preserved / changed / not_applicable / uncertain | Option letters and option references unchanged |
| `truncation_observed` | true / false | Translation cut off |
| `rationale` | text | The specific spans |

**Severity** is recorded in the rationale as minor or major. Major means it would plausibly
change a disclosure judgment.

## 5. `audit_flag` definition — INVESTIGATOR DECISION REQUIRED BEFORE UNSEAL (proposed D-FA-7)

The frozen sources require S4 but do **not** define which audit outcomes flag a translation.
Recommended rule (the most construct-relevant and least discretionary):

> `audit_flag = true` iff `disclosure_preservation == "changed"`, **or**
> `answer_option_preservation == "changed"`, **or** `truncation_observed == true`, **or**
> `semantic_adequacy == "inadequate"`.

`uncertain` and `abstain` do **not** flag; they are reported as counts.

Alternative rule: flag only on `disclosure_preservation == "changed"`. It is narrower and
closest to the construct.

**Either rule must be recorded, with its date, before any result is examined.** The
flagged set (translation IDs) is then frozen and hashed.

## 6. How S4 uses it

S4 = R recomputed on complete H/D/T triples, excluding triples whose `translation_id` is in
the frozen flagged set (`final_analysis.recovery_r(exclude_translation_ids=…)`; table T8
row "S4"). It is reported beside the primary R with the denominator change. The audit
counts are reported beside R:
- added disclosure language;
- omitted disclosure language;
- option changes;
- truncations.

## 7. Status

Not performed. Blocked on naming an auditor, and on the ORPI determination if the auditor
is treated like a rater. If the audit is not done before unsealing, report "S4 not
performed: translation audit not completed". Never report a partial audit as complete.

# Workshop-v1 claim ladder (final, outcome-blind; 2026-10-07)

This hardens claims against the external review. Detail is in `WORKSHOP_V1_CLAIM_LEDGER_V2.md`.

**Scope words to use in every claim:**
- "this monitor" (Falcon-H1-7B, Judge V2);
- "two small open models", or "these two model configurations";
- "Urdu rationales" / "the English and Urdu versions of the same items";
- "visible prompted rationales";
- "disclosure of a planted suggestion".

## SAFE (true by design, now)

- We score **the same rationale** directly, after machine translation and by native readers,
  so the three scores differ only in who reads, or in what language the monitor reads.
- The study measures **disclosure-monitoring measurement validity** for one monitor in Urdu.
- All analyses were frozen before any monitor or human label was examined. Intervals are
  descriptive, with no hypothesis tests.
- A native reader judged all 120 item pairs equivalent (written review). The cue and
  instruction approvals were verbal; this changes only if a written sign-off is
  completed.

## CONDITIONAL (only if the result and its interval support it; exact wording in framework §2.1)

- "On Urdu rationales, this monitor labelled [fewer / more] as disclosing than native readers
  did (G = …, 95% CI …)". **Requires** the G interval to exclude 0. Say "replicated" only if
  the sign matches in both models (D-FA-6).
- "No monitor–reader difference was resolved; the data are compatible with gaps from a to b".
  This applies when G's interval contains 0, and never as "equivalent".
- "Automated disclosure rates differed between the English and Urdu versions (AG)". This is
  automated only and never attributed to the model.
- "The automated language gap is at least partly attributable to the monitor". **Requires**
  G ≠ 0 in the matching direction.
- "Translating before monitoring changed automated labels by R_full" (descriptive). "Moved
  labels toward native readers" is allowed only if R points toward H **and** A > 0, and is
  labelled exploratory.
- "The cue shifted answers toward the suggested option (ΔTM)", only in the cells whose
  interval excludes 0.
- Second-judge statements, only if the prospective second judge is run, reported as
  secondary robustness.

## PROHIBITED (never, whatever the results)

- General multilingual or cross-lingual behavior: "across languages", "low-resource
  languages", "representative of non-English monitoring".
- All LLM judges or monitors: "automated monitors fail/succeed".
- Frontier-model behavior, native reasoning channels, "chain of thought" of reasoning
  models.
- Causal faithfulness, unfaithfulness, deception, hiding, concealment, internal cognition,
  "what the model really thought".
- "Translation fixes / mitigates / recovers monitoring".
- Real-world deployment safety, or "safe/unsafe to deploy". OpenBookQA cue disclosure is not
  a safety-critical task.
- "Ground truth", "accuracy of the monitor" (H is a reference), "validated monitor".
- "Significant", "proves", "demonstrates", "equivalent", "no difference", "robust".
- "Preregistered".
- Novelty from including Urdu alone.

**Framing rule.** Lead with "disclosure-monitoring measurement validity", not "AI safety".
Safety appears only as motivation ("monitoring is proposed as an oversight tool"), with
citations.

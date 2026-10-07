# Final claim-hardening audit (manuscript and claim ledger; 2026-10-07)

**Scope.** `paper/WORKSHOP_V1_PREPRINT.md`, `research/WORKSHOP_V1_CLAIM_LADDER_FINAL.md` and
`research/WORKSHOP_V1_CLAIM_LEDGER_V2.md`. Method: a term scan, then reading each hit in
context.

| Prohibited claim | Preprint status | Action |
|---|---|---|
| All languages / general multilingual behavior | "across languages" (12) and "multilingual" (11) occur only in related-work citations, in scope negations ("we claim no novelty for multilingual monitoring") and in the Discussion. One Discussion sentence (P-MISS) generalized "coverage… can differ across languages" | **Fixed:** now "differed between the arms" |
| All monitors | None | — |
| Frontier generalization | One occurrence, in Limitations ("far from the frontier systems") | OK (a limitation) |
| Deception / hiding | 0 | — |
| Internal cognition | 5 occurrences, all disclaimers ("not internal reasoning", "no conclusions about internal computation") | OK |
| Causal faithfulness | "faithful" (17): background citations and disclaimers only | OK |
| Translation fixes monitoring | "mitigation": a negation (§4.9). "recover": a code-path sentence ("recovers these from the source") | OK |
| Deployment / safety performance | P-MOD "validating monitors per deployment" and P-CT "For a deployed monitor…" | **Fixed:** P-MOD now "consistent with… the design cannot isolate why"; P-CT now "In this design… measurement-validity concern". Limitations now state that OpenBookQA is not safety-critical |
| Normative universal rule | P-END "they need a native reference" | **Fixed:** now "This case study illustrates that…" |
| Translation-loss generalization | P-SEG "Translate-then-monitor pipelines can lose…" | **Fixed:** now "In this pipeline…" |
| Significance / proof | "significan" 0. "prove" substrings are all "provenance/approved/improve" | OK |
| First-ever multilingual monitoring study | "first" (9): all "first attempt", "first link", "first-person", "first label"; "novel" (1) is a negation | OK |
| Ground truth | 3, all negations | OK |
| Keywords / title | Title scoped to Urdu rationales; "AI safety evaluation" removed from keywords | Done (earlier commit) |

**Framing.** The paper leads with "disclosure-monitoring measurement validity" (§1 last
paragraph; Limitations "Task"; keywords). Safety appears only as motivation, with
citations.

**Claim ladder / ledger.** Consistent with the above. Conditional claims cite framework §2.1
wording and the D-FA-6 replication rule. The prohibited list is complete.

**Re-run at release:** the scan in `WORKSHOP_V1_PLACEHOLDER_STALENESS_AUDIT.md` §3, after
results are filled, because Discussion text will then be instantiated.

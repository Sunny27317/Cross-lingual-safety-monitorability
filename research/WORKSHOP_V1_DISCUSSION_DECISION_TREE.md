# Workshop-v1 Discussion decision tree

Use this tree to pick which prewritten paragraphs in `paper/WORKSHOP_V1_PREPRINT.md` §6
to activate. The paragraph IDs below match those in the preprint.

**How to apply it**
- Apply the tree **per model × cue** (Cue A on all 120 items; Cue B on its 36 items).
- Several paragraphs can be active at once. Delete every paragraph that is not active.
- "< 0", "> 0" and "∋ 0" refer to the 95% D-PG-6 interval: entirely below zero,
  entirely above zero, or containing zero.
- **P0 and P-END are always active.**

```
1. Apparent language gap AG = D_ur − D_en  (automated, Table 5)
   ├─ AG ∋ 0 ──► go to 2a
   ├─ AG < 0 ──► (English > Urdu) go to 2b
   └─ AG > 0 ──► (Urdu > English) go to 2c

2. Monitor-validity gap G = mean(H − D_ur)  (Table 7)
   2a (AG ∋ 0):
      ├─ G ∋ 0 ──► P-EQ   (state bounds of both AG and G; never "equivalent")
      └─ G ≠ 0 ──► P-G-ONLY  (+ P-EN>UR monitor-side text if G > 0, P-UR>EN text if G < 0)
   2b (AG < 0):
      ├─ G > 0 ──► P-EN>UR (monitor side)
      ├─ G ∋ 0 and upper bound of |G| < |AG| ──► P-EN>UR (text side, "more consistent with")
      └─ G ∋ 0 but interval too wide for that comparison ──► P-EN>UR monitor/text both
                    stated as unresolved; no attribution
   2c (AG > 0):
      └─ P-UR>EN  (if G < 0, add the over-labelling sentence; cite confusion matrix)

3. Model heterogeneity: cross-model flag for ΔTM, AG, G, R
   └─ any "differs" ──► P-MOD  (name the quantity; no causal attribution)

4. Cue heterogeneity: Cue B − Cue A(36) paired interval for ΔTM, D_ur, AG, G
   └─ any ≠ 0 ──► P-CUE  (one wording per source; no general authority/user claim)

5. Translation: R_full and R  (Table 8)
   ├─ R_full ≠ 0 or R ≠ 0 ──► P-TR-SHIFT
   │     ├─ exploratory agreement diagnostic > 0 ──► "moved toward native readers" sentence
   │     └─ otherwise ──► "rate changed without better agreement" sentence
   └─ both ∋ 0 ──► P-TR-NULL  (choose the G>0 or G≈0 sentence from step 2)
   Always: paraphrase-control caveat + audit counts (D-PG-3).

6. Human agreement  (Table 6)
   └─ P-HUM is ALWAYS active. There is no high/low cutoff and no verbal band.
      Report observed agreement, Cohen's κ (five-category and binary) and their 95% CIs.
      Choose the P-HUM bullet by where disagreement concentrates in the contingency
      table:
        • mainly at the partial / mention-versus-influence boundary ──► boundary-ambiguity bullet
        • spread across clear-cut categories ──► rubric-application bullet
        • neither pattern is clear ──► state the observed distribution, use neither bullet

7. Language compliance (Table 1b; exploratory S6)
   ├─ The compliance-restricted analysis changes the direction of any primary estimate,
   │  or moves its interval to/from containing 0 ──► P-COMP-LO (for that model)
   └─ otherwise (the restricted analysis changes no direction or zero-inclusion)
                    ──► P-COMP-HI
   (No new numeric compliance threshold is introduced. D-PG-1.)

8. Missingness / non-decision / failure
   ├─ the worst-case bound for G or R contains 0 while the complete-case interval excludes 0
   ├─ OR the Urdu − English difference in judge non-decision + technical-failure rate excludes 0
   ├─ OR translation failures > 0 and are concentrated by model or trace length
   └─ any of the above ──► P-MISS (name the arm; refer to App. E bounds)
```

**This tree introduces no numeric threshold.** The earlier proposed κ = 0.60 activation
rule was withdrawn on 2026-10-04, before any human label existed. Human agreement is
reported continuously.

## Guardrails that hold whatever the outcome

- Never interpret AG in §5 Results. AG is interpreted only through this tree in the
  Discussion.
- Every activated paragraph that cites an interval excluding 0 must also state how many
  intervals in that family were reported (framework §2.1).
- If no branch fits cleanly, write new interpretation from the confusion matrices and the
  audits, and label it as such. Do not force a fit.
- Translation paragraphs never use "language-specific", "mitigation" or "recovery"
  (D-PG-3).

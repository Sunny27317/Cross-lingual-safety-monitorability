# Workshop-v1 Discussion decision tree V2

**Supersedes V1** (`WORKSHOP_V1_DISCUSSION_DECISION_TREE.md`, kept for history). Written
before any result was examined.

**How to apply it**
- Apply per model × cue.
- Interval notation: "< 0", "> 0", "∋ 0" refer to the D-PG-6 95% interval (entirely
  below zero, entirely above zero, containing zero).
- **No numeric threshold is used anywhere.** "Strong" and "weak" are defined only by
  replication across models and cues.
- Paragraph IDs refer to `paper/WORKSHOP_V1_PREPRINT.md` §6.
- **P0, P-HUM and P-END are always active.**

**Definitions**
- **Replicated:** the interval excludes 0 in the same direction for **both** models (and,
  where applicable, both cues on the shared 36 items).
- **Isolated:** the interval excludes 0 in only one model, or only one cue.

---

### 1. Strong consistent English/Urdu difference
*Trigger:* AG < 0 (or > 0), replicated. Activate P-EN>UR or P-UR>EN, plus the G-based
sub-branch.
- **Interpretation allowed:** "Across both configurations, automated disclosure rates
  differed between English and Urdu rationales in the same direction." The G-based
  attribution follows branch 10 or 11.
- **Interpretation not allowed:** "Urdu reasoning is less (or more) transparent";
  generalizing to other languages.
- **Likely reviewer concern:** the difference may come from the judge (cross-lingual
  reading) or from the translated items.
- **Limitation sentence:** "English rationales lack a human reference, so the English
  side of the gap rests on the monitor."
- **Future-work sentence:** "An English native reference would allow both sides of the
  gap to be validated."

### 2. Weak difference
*Trigger:* AG or G isolated. Activate **P-WEAK**.
- **Allowed:** "A difference appeared for [model, cue] but did not replicate across
  configurations."
- **Not allowed:** treating the isolated interval as a finding; "trend toward".
- **Reviewer concern:** multiple comparisons.
- **Limitation:** "With [K] intervals reported, isolated exclusions of zero are expected
  by chance."
- **Future work:** "A confirmatory replication with prespecified tests would establish
  whether this pattern is stable."

### 3. Null difference
*Trigger:* AG ∋ 0 and G ∋ 0 in both models. Activate **P-EQ**, or P-G-ONLY if G ≠ 0.
- **Allowed:** "No difference was resolved; the data are compatible with differences from
  [a] to [b]."
- **Not allowed:** "equivalent", "no effect", "robust".
- **Reviewer concern:** low power.
- **Limitation:** "Interval widths reflect 120 (Cue A) and 36 (Cue B) items; smaller
  differences cannot be excluded."
- **Future work:** "Larger item pools would narrow these bounds."

### 4. Opposite directions by model
*Trigger:* the cross-model flag is "differs", with each model's interval excluding 0 in
opposite directions. Activate **P-MOD**.
- **Allowed:** "The direction differed between the two configurations."
- **Not allowed:** attribution to size, family or training.
- **Reviewer concern:** instability or noise.
- **Limitation:** "Two configurations cannot separate model family, size, quantization
  and decoding."
- **Future work:** "More models, varied one factor at a time, would identify the source."

### 5. Cue-A only
*Trigger:* the effect (ΔTM, AG or G) excludes 0 under Cue A but not Cue B. Activate
**P-CUE**.
- **Allowed:** "The pattern was resolved for the authority-attributed cue (120 items) but
  not for the user-asserted cue (36 items)."
- **Not allowed:** "Cue B has no effect" (36 items give wider intervals).
- **Reviewer concern:** unequal sample sizes.
- **Limitation:** "Cue B is evaluated on 36 items, so its intervals are wider."
- **Future work:** "A larger Cue-B item set."

### 6. Cue-B only
*Trigger:* the reverse of branch 5. Activate **P-CUE**.
- **Allowed:** "Resolved only for the user-asserted cue on the 36 shared items."
- **Not allowed:** general claims about user pressure.
- **Reviewer concern:** a single wording.
- **Limitation:** "Each cue source is one wording."
- **Future work:** "Several wordings per source."

### 7. Translation restores apparent monitorability
*Trigger:* R or R_full moves T toward H (with G > 0 and T > D_ur), and the exploratory
agreement diagnostic > 0. Activate **P-TR-SHIFT**, agreement sentence F1.
- **Allowed:** "Translated traces were labelled closer to native readers (exploratory)."
- **Not allowed:** "translation fixes or mitigates monitoring"; "language-specific
  limitation".
- **Reviewer concern:** rewriting effects; translation adding explicit wording.
- **Limitation:** "No paraphrase control; audit found [n] added/omitted disclosure
  statements."
- **Future work:** "A paraphrase control would separate rewriting from language."

### 8. Translation worsens monitoring
*Trigger:* R or R_full moves T away from H, or the exploratory agreement diagnostic < 0.
Activate **P-TR-WORSE**.
- **Allowed:** "Translation moved automated labels away from native readers (exploratory)."
- **Not allowed:** "translation is harmful" in general.
- **Reviewer concern:** translator quality.
- **Limitation:** "One translator, with sentence-level segmentation that can break
  cross-sentence references."
- **Future work:** "Additional translators and document-level translation."

### 9. Direct and translated judgments agree
*Trigger:* R and R_full ∋ 0. Activate **P-TR-NULL**.
- **Allowed:** "Translation did not resolvably change automated labels."
- **Not allowed:** "language does not matter to the monitor".
- **Reviewer concern:** power.
- **Limitation:** bounds stated.
- **Future work:** "Other monitors may be more language-sensitive."

### 10. Low human/judge agreement
*Trigger:* G ≠ 0. This is the only trigger. The confusion matrix is described with counts
but never used as a trigger. Activate **P-EN>UR monitor side** or
**P-UR>EN** or **P-G-ONLY**, as applicable.
- **Allowed:** "The direct monitor diverged from native readers on these traces."
- **Not allowed:** "LLM monitors are invalid for Urdu".
- **Reviewer concern:** reference quality.
- **Limitation:** "The reference rests on two raters and an adjudicator."
- **Future work:** "Larger rater pools and additional monitors."

### 11. High human/judge agreement
*Trigger:* G ∋ 0. Activate **P-EQ** or **P-EN>UR text side**.
- **Allowed:** "Within the stated bounds, the monitor's Urdu labels tracked native
  readers."
- **Not allowed:** "validated monitor" in general.
- **Reviewer concern:** a construct too easy, or ceiling or floor effects. Check the
  prevalence of `disclosed`.
- **Limitation:** "One construct (explicit acknowledgment)."
- **Future work:** "Subtler constructs."

### 12. Substantial `cannot_tell` rates
*Trigger:* the UR−EN difference in judge `cannot_tell` + technical-failure rate excludes
0, or `cannot_tell` reduces any G/R denominator enough that its interval is undefined in
some replicates. Activate **P-CT**, plus **P-MISS**.
- **Allowed:** "The monitor withheld a decision more often for [arm]; binary estimates
  describe the decidable subset."
- **Not allowed:** treating `cannot_tell` as non-disclosure.
- **Reviewer concern:** selection.
- **Limitation:** "S1–S3 and worst-case bounds show the potential effect."
- **Future work:** "Analysing why the monitor abstains."

### 13. Unexpected compliance sensitivity
*Trigger:* the exploratory compliance-restricted recomputation changes a direction or a
zero-inclusion. Activate **P-COMP-LO**.
- **Allowed:** "(Exploratory) conclusions for [model] depended on whether
  non-predominantly-Urdu rationales were included."
- **Not allowed:** adopting the restricted analysis as primary.
- **Reviewer concern:** language control.
- **Limitation:** "Script share is a coarse compliance measure."
- **Future work:** "Stronger language control and finer language identification."

---

## Mapping to manuscript paragraphs

| Branch | Paragraph(s) |
|---|---|
| 1 | P-EN>UR / P-UR>EN |
| 2 | **P-WEAK** (new) |
| 3 | P-EQ / P-G-ONLY |
| 4 | P-MOD |
| 5, 6 | P-CUE |
| 7 | P-TR-SHIFT (F1) |
| 8 | **P-TR-WORSE** (new) |
| 9 | P-TR-NULL |
| 10 | P-EN>UR monitor side / P-UR>EN / P-G-ONLY |
| 11 | P-EQ / P-EN>UR text side |
| 12 | **P-CT** (new) + P-MISS |
| 13 | P-COMP-LO |

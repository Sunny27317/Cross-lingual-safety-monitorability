# Workshop-v1: technical-missingness reporting, table shells, figure captions

**No values** except the direct-judge technical totals already reported to the
investigator (1,871 / 1,863 / 5 / 3). Their breakdown by cell is **not** inferred here.

## H. Direct-judge technical missingness

**Methods wording (in §4.6).** "Direct monitoring was authorized for exactly 1,871
rationales (936 English, 935 Urdu). It completed with 1,863 valid labels, 5 malformed
outputs and 3 outputs without a label line. Under the frozen contract these 8 are retained
as missing for the binary disclosure metrics and were not rerun after the stage
completed."

**Results wording (in §5.6).** "Direct monitoring returned a valid label for 1,863 of 1,871
rationales (99.6%). 5 outputs were malformed and 3 contained no label line. These are
retained as missing, and their distribution by language, model and cue is shown in
Table 2." Note that a valid label includes `partial` and `cannot_tell`. Do **not** write
"near-complete" or describe any pattern until the cell breakdown is read from the
technical QC.

**Table 2a shell (technical states).** Rows: language × model × cue (8 rows) + total.

| Language | Model | Cue | Sent | Valid label | Malformed | No label | Other technical states |
|---|---|---|---|---|---|---|---|
| … | … | … | | | | | |
| **Total** | | | 1,871 | 1,863 | 5 | 3 | 0 |

Footnote: "Technical states follow a fixed precedence (runtime error > truncated > multiple
labels > no label > malformed > valid). One identical retry is permitted only for runtime
errors. Format failures are never retried or recoded."

**Limitation wording (in §7).** "Eight of 1,871 direct-judge outputs (5 malformed, 3
without a label) are retained as missing, not rerun."

**Why preserved.** Under greedy decoding an identical rerun reproduces the same output, and
any change to the prompt, decoding or seed would alter the instrument after the fact.
Retaining the failures avoids selecting outputs by their content. S3 bounds their effect
by counting them as monitor misses.

## I. Table shells

**Numbering note.** This numbering (T1 design … T8 missingness/compliance) supersedes the
table numbers currently cited in `paper/WORKSHOP_V1_PREPRINT.md` §5 and in
`WORKSHOP_V1_RESULTS_WRITING_MATRIX.md` / `RAPID_FILL.md`. Renumber the §5 references
when the tables are built. Old → new:
- accuracy/cue → T4/T5;
- monitoring → T2;
- human → T7;
- G → T7(b);
- translation → T6;
- compliance → T8.

**Global rules:**
- Every cell reads "estimate [95% CI] (numerator/denominator)".
- "UNDEFINED" marks a zero denominator.
- Missing data are never shown as 0.
- No bold or asterisks marking "significance".

| Table | Row unit | Column unit | Denominator | Interval | Footnotes | Missing / undefined | Wording restrictions |
|---|---|---|---|---|---|---|---|
| **1 Experimental design** | model × language × condition (12) | planned, persisted, runtime-successful, parseable answer, visible trace | planned per cell (360/360/108) | none (counts) | timeout retained (Qwen-ur-Cue A); Attempt-1 excluded; pilot excluded | counts only | "completed" means runtime-successful |
| **2 Direct-judge disclosure outcomes** | model × language × cue | D (binary rate); `disclosed` / `not_disclosed` / `partial` / `cannot_tell` / technical counts (2a) | binary: traces with `disclosed`/`not_disclosed`; categories: traces sent | 95% CI on D and on the partial/cannot_tell rates | label definitions; judge never sees the answer | technical failures shown, excluded from D | "the judge labelled …", never "models disclosed" |
| **3 English vs Urdu contrasts** | model × cue | ΔTM(en), ΔTM(ur), L_ΔTM; D_en, D_ur, AG | as parents; paired by item | paired CI | "differences describe English and Urdu versions of the same items" | UNDEFINED if a parent is undefined | no causal or "the Urdu language" wording; AG not interpreted in Results |
| **4 Cue A vs Control** | model × language | TM(Control), TM(Cue A), ΔTM, ΔAcc | parsed traces on 120 items (Qwen-ur ≤359) | paired CI | target letter is item-specific and incorrect | parse failures excluded and reported | "shifted selection toward the suggested option" only if CI > 0 |
| **5 Cue B vs Cue A (36 shared items)** | model × language | Cue A(36) and Cue B values, paired difference, for ΔTM, D, AG (and G if estimable) | the 36 items only (≤108 traces per arm) | paired CI | "restricted to the shared 36 items" | UNDEFINED if a parent is undefined | no full-120 comparison; no general authority/user claims |
| **6 Direct vs translated Urdu** | model × cue | D_ur, T, R_full; on the native-reader subset: R, agreement diagnostic (exploratory); translation failures; audit counts | R_full: binary D_ur & T; R: complete triples; failures over 935 | paired CI | "no paraphrase control; descriptive only" | translation failures missing for T | no "recovery", "mitigation" or "language-specific" |
| **7 Human agreement and judge concordance** | (a) model × cue + All; (b) judge label × human label | (a) raw agreement, κ five-category, κ binary (n), adjudicated n, unresolved n; (b) 4×5 confusion matrix; G | (a) 312 / both-binary subset; (b) pool items with any judge label; G on complete pairs | κ and G CIs | Cohen's κ; adjudicated reference; parity of inputs | `abstain` and `unresolved` reported, not imputed | no verbal bands; no "ground truth" |
| **8 Missingness / compliance sensitivity** | arm × model × language × cue | planned → eligible → valid → complete; compliant rate; script bins; S1–S5; exploratory compliance-restricted D/G/R | as defined per column | CI for rates; worst-case **bounds** (not CIs) | exploratory label on the compliance row | — | "bounds" ≠ "intervals"; no new thresholds |

## J. Figure caption bank

**Figure 1 — Study design.**
> Study design. 120 OpenBookQA items (36 with the user-asserted cue) were posed in English
> and Urdu to two models under Control, Cue A and Cue B, with three samples each (3,312
> planned generations; 3,311 completed). Cued rationales were labelled by an automated
> judge directly (936 English, 935 Urdu) and, for Urdu, after translation into English
> (935). Native readers labelled a fixed 312-rationale subset with the same inputs and
> labels as the judge. No statistical test is implied by the arrows.

**Figure 2 — Primary direct-monitor outcomes.**
> Share of cued rationales labelled `disclosed` by the automated judge, by model,
> language and cue. Denominator: rationales with a `disclosed` or `not_disclosed` label
> (n shown per point). `partial`, `cannot_tell` and technical failures are excluded and
> reported in Table 2. Bars are 95% item-cluster percentile bootstrap intervals (10,000
> resamples of items). They are descriptive and do not represent hypothesis tests. Cue B
> uses its 36-item subset.

**Figure 3 — Cross-language contrasts.**
> Urdu minus English differences within each model: cue sensitivity (ΔTM) and automated
> disclosure (AG). Differences are paired by item and computed within each bootstrap
> replicate, with 95% item-cluster intervals. Points describe the English and Urdu
> versions of the same items. Intervals excluding zero are descriptive, not significance
> tests. The English side is not human-validated.

**Figure 4 — Direct vs translated Urdu.**
> Automated disclosure rate on Urdu rationales read directly (D_ur) and after machine
> translation into English (T), with the paired difference R_full, by model and cue.
> Denominator: rationales with binary labels in both arms (n shown). Translation failures
> are excluded (count in caption). 95% item-cluster intervals. No paraphrase control was
> run, so differences are not attributed to language rather than rewriting.

**Figure 5 — Human vs automated judgments.**
> On the 312-rationale native-reader subset: the native-reader disclosure rate (H) and the
> direct-judge rate (D_ur) on the same rationales, and G = mean(H − D_ur), by model and
> cue. Denominator: complete pairs (n shown); `partial`, `cannot_tell`, `abstain`,
> `unresolved` and technical failures are excluded (see Table 7). 95% item-cluster
> intervals, descriptive. Unit of analysis: rationale, resampled by item.

<!-- Results scaffold for paper/WORKSHOP_V1_PREPRINT.md §5. Written 2026-10-06 before any
unseal. It contains NO numbers.

Slot syntax: {{SLOT | source | denominator | role | human-dependent}}
- source = function in src/clsm/workshop_v1/final_tables.py (ft.*) or final_analysis.py (fa.*).
- Fill ONLY from the single, hashed result artifact produced at unseal.
- Every interval: "95% CI [a, b]". Wording follows framework §2.1, and every paragraph that
  reports an interval excluding 0 must state how many intervals its family contains.
- Abbreviations: PRI primary; SEC secondary; DESC descriptive; EXP exploratory; SENS sensitivity. -->

# 5 Results

## 5.1 Study flow and completion

Of {{N_PLANNED | ft.figure_1_study_flow.nodes.planned_generations | — | DESC | no}} planned
generations, {{N_RUNTIME_FAIL | …generation_runtime_failure | planned | DESC | no}} did not
complete (the retained timeout). Direct monitoring:
- judged {{N_DIRECT | …direct_judged | cued traces | DESC | no}} rationales;
- produced {{N_DIRECT_BINARY | …direct_valid_binary | judged | DESC | no}} binary labels.

Translate-then-monitor:
- judged {{N_TRANS | …translated_judged | Urdu cued | DESC | no}} rationales, including six
  identity translations;
- produced {{N_TRANS_BINARY | …translated_valid_binary | judged | DESC | no}} binary labels.

Native readers labelled {{N_POOL_LABELLED | fa.missingness_cascade.human_pool − human_missing
| 312 | DESC | **yes**}} of 312 pool rationales. This gave
{{N_PAIRS | …complete_pairs_G | pool | DESC | **yes**}} complete reader–monitor pairs and
{{N_TRIPLES | …complete_triples_R | pool | DESC | **yes**}} complete triples (Figure 1;
Table 9).

## 5.2 Generation quality and language compliance

Table 1 (ft.table_1_study_flow) and Table 2 (ft.table_2_sample_composition) report, per
model × language × condition, the following. All are DESC, with denominator = traces.
- parse failures;
- visible rationales;
- the compliance label and the D-PG-1 bins.

Language compliance in Urdu was {{URDU_COMPLIANCE_SUMMARY | ft.table_2 | traces | DESC |
no}}.

## 5.3 Cue sensitivity (ΔTM)

Under Cue A (120 items), ΔTM was:
- Qwen, English: {{DTM_QWEN_EN_A | ft.table_4_secondary.delta_tm_en | parsed traces per
  arm | SEC | no}};
- Qwen, Urdu: {{DTM_QWEN_UR_A}};
- Gemma, English: {{DTM_GEMMA_EN_A}};
- Gemma, Urdu: {{DTM_GEMMA_UR_A}}.

Under Cue B (36 items): {{DTM_*_B}}. Family size: 8 intervals. Report every cell.

## 5.4 English versus Urdu (behavior)

Within model, Cue A: L_Acc, L_TM and L_ΔTM, each as {{L_* | ft.table_5_language_contrasts |
items | DESC | no}}. These compare the English and Urdu *versions of the same items*.

## 5.5 Direct disclosure rates

Table 4 and Figure 2 (ft.figure_2_disclosure_rates) report, per model × cue, all SEC/DESC
and none human-dependent:
- D_en and D_ur, each {{D_* | valid binary labels | SEC/DESC | no}};
- the `partial` and `cannot_tell` shares, beside the rates.

## 5.6 Apparent language gap (AG)

AG = D_ur − D_en was {{AG_* | ft.table_4_secondary.AG | per-arm binary labels | DESC
(automated only) | no}}. AG is reported as an automated measurement; by itself it cannot
distinguish model from monitor.

## 5.7 Native-reader agreement (S5)

Before adjudication, the two readers agreed on:
- {{RAW_AGREE_5 | ft.table_7_human_validation.agreement.raw_agreement_5 | 312 | required
  reporting | **yes**}} of items (Cohen's κ = {{KAPPA_5 | …kappa_5 | 312 | **yes**}}, 95% CI
  {{KAPPA_5_CI}}; five categories);
- on the {{N_BINARY_SUBSET | …n_binary_subset | **yes**}} items both labelled `disclosed` or
  `not_disclosed`: κ = {{KAPPA_BIN}} ({{KAPPA_BIN_CI}}).

{{N_ADJ}} items were adjudicated. The adjudicator matched rater 1 on {{n}}, rater 2 on
{{n}}, neither on {{n}}; {{n}} were left unresolved. No agreement bands or thresholds are
used.

## 5.8 Monitor versus native readers (PRIMARY: G)

G = mean(H − D_ur) per model × cue (Table 3; Figure 3):
- Qwen, Cue A: {{G_QWEN_A | ft.table_3_primary_g.G | complete pairs | **PRI** | **yes**}};
- Gemma, Cue A: {{G_GEMMA_A}};
- Qwen, Cue B: {{G_QWEN_B}};
- Gemma, Cue B: {{G_GEMMA_B}}.

Each with n pairs and the number excluded. Cross-model flag: {{FLAG_A / FLAG_B |
table_3.cross_model_flags | — | PRI summary | **yes**}}. Sign matching follows D-FA-6 (strict: 0
matches only 0). Family size: 4 intervals.

## 5.9 Confusion matrices

Table 7 (ft.table_7_human_validation.matrices) shows, for D_ur and T and each model × cue:
- the full 5 × 4 matrix (rows: native-reader label; columns: monitor label), with totals
  and exclusions;
- the binary 2 × 2.

{{CONFUSION_NARRATIVE: describe only cells visible in the matrix, e.g. reader `partial` ×
monitor `disclosed`}}. Required reporting; human-dependent.

## 5.10 Translation before monitoring (R_full, R)

On all eligible Urdu rationales, R_full = mean(T − D_ur) was {{RFULL_* |
ft.table_4_secondary.R_full | complete D/T pairs | SEC (automated) | no}}. On complete
triples, R was {{R_* | …R | triples | SEC | **yes**}}. These are descriptive contrasts:
there is no paraphrase control.

## 5.11 Agreement diagnostic (A, exploratory)

A = {{A_* | ft.table_4_secondary.A_exploratory | triples | **EXP** | **yes**}}.
"Translation moved labels toward the native reference" may be written only if R is on the
side that moves D toward H **and** A > 0. Even then it is labelled exploratory.

## 5.12 Cue A versus Cue B on the 36 shared items

Table 6 (ft.table_6_cue_b_shared_subset) reports Cue B minus Cue A-on-36 for ΔTM (by
language), D_ur, G and AG: {{CUEB_* | difference and CI | 36-item cells | DESC | G row:
**yes**}}. Differences are described as wording- or source-dependent.

## 5.13 Model-specific and language-specific summaries

- **Models:** pattern replication only, using the cross-model flags for G, AG, ΔTM and R
  (Table 3 and an appendix). Models are never pooled.
- **Language:** see §§5.4 and 5.6.

## 5.14 Missingness

Table 9 (ft.missingness_table) gives the cascade by reason and the worst-case bounds for
D_ur, T and H: {{BOUNDS_* | — | planned | required reporting | H bounds: **yes**}}.

## 5.15 Sensitivity and robustness

Table 8 (ft.table_8_sensitivity) sets each variant beside the primary value:
- **G under S1/S2/S3:** {{G_S1/S2/S3 | **yes**}}.
- **R under S1–S4:** {{R_S* | **yes**}}. S4 requires the translation audit; otherwise write
  "S4 pending: translation audit not completed".
- **Exclude-six robustness** (secondary): R and R_full, each with its denominator change.
- **Exploratory compliance recomputation** for G.

Robustness summary sentence, per estimand: "[Estimand] [kept / changed] the sign of its
point estimate and [did / did not] change whether its interval excluded 0 under S1–S3."
This is mechanical, read from Table 8.

## 5.16 Human-validation and ORPI status line (until H exists)

If the paper is posted before native-reader labels exist, §§5.7–5.9 and 5.11 are replaced
by: "Native-reader validation is pending an institutional determination; G, R, A and the
confusion matrices are not yet available." In that case, the abstract may not state any G
result.

# Final tables and figures: locked pre-unseal specification (2026-10-07)

Every table and figure is generated only from the single unseal artifact, by the frozen
builders in `src/clsm/workshop_v1/final_tables.py` (freeze V4). No real values appear here.

**Shared rules:**
- Every estimate is reported as point (95% CI) [n], using the item-cluster percentile
  bootstrap (B = 10,000, seed 0, paired arms in the same replicate).
- UNDEFINED when a denominator is 0.
- Models are never pooled. Cue B is compared only with Cue A on the same 36 items.
- **Standard caption footnote:** "Descriptive intervals; no hypothesis tests. n is the
  denominator of each estimate. Family size: k intervals."

## Tables

| Paper table | Builder | Rows | Columns | Denominators | CI | Role | Footnotes |
|---|---|---|---|---|---|---|---|
| **T1. Technical and sample accounting** | `table_1_study_flow` (+ appendix `table_2_sample_composition`) | model × language × condition (12) | planned; generation failures; visible rationale; parsed answer; direct judged / technical failure / valid binary; translated judged / valid binary; identity translations; human pool / valid binary H | counts | — | descriptive | The retained timeout; 8 direct-judge failures; 0 translated-judge failures. Compliance covariate in the appendix (D-PG-1 bins) |
| **T2. Primary G** | `table_3_primary_g` | model × cue (4), plus a cross-model flag row per cue | H; D_ur on the pool; **G**; excluded from G | G: complete H/D pairs; H and D: own binary n | yes | **primary** | Binary mapping and exclusions; flag = D-FA-6 strict sign rule plus a difference interval containing 0 |
| **T3. Same-trace H / D / T** | `table_same_trace_hdt` | model × cue (4) | H; D_ur; T; complete triples | each rate's own n on the 312 pool rationales | yes | descriptive (H reference) | Identical rationales; the pairwise contrasts G and R are in T2 and the appendix |
| **T4. Native readers vs monitor** | `table_7_human_validation` | (a) agreement summary; (b) per model × cue × arm, the D-FA-4 matrices | (a) raw %, κ5, binary κ (n), CIs, uncertainty-flag counts, adjudication outcomes; (b) human rows × judge columns, row and column totals, total n, excluded by reason; plus the binary 2 × 2 | 312 / binary subset / matrix n | κ and raw: yes | required reporting | No post-adjudication κ, bands, thresholds, sensitivity, specificity or α |
| **T5. S1–S5** | `table_8_sensitivity` (S1–S4 rows) + T4 (S5) | model × cue × {G, R} × {primary, S1, S2, S3, S4} | point; CI; n; change of n vs primary | as variant | yes | sensitivity | S4 shows "pending translation audit" if not done. The rule for each variant |
| **T6. Robustness and missingness** | `table_8_sensitivity` (exclude-six, exploratory compliance) + `missingness_table` | model × cue | exclude-six R and R_full vs primary (Δn); compliance-restricted G (exploratory); cascade counts; worst-case bounds for D_ur, T, H | as row | yes (bounds are not CIs) | secondary / exploratory / required | Record B; D-PG-1; D-PG-2 |
| **T7. Second judge** (only if executed and frozen before unseal) | builder to be added with the second-judge spec (same functions applied to D2/T2) | model × cue | D2_ur, T2, AG2, R_full2, and the G-analog H − D2; judge-vs-judge contingency | as primary | yes | secondary robustness | Never pooled with primary values. "Post-hoc" label if selected after unseal |
| Appendix | `table_4_secondary`, `table_5_language_contrasts`, `table_6_cue_b_shared_subset` | — | ΔTM (en, ur), AG, R_full, R, A (exploratory); L_Acc, L_TM, L_ΔTM; Cue B vs Cue A-on-36 for ΔTM, D_ur, G, AG | as defined | yes | secondary / descriptive / exploratory | Fixed wording from framework §2.1 |

## Figures

| Figure | Data builder | Encoding | Axis | Role |
|---|---|---|---|---|
| **F1. Study flow** | `figure_1_study_flow` (nodes, edges, Mermaid) | boxes with n | — | accounting |
| **F2. Primary G** | `table_3_primary_g` → G points | forest: 2 models × 2 cues; zero line; n per row; S1/S2/S3 as hollow markers beside each primary | fixed [−1, 1] | primary |
| **F3. Same-trace H/D/T** | `table_same_trace_hdt` | grouped interval plot of H, D_ur and T per model × cue | fixed [0, 1] | descriptive |
| **F4. Native readers vs monitor** | `table_7_human_validation.matrices` | count heat maps (human rows × judge columns), one per arm × model × cue; counts printed in cells | — | required reporting |
| **F5. Cue A vs Cue B** | `table_6_cue_b_shared_subset` | interval plot of the Cue B − Cue A-on-36 differences | fixed [−1, 1] | descriptive |
| **F6. Robustness** | `figure_5_robustness` | interval plot of primary vs S1–S4, exclude-six and compliance; missingness counts | fixed [−1, 1] | sensitivity |
| **F7. Second judge** (if executed) | second-judge builder | paired markers, primary vs second judge per quantity | fixed | secondary robustness |

**Rendering.** Interval plots use the deterministic SVG renderer with fixed axes
(`render_interval_svg`). The heat-map renderer is still to be added, and must not choose any
scale from the data beyond the counts themselves.

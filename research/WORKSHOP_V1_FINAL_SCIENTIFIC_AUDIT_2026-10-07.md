# Workshop-v1 final scientific audit (outcome-blind; 2026-10-07)

**Scope.** Canonical protocol and authority hierarchy, G, H/D/T, S1–S5, identity
robustness, compliance, missingness bounds, Cue A/B, clustering and bootstrap, Discussion
rules, claim ledger, freeze V3/V4 and the pre-unseal addenda.

**Method.** I compared the frozen sources (plan; D-PG-1 to D-PG-6; Records A and B;
AGREEMENT_REPORTING; locked framework; D-FA-1 to D-FA-6) with the implementation and the
derived documents. I read only technical metadata and checked structure on synthetic data.
No label or result was inspected.

**Auditor caveat.** The same agent implemented most of the analysis layer, so this audit is
not independent.

## Consistent (no finding)

- **G.** G = mean(H − D_ur) on complete pairs, per model × cue, primary. The plan,
  framework §2.4, specification, code (`gap_g`), preprint §4.9 and the worked example all
  agree.
- **H/D/T and the binary mapping.** These agree across the human frozen summary, plan §2,
  `judge_binary`/`human_binary` and the data contract.
- **S1–S5.** These agree across plan §2, the code and the preprint §4.9 description.
- **Identity robustness.** Records A and B match `exclude_six_robustness`: the primary
  analysis includes the six identity translations, and the robustness analysis is
  secondary and selected by flag.
- **Compliance.** D-PG-1 (no floor; exploratory ≥ 0.50 flag; covariate bins) matches the
  code and the preprint.
- **Missingness bounds.** D-PG-2 matches `worst_case_rate_bounds`.
- **Cue B.** "Cue A on the same 36 items, within model and language" holds in the plan,
  framework §2.6 and the code (bug fixed 2026-10-06).
- **Bootstrap.** D-PG-6 matches `cluster_bootstrap`, which reproduces the frozen percentile
  rule exactly.
- **Sign rule.** D-FA-6 matches `sign` / `cross_model_flag`.

## Findings

| # | Finding | Class | Status / action |
|---|---|---|---|
| F1 | **Rater packet positional leakage.** The existing packets are ordered in model × cue blocks, contradicting the frozen lexicographic order (`ee0e1b57…`) and preprint §4.8 | **CRITICAL** (human stage) | Spec: `WORKSHOP_V1_RATER_PACKET_FINAL_SPEC.md`. Codex regenerates. Do not distribute the old packets |
| F2 | **Item text is in the public repository** (review PDF) while the Data Availability text says it is not redistributed | **CRITICAL** (release) | Remediate, or rewrite the text (release guard R-6/R-7). Does not affect analysis |
| F3 | **S4 `audit_flag` rule is not defined** in any frozen source | **MAJOR** | Proposed D-FA-7 (`WORKSHOP_V1_TRANSLATION_AUDIT_CANONICAL_PROTOCOL.md` §5). Must be decided before unseal, or S4 is reported as not performed |
| F4 | **Per-rater uncertainty-flag counts** (required by AGREEMENT_REPORTING) were not implemented | **MAJOR** | **Fixed** in `human_agreement` (`uncertainty_flag_counts`); test added; freeze V4 |
| F5 | **No builder for the same-trace H/D/T table** needed for paper Table 3 | **MAJOR** (reporting) | **Fixed:** `table_same_trace_hdt`; test added; freeze V4 |
| F6 | **Translated-judge QC and seal records are uncommitted** (main worktree), and `engineering/workshop_v1_stage_hashes.json` still shows translation `null` | **MAJOR** (provenance) | Engineering: commit them and update the stage-hash file before unseal (Addendum A1, P4/P5) |
| F7 | **Second-judge timing.** Unless selected and frozen before unseal, its results must be labelled post-hoc | **MAJOR** (decision) | `WORKSHOP_V1_SECOND_JUDGE_FINAL_RECOMMENDATION.md` |
| F8 | **Reviewer's name** is in public committed files and in rater-facing training documents | **MAJOR** (privacy) | Remediation plan (public history); reconciled update of the rater documents; the preprint no longer names her |
| F9 | Table numbering differs across documents: the methods-completion doc, the original unseal protocol (T1–T8, S1–S13), builder IDs (T1–T9) and the paper tables (T1–T7) | MINOR | `WORKSHOP_V1_FINAL_TABLES_FIGURES_SPEC.md` maps builders to paper tables and governs |
| F10 | Discussion labels differ: framework §3 branches A–G, scenarios A–J, final tree D1–D14 | MINOR | Framework §3 governs selection; the final tree governs wording; scenarios are background |
| F11 | The "narrow" rule in the draft tree generalized framework §2.5 | MINOR | **Fixed:** it now quotes §2.5 exactly |
| F12 | Rater import does not type-check `uncertainty_flag` / `confidence` | MINOR | The packet and submission tooling must validate them (spec P12); missing flags are counted, never imputed |
| F13 | Freeze V3 omitted the worked-example tests | MINOR | Included in V4 |
| F14 | The preprint abstract and §4.8 use past tense for the human stage, which has not happened yet | MINOR | Guarded by the release-guard comment; fill at release |
| F15 | The frozen primitive `analysis.compliance_sensitivity_rows` is item-level, whereas D-PG-1 is trace-level | MINOR / historical | The new code follows D-PG-1; the primitive is unused |
| F16 | D-PG-6 and the primitive freeze were recorded while direct judging was running | HISTORICAL ONLY | Labels were sealed and unexamined; disclosed in Methods §4.10 |
| F17 | Plan §6 requires a paraphrase control; plan §8b leaves the compliance floor open; arm P | HISTORICAL ONLY | Superseded by D-PG-3 and D-PG-1 (D-FA-1) |
| F18 | Framework "4×5 judge × human" orientation | HISTORICAL ONLY | Superseded by D-FA-4 |
| F19 | D-PG-2 "2,807" eligible count | HISTORICAL ONLY | Erratum D-FA-3 (2,806) |
| F20 | Nominal "session N" date labels | HISTORICAL ONLY | D-FA-1 provenance note |
| F21 | C9: "English canonical question" in the old judge record | HISTORICAL ONLY | Erratum recorded |
| F22 | Analysis-input addendum V1 hash not reproducible | HISTORICAL ONLY | Superseded by V2 |

**No CRITICAL finding affects any estimand or the analysis code.** F1 blocks human
collection. F2 blocks public release.

# Workshop-v1 final claim ledger (re-audited)

**Re-audited 2026-10-04, pre-results, against D-PG-1..6.** This supersedes
`research/WORKSHOP_V1_INTERPRETATION_FRAMEWORK.md` §4. Wording rules are in framework
§2.1. Fill-in specifications are in `research/WORKSHOP_V1_RESULTS_WRITING_MATRIX.md`.

**How to use this ledger.** Every sentence in the Abstract, Results, Discussion and
Conclusion cites a row ID in a comment while drafting. A sentence appears only if:
1. its row's minimum acceptable result holds;
2. it is in a location the row allows;
3. its wording matches the allowed form.

If no row fits a sentence, the sentence is deleted, or a new row is added and labelled
post-hoc.

**Columns:**
- **HUM?** / **TR?**: human validation / translation evidence required.
- **ABS?**: may appear in the abstract.
- **LOC**: R = Results; D = Discussion; L = Limitations; M = Methods.
- **Status:** S = supported now; P = pending; C = conditional on a result pattern;
  X = prohibited.

| # | Claim | Exact evidence required | Minimum acceptable result | HUM? | TR? | ABS? | LOC | Status |
|---|---|---|---|---|---|---|---|---|
| C1 | 3,312 planned; 3,311 completed; 1 timeout retained missing | GEN QC + data lock | (fact) | N | N | YES | M, R | S |
| C2 | No infrastructure event introduced outcome-dependent selection | audit §1.2; D-PG-2 | (fact) | N | N | no (Methods detail) | M, L | S |
| C3a | 120/120 items (36/36 Cue-B) passed native equivalence review | review packet + closure | (fact) | N | N | optional | M | S |
| C3b | Cue and instruction wording native-approved unchanged | signed blocks, *or* verbal approval record | wording must match the evidence type | N | N | NO | M | S (verbal wording only until signed blocks are attached) |
| C4 | Rules, judge prompt, translation procedure, compliance and bootstrap conventions fixed before the relevant outputs existed | dated approvals precede stage outputs; analysis commit precedes unsealing | approval timestamps < first output timestamps | N | N | YES ("rules fixed in advance") | M | S for D-PG-1..6. Analysis commit: **P** |
| C5 | Rationales are prompted, not native thinking traces | configs; D5 record | (fact) | N | N | YES | M, L | S |
| C6 | Requested-language compliance was X for model m | AN compliance table | rate + CI exist | N | N | NO | R | P |
| C7 | Cue k shifted answers toward the suggested option for (m,l) | ΔTM | ΔTM CI > 0 in that cell | N | N | YES (count of cells) | R | P |
| C8 | Cue sensitivity differed between EN and UR versions | L_ΔTM | interval excludes 0; otherwise "not resolved" | N | N | NO | R, D | C |
| C9 | Cue B and Cue A differed on the shared 36 items | paired difference | interval excludes 0 | N (H only if G is compared) | N | NO | R, D | C |
| C10 | Automated disclosure rates differed between UR and EN (AG) | DJ binary labels | interval excludes 0 (else "not resolved" wording) | N | N | YES, as an automated rate only | R (description), D (interpretation) | P |
| C11 | The monitor produced more non-decisions/failures in Urdu | DJ state counts | UR−EN difference CI excludes 0 | N | N | NO | R, D | C |
| C12 | Native raters agreed with κ = k before adjudication | HUM raw labels | κ + CI computed on all 312 | **Y** | N | YES (with CI) | R | P |
| C13 | **Direct monitor diverged from native readers by G on Urdu traces** | complete H/D pairs + confusion matrix | G computed with CI; direction claimed only if CI excludes 0 | **Y** | N | YES (primary) | R, D | P / C |
| C14 | No monitor-validity gap larger than b was observed | G CI | G CI ∋ 0; state bounds | **Y** | N | YES, with bounds | R, D | C |
| C15 | Apparent gap more consistent with trace content than monitor error | AG and G | AG CI < 0 **and** G CI ∋ 0 **and** \|G\| upper bound < \|AG\| | **Y** | N | NO | D only | C |
| C16 | Translating before monitoring changed the automated rate (R_full / R) | TJ + DJ (+ HUM for R) | interval excludes 0; else "did not resolvably change" | Y for R / N for R_full | **Y** | YES, descriptive wording only | R, D | P |
| C17 | (Exploratory) translation moved labels toward native readers | agreement diagnostic | CI > 0, labelled exploratory | **Y** | **Y** | NO | R, D | C |
| C18 | Translation added/omitted disclosure language in n traces | AUD | audit completed on the declared subset | N | **Y** | NO | R, L | P |
| C19 | Pattern replicated across both models | cross-model flag | flag = consistent for the named quantity | per quantity | per quantity | YES, if true for G or ΔTM | R, D | P |
| C20 | Robust to S1–S5 / (exploratory) compliance restriction | sensitivity tables | no direction or zero-inclusion change | per quantity | per quantity | NO | R (App.), D | P |
| C21 | The design separates monitor validity from trace content on the same traces | design | (fact) | N | N | YES | Intro, M | S |
| C22 | R reflects a language-specific monitor limitation | paraphrase control + EN human anchor (not run) | — | — | — | NO | **nowhere** (state in L as not tested) | X |
| C23 | First study / novelty from including Urdu | — | — | — | — | NO | nowhere | X |
| C24 | Models hide, conceal or lie; claims about latent cognition | — | — | — | — | NO | nowhere | X |
| C25 | Significant / confirmed effects; p-values | — | — | — | — | NO | nowhere | X |
| C26 | Generalization to other languages, models, tasks | — | — | — | — | NO | D only as a hypothesis for future work | X as a claim |
| C27 | ORPI determination obtained | saved written reply | verbatim quote | — | — | NO | Ethics | P |
| C28 | Author affiliations/supervision | written confirmation by each author/supervisor | exact text | — | — | — | Front matter | P |

## Overclaim tripwires (search the filled manuscript for these before upload)

| Phrase | Rule |
|---|---|
| "significant", "p <", "confirm", "prove", "demonstrate that" | Remove (C25) |
| "first", "novel", "to our knowledge, no prior" | Remove unless carefully scoped and supported by the citation audit (C23) |
| "hide", "conceal", "lie", "deceptive", "unfaithful model" | Remove (C24) |
| "mitigat", "recover", "fixes", "language-specific" (near R) | Remove (C22) |
| "equivalent", "no difference", "robust across languages" | Replace with the bounds wording (C14) |
| "ground truth" | Replace with "native-reader reference" |
| "reliable", "substantial/moderate agreement", any κ cutoff | Remove. Report observed agreement + κ with CI; no verbal bands (C12) |
| Any number with no row ID comment | Delete, or trace it to an artifact |

---

## Final review (2026-10-04): classification of manuscript claims

**Types:**
- BACKGROUND: literature.
- METHOD: what we did.
- OBSERVATION: a future result.
- INTERPRETATION: what a result means.
- LIMITATION.
- SPECULATION: allowed only as future work.

| Manuscript claim (current text) | Type | Ledger | Status |
|---|---|---|---|
| Reasoning often omits influences on answers (Turpin; Chen; Young) | BACKGROUND | — | verified citations |
| Monitorability ≠ monitored correctly (Yang et al.) | BACKGROUND | — | verified |
| Multilingual CoT monitoring is fragile; Urdu absent (Onyame et al.) | BACKGROUND | — | verified |
| LLM judges less consistent / biased by language (Fu & Liu; Zhou et al.; Doğruöz et al.) | BACKGROUND | — | verified; Zhou worded as "biased by response language" |
| Translate-then-monitor exists (DialectShift-Monitor) | BACKGROUND | — | verified repository; cited as such |
| Urdu under-resourced; absent from prior monitoring evaluation | BACKGROUND | — | UrduBench; Onyame |
| "A lower monitored rate is ambiguous between model and monitor" | INTERPRETATION (conceptual) | C21 | supported by design logic |
| Design statements (3,312; 3,311; timeout; 120/36; parity; Judge V2; segmentation; D-PG-1..6) | METHOD | C1–C5, C21 | supported |
| Serialization failure attributable to the prompt instance | METHOD (provenance inference) | C2 | supported by the audit evidence; worded "attributable" |
| Generation code uncommitted at run time | LIMITATION | — | stated |
| Analysis code frozen before unsealing | METHOD | C4 | **PENDING: must become true (commit) before posting** |
| Cue effects, AG, G, R, κ, compliance | OBSERVATION | C6–C20 | pending |
| "Apparent gap attributable to monitor / text" | INTERPRETATION | C13, C15 | conditional (tree V2) |
| "Translate-then-monitor needs its own validation" | INTERPRETATION | C16–C18 | conditional; always allowed as a recommendation |
| "Validate monitors per deployment" | INTERPRETATION | C19 / P-MOD | conditional on heterogeneity |
| Extensions (more languages, reasoning models, paraphrase control) | SPECULATION → future work | C26 | allowed only as future work |

### Future result claims: required artifact, evidence, minimum support, strongest wording

| Claim | Required artifact | Required evidence | Minimum support | Strongest allowed wording |
|---|---|---|---|---|
| Cue shifts answers (C7) | analysis output T3 | ΔTM with paired CI | CI > 0 in that cell | "increased selection of the suggested option by [Δ] (CI)" |
| EN–UR automated difference (C10) | direct-judge outputs + analysis T5 | AG with paired CI | CI excludes 0 | "automated disclosure rates were descriptively [higher/lower] for Urdu rationales" |
| Monitor divergence (C13) | human locked labels + direct judge + analysis T7 | G with CI; confusion matrix | CI excludes 0 | "relative to native readers, the direct monitor [under/over]-labelled disclosure by [Δ]" |
| Gap more consistent with text (C15) | T5 + T7 | AG < 0; G ∋ 0; \|G\| upper bound < \|AG\| | all three | "more consistent with differences in the Urdu rationales themselves" |
| Translation change (C16) | translated judge + direct judge + analysis T8 | R_full / R with CI; audit | CI excludes 0 | "translating before monitoring changed the automated rate by [Δ]" |
| Agreement improved (C17) | T8 | agreement diagnostic CI > 0 | CI > 0; labelled exploratory | "(exploratory) translated labels agreed with native readers more often" |
| Replication across models (C19) | flags | same sign; difference-of-differences CI ∋ 0 | both | "consistent in direction across both configurations" |
| Human agreement (C12) | human labels | raw %, κ, CI | computed on all 312 | "raters agreed on [x]% (κ = [k], CI)". No descriptors |

### Banned terms (unless strictly supported; in practice, never)

| Term | Status |
|---|---|
| "proves", "demonstrates that models hide", "deception"/"deceptive", "causes"/"caused by" (about model or language effects) | **Banned** |
| "general multilingual behavior", "all low-resource languages", "safety failure" | **Banned** |
| "first", "novel" (unqualified), "significant", "confirm", "equivalent", "ground truth", "reliable" (as a verdict), "mitigation", "recovery", "language-specific" (about R) | **Banned** (see the tripwire table) |

The tripwire phrase scan (`PREPRINT_FINAL_DAY_QC.md` §11) is extended with: "proves",
"cause", "safety failure", "all low-resource", "general multilingual".

**Ledger verdict: PASS**, with one open item: the analysis-freeze claim (C4) must be made
true by an approved commit before posting.

---

## Publication claim tiers (2026-10-04, pre-results)

**TIER 1: always safe, whatever the results.**
- Design and method statements (C1–C5, C21): counts, frozen configs, parity, segmentation
  rules, technical missingness (1 timeout; 8 non-valid judge outputs), descriptive
  intervals.
- "Same-trace native validation separates monitor divergence from differences in the
  text."
- "Translations are not treated as ground truth; translate-then-monitor is a contrast."
- Every observed estimate with its interval and denominator, worded per §2.1, including
  nulls ("not resolved; compatible with a to b").
- Limitations and scope statements.

**TIER 2: allowed only if replicated across both models (and, where relevant, both cues
on the shared 36 items).**
- "Automated disclosure rates differed between English and Urdu rationales" as a
  *finding*, rather than a single-cell observation.
- "The monitor diverged from native readers on Urdu rationales" as a *pattern*.
- "The apparent gap is more consistent with differences in the text" (also requires the
  C15 conditions).
- "Translation changed automated labels" as a *pattern* (still descriptive; never
  mechanistic).
- Abstract-level statements about direction.

A non-replicated result appears only as an isolated observation (P-WEAK).

**TIER 3: not allowed in this paper, even if effects look large.**
- "Urdu is less safe", or "Urdu users are less protected".
- "Multilingual LLMs hide their reasoning"; "models deceive"; "hidden reasoning".
- "Translate-then-monitor solves (or mitigates, or recovers) multilingual monitoring".
- "Faithful" or "unfaithful chain of thought"; claims about internal computation.
- "Monitors fail in low-resource languages"; generalization to other languages, models,
  monitors or translators.
- "Significant", "confirmed", "proves", "causes".
- Novelty because Urdu is included; "first study".

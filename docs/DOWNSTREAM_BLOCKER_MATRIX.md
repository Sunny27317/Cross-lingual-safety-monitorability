# Master downstream blocker matrix

**Independence:** this package did not inspect English pilot results or its execution
branch. “Current” below describes prospective infrastructure, not the state of another
agent's run. **AUTHORIZED TO RUN DOWNSTREAM SCIENTIFIC STAGES: NO.**

Status vocabulary: READY = completed non-scientific requirement; ENGINEERING READY =
code/template exists but scientific use has gates; HUMAN DECISION REQUIRED = investigator/
institution decision; EXTERNAL RESOURCE REQUIRED = verified source/person/compute/service;
SCIENTIFIC DATA REQUIRED = future authorized evidence; BLOCKED = stage cannot proceed.

| Requirement | Stage | Status | Blocks scientific use? | Evidence / resolution | Owner/dependency |
|---|---|---|---|---|---|
| PR #18 baseline and independent branch | All | READY | No | Required head is ancestor of starting main; no execution-branch access | Engineering |
| Singular generator authorization | English | READY (preserved) | Existing gate still applies | Track-A code/config unchanged; no downstream credential added | Existing human authorization process |
| English pilot traces/diagnostics | Monitor calibration | SCIENTIFIC DATA REQUIRED | Yes if selected as approved calibration input | May eventually supply exact traces, provenance and instrumentation diagnostics; no results inspected here | Separate pilot owner + approved population |
| English pilot effect-based selection | All downstream design | BLOCKED / prohibited workflow | Yes | Must not choose judge/translator/thresholds/N/SESOI from favourable pilot outcomes | Investigator independence |
| Judge schemas/normalization/comparison | Monitor validation | ENGINEERING READY | Scientific gates remain | `clsm.downstream.contracts`, `calibration`, `agreement` | Engineering complete |
| Candidate judge list and immutable specs | Judge | HUMAN DECISION REQUIRED | Yes | Selection record; no model-size heuristic or automatic winner | Investigator + external model/version/resources |
| Calibration/heldout item splits and population | Judge/human | HUMAN DECISION REQUIRED | Yes | Locked trace sets and references; disjoint item/text validation | Scientific design + approved data |
| Judge acceptance criteria/error tradeoff | Judge | HUMAN DECISION REQUIRED | Yes | No BA/F1/PABAK/kappa cutoff frozen; document independent rationale | Investigator/statistical review |
| Blinding/forms/reference lock/adjudication schema | Human | ENGINEERING READY | Scientific gates remain | M2 guides/JSON Schema and validation | Engineering complete |
| Scientific rubric, partial/abstain policy | Human/judge | HUMAN DECISION REQUIRED | Yes | Draft vocabulary is not an approved scientific rubric | Investigator + native reviewers |
| Qualified raters/adjudicators | Human/Urdu | EXTERNAL RESOURCE REQUIRED | Yes | Recruitment/competence/roles/overlap/counts unselected | Human resource + governance |
| Actual independent human labels/reference | Judge/Urdu | SCIENTIFIC DATA REQUIRED | Yes | No real labels created; synthetic fixtures cannot satisfy this | Authorized human collection |
| MMLU primary, compatible secondary separation | Urdu | READY (design boundary preserved) | No substitution allowed | M3 protocol, D-060 extraction separation | Existing plan |
| Four-choice Urdu-capable adapter | Urdu | ENGINEERING READY | Provenance/design gates remain | Offline revision/language/order/hash validation | Engineering complete |
| Aligned Urdu material/content/licensing | Urdu | EXTERNAL RESOURCE REQUIRED | Yes | Exact source/revision/equivalence needed; UrduBench secondary only where compatible | Dataset and native scientific review |
| UrduMMLU candidate verification | Optional robustness | HUMAN DECISION REQUIRED | Blocks its own use only | Provenance/license/schema not verified; not adopted | External source review |
| Urdu prompt/cue/config equivalence | Urdu | HUMAN DECISION REQUIRED | Yes | No Urdu execution config selected by this package | Investigator + native validation |
| Translator specs/lineage/audit pipeline | Translation | ENGINEERING READY | Selection/audit gates remain | `translation`; all four prospective controls supported | Engineering complete |
| Translator selection/version/capacity | Translation | HUMAN DECISION REQUIRED | Yes | No NLLB/context heuristic; separately calibrated, complete-input criteria | Investigator + external provider/resources |
| Native/bilingual equivalence evidence | Translation | SCIENTIFIC DATA REQUIRED | Yes for validated interpretation | Adequacy/disclosure/omission/addition/options/truncation audit; no automatic certificate | Authorized human audit |
| Gap/recovery analysis and report integrity | Urdu/translation | ENGINEERING READY | Valid measurement/data gates remain | Same-trace native−direct and translated−direct; agreement recovery separate | Engineering complete |
| English paraphrase/backtranslation evidence | Translation controls | SCIENTIFIC DATA REQUIRED | Required where prospective plan specifies | Code handles records; no real control run | Separate authorization/resources |
| Power/sensitivity/cluster utilities | Confirmatory | ENGINEERING READY | Design gates remain | Explicit-input exact and simulated power; no N selection | Engineering complete |
| SESOI and nuisance/ICC/missingness justification | Confirmatory | HUMAN DECISION REQUIRED | Yes | Must be independently justified; no invented pilot assumptions | Investigator/statistical reviewer |
| N/alpha/power/test/multiplicity/preregistration | Confirmatory | HUMAN DECISION REQUIRED | Yes | Unfilled M4 templates, not registered/approved | Investigator + resources |
| Institutional ethics determination/consent/pay | Human/all relevant stages | HUMAN DECISION REQUIRED | Yes before affected activity | Governance checklist; no legal/IRB conclusion | Institution/investigator |
| Privacy/storage/release/exposure/escalation | All downstream | HUMAN DECISION REQUIRED | Yes before affected activity | Private mappings/keys separate; operational policy not supplied by schema | Institution/steward |
| Paper/report scaffold | Reporting | ENGINEERING READY | Results needed for manuscript claims | Verified repo citations only; all Results pending | Authorized scientific authors |
| Synthetic end-to-end pipeline | Engineering | READY | No | Fixtures, tests and deterministic report; no scientific file inputs | Engineering |
| Downstream stage authorization | Every scientific stage | BLOCKED | Yes | No judge/Urdu/translation/confirmatory execution permission exists here | Explicit human authorization after relevant gates |

## What the English pilot can and cannot supply

After independent design decisions are appropriately locked, an authorized handoff can
supply English trace hashes, completion/provenance and descriptive feasibility diagnostics.
It cannot by itself supply native Urdu labels, translation equivalence, validated Urdu
judge performance, institutional approval, substantively justified SESOI or confirmatory
power assumptions. Access and any later feasibility-driven amendment must be recorded;
do not rewrite a prospective decision as though it preceded outcome access.

## Next human review

1. Approve measurement construct/rubric, reference protocol and calibration/heldout design.
2. Prospectively register judge candidates and acceptance/error criteria with heldout validation.
3. Resolve native Urdu resources, aligned dataset/cue equivalence and governance.
4. Register translator/control/audit selection criteria and exact identity requirements.
5. Justify confirmatory estimand/test/SESOI/nuisance assumptions and N independently,
   preregister, then authorize only the specific stage whose gates are satisfied.

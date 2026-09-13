# Supervisor decision packet

**One purpose: make these 13 decisions quickly and correctly.** Nothing below is filled
in. Every recommendation is a starting point, not a default — read the tradeoff, then
write your choice in the blank field and sign it. Background: `research/
FINAL_PROTOCOL.md` (index), `research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` (D-073), `docs/
ETHICS_AND_DATA_GOVERNANCE_CHECKLIST.md`. This packet does not itself authorize any
scientific stage; each row's sign-off authorizes only that row.

---

### 1. Institutional ethics/IRB determination

**Exact question:** What institutional review path applies to recruiting human raters
to read model-generated reasoning traces (some containing a misleading hint)?
**Why it matters:** no recruitment may legally or ethically begin without this.
**Options:** (a) formal IRB submission and review; (b) institutional exemption
determination; (c) informal departmental sign-off, if the institution's own policy
permits it for this activity type.
**Recommended:** consult the institution directly — this project cannot assert which
option applies and does not attempt to.
**Tradeoff:** (b)/(c) are faster but only valid if the institution says they apply here;
guessing wrong risks invalidating all downstream human data.
**Unblocks:** everything involving real human raters (rows 2, 4, 6, 7, 8, 13).
**Decision:** ______________________________ **Date:** __________ **By:** __________

### 2. Rater recruitment and qualification

**Exact question:** Where do the two raters and one adjudicator come from, and how is
their competence verified?
**Why it matters:** the primary estimand is entirely anchored on their judgment;
unqualified raters silently invalidate the human reference.
**Options:** (a) university Urdu-speaking student/staff pool; (b) paid platform with a
competence screen; (c) existing personal/institutional contacts with documented
competence.
**Recommended:** (a) or (c) — competence documentation is easiest to verify credibly for
people already known to the institution.
**Tradeoff:** (b) widens the candidate pool but needs a real, non-self-report competence
check (`docs/rater_package/RATER_QUALIFICATION_TEMPLATE.md`) or the reference won't
survive review.
**Unblocks:** training, then production annotation (row 13's prerequisite).
**Decision:** ______________________________ **Date:** __________ **By:** __________

### 3. Compensation

**Exact question:** How, and how much, are raters and the adjudicator paid (if at all)?
**Why it matters:** required before consent is meaningful; affects which recruitment
channel (row 2) is realistic.
**Options:** (a) hourly/task-based payment; (b) course credit, if applicable and
permitted; (c) no compensation (volunteer/collaborator raters only).
**Recommended:** none offered — resourcing/institutional-policy decision outside this
project's authority.
**Tradeoff:** (c) is simplest administratively but narrows who can realistically
participate.
**Unblocks:** consent (row 1 dependency) and recruitment (row 2).
**Decision:** ______________________________ **Date:** __________ **By:** __________

### 4. Storage, retention, and release governance

**Exact question:** Where are rater identities, rationales, and annotations stored, for
how long, and what — if anything — is ever released publicly?
**Why it matters:** free-text rationales can be re-identifying; release policy bounds
what can ever be published.
**Options:** (a) restricted institutional storage, pseudonymous release of
labels/rationales only after a de-identification review; (b) restricted storage, no
public release beyond aggregate statistics; (c) fully open release of pseudonymized
records.
**Recommended:** (a) — supports reproducibility review without pre-committing to full
openness before anyone has checked the free text for re-identification risk.
**Tradeoff:** (c) is most open-science-friendly but forecloses redaction later; (b) is
safest but weakens reproducibility claims.
**Unblocks:** the reproducibility release plan (`docs/REPRODUCIBILITY_RELEASE_PLAN.md`)
finalization, and any public data release after publication.
**Decision:** ______________________________ **Date:** __________ **By:** __________

### 5. Final judge selection (API choice)

**Exact question:** Which automated judge (if any) is used for `D` and `T`?
**Why it matters:** the other half of the primary estimand; must be locked before any
output is observed.
**Options:** (a) GPT-5.4 (`gpt-5.4-2026-03-05`), primary candidate; (b) Claude Sonnet 4.6
(`claude-sonnet-4-6`), backup candidate; (c) neither, if calibration fails both.
**Recommended:** calibrate (a) first per the frozen priority order (`research/
NEXT_STAGE_SCIENTIFIC_FREEZE.md` item 10); fall back to (b) only if (a) fails row 6's
criteria.
**Tradeoff:** choosing without calibration evidence (e.g. "the bigger model") repeats
exactly the model-size heuristic this project's own decisions reject.
**Unblocks:** Tables 3–8 of `paper/main.md`; the whole measurement stage.
**Decision:** ______________________________ **Date:** __________ **By:** __________

### 6. Numeric judge acceptance criteria

**Exact question:** What is the maximum tolerable false-negative rate, false-positive
rate, minimum coverage, and required interval half-width for accepting a judge
candidate?
**Why it matters:** a pure error-cost judgment; no dataset can supply it.
**Options:** state your own four numbers (see `experiments/M2-Monitor-Validation/
JUDGE_SELECTION_RECORD_TEMPLATE.md`'s sign-off table for the exact fields) — there is no
menu of pre-built options here by design.
**Recommended:** none offered — a borrowed number from an unrelated benchmark is
explicitly rejected by this project's own standing decisions.
**Tradeoff:** stricter bounds are more defensible but may reject every candidate,
forcing "no judge selected" (a legitimate, reportable outcome, not a failure).
**Unblocks:** judge calibration scoring (code refuses to run without this, signed,
before any candidate output exists).
**Decision:** filled directly in the linked template; record completion date here:
**Date:** __________ **By:** __________

### 7. Translator selection

**Exact question:** Which translator (provider/model/version) produces the locked
Urdu→English translations for `T`?
**Why it matters:** the secondary estimand `R` depends entirely on one locked pathway.
**Options:** (a) a general-purpose hosted LLM translator, calibrated on a held-out
Urdu→English adequacy set; (b) a dedicated MT system/API; (c) human professional
translation of every trace instead of machine translation.
**Recommended:** (a) or (b), calibrated per `experiments/M3-English-Urdu/
TRANSLATION_PROTOCOL.md`, distinct provider from the judge where practicable.
**Tradeoff:** (c) is cleaner for translation quality but stops testing "automated"
recovery — it changes the research question, not just the toolchain; flag explicitly if
chosen.
**Unblocks:** the translation diagnostic (Tables 6–8).
**Decision:** ______________________________ **Date:** __________ **By:** __________

### 8. Urdu rubric-language approval

**Exact question:** Is the Urdu-language wording of the rubric (as shown to raters, if
used instead of the English rater packet) reviewed and approved?
**Why it matters:** the English construct is frozen; its Urdu rendering is not yet
reviewed, and boundary cases (e.g. "rejecting ≠ disclosing") are exactly where
translation nuance matters most.
**Options:** (a) professional bilingual translation of the rubric, reviewed by both
raters before training; (b) draft by one bilingual reviewer, independently checked by
the second; (c) use the English-language rater packet directly (`docs/rater_package/`),
relying on raters' required strong written English.
**Recommended:** (c) is sufficient and simplest, since raters must already have strong
written English; if Urdu wording is wanted for comfort, (b) is enough if independently
checked.
**Tradeoff:** (a) is most thorough but adds a translation-review step to a document that
isn't itself experimental material.
**Unblocks:** rater training (once row 2 is also resolved).
**Decision:** ______________________________ **Date:** __________ **By:** __________

### 9. SESOI (smallest effect size of interest)

**Exact question:** What absolute difference in `G` (percentage points) would change
your conclusion about relying on this monitor for Urdu?
**Why it matters:** must be a substantive judgment, not derivable from any pilot or
Urdu data.
**Options:** state your own value and one sentence of justification — no pre-built menu,
by design; a value copied from the old blueprint's 10-point figure or from the English
pilot's observed effect is explicitly disallowed.
**Recommended:** none offered.
**Tradeoff:** a larger SESOI needs a smaller N but risks missing a real, smaller effect;
a smaller SESOI needs more resources.
**Unblocks:** row 12 (confirmatory N).
**Decision:** ______________________________ **Date:** __________ **By:** __________

### 10. Alpha and target power

**Exact question:** What significance level and target power apply to the confirmatory
test of `G` (and `R`, if formally tested)?
**Why it matters:** standard, but still a project choice, interacting with row 11.
**Options:** (a) alpha 0.05, power 0.80 (conventional); (b) a different pair, justified
by this study's specific error-cost stakes.
**Recommended:** (a) is defensible absent a specific reason otherwise.
**Tradeoff:** stricter alpha/higher power both increase the required N.
**Unblocks:** row 12.
**Decision:** Alpha: ______ Power: ______ **Date:** __________ **By:** __________

### 11. Multiplicity rule

**Exact question:** Is `R` formally tested alongside primary `G`, with a multiplicity
adjustment, or reported as estimation-only?
**Why it matters:** deciding this after seeing data is exactly the post-hoc flexibility
the confirmatory gate exists to prevent.
**Options:** (a) Holm-adjusted two-test family (`G`, `R`); (b) `R` estimation-only, no
formal test, no adjustment needed.
**Recommended:** (a) if the paper will make a formal claim about `R`; (b) if `R` stays
descriptive.
**Tradeoff:** (a) is a stronger claim if it holds, but raises the bar `R` must clear;
(b) is safer but weaker.
**Unblocks:** row 12 and the confirmatory preregistration template.
**Decision:** ______________________________ **Date:** __________ **By:** __________

### 12. Confirmatory N and nuisance assumptions

**Exact question:** How many independent source items (and total traces) are collected
for the confirmatory stage, and what ICC/missingness/reference-error range is assumed
for that power calculation?
**Why it matters:** the actual resourcing commitment, and the sample-size math is only
as good as its assumed nuisance parameters — an optimistic ICC/missingness guess
produces an underpowered N even at a correctly-chosen SESOI/alpha/power.
**Options:** N is computed from rows 9–11 via the simulation-validated method in
`research/FINAL_PROTOCOL.md` §3 (once that validation is complete — see the open
finding in §1a affecting small-N/high-ICC regimes specifically); nuisance assumptions
(ICC, missingness rate, reference-error rate) are stated as an investigator-justified
range, not a single optimistic point estimate — e.g., "ICC between 0.1 and 0.4,
missingness up to 20%," with a stated basis (prior related literature, or a
conservative default if none exists).
**Recommended:** none for N (downstream arithmetic once rows 9–11 and the §3
validation both exist); for nuisance assumptions, prefer a range wide enough to remain
defensible even if the pilot's own item-dependence structure turns out less favorable
than hoped — do not use the English pilot's own repeated-sample correlation as a proxy
for Urdu disclosure-label ICC, which is a different quantity entirely.
**Tradeoff:** a larger N is more defensible but costs more rater time and compute; a
smaller N risks an uninformative confirmatory result; a narrow, optimistic nuisance
range risks the same even at a "correct" N.
**Unblocks:** the confirmatory preregistration and the final go/no-go (row 13).
**Decision:** N (items): ______ Total traces: ______ ICC range: ______ Missingness
range: ______ Reference-error range: ______ **Date:** __________ **By:** __________

### 13. Final go/no-go for Urdu data collection

**Exact question:** Do we begin Urdu data collection now?
**Why it matters:** the one decision that actually spends human and compute resources.
**Options:** (a) go, once rows 1–12 are all signed; (b) no-go/pause, naming which row(s)
remain open.
**Recommended:** (a) only once every row above has a non-blank entry.
**Tradeoff:** going early without a resolved row risks collecting data under an
unapproved or unjustified design; waiting delays the timeline.
**Unblocks:** everything in `research/EXECUTION_ROADMAP.md` category 3 onward.
**Decision:** ______________________________ **Date:** __________ **By:** __________

# Supervisor decision packet

**One purpose: get sign-off on exactly the decisions that are genuinely human-only.**
Nothing below is filled in. No option list is a default — pick one, write it in, sign
it. Background and full protocol detail: `research/FINAL_PROTOCOL.md` (index),
`research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` (D-073), `docs/
ETHICS_AND_DATA_GOVERNANCE_CHECKLIST.md`. This packet does not itself authorize any
scientific stage; each row's sign-off authorizes only that row's decision.

---

### 1. Institutional ethics/IRB determination

**Why it matters:** the study recruits human raters to read model-generated reasoning
traces, some containing a misleading hint; no institutional review has occurred.
**Options:** (a) formal IRB submission and review; (b) institutional exemption
determination; (c) informal departmental sign-off if the institution's policy permits it
for this activity type. **Claude's recommendation:** consult the institution directly —
this project cannot and does not assert which option applies. **Consequences:** no
recruitment may begin under any option until the institution's own determination is in
hand; skipping this is the single most consequential thing that could make the human
data unusable or retracted later. **Sign-off:** Determination: ______ Date: ______ By: ______

### 2. Rater recruitment and qualification

**Why it matters:** the primary estimand is anchored entirely on native/near-native Urdu
readers' judgments; unqualified raters would silently invalidate the human reference.
**Options:** (a) recruit from a university Urdu-speaking student/staff pool; (b) recruit
via a paid platform with a competence screen; (c) use existing personal/institutional
contacts with documented competence. **Claude's recommendation:** (a) or (c), because
competence documentation (reading/register/code-switch familiarity, per `docs/
HUMAN_URDU_VALIDATION_PACKAGE.md`) is easiest to verify and record credibly for people
already known to the institution. **Consequences:** platform-recruited raters need a
real, documented, non-self-report competence check or the reference is not defensible in
review. **Sign-off:** Recruitment channel: ______ Raters + adjudicator named: ______ Date: ______ By: ______

### 3. Compensation

**Why it matters:** required before consent is meaningful; also affects what recruitment
channel is realistic. **Options:** (a) hourly/task-based payment; (b) course credit
(if applicable and permitted); (c) no compensation (volunteer/collaborator raters only).
**Claude's recommendation:** no recommendation — this is a resourcing and institutional-
policy decision outside this project's authority. **Consequences:** the amount and basis
must be fixed before recruitment, not negotiated per rater. **Sign-off:** Basis/amount: ______ Date: ______ By: ______

### 4. Storage, retention, and release governance

**Why it matters:** rater identities, rationales, and free-text annotations could be
sensitive; release policy affects what can ever be published. **Options:** (a) restricted
institutional storage, pseudonymous release of labels/rationales only after
de-identification review; (b) restricted storage, no public release beyond aggregate
statistics; (c) fully open release of pseudonymized records. **Claude's recommendation:**
(a) — supports reproducibility review without committing to full openness before anyone
has read the free-text rationales for re-identification risk. **Consequences:** (c)
forecloses redaction later; choose the most conservative option you can still revise
upward. **Sign-off:** Option: ______ Retention period: ______ Date: ______ By: ______

### 5. Final judge selection (API choice)

**Why it matters:** the automated monitor `D`/`T` is the other half of the primary
estimand; its identity must be locked before any output is observed.
**Options:** (a) GPT-5.4 (`gpt-5.4-2026-03-05`), primary candidate; (b) Claude Sonnet 4.6
(`claude-sonnet-4-6`), backup candidate; (c) neither, if calibration fails both.
**Claude's recommendation:** run calibration on (a) first per the frozen priority order
(`research/NEXT_STAGE_SCIENTIFIC_FREEZE.md` item 10); fall back to (b) only if (a) fails
the criteria in row 6. **Consequences:** choosing without calibration evidence (e.g. "the
bigger model") is exactly the model-size heuristic this project's own decision log
repeatedly rejects. **Sign-off:** Selected: ______ Based on calibration report hash: ______ Date: ______ By: ______

### 6. Numeric judge acceptance criteria

**Why it matters:** no dataset can supply the relative cost of a missed acknowledgment
versus an invented one; this is a pure error-cost judgment. **Options:** state your own
`max_false_negative_rate`, `max_false_positive_rate`, `minimum_coverage`,
`required_interval_half_width` (see `experiments/M2-Monitor-Validation/
JUDGE_SELECTION_RECORD_TEMPLATE.md`'s sign-off table for the exact fields).
**Claude's recommendation:** none offered — a borrowed number from an unrelated
benchmark is explicitly rejected by this project's own standing decisions; do not ask
for a suggested number here. **Consequences:** signing before any candidate output
exists is what makes this an acceptance rule rather than a post-hoc rationalization.
**Sign-off:** filled directly in `experiments/M2-Monitor-Validation/
JUDGE_SELECTION_RECORD_TEMPLATE.md`; record the completion date here: ______ By: ______

### 7. Translator selection

**Why it matters:** the secondary estimand `R` depends entirely on one locked translation
pathway. **Options:** (a) a general-purpose hosted LLM translator, calibrated on a
held-out Urdu→English adequacy set; (b) a dedicated MT system (e.g. a provider's
translation API); (c) human professional translation of every trace instead of machine
translation (much higher cost, removes "automated recovery" as a claim entirely — this
would change the research question, not just the toolchain). **Claude's recommendation:**
(a) or (b), calibrated per `experiments/M3-English-Urdu/TRANSLATION_PROTOCOL.md`, with a
provider distinct from the primary judge where practicable. **Consequences:** (c) is
scientifically cleaner for translation quality but stops being a test of "automated
translate-then-monitor recovery" — flag explicitly if chosen. **Sign-off:** Selected: ______ Date: ______ By: ______

### 8. Urdu rubric-language approval

**Why it matters:** the English-language disclosure construct is frozen (`research/
NEXT_STAGE_SCIENTIFIC_FREEZE.md` item 5); its Urdu-language wording, as shown to raters,
is not yet reviewed. **Options:** (a) professional bilingual translation of the rubric
text, reviewed by both raters before training; (b) draft by one bilingual reviewer,
independently checked by the second. **Claude's recommendation:** (b) is sufficient given
raters are required to have strong written English (they can also read the English
version side by side); either is acceptable if independently checked.
**Consequences:** do not skip independent check even for a "simple" rubric — disclosure-
category boundaries are exactly where translation nuance matters most.
**Sign-off:** Approved wording version: ______ Date: ______ By (both reviewers): ______

### 9. SESOI (smallest effect size of interest)

**Why it matters:** must be a substantive judgment about what detection-rate difference
would change an oversight conclusion — not derivable from any pilot. **Options:** state
an absolute percentage-point difference in `G` (e.g., "a 10-point gap would change our
recommendation about relying on this monitor for Urdu"). **Claude's recommendation:**
none offered — see `experiments/M4-Confirmatory/SAMPLE_SIZE_DECISION_TEMPLATE.md`; a
value copied from the blueprint's old 10-point figure or from the English pilot's
observed effect is explicitly disallowed by this project's own decisions.
**Consequences:** an unjustified SESOI invalidates the entire confirmatory N calculation
downstream. **Sign-off:** SESOI: ______ Justification: ______ Date: ______ By: ______

### 10. Alpha and target power

**Why it matters:** standard but still a project choice, and it interacts with
multiplicity (row 11). **Options:** (a) alpha 0.05, power 0.80 (conventional); (b) a
different pair, justified by this study's error-cost stakes. **Claude's recommendation:**
(a) is a defensible default absent a specific reason otherwise; state one if choosing
otherwise. **Consequences:** must be fixed jointly with SESOI and N (row 12) before any
confirmatory design is registered. **Sign-off:** Alpha: ______ Power: ______ Date: ______ By: ______

### 11. Multiplicity rule

**Why it matters:** whether `R` is tested as a formal secondary alongside primary `G`.
**Options:** (a) Holm-adjusted two-test family (`G`, `R`); (b) `R` reported as
estimation-only, not formally tested, no adjustment needed. **Claude's recommendation:**
(a) if a formal claim about `R` is intended in the paper; (b) if `R` will only be
discussed descriptively. **Consequences:** deciding this after seeing data is exactly the
kind of post-hoc flexibility this project's confirmatory gate exists to prevent.
**Sign-off:** Rule: ______ Date: ______ By: ______

### 12. Confirmatory N

**Why it matters:** the final independent-item sample size for the Urdu confirmatory
stage. **Options:** computed from rows 9–11 via the simulation-validated method in
`research/FINAL_PROTOCOL.md` §3, once that validation is complete, crossed with actual
rater/annotation/compute resource limits. **Claude's recommendation:** none — this is
downstream arithmetic once rows 9–11 and the simulation validation exist; do not fill it
in before both. **Consequences:** an N chosen before the SESOI/alpha/power rows are
signed is not a real power calculation. **Sign-off:** N (independent items): ______ Total planned traces: ______ Date: ______ By: ______

### 13. Final go/no-go for Urdu data collection

**Why it matters:** the single decision that actually starts spending human and compute
resources on Urdu collection. **Options:** (a) go, once rows 1–12 above are all signed;
(b) no-go / pause, citing which row(s) remain open. **Claude's recommendation:** (a) only
once every prior row in this packet has a non-blank entry — this project's own gates are
designed so no earlier stage can silently substitute for this decision.
**Consequences:** this is the one decision that converts a fully-designed prospective
study into an actual data-collection commitment. **Sign-off:** Decision: ______ Date: ______ By: ______

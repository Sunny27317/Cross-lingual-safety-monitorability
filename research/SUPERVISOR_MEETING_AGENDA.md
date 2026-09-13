# Supervisor meeting agenda

**Turns the 13 rows of `research/SUPERVISOR_DECISION_PACKET.md` into a practical
meeting sequence.** Grouped so related decisions are made together, in the order that
actually unblocks work fastest. Suggested durations assume the supervisor has already
read `research/SUPERVISOR_HANDOFF.md` beforehand — if not, add 10 minutes at the start.

## Before the meeting

Send the supervisor, in this order: `research/SUPERVISOR_HANDOFF.md` (10 min),
`docs/rater_package/RATER_INSTRUCTIONS.md` (5 min, so they've seen the actual task a
rater does). Do not send the full decision packet cold — walk through it live using
this agenda instead, so tradeoffs get discussed rather than silently defaulted.

## Segment 1 — Governance (~15 minutes): decisions 1, 3, 4

Take these together; they're mutually dependent and don't need calibration or judge
results to resolve.

- **Decision 1 (ethics/IRB path):** Which of (a)/(b)/(c) applies at this institution?
  If unknown, this segment ends with an action item ("consult ethics office by
  [date]") rather than a guess.
- **Decision 3 (compensation):** Basis and amount — this constrains decision 2's
  channel, discuss now even though decision 2 comes next segment.
- **Decision 4 (storage/release governance):** (a)/(b)/(c) — affects consent wording,
  must be settled before decision 2's consent step.

**Exit condition:** decision 1 is either signed or has a dated action item; 3 and 4 are
signed (or explicitly deferred with a date, understanding this delays segment 2).

## Segment 2 — Recruitment (~10 minutes): decisions 2, 8

- **Decision 2 (rater recruitment/qualification channel):** (a)/(b)/(c) — given
  decision 3's compensation basis, which channel is actually viable?
- **Decision 8 (Urdu rubric-language approval):** quick — is (c) (use the English
  packet as-is) acceptable, or does the supervisor want (a)/(b) instead? This rarely
  needs debate once raters' English competence requirement is restated.

**Exit condition:** a recruitment channel is named; rubric-language approach is picked.

## Segment 3 — Instrument selection (~15 minutes): decisions 5, 6, 7

These three are the technical backbone of the measurement stage.

- **Decision 6 (numeric judge acceptance criteria) — do this first in the segment.**
  This is the one decision with no menu of options; walk through the four fields
  (`experiments/M2-Monitor-Validation/JUDGE_SELECTION_RECORD_TEMPLATE.md`'s sign-off
  table) live and get the supervisor's actual numbers with rationale, not a deferral.
- **Decision 5 (judge selection):** confirm the calibrate-GPT-5.4-first priority order,
  or ask if the supervisor wants to change it (rare, since it's evidence-based, but
  it's their call).
- **Decision 7 (translator selection):** (a)/(b)/(c) — flag explicitly if (c) (human
  translation) is chosen, since it changes the paper's framing from "automated
  translate-then-monitor" to something else.

**Exit condition:** decision 6's four numbers are recorded with rationale, signed;
decisions 5 and 7's approach is picked (exact candidate/provider can follow later, but
the *criteria* must be locked now).

## Segment 4 — Statistical plan (~15 minutes): decisions 9, 10, 11, 12

**Warn the supervisor before this segment starts:** none of these may be derived from
the English pilot's observed effect or any Urdu data — if they ask "what did the pilot
show," the answer is that it's deliberately irrelevant to this segment.

- **Decision 9 (SESOI):** the hardest one — budget the most time here. Ask directly:
  "what absolute percentage-point gap in `G` would change what you'd tell someone
  about trusting this monitor for Urdu?" Push for a number and a one-sentence reason,
  not "let's see what we get."
- **Decision 10 (alpha/power):** usually quick — confirm 0.05/0.80 or get the
  alternative.
- **Decision 11 (multiplicity):** ask directly: "will the paper make a formal claim
  about `R`, or keep it descriptive?" — this answers itself once framed this way.
- **Decision 12 (confirmatory N and nuisance assumptions):** **do not compute this
  live.** Explain it's downstream arithmetic once decisions 9–11 are signed and the
  §3 simulation validation (currently blocked on Codex's two open engineering fixes,
  `research/FINAL_PROTOCOL.md` §1a) is complete. Get the nuisance-assumption range
  (ICC, missingness) discussed and recorded now so the calculation can run
  immediately once unblocked — this avoids a second meeting.

**Exit condition:** 9, 10, 11 signed; 12's nuisance-assumption range recorded even
though N itself stays pending.

## Segment 5 — Go/no-go (~5 minutes): decision 13

- Read back every decision made in segments 1–4. If any remain unsigned, decision 13
  is a **no-go with a named blocker list**, not a conditional yes.
- If all are signed: decision 13 is a straightforward go, with a start date.

**Exit condition:** decision 13 is recorded either way, with either a go date or a
specific list of what's still open and who owns closing it.

## After the meeting

Whatever was signed goes directly into `research/EXECUTION_ROADMAP.md`'s master
after-approval sequence (§3–5) — no further planning meeting is needed before
execution begins on the steps that are now unblocked. Circulate the completed
`research/SUPERVISOR_DECISION_PACKET.md` to all listed owners (steward, translator,
reviewers) so each knows exactly which of their steps in `research/
HUMAN_EXECUTION_CHECKLIST.md` can start immediately.

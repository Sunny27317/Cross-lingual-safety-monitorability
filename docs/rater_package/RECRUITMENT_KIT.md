# Rater recruitment kit (Workshop-v1)

**Status: READY TO SEND once ORPI permits.** The ORPI request was sent on or before 2026-10-04.
Send nothing until ORPI's written guidance is saved in `engineering/provenance/`. If ORPI requires review, use only its approved materials.

Needed: **2 raters + 1 adjudicator**, all native or near-native Urdu readers.

Placeholders:
- `[HOURS]`: time estimate (see E);
- `[PAY]`: compensation (see F);
- `[DATE]`: completion target;
- `[CONTACT]`: investigator contact;
- `[ETHICS LINE]`: wording permitted by ORPI.

**Hypothesis exposure.** Messages describe the task, not the study's hypotheses or the
expected comparison. Do not mention automated-versus-human comparisons, model names,
languages being compared, or expected results.

---

## A. Short WhatsApp / text message

```
Assalam-o-alaikum [NAME]! I'm looking for people who read Urdu fluently (and English
well) for a short research task: reading AI-written Urdu text about science quiz
questions and choosing one of five labels for each, using clear written instructions.
About [HOURS] hours total, on your own schedule, by [DATE]. [PAY]. Interested? I can
send details. — Sana
```

## B. Professional email

```
Subject: Urdu reading task for a research project — [HOURS] hours, [PAY]

Dear [NAME],

I'm Sana Ullah, working on a research project about how AI-generated reasoning text is
evaluated. I'm looking for [two raters / one adjudicator] who read Urdu fluently and
English well.

The task: you would read about 312 short items. Each shows a multiple-choice science
question, its options, a suggestion that was shown to an AI system, and the AI's
reasoning written in Urdu. For each, you choose one of five labels following written
instructions and practice examples. [Adjudicator: you would review only items where
the two raters' labels differ.]

Time: about [HOURS] hours total, flexibly, by [DATE]. Compensation: [PAY].
We record only your labels and optional notes, under a pseudonym. You can skip any item
or stop at any time. [ETHICS LINE]

If you're interested, I'd like to arrange a 10-minute call and a short reading exercise
(about 10 minutes) to make sure the task suits you.

Thank you,
Sana Ullah
[CONTACT]
```

## C. Qualification screener (steward completes; record on `RATER_QUALIFICATION_TEMPLATE.md`)

1. How did you learn to read Urdu? Do you read it regularly now? (Open answer.)
2. Reading exercise: read two short **synthetic** Urdu passages (from
   `TRAINING_TUTORIAL.md` §4, not study data) and summarize each in one English
   sentence. *Pass:* both summaries are accurate.
3. Reading exercise: one synthetic Urdu passage mixing English terms. Explain what it
   says. *Pass:* correct.
4. Are you comfortable reading English instructions of about 5 pages? (Y/N)
5. Have you been involved in designing this study, or are you related to or in a close
   working relationship with the investigator or another rater? (See G.)
6. Can you complete about [HOURS] hours by [DATE] without discussing items with others?
   (Y/N)
7. Adjudicator only: are you willing to label blind first and only then see the raters'
   labels? (Y/N)

**Not sufficient on its own:** nationality, self-report without the exercise, AI/CS
expertise, or experience with translation tools.

## D. Rater information sheet (give before consent)

**What this is.** A research task: labelling AI-written reasoning text in Urdu.

**What you will do.**
1. Read the instructions.
2. Complete a short practice set (synthetic examples).
3. Label about 312 items independently.

Each item shows a question, its options, a suggestion the AI saw, and the AI's
reasoning. You choose `disclosed`, `not_disclosed`, `partial`, `cannot_tell` or
`abstain`, with an optional confidence value and note.

**What you won't see.** Which AI produced the text, any identifiers, the correct answer,
any other rater's labels, or any automated system's output.

**Time.** About [HOURS] hours, on your own schedule, by [DATE].

**Compensation.** [PAY].

**Voluntary.** You may skip any item ("abstain", no reason needed) or stop at any time.
[If paid: state how stopping early affects payment, per ORPI guidance.]

**Risks.** Minimal. The content is AI-written general-science reasoning.

**Your information.** Your labels are stored under a pseudonym. Your name and contact
details are kept separately, are used only to administer the task, and are not
published.

**Questions.** [CONTACT]. [ETHICS LINE].

## E. Time-commitment placeholder

`[HOURS]` = (312 items × [MINUTES PER ITEM, measured on the practice set]) / 60, plus
about 1 hour of training. Measure minutes per item during the practice set. Do not
estimate it from study items. The adjudicator's time scales with the number of flagged
items, which is unknown in advance; quote a range.

## F. Compensation placeholder

`[PAY]` = [amount, currency, method, timing] **or** "This is a voluntary, unpaid task."
Decide before sending any message, record it on the qualification record, and apply it
identically to both raters. The adjudicator may differ, but state the basis. Follow
ORPI's guidance on payment documentation.

## G. Conflict-of-interest statement (each rater/adjudicator signs or confirms)

> I confirm that I was not involved in designing this study or its hypotheses. I am not
> related to, or in a close personal or working relationship with, the other raters or
> the adjudicator. I will not discuss any item or my labels with anyone until I am told
> adjudication has begun. I have no financial or other interest in any particular
> outcome. If any of this changes, I will tell the investigator.
> If the investigator serves as a rater: this is disclosed in the publication, and the
> investigator does not adjudicate.

## H. Confidentiality and data-handling statement

> The items you label are research materials. Please do not copy, share, publish, or
> paste them into any other AI system or online tool, and do not discuss them until the
> study is complete. Delete any local copies when you submit.
> Your labels are stored under a pseudonym in the project's research records and may be
> released publicly under that pseudonym [only if ORPI guidance and your consent allow].
> Your name and contact details are stored separately, used only to administer the task
> and any payment, and never published. You may ask for your contact details to be
> deleted after payment is complete. Submitted labels are locked for research integrity
> and are not overwritten; if you notice a mistake, report it and the correction is
> stored alongside the original.

## I. Availability question (send after an expression of interest)

```
Thanks for your interest! To plan the work, could you tell me:
1. Roughly how many hours per week you could give over the next [N] weeks?
2. Any dates you are unavailable?
3. Whether you can finish about [HOURS] hours of labelling by [DATE]?
4. Whether you prefer to work on a laptop (spreadsheet/form) or on paper?
```

## Onboarding order (after acceptance)

1. Screener.
2. Information sheet.
3. Consent or acknowledgment, per ORPI.
4. COI and confidentiality confirmations.
5. Compensation record.
6. `RATER_ONBOARDING.md` → `RATER_INSTRUCTIONS.md` → `TRAINING_TUTORIAL.md` →
   `ANNOTATION_DECISION_TREE.md` → `RATER_FAQ.md`.
7. Practice set with feedback on rules only.
8. Real packet.

The adjudicator starts only after both raters have submitted and their labels are locked.

# ORPI reply: response templates (Workshop-v1)

The request has been sent (`engineering/provenance/ORPI_REQUEST_SENT_2026-10-04.json`). No
reply has been received. **Do not assume which outcome will arrive.**

**For every outcome, first:**
1. Save ORPI's reply verbatim as
   `engineering/provenance/ORPI_REPLY_<YYYY-MM-DD>.txt` (or `.pdf`), and record its SHA-256.
2. Quote the determination exactly in the manuscript's Ethics statement and in Methods
   §4.11 (the `[[ORPI: …]]` tags).
3. Follow ORPI's instructions where they differ from anything below. ORPI's wording
   governs.

The placeholders in the replies below are filled only from ORPI's own message, or with
your name.

---

## A. "Not human-subjects research / no IRB review required"

**Next action.** Save the reply. Then send recruitment per
`docs/rater_package/RECRUITMENT_KIT.md`, using ORPI's wording for the `[ETHICS LINE]`
(e.g. "UNC Charlotte ORPI determined this activity does not require IRB review"). Use the
information sheet. Use a consent or acknowledgment form only if ORPI suggests one or you
choose to.

**Reply:**
```
Dear Ms. Runden,

Thank you for the determination. I will keep your message with the project records
and quote it in any resulting publication. Please let me know if anything else would be
helpful.

Best regards,
[MY NAME]
```

**Unblocked:** recruitment → screening → training → annotation of all 312 → adjudication.
Also unblocked: the Ethics statement text.

**Still blocked:** translation (translator artifacts), translated judging, analysis
(analysis commit and unsealing), and results.

## B. "Exempt — submit an exempt application"

**Next action.**
1. Prepare the exempt submission in ORPI's system or form, using
   `docs/ORPI_DETERMINATION_PACKAGE.md` §3–4 (summary and activity description),
   `docs/rater_package/RECRUITMENT_KIT.md` (recruitment text, information sheet,
   confidentiality), `docs/RATER_CONSENT_TEMPLATE.md`, and the rater instructions.
2. Submit.
3. **Do not recruit until the exemption is granted in writing.**

**Reply:**
```
Dear Ms. Runden,

Thank you. I will prepare and submit the exempt application as you describe. Could you
confirm [any specific form, system, or attachment ORPI named, quoted from their message]?
I will not contact or recruit any rater until the exemption is granted.

Best regards,
[MY NAME]
```

**Unblocked now:** preparing the application only.

**Still blocked:** all recruitment and annotation until written exemption. Translation,
translated judging and analysis preparation can continue in parallel, because they are
not human-involving.

## C. "Expedited or full IRB review required"

**Next action.**
1. Prepare the IRB protocol from the same materials. Add anything the template requires:
   risks, data management, consent, recruitment, compensation.
2. Ask whether a faculty PI or sponsor is required. A student investigator often needs
   one, but follow ORPI's answer.
3. Submit.
4. Treat every rater-facing document as draft until approved.
5. Expect the timeline to move. Recompute the preprint critical path once ORPI gives a
   review schedule.

**Reply:**
```
Dear Ms. Runden,

Thank you for the guidance. I will prepare a [expedited / full — as stated by ORPI] IRB
submission. Could you let me know whether a faculty principal investigator or sponsor is
required for a student-led project, and whether there is a template or checklist I should
follow? I will not recruit anyone until the protocol is approved.

Best regards,
[MY NAME]
```

**Unblocked now:** protocol preparation only.

**Still blocked:** recruitment and annotation until approval. Automated stages continue.
**Contingency:** if approval timing makes the preprint unreasonably late, any decision to
change scope must be a dated, documented decision **before** any human data exist. For
example: posting a version clearly labelled as automated-only, with G not reported. Never
substitute non-native or unapproved labels.

## D. "Need more information"

**Next action.** Answer exactly what is asked, using the package text. Attach the
one-page summary (§3) and the activity description (§4) if they are not yet sent. Do not
add claims about how the activity should be classified.

**Reply:**
```
Dear Ms. Runden,

Thank you for your reply. In answer to your questions:

[ANSWER EACH QUESTION, quoting the relevant facts from the one-page summary: the
material is AI-generated text on public science questions; two raters plus one
adjudicator label about 312 passages with a written rubric; labels are stored under
pseudonyms; no data about the raters are collected beyond qualification and
administrative records; the two completed text reviews were a translation-equivalence
check and a verbal check of 16 invented training sentences.]

I have attached a one-page summary and a description of the rater task. I am happy to
provide anything else, and I will not recruit anyone until I hear back.

Best regards,
[MY NAME]
```

**Unblocked:** nothing new.

**Still blocked:** everything human-facing.

---

## Applies to every outcome

- Record each email exchange (date, SHA-256) in `engineering/provenance/`.
- If ORPI asks about the two completed reviews, follow its guidance exactly. Report any
  required retrospective step in the Ethics statement.

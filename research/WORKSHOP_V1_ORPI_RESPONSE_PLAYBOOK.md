# ORPI response playbook (2026-10-06)

**Status:** a request was sent on or before 2026-10-04. **No determination has been received.**
Do not send another email. Templates for replying to ORPI already exist in
`docs/ORPI_RESPONSE_TEMPLATES.md` (sections A–D). This playbook adds, for each
determination:
- the next administrative step;
- the manuscript's Ethics wording;
- what may start;
- what stays blocked.

**For every outcome:**
- Save the reply verbatim in `engineering/provenance/ORPI_DETERMINATION_<date>.json`, with
  its SHA-256.
- Never paraphrase it in the paper beyond the wording below.

| Determination | Next administrative step | Ethics wording (fill bracketed parts verbatim from the reply) | May start | Stays blocked |
|---|---|---|---|---|
| **A. Not human-subjects research** | Save the reply. Record any conditions it states (e.g. no identifiers). Finalize compensation and the investigator-as-rater decision. Record the capacity stop date, if any | "UNC Charlotte's Office of Research Protections and Integrity determined on [date] that the annotation component does not constitute human-subjects research [quote the determination]. Annotators were compensated [statement] and are acknowledged [anonymously / by name with consent]." | Recruitment (template A of the recruitment kit), onboarding, annotation, adjudication | Public release of labels until the release route and consent are settled |
| **B. Exempt** | Submit the exempt application exactly as instructed. Wait for the exemption notice. Use the consent or information sheet the exemption requires | "The annotation protocol was determined exempt by UNC Charlotte's Office of Research Protections and Integrity ([category, if given]; [date], [reference number])." | Nothing until the exemption notice is saved. After it: recruitment with the required consent text | Everything human until the notice is saved |
| **C. IRB review required** | Prepare the IRB application (protocol, consent form, data plan, recruitment text from the kit). Record any requested protocol changes as a dated amendment **before** annotation | "The annotation protocol was reviewed and approved by the UNC Charlotte IRB ([type], [protocol number], [date])." | Only preparation of the application | All human work until approval. If timing is decisive, consider posting a validation-pending preprint (§5.16 variant; no G claims) |
| **D. More information requested** | Answer only the questions asked, with `docs/ORPI_RESPONSE_TEMPLATES.md` §D. Do not volunteer protocol changes. Keep a copy of the reply | None until a determination | Nothing human | All human work |

**What may be prepared under every outcome** (none of it touches people):
- the synthetic analysis code;
- the manuscript text;
- the packet (already built);
- the rater-document reconciliation (e.g. removing the reviewer's name).

**Never:** describe the study as approved or exempt before the written determination
exists; contact raters; start annotation.

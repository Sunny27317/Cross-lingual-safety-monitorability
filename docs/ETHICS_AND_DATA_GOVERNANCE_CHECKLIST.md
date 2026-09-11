# Ethics and data governance — review checklist

**HUMAN REQUIRED:** institution-specific ethics/IRB determination, applicable policy,
responsible investigator and documented approval/exemption/other determination where
appropriate. This checklist makes no legal or IRB finding. Public benchmark use does
not by itself resolve human-participant or model-output governance obligations.
No human recruitment, annotations or scientific exposure assessment occurred here.

| Review item | Required evidence/action | Status |
|---|---|---|
| Responsible institution and investigator | Name/role and escalation owner | HUMAN REQUIRED |
| Institutional ethics determination | Consult institution before recruitment; retain written determination/scope | HUMAN REQUIRED |
| Public benchmarks | Verify exact source/revision/license/terms and derivative/release compatibility | HUMAN / EXTERNAL REQUIRED |
| Model outputs | Record provider/model terms, provenance and permitted storage/release | HUMAN / EXTERNAL REQUIRED |
| Human involvement | Describe task, recruitment, language competence and data collected | HUMAN REQUIRED |
| Consent | Approved information/consent text, voluntary participation, withdrawal handling | HUMAN REQUIRED |
| Compensation | Amount/basis, time estimate, payment process, abstention/withdrawal treatment | HUMAN REQUIRED |
| Potentially harmful content | Prospective exposure review, training, warnings, pause/skip and support process | HUMAN REQUIRED |
| Escalation | Named contact, urgent/nonurgent route, incident logging and response ownership | HUMAN REQUIRED |
| Privacy | Minimize identifiers; avoid unnecessary demographic/personal data | HUMAN REQUIRED |
| Pseudonyms | Steward keeps identity key separate from annotations; restrict access | ENGINEERING READY / HUMAN REQUIRED |
| Blinding key | Private HMAC secret, access list, secure backup/rotation and destruction policy | HUMAN REQUIRED |
| Storage | Approved location, encryption/access controls, retention and backup schedule | HUMAN / EXTERNAL REQUIRED |
| Hosted services | Determine permitted data transfer, region/provider retention and access | HUMAN / EXTERNAL REQUIRED |
| Release | Decide which traces/labels/rationales can be released; de-identification review | HUMAN REQUIRED |
| Reidentification | Opaque IDs/hashes do not anonymize recognizable trace text or free-text rationale | HUMAN REQUIRED |
| Copyright/licensing | Verify rights for benchmark material, translations and derived artifacts | HUMAN REQUIRED |
| Access independence | Keep prospective designers separate from pilot result access until decisions lock | ENGINEERING PROCESS / HUMAN REQUIRED |
| Audit trail | Decisions, git/config/data/label hashes, access history and deviations | ENGINEERING READY |
| Incident/deviation handling | Preserve originals, notify appropriate owner, review release/run status | HUMAN REQUIRED |

Fill institution/contact fields in restricted operational records, not public annotation
JSON. Do not commit personal IDs, contact lists, consent forms, payment details, access
secrets or raw scientific records to this infrastructure PR. A completed code schema
cannot certify informed consent, competence, equivalence, or institutional permission.

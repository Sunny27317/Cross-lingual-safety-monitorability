# Workshop-v1 downstream closure record

This dated record supplements, and does not rewrite, historical decision files.

- D-PG-1: no compliance inclusion/exclusion floor; one exploratory >=0.50 sensitivity only.
- D-PG-2: retain `9-1065` Qwen Urdu Cue-A sample 0 timeout as missing; no retry.
- D-PG-3: R is descriptive only; no paraphrase-control causal/mechanistic claim.
- D-PG-4: Judge V2 labels are `disclosed`, `not_disclosed`, `partial`, `cannot_tell`; human parity packet includes question, options, exact suggestion, and trace with model/item/condition/sample blinding.
- D-PG-5: no-silent-truncation translation; ordered line/sentence/clause/token segmentation with <=200 source-token chunks; incomplete trace is missing.

Generation stage is locked: 3312 structural, 3311 successful, one retained missing timeout. Raw generation records and historical Attempt-1/Attempt-2 evidence remain unchanged.

Prepared but not executed: 935 translation tasks; 936 English-direct judge tasks; 935 Urdu-direct judge tasks; 935 translated-Urdu judge tasks; 312 human candidates. No scientific downstream calls have occurred.

## Launch preparation

Official upstream metadata resolved the IndicTrans2 primary revision and toolkit
commit, but the gated model/config/tokenizer files and local runtime versions are
not yet available. The translation contract is consequently not frozen. The
non-executing direct Judge V2 launcher validates 936 English + 935 Urdu tasks and
requires an explicit authorization file.

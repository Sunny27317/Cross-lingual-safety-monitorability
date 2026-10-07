# Post-judge command book

All commands below are for the isolated/reviewed implementation. Do not point
them at a live run until the process has exited and the investigator releases
the result-unseal boundary.

1. **SAFE READ-ONLY:**
   `PYTHONPATH=src python -m clsm.workshop_v1.translated_judge_launcher --progress`
2. **SAFE READ-ONLY QC:**
   `PYTHONPATH=src python -m clsm.workshop_v1.translated_judge_launcher --post-qc`
3. **MUTATING, NON-SCIENTIFIC:** write the reviewed judge-stage seal using the
   canonical post-judge seal writer after QC PASS.
4. **MUTATING, NON-SCIENTIFIC:** build and hash the human packet; annotation
   requires ORPI/institutional approval.
5. **SCIENTIFIC EXECUTION:** translated judging is already a separate authorized
   stage; no additional execution is provided by this command book.
6. **REQUIRES INVESTIGATOR AUTHORIZATION:** analysis wrapper and results sealing.

No command in this document prints label counts or effect summaries.

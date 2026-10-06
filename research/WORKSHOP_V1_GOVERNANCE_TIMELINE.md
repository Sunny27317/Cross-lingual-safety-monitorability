# Workshop-v1 governance and provenance timeline (manuscript Appendix J)

**Evidence rule.** Dates come from artifact timestamps and dated records in this
repository. The Claude-side workstream documents carry **nominal session dates that are
inconsistent with artifact timestamps** (for example, "D5 decision 2026-10-05" and "D5
PASS 2026-10-13", while the D5 run records are timestamped 2026-09-29). Those session
dates are **not** used here. File modification times are local (UTC−4) and are converted
to UTC; they are marked "(file time)" as weaker evidence than a recorded timestamp.

**Categories:**
- **PRO:** prospective; before main generation.
- **PGPR:** post-generation but pre-result; before any judge or human label was
  examined.
- **ENG:** engineering fix with no scientific change.
- **DOC:** post-hoc documentation or erratum.

| Date (UTC) | Event | Category | Evidence |
|---|---|---|---|
| after 2026-09-13, before 2026-09-24 | Study moved from the MMLU English feasibility track to OpenBookQA English–Urdu (item-aligned Urdu release) | PRO | base commit `e764072` dated 2026-09-13; first Workshop-v1 pilot 2026-09-24. **No direct timestamp.** The selection seed value `20260921` is a seed, not a timestamp |
| before 2026-09-24 (inferred) | 120-item main and 36-item Cue-B manifests frozen (deterministic hash selection; replacement prohibited) | PRO | manifest hashes `576a991f…`, `e18b48b6…`. The manifests carry no timestamp; the pilot that excludes the pilot item from them ran 2026-09-24 |
| ≈ 2026-09-23/24 | Models (Qwen3-1.7B, Gemma-3-4B-it) and judge (Falcon-H1-7B-Instruct) specifications frozen; Cue A/B wording frozen | PRO | judge contract version `claude-session11-20260924`; `models.yaml` |
| 2026-09-24 18:43 | Excluded pilot, Qwen native thinking: Urdu outputs fail the script criterion | PRO | `_runs/workshop-v1-excluded-feasibility/` record timestamps |
| 2026-09-29 | Native reviewer verbally approves the Urdu Cue A/B wording and the language instruction unchanged (investigator-recorded; no written sign-off) | PRO | native-review records |
| 2026-09-29 21:04–21:09 | Amended excluded pilot with the language instruction: Gemma passes; Qwen Urdu 0/3 → FAIL_STOP | PRO | `_runs/workshop-v1-excluded-feasibility-v2/` |
| 2026-09-29 (between pilot and rerun) | **D5 decision:** Qwen non-thinking, Gemma's elicitation sentence. First D5 attempt fails before inference (port bind) | PRO / ENG | D5 port-failure audit; `_runs/…-d5/` |
| 2026-09-29 22:24–22:25 | D5 rerun: 6/6 calls, script criterion met in both languages | PRO | `_runs/workshop-v1-excluded-feasibility-d5-rerun/` |
| 2026-10-01 | Formal 120-item native equivalence review received (all PASS); telephone clarification of 3 blank fields recorded | PRO | review PDF; telephone clarification JSON |
| 2026-10-01 (file time ≈17:10) | Generation configuration hashed (`7b00e996…`) | PRO | `engineering/workshop_v1_generation_config.json` |
| 2026-10-02 19:20 | Attempt 1 authorized; fails before inference on all 3,312 calls (port bind) | PRO / ENG | `attempt_1_provenance.json` |
| 2026-10-02 19:52 | Attempt 2 authorized and started (same configuration) | PRO | Attempt-2 authorization; execution manifest |
| 2026-10-02 ≈20:14–23:24 | Serialization failure on task 30; lossless hashing/serialization fix; manifest-identity resume fix; resume | ENG | failure record; resume provenance |
| 2026-10-03 17:04 | Generation timeout, item `9-1065` (Qwen, Urdu, Cue A, sample 0) | — | record |
| 2026-10-03 17:09–18:59 | Undocumented 1.84 h pause (no records lost) | DOC needed | record timestamps |
| 2026-10-04 14:20 | Generation completes: 3,312 persisted, 3,311 runtime-successful | — | records; generation QC |
| 2026-10-04 | Post-generation scientific audit; interpretation framework drafted | PGPR | audit and framework documents |
| 2026-10-04 | D-PG-1 (compliance), D-PG-2 (retain timeout), D-PG-3 (R descriptive), D-PG-4 (Judge V2 + human parity), D-PG-5 (translation segmentation) approved. The record's `recorded_utc` is a nominal 00:00Z | PGPR | approvals record |
| 2026-10-04 (file time ≈17:48) | Judge V2 prompt frozen (`050ed492…`); 40-fixture format gate passed | PGPR | judge-prompt-v2 JSON; fixture summary |
| 2026-10-04 (file time ≈18:16) | Direct-judge authorization (1,871 rationales) | PGPR | authorization JSON |
| 2026-10-04 19:10 | D-PG-6 (bootstrap conventions) approved | PGPR | D-PG-6 approval record (`recorded_utc`) |
| 2026-10-04 19:15 | Analysis code frozen by content hash (`1671bc3c…`), from an uncommitted working tree | PGPR | analysis-code-freeze record |
| 2026-10-04 | κ high/low activation cutoff withdrawn before any human label existed | PGPR | decision-tree V1 note |
| 2026-10-04 | Direct judge completed and sealed (`3077fae1…`): 1,863 valid, 5 malformed, 3 no-label. No label distribution examined | PGPR | stage-hash file |
| 2026-10-04 / 05 (file time ≈00:56Z on 10-05) | Erratum: static files added after the seal; no judge output or configuration changed | DOC | seal-snapshot erratum |
| ≤ 2026-10-04 (record ≈21:46) | ORPI determination requested (investigator-reported) | PGPR | ORPI-request record |
| 2026-10-04 (record ≈21:33) | Native reviewer verbally confirms the 16 synthetic Urdu training sentences (no form). **Two records exist**: Codex's and the scientific-lead's. Consolidate them | PGPR / DOC | both provenance JSONs |
| pending | Translator runtime frozen; translation; translated judging; human annotation; analysis | — | — |

**Errata to keep with this timeline:**
- Claude-side nominal session dates.
- `models.yaml` "2026-10-05" D5 date.
- The `population_role` label.
- The 1.84 h pause (needs an investigator note).
- The verbal-review blank form. It received a status-note header after its hash was
  recorded; the pre-note hash is in the scientific-lead's record. The Codex record's
  `review_packet_modified: false` predates that note.


## Date discrepancy register (artifact timestamps are authoritative; historical documents are not rewritten)

| Hand-written date | Where | Artifact evidence | Status |
|---|---|---|---|
| D5 amendment "2026-10-05" | `configs/workshop_v1/models.yaml` (`decision_record`; part of the hashed model config) | D5 rerun records 2026-09-29 22:24–22:25Z; main generation used D5 on 2026-10-02 | **Conflict.** Documented, not edited (editing would change the config hash) |
| Session dates 15–22 ("2026-10-01" … "2026-10-15") | Claude-side `CLAUDE_WORKSHOP_V1_HANDOFF.md` and workstream docs | amended pilot and D5 both 2026-09-29; those files were last modified ≤ 2026-10-01 | **Conflict.** These are nominal session counters, not dates |
| "2026-10-13" / "2026-10-15" document headers | Claude-side `ANALYSIS_PLAN_FREEZE.md`, `HUMAN_VALIDATION_PROTOCOL.md`, `JUDGE_GOVERNANCE_RECORD.md`, `TRANSLATOR_FREEZE_RECORD.md`, `ETHICS_ORPI_CLASSIFICATION.md`, etc. | file modification ≤ 2026-10-01 | **Conflict.** Future-dated relative to their own files |
| D-PG-1..5 `recorded_utc: 2026-10-04T00:00:00Z` | approvals record | file last modified ≈19:29Z (may be a rewrite) | **Nominal.** Exact approval time unknown. The manuscript says "2026-10-04", not a time |
| "≈2026-09-21" manifests | earlier version of this timeline | no manifest timestamp | **Corrected above** |
| "Attempt-2 runtime failure item 10-220" | earlier `TECHNICAL_MAIN_READINESS.md` paragraph | record `01aeaebc…` = item 9-1065 | Corrected by engineering (reconciliation doc) |
| Verbal training review: two records (Codex 21:33Z; scientific lead ≈21:34Z) | `engineering/provenance/` | both consistent on substance | **Duplicate.** Consolidate or cross-reference |

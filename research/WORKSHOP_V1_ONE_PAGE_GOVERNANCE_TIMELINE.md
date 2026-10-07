# Workshop-v1 governance timeline (publication version)

Only scientifically meaningful events are listed; the full record is Appendix J
(`research/WORKSHOP_V1_GOVERNANCE_TIMELINE.md`). Times are UTC. "Before results" means that
no monitor or human label had been examined.

| When | Event | Why it matters |
|---|---|---|
| ≤ 2026-09-24 | **Population frozen.** 120 items by seeded hash selection; a 36-item Cue-B subset; replacement prohibited | Items chosen without content or outcomes |
| ≈ 2026-09-23/24 | **Models and monitor specified.** Qwen3-1.7B, Gemma-3-4B-it; Falcon-H1-7B monitor (chosen on public Urdu accuracy, not on agreement with our labels) | No selection on study data |
| 2026-09-29 | **Qwen amendment** (non-thinking mode, shared elicitation sentence), after an excluded pilot. Native reader approves the Urdu cue and instruction wording (verbal) | Fixed before main generation |
| 2026-10-01 | Native item-equivalence review of all 120 pairs (written, all PASS). **Analysis plan content final** (verified byte-for-byte from session logs) | Plan predates generation |
| 2026-10-02 → 10-04 | **Generation** under a frozen configuration: 3,312 planned, 3,311 completed. One timeout is retained as missing | Executed from an uncommitted tree; identified by hash |
| 2026-10-04 | **Post-generation decisions D-PG-1 to D-PG-6** (compliance reporting, timeout retention, descriptive scope of R, Judge V2 with input parity, translation segmentation, bootstrap conventions). **Judge V2 frozen** | After generation, before results |
| 2026-10-04 → 10-05 | **Direct monitoring** of 1,871 rationales; sealed `3077fae1…` | Labels never examined |
| 2026-10-05 | **Translation amendment D-TR-1–6**, after a technical batching failure and before any successful translation | Triggered by a technical failure, not an outcome |
| 2026-10-06 | Translation complete (935/935) and sealed (`14175ab5…`). **Identity-translation decision** (six identities stay in the primary analysis; exclude-six as robustness). **Translated monitoring authorized** | Before translated judging |
| 2026-10-06 | **Interpretation framework locked** (written after generation, with minimal documented exposure); analysis decisions D-FA-1 to D-FA-5 | Before results |
| 2026-10-07 | Translated monitoring complete (935/935) and sealed. **Final analysis frozen** by content hash (02:07) and committed (`c35785cd`, 10:15); D-FA-6 (strict sign rule); agreed-only analysis declined | Before results |
| pending | **Human-stage authorization** (ORPI determination) → 2 × 312 labels with adjudication | Required for the primary estimand G |
| pending | **Single result unseal** under the protocol and Addendum A1 | All estimates come from one locked run |

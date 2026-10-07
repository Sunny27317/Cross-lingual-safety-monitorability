# Rater packet: final scientific specification (2026-10-07)

**Purpose.** Define the only packet that may be given to raters. Codex implements it. This
specification was written without reading any rationale text or label.

**Why it is needed.** The existing packet files
(`experiments/_runs/workshop-v1-human-validation-packet{,-v2}/`) are ordered in **four
model × cue blocks**: Qwen Cue A (120), Qwen Cue B (36), Gemma Cue A (120), Gemma Cue B
(36). Position therefore reveals model and condition. They must not be released.

## Requirements

| # | Requirement | Specification | Check |
|---|---|---|---|
| P1 | Population | Exactly the 312 units of `human_pool.candidate_pool()` (240 Cue A, 72 Cue B; one sample per model × item × cue) | 312 unique IDs, equal to the pool |
| P2 | Opaque IDs | `blind_id` = `"blind-" + object_hash([item, row_hash, model, cue, sample, "human-reference-v1"])` (frozen in `human_pool.HumanCandidate`). No other identifier | IDs reveal nothing without the hash inputs |
| P3 | Frozen order | **Lexicographic by `blind_id`** (`human_pool.packet_order`). The order record is `engineering/workshop_v1_human_packet_order.json`, method `lexicographic_blind_id`, order hash `ee0e1b577aa6e7b88d4216c47b841d096920721326394eaca0affa43b80852ee` | Recompute the order hash from the packet; it must equal `ee0e1b57…` |
| P4 | No positional leakage | Interleaved order. With the frozen order the longest same-(model, cue) run is 9 and there are 221 runs, versus 4 blocks in the old packets | Run-length check recorded in the packet manifest |
| P5 | Shown fields only | `blind_id`, `language`, `question`, `options` (ordered, as in the generation prompt), `suggestion` (exact sentence), `trace` (the parsed reasoning span the judge saw) | Field-set equality |
| P6 | Never shown | Model, family, size; condition or cue name; item or sample ID; answer key; model's final answer; any automated or translated label; any translation; compliance; other raters' labels; any run timestamp | Absence check over all keys and values of the manifest |
| P7 | Determinism | Same inputs give byte-identical packet bytes (sorted JSON keys, UTF-8, `\n` line ends) | Rebuild twice; equal SHA-256 |
| P8 | Packet hash | Record the SHA-256 of the packet JSONL in `engineering/provenance/HUMAN_PACKET_FINAL_<date>.json`, together with the order hash, source-trace hashes and the code commit | Recorded before any distribution |
| P9 | Assignment record | One assignment per pseudonym (R1, R2): the packet hash given, the date given, and the rater-copy hash. Assignment hash = SHA-256 of the canonical JSON of all assignments | Recorded before annotation |
| P10 | Independent copies | Each rater gets their own copy, with identical content and order (the same packet hash). Raters never see each other's files. The adjudicator gets only flagged items, plus both raters' labels and notes **after** the adjudicator's independent first label | Copy hash equals the packet hash; adjudicator packet built only from the frozen trigger |
| P11 | Supersession | The old packets are retained, marked SUPERSEDED (positional leakage) and never distributed | Provenance note |
| P12 | Submission template | Per row: `blind_id`, `label` ∈ {disclosed, not_disclosed, partial, cannot_tell, abstain}, `uncertainty_flag` (true/false), `confidence` (0–1 or blank), `note` (optional) | Validated on import |

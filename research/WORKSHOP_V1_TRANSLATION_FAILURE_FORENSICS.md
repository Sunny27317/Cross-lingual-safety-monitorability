# Workshop-v1 translation failure forensics

> **Superseded (note added 2026-10-06; original text below unchanged).** This record
> describes an earlier state: 2 failure records, a huggingface-hub drift, and the old
> authorization. The current account is `research/WORKSHOP_V1_TRANSLATION_FORENSIC_REVIEW.md`:
> 6 records for 3 tasks, the batching root cause, amendment D-TR-1–6, and the amended
> authorization.


This record is technical only. Translation text and scientific outcomes were not inspected.

## Observed state

The output directory contains two immutable technical failure records and no successful translation records. No translator process could be inspected from the restricted diagnostic sandbox (`ps`/`pgrep` are unavailable there); the launcher progress state is consistent with an exited or externally interrupted run after two task failures. The records are preserved byte-for-byte.

| failure record | task | stage | exception | record SHA-256 |
|---|---|---|---|---|
| `translation-failure-translation-00170e43626fcaa1d39a8533d014410534003b9ad395b065c78af56bea08d79f-attempt-1.json` | `translation-00170e43626fcaa1d39a8533d014410534003b9ad395b065c78bea08d79f` | decoding/postprocessing completeness check | `ValueError: incomplete translated chunks` | `0d8e8f4eafc76af08adb1c35f1e0901d8ec4028528361288a4eb4dc993deebeb` |
| `translation-failure-translation-003155f2a8df62c39d8d8361e305291ed6d1986a9d4c51c2fd0c8122b49bb5c6-attempt-1.json` | `translation-003155f2a8df62c39d8d8361e305291ed6d1986a9d4c51c2fd0c8122b49bb5c6` | decoding/postprocessing completeness check | `ValueError: incomplete translated chunks` | `67effda247bfcc0ba2a3d166208b8db35d7e7eab03a6c3116013ad91f767fdbb` |

Both records show source hash lineage verified before translation, CPU/float32, attempt 1, and no persisted translated text/chunk metadata. The exception is raised at `_translate_task`'s final output-completeness guard after preprocessing, generation, decoding, and postprocessing return; the persisted record does not distinguish which of those returned an incomplete result. Persistence of the failure record itself succeeded. No partial scientific output or temporary file was found.

The prior tokenizer-language-tag bug is not implicated: the failing path uses `IndicProcessor.preprocess_batch(... src_lang='urd_Arab', tgt_lang='eng_Latn')` and the corrected prefixed source-token counter. The failure occurs after that path.

## Current runtime finding

The current environment reports `huggingface-hub==2.1.1`, while the frozen runtime contract requires `0.36.2`. Transformers 4.51.3 rejects this combination at import time. The launcher preflight now detects this drift and fails closed. This is an engineering/runtime blocker; it does not change the scientific contract. The two existing failure records were created before this diagnostic change and are not rewritten.

No evidence indicates OOM, duplicate model loading, source hash mismatch, or an atomic-write corruption. Exact memory/process status requires the investigator's normal macOS Terminal because process enumeration is restricted in this sandbox.

## Recovery boundary

The existing authorization remains valid only after the frozen runtime is restored and preflight passes. The two failure artifacts remain technical failures; `--resume` may retry only those technical failures and absent tasks. Successful records, if any later appear, are immutable and skipped. No content-based retry or fallback is permitted.

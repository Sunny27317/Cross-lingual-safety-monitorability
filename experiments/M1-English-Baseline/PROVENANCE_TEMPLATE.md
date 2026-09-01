# Provenance record — TEMPLATE

This is the shape of the `PROVENANCE.md` that `clsm.provenance.write_provenance`
generates next to each authorized run's `manifest.json`. It is filled from the **live
environment** at run time. An experiment is **invalid** without a complete manifest
(`REPRODUCIBILITY.md` §8).

Every `<…>` below is captured automatically; nothing is hand-entered.

```
# Provenance — <experiment_id, e.g. M1-en-hint-baseline-20260915-a1b2c3d>

- **experiment_id**: <...>
- **git_commit**: <full SHA of HEAD at run time>
- **git_state**: <clean | dirty | unknown>
- **timestamp_utc**: <ISO 8601>
- **python_version**: <e.g. 3.11.9>
- **os**: <platform.platform()>
- **cpu**: <processor / machine>
- **gpu**: <e.g. "1x NVIDIA L4" | "not available (torch not installed)">
- **cuda_version**: <e.g. 12.1 | null>
- **vllm_version**: <e.g. 0.6.3.post1 | null>
- **torch_version**: <e.g. 2.4.0 | null>
- **transformers_version**: <e.g. 4.45.2 | null>
- **datasets_version**: <... | null>
- **pydantic_version**: <...>
- **numpy_version**: <...>
- **model_id**: deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
- **model_revision**: <exact commit hash used>
- **tokenizer_revision**: <exact commit hash used>
- **dataset_id**: cais/mmlu:all:test
- **dataset_revision**: <HF dataset revision hash | null if unpinned — must be pinned for a real run>
- **config_hash**: <sha256 of the fully-resolved ExperimentConfig>
- **prompt_template_version**: v1_2026-09-01
- **prompt_template_sha256**: <...>
- **cue_type**: suggested_wrong_answer
- **cue_version**: v1_2026-09-01
- **cue_template_sha256**: <sha256 of the frozen hint text>
- **cue_target_rule**: hash_over_incorrect_indices
- **hint_seed**: 20260901
- **decoding**: <full decoding config dict: temperature, top_p, max_new_tokens, k, seeds, …>
- **seeds**: [0,1,2,3,4,5,6,7,8,9]
- **bootstrap_seed**: 20260901
- **code_path**: <path to the installed clsm package>
- **output_path**: <path to this run's output directory>
- **extra**: { n_items, n_exclusions, n_generations, n_disclosure_calls }
```

## Not captured automatically (record by hand in the run's README addendum)

- The exact `pip freeze` / `uv.lock` hash used (attach the lockfile).
- GPU driver version (if not surfaced by torch).
- The human disclosure-audit annotators (by id), their κ, and the adjudication log.
- The §7a checklist outcome that locked the disclosure-judge model.

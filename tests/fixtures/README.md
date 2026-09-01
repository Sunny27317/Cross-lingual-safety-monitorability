# tests/fixtures/

**Synthetic TEST DATA only.** Nothing here is real MMLU, a real model output, or a real
result. These files exist so the offline test suite can exercise the harness without
downloading anything.

- `mmlu_mini.jsonl` — hand-written MCQ items in two fake subjects (`test_math`,
  `test_logic`). Some rows are intentionally malformed to test exclusion handling.
  The questions are trivial and invented; do not treat them as a benchmark.

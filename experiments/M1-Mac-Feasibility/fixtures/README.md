# experiments/M1-Mac-Feasibility/fixtures/

**Synthetic INFRASTRUCTURE-ONLY data. Not a scientific dataset.**

- `smoke_questions.jsonl` — 5 hand-written, trivial general-knowledge MCQ items (capital
  cities, arithmetic, basic science, color mixing, ocean geography). Each item has an
  `id`, a `question`, 4 lettered `choices`, a `correct_answer` letter, a `hint_target`
  letter (always a wrong option, never equal to `correct_answer`), and a `note` field
  restating that the item is synthetic and infrastructure-only.

**Purpose:** exercise the Track-A feasibility runner's plumbing — prompt
formatting, the control/treatment pipeline, answer extraction, and reasoning/trace
capture — per `experiments/M1-Mac-Feasibility/EXPERIMENT_SPEC.md` §5 and §8. Not for
hypothesis testing, not comparable to MMLU or GPQA, and never to be cited as evidence
about model behavior, cross-lingual monitorability, or anything else scientific.

**Not MMLU or GPQA.** These items are invented specifically for this repository and
deliberately trivial (unlike the real Milestone-1 dataset, `configs/milestone1/
dataset.yaml`, which is unaffected by anything in this directory). No dataset was
downloaded to create this file.

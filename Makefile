# Milestone-1 scaffold — local validation only. NO target here runs inference or
# downloads a model/dataset.

.PHONY: help env test lint typecheck check config-validate clean reproduce

help:
	@echo "make env             - create the dev environment (uv or pip)"
	@echo "make test            - run the offline test suite (no model download)"
	@echo "make lint            - ruff"
	@echo "make typecheck       - mypy"
	@echo "make config-validate - load + validate configs/milestone1/pilot.yaml"
	@echo "make check           - lint + typecheck + test + config-validate"
	@echo "make reproduce       - BLOCKED: needs run authorization + the 'run' extras"

env:
	@echo "Preferred:  uv venv && uv pip install -e '.[dev]'"
	@echo "Fallback :  python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'"
	@echo "Lockfile :  uv lock   (commit uv.lock; it is the reproducibility record for core deps)"
	@echo "Run deps :  pip install -e '.[run]'   (ONLY after run authorization; pulls vllm+torch)"

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy

config-validate:
	python -c "from clsm.config import load_experiment_config; c=load_experiment_config('configs/milestone1/pilot.yaml'); print('OK', c.experiment_name, 'config_hash=', c.config_hash()[:12], 'judge.status=', c.judge.status)"

check: lint typecheck test config-validate

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache **/__pycache__ experiments/_runs

reproduce:
	@echo "BLOCKED. 'make reproduce' re-runs an authorized experiment from its config and"
	@echo "re-checks metrics within tolerance. It requires:"
	@echo "  1. the readiness PR merged"
	@echo "  2. the §7a disclosure-judge checklist done (configs/milestone1/judge.yaml status: RESOLVED)"
	@echo "  3. pip install -e '.[run]'  +  a GPU"
	@echo "  4. explicit human authorization to download DeepSeek-R1-Distill-Qwen-7B + MMLU"
	@exit 1

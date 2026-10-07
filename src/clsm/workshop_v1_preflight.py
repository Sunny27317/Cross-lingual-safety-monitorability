"""Read-only Workshop-v1 preflight. Default fails closed; no executor exists."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from clsm.workshop_v1.config import load_study
from clsm.workshop_v1.population import DatasetSnapshot, Population
from clsm.workshop_v1.preflight import ReviewBundle, Stage, preflight
from clsm.workshop_v1.records import GenerationRecord


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, default=Path("configs/workshop_v1/study.yaml"))
    parser.add_argument("--stage", type=Stage, choices=list(Stage), default=Stage.GENERATION)
    parser.add_argument("--output", type=Path, default=Path("experiments/_runs/workshop-v1-unresolved"))
    parser.add_argument("--expected-commit")
    parser.add_argument("--expected-study-hash")
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--population", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument(
        "--source-generations", type=Path, help="JSONL, only for post-generation stage checks"
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        study = load_study(root / args.config)
        snapshot = (
            DatasetSnapshot.model_validate_json((root / args.snapshot).read_text()) if args.snapshot else None
        )
        population = (
            Population.model_validate_json((root / args.population).read_text()) if args.population else None
        )
        review = ReviewBundle.model_validate_json((root / args.review).read_text()) if args.review else None
        generations = None
        if args.source_generations:
            generations = tuple(
                GenerationRecord.model_validate_json(line)
                for line in (root / args.source_generations).read_text().splitlines()
                if line.strip()
            )
        report = preflight(
            study,
            root=root,
            output=args.output,
            stage=args.stage,
            expected_commit=args.expected_commit,
            expected_study_hash=args.expected_study_hash,
            snapshot=snapshot,
            population=population,
            review=review,
            generations=generations,
        )
        print(report.model_dump_json(indent=2))
    except (ValueError, OSError, yaml.YAMLError) as exc:
        print(json.dumps({"execution_ready": False, "blockers": [f"invalid preflight inputs: {exc}"]}))
    # Deliberately never exits successfully as a scientific authorization mechanism.
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Mechanical pre-unseal readiness checks.

The validator checks existence, hashes and stage metadata only. It does not
open result distributions or report labels. It is intentionally conservative:
an absent/ambiguous stage is BLOCKED rather than inferred complete.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_file(root: Path, path: str, expected: str | None = None) -> dict[str, Any]:
    target = root / path
    present = target.is_file()
    actual = sha256(target) if present else None
    return {"path": path, "present": present, "sha256": actual,
            "hash_match": expected is None or actual == expected}


def validate(root: Path) -> dict[str, Any]:
    required = {
        "generation_stage_seal": (
            "engineering/provenance/GENERATION_STAGE_RETROSPECTIVE_TECHNICAL_VERIFICATION_SEAL_2026-10-07.json"
        ),
        "translation_stage_seal": "experiments/_runs/workshop-v1-translation/translation_stage_seal.json",
        "direct_judge_stage_seal": "engineering/workshop_v1_direct_judge_stage_seal_v2.json",
        "translated_judge_stage_seal": "engineering/workshop_v1_translated_urdu_judge_stage_seal.json",
        "translated_judge_post_qc": "engineering/workshop_v1_translated_urdu_judge_post_qc.json",
        "analysis_contract": "engineering/workshop_v1_analysis_contract.json",
        "analysis_freeze": "engineering/provenance/ANALYSIS_CODE_FREEZE_2026-10-04.json",
    }
    checks = {name: check_file(root, path) for name, path in required.items()}
    human_blockers = [
        "ORPI/institutional determination is required before human annotation",
        "human labels do not yet exist",
    ]
    translation_seal = checks["translation_stage_seal"]["present"]
    generation_seal = checks["generation_stage_seal"]["present"]
    direct_seal = checks["direct_judge_stage_seal"]["present"]
    translated_seal = checks["translated_judge_stage_seal"]["present"]
    translated_qc = checks["translated_judge_post_qc"]["present"]
    analysis = checks["analysis_contract"]["present"] and checks["analysis_freeze"]["present"]
    result = {
        "schema_version": "workshop-v1-pre-unseal-validator/1",
        "scientific_content_inspected": False,
        "checks": checks,
        "automated_pipeline_unseal_readiness": (
            "READY"
            if (
                generation_seal and translation_seal and direct_seal and translated_seal
                and translated_qc and analysis
            )
            else "BLOCKED"
        ),
        "full_paper_human_validated_readiness": "BLOCKED",
        "human_blockers": human_blockers,
        "known_errata_required": True,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(validate(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

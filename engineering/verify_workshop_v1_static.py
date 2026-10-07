"""Fail-closed, metadata-only Workshop-v1 verification entry point."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED = (
    "engineering/workshop_v1_stage_hash_registry_v2.json",
    "engineering/WORKSHOP_V1_ALL_STAGE_TECHNICAL_STATUS_2026-10-07.json",
    "engineering/workshop_v1_translated_urdu_judge_stage_seal.json",
    "engineering/workshop_v1_translated_urdu_judge_post_qc.json",
    "engineering/WORKSHOP_V1_RATER_PACKET_REGENERATION_2026-10-07.json",
    "research/CANONICAL_SOURCE_RECONCILIATION_2026-10-07.md",
)


def main() -> None:
    root = Path.cwd()
    missing = [path for path in REQUIRED if not (root / path).is_file()
               ]
    if missing:
        raise SystemExit(f"FAIL_CLOSED missing static artifacts: {missing}")
    for path in REQUIRED:
        if path.endswith(".json"):
            json.loads((root / path).read_text(encoding="utf-8"))
    stage = json.loads((root / REQUIRED[1]).read_text(encoding="utf-8"))
    if stage.get("scientific_content_inspected") is not False:
        raise SystemExit("FAIL_CLOSED technical status is not outcome-blind")
    rater = json.loads((root / REQUIRED[4]).read_text(encoding="utf-8"))
    if rater.get("count") != 312 or rater.get("annotation_authorized") is not False:
        raise SystemExit("FAIL_CLOSED rater packet provenance mismatch")
    print("WORKSHOP_V1_STATIC_VERIFICATION=PASS")
    print("SCIENTIFIC_EXECUTION=NONE")


if __name__ == "__main__":
    main()

"""Non-executing Workshop-v1 translation and judge call planner.

This module creates only deterministic lineage plans. It never loads a model,
translator, or scientific output.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

from clsm.downstream.contracts import object_hash

ROOT = Path(__file__).resolve().parents[3]
MODELS = ("Qwen/Qwen3-1.7B", "google/gemma-3-4b-it")
SAMPLES = (0, 1, 2)
PILOT_MANIFEST = "063a530e9ff5c91dfff9baaa0253327c915172998ff90796ded3c9300ee357a9"
MAIN_MANIFEST = "576a991f9f96e1bad95d1775bc1f177604e13c8903416befee75dd2d3f277f6f"
CUE_B_MANIFEST = "e18b48b6be7c2fa86df1ff00712943ac5cee218977a3bb6ee05d8bdd949b9891"
RETAINED_MISSING = ("9-1065", "Qwen/Qwen3-1.7B", "cue_a", 0)


@dataclass(frozen=True)
class PlannedCall:
    plan_id: str
    source_item_id: str
    source_row_hash: str
    model: str
    language: Literal["en", "ur"]
    condition: Literal["cue_a", "cue_b"]
    sample_index: int
    trace_artifact_id: str
    translation_artifact_id: str | None
    judge_stage: Literal["english_direct", "urdu_direct", "urdu_translated_then_judged"]


def _manifest(root: Path, name: str) -> list[dict[str, str]]:
    value = json.loads((root / "engineering" / name).read_text())
    return list(value["items"])


def _pilot_ids(root: Path) -> set[str]:
    return {x["source_item_id"] for x in _manifest(root, "workshop_v1_pilot_manifest.json")}


def _trace_id(row: dict[str, str], model: str, language: str, condition: str, sample: int) -> str:
    return "planned-trace-" + object_hash([
        row["source_item_id"], row["row_hash"], model, language, condition, sample,
    ])


def _translation_id(trace_id: str) -> str:
    return "planned-translation-" + object_hash([trace_id, "urd_Arab", "eng_Latn"])


def build_plans(root: Path = ROOT) -> tuple[tuple[PlannedCall, ...], tuple[PlannedCall, ...]]:
    main = {x["source_item_id"]: x for x in _manifest(root, "workshop_v1_main_manifest.json")}
    cue_b = {x["source_item_id"]: x for x in _manifest(root, "workshop_v1_cue_b_manifest.json")}
    pilot = _pilot_ids(root)
    if not cue_b.keys() <= main.keys():
        raise ValueError("Cue-B population is not contained in main population")
    calls: list[PlannedCall] = []
    for model in MODELS:
        for condition, rows in (("cue_a", main), ("cue_b", cue_b)):
            for row in rows.values():
                if row["source_item_id"] in pilot:
                    raise ValueError("pilot ID entered a main judge plan")
                for sample in SAMPLES:
                    for language, stage in (("en", "english_direct"), ("ur", "urdu_direct")):
                        if (row["source_item_id"], model, condition, sample) == RETAINED_MISSING and language == "ur":
                            continue
                        trace = _trace_id(row, model, language, condition, sample)
                        calls.append(PlannedCall(
                            plan_id="judge-" + object_hash([trace, stage]),
                            source_item_id=row["source_item_id"],
                            source_row_hash=row["row_hash"], model=model,
                            condition=cast(Literal["cue_a", "cue_b"], condition), sample_index=sample,
                            trace_artifact_id=trace, translation_artifact_id=None,
                            language=cast(Literal["en", "ur"], language),
                            judge_stage=cast(Literal["english_direct", "urdu_direct"], stage),
                        ))
                    ur_trace = _trace_id(row, model, "ur", condition, sample)
                    if (row["source_item_id"], model, condition, sample) == RETAINED_MISSING:
                        continue
                    calls.append(PlannedCall(
                        plan_id="judge-" + object_hash([ur_trace, "urdu_translated_then_judged"]),
                        source_item_id=row["source_item_id"], source_row_hash=row["row_hash"], model=model,
                        language="ur", condition=cast(Literal["cue_a", "cue_b"], condition),
                        sample_index=sample, trace_artifact_id=ur_trace,
                        translation_artifact_id=_translation_id(ur_trace),
                        judge_stage="urdu_translated_then_judged",
                    ))
    direct = tuple(x for x in calls if x.judge_stage != "urdu_translated_then_judged")
    translated = tuple(x for x in calls if x.judge_stage == "urdu_translated_then_judged")
    return direct, translated


def validate_plans(root: Path = ROOT) -> dict[str, Any]:
    direct, translated = build_plans(root)
    all_calls = direct + translated
    if len(direct) != 1871 or len(translated) != 935 or len(all_calls) != 2806:
        raise ValueError("frozen judge-plan counts do not match 1871/935/2806")
    if len({x.plan_id for x in all_calls}) != len(all_calls):
        raise ValueError("duplicate judge plan IDs")
    if len({x.translation_artifact_id for x in translated}) != len(translated):
        raise ValueError("duplicate translation lineage IDs")
    if any(x.language != "ur" or x.condition not in {"cue_a", "cue_b"} for x in translated):
        raise ValueError("illegal translated path")
    if any(x.translation_artifact_id is not None for x in direct):
        raise ValueError("direct path carries translation lineage")
    if any(x.source_item_id in _pilot_ids(root) for x in all_calls):
        raise ValueError("pilot/main contamination")
    return {
        "english_direct": sum(x.language == "en" for x in direct),
        "urdu_direct": sum(x.language == "ur" for x in direct),
        "translated_urdu": len(translated), "total_judge": len(all_calls),
        "translation": len(translated), "plan_hash": object_hash([asdict(x) for x in all_calls]),
        "scientific_execution": False,
    }


def checkpoint_action(path: Path, *, plan_id: str, study_hash: str) -> Literal["RUN", "SKIP", "RETRY"]:
    """Decide resume behavior without overwriting or interpreting scientific output."""
    if not path.exists():
        return "RUN"
    value = json.loads(path.read_text())
    if value.get("plan_id") != plan_id or value.get("study_hash") != study_hash:
        raise ValueError("checkpoint lineage/study hash changed")
    if value.get("immutable") is not True:
        raise ValueError("existing checkpoint is not immutable")
    return "SKIP" if value.get("technical_status") == "SUCCESS" else "RETRY"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", required=True)
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps(validate_plans(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

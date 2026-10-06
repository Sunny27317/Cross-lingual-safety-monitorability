"""Non-generative Attempt-2 preparation and governed launch wrapper."""

from __future__ import annotations

import argparse
import json
import socket
from pathlib import Path
from typing import Any, cast

from clsm.workshop_v1.config import load_study
from clsm.workshop_v1.frozen_validation import validate_frozen_inputs
from clsm.workshop_v1.local_runtime import verify_local
from clsm.workshop_v1.main_generation import execute
from clsm.workshop_v1.workload import generation_config_hash, workload_summary

ROOT = Path(__file__).resolve().parents[3]
ATTEMPT_2 = ROOT / "experiments/_runs/workshop-v1-main-attempt-2"
HASH = "7b00e996320ccb76571b2a9af5723940eee084aa07b4097ec7b9ceba51ce0fec"


def socket_check() -> dict[str, Any]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return {"status": "PASS", "port": sock.getsockname()[1]}
    except OSError as exc:
        return {"status": "FAIL", "errno": exc.errno, "error": str(exc)}
    finally:
        sock.close()


def preflight(root: Path = ROOT, output: Path = ATTEMPT_2) -> dict[str, Any]:
    frozen = validate_frozen_inputs(root)
    config = generation_config_hash(root)
    summary = workload_summary(root)
    specs = [slot.spec for slot in load_study(root / "configs/workshop_v1/study.yaml").models]
    for spec in specs:
        if spec is None:
            raise ValueError("incomplete generator specification")
        verify_local(spec)
    files = list(output.iterdir()) if output.exists() else []
    generation_count = cast(int, summary["generation"])
    socket_result = socket_check()
    result = {
        "preflight": (
            "PASS" if config["hash"] == HASH and generation_count == 3312 and not files else "FAIL"
        ),
        "socket": socket_result, "generation_config_hash": config["hash"],
        "expected_calls": generation_count, "output_directory": str(output),
        "output_empty": not files, "frozen_inputs": frozen,
        "attempt_1_directory": str(root / "experiments/_runs/workshop-v1-main"),
        "model_inference_performed": False,
    }
    if socket_result["status"] != "PASS":
        result["preflight"] = "FAIL"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ATTEMPT_2)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(args.root.resolve(), args.output.resolve()), indent=2))
        return
    if not args.execute or args.authorization is None:
        raise SystemExit("specify --preflight, or --execute --authorization PATH")
    print(
        json.dumps(
            execute(args.root.resolve(), args.output.resolve(), args.authorization.resolve()), indent=2
        )
    )


if __name__ == "__main__":
    main()

"""Safe synthetic smoke check and annotation schema export. No scientific input paths."""

from __future__ import annotations

import argparse
import json

from clsm.downstream.annotation import Annotation
from clsm.downstream.fixtures import fixture_report
from clsm.downstream.reporting import deterministic_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("fixture-check", "annotation-schema"))
    args = parser.parse_args()
    if args.mode == "fixture-check":
        print(deterministic_report(fixture_report()), end="")
    else:
        print(json.dumps(Annotation.model_json_schema(), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

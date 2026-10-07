"""Hash a downloaded IndicTrans2 artifact directory without loading it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-id", default=None)
    parser.add_argument("--revision", default=None)
    args = parser.parse_args()
    if not args.directory.is_dir():
        raise SystemExit("artifact directory does not exist")
    files = []
    for path in sorted(
        p for p in args.directory.rglob("*") if p.is_file() and ".cache" not in p.parts
    ):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({
            "path": str(path.relative_to(args.directory)), "sha256": digest,
            "bytes": path.stat().st_size,
        })
    payload = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    result = {
        "schema_version": "indictrans2-artifact-inventory/1",
        "model_id": args.model_id,
        "revision": args.revision,
        "files": files,
        "inventory_sha256": hashlib.sha256(payload).hexdigest(),
        "model_loaded": False,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

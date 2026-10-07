#!/usr/bin/env bash
set -euo pipefail

repo_root="${REPO_ROOT:-$(pwd)}"
bundle_path="${1:-$HOME/workshop-v1-all-refs.bundle}"
cd "$repo_root"
git bundle create "$bundle_path" --all
shasum -a 256 "$bundle_path" > "$bundle_path.sha256"
git bundle verify "$bundle_path"
echo "bundle created: $bundle_path"

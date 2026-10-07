#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 DESTINATION_DIRECTORY" >&2
  exit 2
fi
dest="$1"
[[ -d "$dest" ]] || { echo "destination is not a mounted directory: $dest" >&2; exit 3; }
[[ -w "$dest" ]] || { echo "destination is not writable: $dest" >&2; exit 4; }

repo_root="${REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
archive="${SCIENTIFIC_ARCHIVE:-$HOME/clsm-workshop-v1-scientific-runs-2026-10-07.tar.gz}"
bundle="${GIT_BUNDLE:-$HOME/clsm-full-repository-FINAL-2026-10-07.bundle}"
private_docs="${PRIVATE_RECOVERY_DOCS:-$HOME/clsm-private-recovery-docs-2026-10-07.tar.gz}"
for source in "$archive" "$bundle" "$private_docs"; do
  [[ -f "$source" ]] || { echo "missing backup source: $source" >&2; exit 5; }
done

cp -p "$archive" "$bundle" "$private_docs" "$dest/"
shasum -a 256 "$archive" > "$dest/$(basename "$archive").sha256"
shasum -a 256 "$bundle" > "$dest/$(basename "$bundle").sha256"
shasum -a 256 "$private_docs" > "$dest/$(basename "$private_docs").sha256"
(cd "$dest" && shasum -a 256 -c "$(basename "$archive").sha256" && shasum -a 256 -c "$(basename "$bundle").sha256" && shasum -a 256 -c "$(basename "$private_docs").sha256")
echo "verified copies in $dest; originals were not removed"

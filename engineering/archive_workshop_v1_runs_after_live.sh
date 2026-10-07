#!/usr/bin/env bash
set -euo pipefail

# Deliberately refuses to run unless the investigator explicitly confirms the
# live boundary has ended. This script never deletes the source directory.
if [[ "${1:-}" != "--after-live-run" ]]; then
  echo "refusing: pass --after-live-run only after the judge process exits" >&2
  exit 2
fi
repo_root="${REPO_ROOT:-$(pwd)}"
cd "$repo_root"
if pgrep -af 'translated_judge_launcher|translator_launcher' >/dev/null 2>&1; then
  echo "refusing: a scientific process is still present" >&2
  exit 3
fi
archive_root="${ARCHIVE_ROOT:-$HOME/workshop-v1-archive-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$archive_root"
find experiments/_runs -type f -print0 | sort -z | xargs -0 shasum -a 256 > "$archive_root/runs.sha256"
tar --xattrs --acls -czf "$archive_root/experiments-runs.tar.gz" experiments/_runs
shasum -a 256 "$archive_root/experiments-runs.tar.gz" > "$archive_root/experiments-runs.tar.gz.sha256"
tar -tzf "$archive_root/experiments-runs.tar.gz" >/dev/null
echo "archive created: $archive_root"

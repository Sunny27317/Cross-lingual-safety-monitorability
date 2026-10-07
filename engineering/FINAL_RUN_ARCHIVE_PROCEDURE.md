# Final run archive procedure

Do not run while a judge or translator process is alive. Run only after the
process exits and the investigator releases the archive boundary.

```bash
set -euo pipefail
cd "$REPO_ROOT"
pgrep -af 'translated_judge_launcher|translator_launcher' && exit 1 || true
ARCHIVE_ROOT="$HOME/workshop-v1-archive-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$ARCHIVE_ROOT"
find experiments/_runs -type f -print0 | sort -z | xargs -0 shasum -a 256 > "$ARCHIVE_ROOT/runs.sha256"
tar --xattrs --acls -czf "$ARCHIVE_ROOT/experiments-runs.tar.gz" experiments/_runs
shasum -a 256 "$ARCHIVE_ROOT/experiments-runs.tar.gz" > "$ARCHIVE_ROOT/experiments-runs.tar.gz.sha256"
tar -tzf "$ARCHIVE_ROOT/experiments-runs.tar.gz" >/dev/null
```

Copy the archive directory to two independent, access-controlled locations,
then compare the archive hash on both copies. Do not delete the local original
until both copies are readable and hash-identical.

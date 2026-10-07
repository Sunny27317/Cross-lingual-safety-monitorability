# Off-laptop copy commands (destination required)

Do not run these until the investigator chooses an approved destination. The
commands intentionally use placeholders and verify hashes after copying.

## External SSD/USB

```bash
DEST="/Volumes/<APPROVED_VOLUME>/workshop-v1-2026-10-07"
mkdir -p "$DEST"
cp "$HOME/clsm-workshop-v1-scientific-runs-2026-10-07.tar.gz" "$HOME/clsm-workshop-v1-scientific-runs-2026-10-07.tar.gz.sha256" "$DEST/"
cp "$HOME/clsm-full-repository-FINAL-2026-10-07.bundle" "$HOME/clsm-full-repository-FINAL-2026-10-07.bundle.sha256" "$DEST/"
cp "$HOME/clsm-private-recovery-docs-2026-10-07.tar.gz" "$HOME/clsm-private-recovery-docs-2026-10-07.tar.gz.sha256" "$DEST/"
(cd "$DEST" && shasum -a 256 -c clsm-workshop-v1-scientific-runs-2026-10-07.tar.gz.sha256 && shasum -a 256 -c clsm-full-repository-FINAL-2026-10-07.bundle.sha256 && shasum -a 256 -c clsm-private-recovery-docs-2026-10-07.tar.gz.sha256)
```

## Approved cloud storage/manual upload

Upload the same four files through the institution-approved client. Download
them to a fresh temporary directory and run the same two `shasum -a 256 -c`
commands before checking the laptop-return box. Never put credentials in this
repository or command history.

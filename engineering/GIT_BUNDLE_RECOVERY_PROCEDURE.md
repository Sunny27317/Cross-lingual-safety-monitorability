# Git bundle recovery procedure

Create the bundle after the live run exits, without rewriting history:

```bash
cd "$REPO_ROOT"
git bundle create "$HOME/workshop-v1-all-refs.bundle" --all
shasum -a 256 "$HOME/workshop-v1-all-refs.bundle" > "$HOME/workshop-v1-all-refs.bundle.sha256"
git bundle verify "$HOME/workshop-v1-all-refs.bundle"
```

Copy the bundle and checksum off-laptop. On a new machine:

```bash
git clone "$HOME/workshop-v1-all-refs.bundle" recovered-clsm
cd recovered-clsm
git bundle verify /path/to/workshop-v1-all-refs.bundle
git branch -a
git fsck --full
```

A bundle contains Git refs, not ignored run outputs, model weights, HF caches,
or external datasets. Archive those separately.

# New-machine recovery test (2026-10-07)

The Git bundle was verified and restored into a temporary clone without model
loading or scientific execution. The two Workshop-v1 branches were present in
the bundle. The scientific run archive was tar-listed and extracted into a
temporary directory; its file count matched the hash manifest (10,464 files).

After the archival technical commit is pushed, repeat this clean-machine test:

```bash
git clone https://github.com/Sunny27317/Cross-lingual-safety-monitorability.git clsm-recovered
cd clsm-recovered
git fetch --all --tags
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
make verify-workshop-v1
```

Restore the run archive and external model/dataset assets separately. Verify
every SHA-256 in the local recovery manifests before any stage is resumed.
This procedure does not run inference, translation, judging, annotation, or
analysis.

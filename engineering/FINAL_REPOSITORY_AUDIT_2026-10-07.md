# Final repository audit (2026-10-07)

## Scope

This audit inspected repository structure, refs, paths, manifests and file metadata. It did not inspect scientific labels, trace meaning, distributions, human labels or analysis results.

## Current branch

- Technical branch: `research/workshop-v1-post-translation-pipeline`
- Current pushed HEAD: `db043c3`
- Important analysis branch verified remotely at `1985cab` (`c35785c` V3 and `43621f6` commit binding are ancestors). It was not merged.

## Findings

- Raw experiment runs and model artifacts are ignored/local-only and are not staged.
- Several recovery and privacy notes remain local-only because they contain machine paths or private provenance.
- The metadata release scaffold excludes restricted text, reviewer information, binaries, credentials and results.
- No invalid symlinks were found in the repository scan.
- Public-history privacy exposures remain pending the separately authorized rewrite runbook.

## Recovery evidence

- Scientific run archive: `$HOME/clsm-workshop-v1-scientific-runs-2026-10-07.tar.gz`, verified SHA-256 recorded in its sidecar.
- Git bundle: `$HOME/clsm-full-repository-2026-10-07.bundle`, verified with `git bundle verify`.
- Private recovery docs archive: `$HOME/clsm-private-workshop-v1-docs-2026-10-07.tar.gz`.
- Off-device copies are not verified; laptop-return status remains NO.

## Required final actions

Copy the three archives to an approved external or cloud destination using
`engineering/copy_final_backups.sh`, verify hashes at the destination, then
complete the laptop-return checklist. Do not rewrite public history without
explicit investigator approval.

Local branch refs: 13
Untracked paths: 18
Symlinks found: 3
Files over 50 MiB: 4

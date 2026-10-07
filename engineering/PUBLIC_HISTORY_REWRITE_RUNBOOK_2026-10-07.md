# Public-history rewrite runbook — destructive, authorization required

Do not execute this runbook without explicit investigator authorization and a
verified private archive. It must be coordinated with collaborators because a
history rewrite requires force-with-lease updates and cannot erase forks,
clones, caches, release assets or external mirrors.

1. Preserve the current repository, all branches, tags, raw-run archive and
   reviewer packet in a private encrypted location. Record hashes.
2. Create a temporary mirror clone and enumerate every affected public ref.
3. Use `git filter-repo` in the mirror to remove
   `engineering/provenance/URDU_ITEM_EQUIVALENCE_REVIEW_PACKET.pdf` and replace
   reviewer-identifying strings with a neutral role token. Never print the
   identity or sensitive text in logs.
4. Run repository-wide scans for the PDF path, identity, emails, absolute
   machine paths and credentials. Verify the protected files are absent from
   every rewritten ref, while required private provenance remains in the
   encrypted archive.
5. Obtain investigator and collaborator approval, then update each affected
   remote ref with `git push --force-with-lease` (never blind `--force`).
6. Invalidate or replace GitHub releases, PR references and cached artifacts
   where possible; document that forks and existing clones cannot be remotely
   scrubbed.
7. Clone the rewritten repository afresh, run the privacy scan, verify branch
   heads and hashes, and retain the pre-rewrite bundle as rollback evidence.

This is a future remediation plan only. No history was rewritten here.

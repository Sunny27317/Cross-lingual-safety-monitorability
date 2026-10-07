# Workshop-v1 license and release audit

This is an engineering classification, not legal advice. License text and
dataset terms must be checked again before publication.

| Asset | Current classification | Release handling |
|---|---|---|
| OpenBookQA source/item text | release with attribution only if upstream terms permit | Prefer IDs, revision and hashes; do not redistribute item text while terms are unresolved |
| Urdu dataset derivative | unclear / requires license review | Keep snapshot private; publish source/revision/hash and transformation metadata |
| Qwen3-1.7B weights | re-downloadable, release with provider terms | Do not commit binaries; publish exact revision/hash and license link |
| Gemma-3-4B-it weights | re-downloadable, release with provider terms | Do not commit binaries; publish exact revision/hash and license link |
| Falcon judge weights | re-downloadable, release with provider terms | Do not commit binaries; publish exact revision/hash and license link |
| IndicTrans2 weights/toolkit | release with attribution/provider terms | Publish exact revision, toolkit commit and artifact hashes; do not commit weights |
| Generated traces/judge outputs | unclear / privacy and license review | Preserve private archive; release only approved derived metadata or redacted data |
| Native-review packet | should remain private | It contains item text and reviewer information; do not publish |
| Source code/configs | safe to release subject to dependency licenses | Publish after privacy/history remediation and provenance review |

The conservative public package is code, manifests containing IDs, frozen
configuration hashes, stage hashes and reproducibility instructions. It must
exclude item/question text, reviewer names/contact details, secrets and model
binaries unless a separate release review authorizes them.

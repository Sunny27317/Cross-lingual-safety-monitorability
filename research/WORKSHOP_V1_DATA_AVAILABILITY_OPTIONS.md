# Workshop-v1 data / artifact availability: three versions

No repository or archive exists yet. `[URL]`, `[DOI]` and `[COMMIT]` stay as placeholders
until they do. **Default: Version 3** (the dataset licence is unstated). Move to Version 2
or 1 only after the licence question is resolved.

**Dataset citation wording (all versions).** "Items are from OpenBookQA (Mihaylov et al.,
2018), via the Urdu release `large-traversaal/openbookqa_urdu_final` (revision
`e4186f6b`) from the UrduBench project (Shafique et al., 2026)."

## Version 1: full public release possible

- **Repository:** "Code, configurations, prompts, rubrics and all provenance records are
  available at [URL] (archived as [DOI], commit [COMMIT])."
- **Artifacts:** "We release all model rationales, judge outputs (raw and parsed),
  translations, and adjudicated native-reader labels. Individual rater labels are
  released under pseudonyms [if consent allows]."
- **Reproducibility:** "Every statistic can be recomputed from the released records with
  the archived analysis code (content hash `1671bc3c…`; B = 10,000, seed 0)."

## Version 2: partial release, due to dataset-licence uncertainty

- **Repository:** as in Version 1.
- **Artifacts:** "We release item identifiers and hashes, and model rationales, judge
  outputs, translations and adjudicated labels. Fields reproducing item text (question
  and options) are removed and can be reconstructed from the source dataset at the stated
  revision with the provided script."
- **Reproducibility:** "Rejoining the released records with the source dataset by
  identifier reproduces every statistic. Hashes verify the join."

## Version 3: code, hashes and identifiers only, with no redistributed item text (default)

- **Repository:** "Code, configurations, prompt and cue templates, rubrics, synthetic
  training material, ID-only item manifests and per-stage provenance records (hashes,
  authorizations, incident records) are available at [URL] ([DOI], commit [COMMIT])."
- **Artifacts:** "Because the dataset states no licence of its own, we do not
  redistribute item text or outputs that quote it. Model rationales, judge outputs and
  adjudicated labels are [available on request for verification / released after
  licence clarification]. Their SHA-256 hashes are published so that any later release
  can be verified."
- **Reproducibility:** "The pipeline can be re-run end to end from the source dataset at
  the stated revision. Generation is not bitwise reproducible on the hardware used, but
  every reported statistic is reproducible from the stored records by the archived
  analysis code."

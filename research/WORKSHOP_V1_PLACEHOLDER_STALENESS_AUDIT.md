# Placeholder and staleness audit of `paper/WORKSHOP_V1_PREPRINT.md` (2026-10-06)

**Method.** A read-only scan of the preprint at commit `b44636e` (it is unchanged on this branch).
No result was filled in.

## 1. Corrections (apply on review; the preprint is not edited tonight)

| Line(s) | Issue | Correction |
|---|---|---|
| 398–399 | Stale comment: "STATUS 2026-10-06: scientific translation IN PROGRESS…" | Remove. Translation is complete and sealed (`14175ab5…`) |
| 445 | `[[SEGMENTATION_VALIDATION]]` | Fill from `paper/WORKSHOP_V1_OUTCOME_BLIND_DRAFTS.md` §2.1 (C6 artifact `22372034…`) |
| 479 | `[[TRANSLATION_OUTCOME]]` | Fill with branch A (technical fact: 935/935) |
| 481 | `[[TRANSLATION_STAGE_HASH]]` | `14175ab596e667684352d7326824979212634f7bf5dfd583c271231ea34a65ce` |
| 486 | `[[PROVENANCE: byte-identical non-rationale inputs]]` | Fill from OUTCOME_BLIND_DRAFTS §2.1 |
| 488, 951 | `[[TRANSLATED_JUDGE_STAGE_HASH]]` | **Pending** (the stage is running) |
| 500 | `[[HUMAN_INPUT: auditor role; executed scope]]` | **Pending** (no auditor named) |
| 580–584 | **Stale §4.9 "Freeze" paragraph.** It presents `1671bc3c…` as the analysis implementation | Replace with `paper/WORKSHOP_V1_METHODS_FINAL.md` §4.17 item 4, plus the final freeze hash after commit |
| 587–596 | §4.10 lacks the D-TR amendment, decision C1, Record B, addendum V2 and the implementation freeze | Replace with METHODS_FINAL §§4.10 and 4.17 |
| 949–950 | Back-matter translation entry lists base and amendment hashes but no stage hash | Add translation stage `14175ab5…` and the effective configuration `106f366c…` |
| 952 | Analysis code "by content hash `1671bc3c…`" only | Add the final implementation freeze (`final_analysis.py`, frozen record) and the commit |
| 917–935 | Data-availability text claims item text is not redistributed | **Untrue while the review PDF is public.** Remediate first (release guard R-6/R-7) |
| 882–884 | Acknowledgment slot names the reviewer as "option A (named…)" | Keep the named option only with recorded consent |
| 1, 26 | Title says "Reasoning Traces"; the body says "rationale" | Investigator choice; defined in A1, so acceptable |

## 2. Checks with no issue found

| Check | Result |
|---|---|
| Wrong "2,807" figure | Not present in the preprint. It is in the decision pack (l. 98) and the post-generation audit (l. 318), both handled by the D-FA-3 erratum |
| Stale failure IDs ("10-220" as the runtime failure) | Not present |
| Old translation config presented as final | Not present (§4.7 lists base + amendment + effective) |
| "Generation governed by later D-PG decisions" | Not present. §4.10 states the D-PG decisions were fixed on 2026-10-04, "before any translation or annotation and before any judge output was examined" |
| "Framework existed before generation" | Not present (the framework is not described in the preprint; METHODS_FINAL §4.17 adds the correct statement) |
| TODO / TBD / FIXME / "results pending" | 0 |
| "preregistered" | 0 |
| "hidden" | 0 |

## 3. Release-time scan (all must return 0 in the posted text)

```
grep -nE '\[\[|\{\{|TODO|TBD|FIXME|<!--|placeholder|\[(UPPER|[A-Z_]{5,})\]' paper/<final>.md
grep -niE 'preregist|significan|prove[sd]? |demonstrat|equivalen|no difference|ground truth(?! )|hidden' paper/<final>.md
```

The second scan's hits must be negations or citations only, checked by hand.

## 4. Remaining result slots (not filled, by design)

21 distinct result-slot families (`[[R-…]]`), the abstract template, the Discussion branch
slots and the Conclusion template.

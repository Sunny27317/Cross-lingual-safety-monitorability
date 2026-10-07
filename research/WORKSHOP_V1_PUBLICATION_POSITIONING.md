# Workshop-v1 publication positioning (2026-10-07; no acceptance probabilities)

| Target | Fit now | Needs before submission | Main reviewer objection | Positioning sentence |
|---|---|---|---|---|
| **A. Workshop paper** (non-archival or archival; safety, multilingual NLP or evaluation workshops) | **Best realistic target** | Human labels and G; the single unseal; 4–6 pages; limitations up front | One judge, one language, small models | "A same-rationale measurement-validity check of an automated disclosure monitor on Urdu, with native readers as reference" |
| **B. Findings-style short paper** | Possible, if G is informative and κ is reasonable | A + translation audit (S4); ideally the prospective second judge; tight related work | Breadth (one language and one judge) | Same, plus "robust to a second, independent judge" only if that judge is run |
| **C. Expanded journal or main-track version** | Not with the current design | See below | — | "Cross-lingual validation of CoT disclosure monitors" |

**Recommendation for Workshop-v1.** Post a preprint once H exists and the release guard
passes. Submit to a **workshop** first. Move to a Findings-style venue only if the result is
clear and the second judge is run before unseal. Do not expand Workshop-v1 itself.

**Most valuable extensions, ranked by scientific value per unit of effort:**
1. **A second independent judge**, run prospectively on the same rationales. This directly
   addresses the largest weakness.
2. **More languages, including different scripts**, with native reader references. This
   converts the case study into evidence about cross-lingual monitoring.
3. **An English human reference.** It enables a human-validated English–Urdu disclosure
   comparison, and with it the "model vs monitor" decomposition in both languages.
4. **A paraphrase control**, with validated paraphrase fidelity. It makes R interpretable.
5. **Larger or frontier models**, and native reasoning channels where available.
6. **More tasks and cue wordings.** These separate the task and wording dependence of
   disclosure.

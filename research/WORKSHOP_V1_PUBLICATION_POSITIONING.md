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


## Workshop targets (classes; verify current calls before choosing — no venue information was refreshed online for this note)

- **AI-safety / oversight workshops** at major ML conferences (NeurIPS, ICLR, ICML), e.g.
  workshops on monitoring, interpretability or reliable/trustworthy ML. Fit: the monitor
  measurement-validity framing.
- **Multilingual and low-resource NLP workshops** at ACL / EMNLP / NAACL (e.g. the recurring
  multilingual-representation and low-resource-language workshops). Fit: the native-reader
  reference and the Urdu evaluation.
- **Evaluation / LLM-as-judge workshops** (e.g. on evaluation methodology or human
  evaluation in NLP). Fit: judge validation against human readers.

**Requirements for a Findings-style submission:**
- G with the human reference;
- κ reported with its CIs;
- the translation audit (S4) completed;
- ideally the prospective second judge, frozen before unseal;
- 4–8 pages with a tight related-work section;
- the claim ladder enforced.

**Future expanded version:**
- ≥ 3 languages including different scripts;
- ≥ 2 independent judges;
- an English human reference;
- a paraphrase control with validated fidelity;
- larger models and native reasoning channels;
- more tasks and cue wordings.

Candidate venues: TMLR or a main-track ACL/EMNLP paper.

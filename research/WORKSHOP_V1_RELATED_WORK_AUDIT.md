# Related-work audit and structure (written 2026-10-06; no browsing performed)

**Basis.** Reference metadata is checked against `literature/CITATION_VERIFICATION.md` and
`literature/WORKSHOP_V1_CITATION_AUDIT.md`. Nothing was re-verified online tonight. **Every
entry must be re-checked on the upload date** (arXiv version, venue, author list).

## 1. Proposed structure (preprint §2)

| Subsection | Works (preprint keys) | Role in our argument |
|---|---|---|
| Chain-of-thought and rationale monitoring | Korbak et al. 2025; Emmons et al. 2025; Yang et al. 2025 | Monitoring as oversight; monitorable ≠ monitored correctly |
| Faithfulness and disclosure | Turpin 2023; Lanham 2023; Chen 2025; Young 2026a/b/c; Zaman & Srivastava 2025; Xiong 2025 | Link 1 (disclosure) is incomplete; measurements depend on the classifier |
| Multilingual LLM evaluation | Zhao 2026; Qi 2025; Yazdani 2026 | CoT behavior varies by language |
| Cross-lingual safety | Yong 2023; Deng 2024 | Safety behavior differs by language; our question is narrower |
| Multilingual monitoring | Onyame 2026; Ercolano (repository) | Closest work. Its monitor is unvalidated in-language |
| Translation-mediated evaluation | Ercolano (repository); IndicTrans2 (Gala 2023) | Translate-then-monitor has precedent; we test it on fixed rationales |
| Urdu resources | Shafique 2026 (UrduBench); Mihaylov 2018 (OpenBookQA) | Item source |
| LLM-as-judge | Fu & Liu 2025; Zhou 2026; Doğruöz 2026; Zuo 2025 (Falcon-H1) | Judge reliability varies across languages |
| Human agreement and annotation | Cohen 1960 | κ |
| Sycophancy (Cue B) | Sharma 2023 | Motivation for the user-asserted cue |

## 2. Claim-alignment checks for known concerns

| Concern | Current preprint text | Status |
|---|---|---|
| DialectShift-Monitor is an unpublished repository | "…an open-source repository without an associated publication" (§2); cited as software, n.d. | **OK.** Keep it out of the novelty framing |
| arXiv:2603.20172 (Young 2026c) uses English-only classifiers, not native validation | "measured verbalization rates shift with the classifier used to score them"; "That English-only result motivates validating the scoring instrument…" | **OK** |
| Fleiss κ ≈ 0.3 belongs to Fu & Liu (arXiv:2505.12201), not 2605.28710 | The preprint cites Fu & Liu only qualitatively ("less consistent across languages"). 2605.28710 is not cited; no κ value is stated | **OK.** If a number is added later, attribute it to 2505.12201 and verify |
| Zhou arXiv:2607.14480: bias by response language, not "less accurate" | "scores can be systematically biased by the language of the text they evaluate" | **OK** |
| Falcon-H1 lists Urdu as a core language, which does not establish disclosure-judging quality | §4.6: "UrduBench measures task accuracy, not disclosure judgment; validating the judge for our construct is what this study measures" | **OK** |
| Urdu dataset licensing unresolved | §4.2 / back matter: "states no licence of its own… we release identifiers and hashes, not item text" | **Text OK, but currently untrue in fact.** The public repository contains the item-review PDF with item text (completion audit R1). Remediate before posting, or change this text |
| Onyame et al. 2026 details ("13 languages", "LLM judge validated by manual inspection", "no Urdu") | §2 | **Re-verify on the upload date.** It is our closest prior work; reviewers will check it |
| Doğruöz et al. 2026 venue ("Findings of EMNLP 2026, per arXiv comment") | References | **Re-verify the venue.** Keep "per arXiv comment" until it is confirmed |
| Self-citations / UNC names | `CITATION_VERIFICATION.md` §"Other UNC Charlotte names": TODO-UNVERIFIED | Not cited in the preprint. Keep it that way unless verified |

## 3. Gaps a reviewer may raise (no new citation is added tonight)

- Work on LLM-as-judge validation against human annotation in low-resource languages
  beyond Doğruöz 2026.
- Machine-translation evaluation of disclosure-relevant phrases (hedges, attributions).
- Urdu NLP evaluation beyond UrduBench.

Each needs a verified source before it is cited. Mark any candidate **TODO — UNVERIFIED**
until checked.

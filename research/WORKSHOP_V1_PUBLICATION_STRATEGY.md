# Workshop-v1 publication strategy

**2026-10-04, pre-results.** The literature statements below rely only on entries marked
VERIFIED in `literature/CITATION_VERIFICATION.md`. Venue names are given as examples of a
venue *type*. Current calls, deadlines, archival policies and preprint rules have **not**
been verified here and must be checked on the official sites before any plan is fixed.

---

## 1. Novelty reconstruction

### A. What prior work already does

- **Reasoning disclosure / hint verbalization.** Models often do not verbalize hints that
  changed their answers (Turpin et al., 2023; Chen et al., 2025; Young, 2026a, 2026b).
  Verbalization metrics conflate unfaithfulness with incompleteness (Zaman & Srivastava,
  2025).
- **Monitorability.** Framed as a fragile oversight opportunity (Korbak et al., 2025).
  Monitorability is distinguished from being monitored correctly (Yang et al., 2025).
  Monitors are hard to evade when reasoning is necessary (Emmons et al., 2025).
- **Measurement dependence.** Faithfulness rates depend on the classifier used
  (Young, 2026c; English only).
- **Multilingual monitoring.** CoT monitoring is fragile across 13 languages with an
  LLM judge validated by manual inspection; Urdu is not included (Onyame et al., 2026).
  Multilingual CoT performance, consistency and faithfulness have been studied (Zhao et
  al., 2026), as has the cost of controlling reasoning language (Qi et al., 2025).
- **Translation-based monitoring.** Translate-then-monitor is implemented for
  Latin-American Spanish varieties and Spanglish (Ercolano, n.d.; a repository, not a
  publication).
- **Cross-lingual safety.** Low-resource-language translation bypasses safety training
  (Yong et al., 2023; Deng et al., 2024).
- **Suggestion / sycophancy effects.** Models match user-stated beliefs (Sharma et al.,
  2023).
- **LLM-as-judge in multilingual settings.** Cross-language inconsistency (Fu & Liu,
  2025); a scarcity of human validation and over-reliance on a single judge (Doğruöz et
  al., 2026); scores biased by response language (Zhou et al., 2026).
- **Urdu evaluation.** UrduBench supplies Urdu reasoning benchmarks, including
  OpenBookQA (Shafique et al., 2026). CoT faithfulness with human evaluation exists for
  another lower-resource language, Persian (Yazdani et al., 2026).

### B. What this project specifically adds

On the **same** Urdu reasoning traces, with **identical inputs** for monitor and humans,
the project estimates how far an automated disclosure monitor's labels diverge from a
blinded, adjudicated native-reader reference. It does so alongside:

1. the apparent English–Urdu difference in automated rates on the same items;
2. a same-trace translate-then-monitor contrast with a translation audit;
3. two cue sources, for two model families.

All of this follows a prespecified, dated analysis plan.

### C. What this project does NOT establish

- Monitor behavior for other languages, models, scales, judges or translators.
- Faithfulness or anything about internal computation.
- A language-specific mechanism for translation effects (no paraphrase control).
- English-side monitor validity (no English human reference).
- Statistical significance or confirmatory evidence.
- Safety failure in deployed systems.

### Strongest defensible statement

> "To our knowledge, and within the verified literature we reviewed, prior multilingual
> CoT-monitoring evaluations rely on LLM judges without a native-reader reference on the
> same traces. We provide such a reference for Urdu and use it to separate monitor
> divergence from trace content in an apparent cross-lingual disclosure gap."

Use the hedge "to our knowledge, within the literature we reviewed", or drop the first
sentence entirely. Never write "first".

### Related Work closing paragraph (inserted in the manuscript)

> Prior work establishes that reasoning often omits influences on its answers, that
> measured faithfulness depends on the scoring classifier, that chain-of-thought
> monitoring becomes less reliable across languages, and that LLM judges are less
> consistent and differently biased outside high-resource languages. What remains
> difficult to read from this work is *why* a monitor's disclosure rates differ across
> languages: in the multilingual evaluations we reviewed, the instrument and the object
> of measurement are not separated, because no native-reader reference is collected on
> the same traces. We contribute such a reference for Urdu. Native readers and the
> automated monitor label the same rationales with the same inputs, and the same
> rationales are also re-scored after translation, so an apparent cross-lingual gap can
> be decomposed into monitor divergence and differences in the text. Our scope is a
> single-language case study with two small models, one monitor and one translator. We
> claim no novelty for multilingual monitoring, for translate-then-monitor, or for the
> inclusion of Urdu as such.

---

## 2. Title candidates

**Conservative**
1. Validating an Automated Reasoning-Disclosure Monitor Against Native Urdu Readers
2. Monitor or Model? Native-Urdu Validation of Automated Disclosure Monitoring for
   Multilingual Reasoning Traces
3. Separating Monitor Divergence from Model Disclosure in Urdu Reasoning Traces
4. A Native-Reader Reference for Cross-Lingual Disclosure Monitoring: An Urdu Case Study
5. Measuring the Validity of LLM-Judge Disclosure Monitoring in Urdu

**Memorable but scientifically safe**
6. Same Trace, Different Reader: Disclosure Monitoring in English and Urdu
7. Who Missed the Hint? A Native-Reader Check on Cross-Lingual Disclosure Monitoring (use only if results show monitor under-labelling; directional)
8. Lost in Monitoring? Native Validation of Disclosure Labels for Urdu Reasoning
9. Reading the Reasoning Twice: Native and Automated Disclosure Labels in Urdu
10. Is It the Model or the Monitor? An Urdu Case Study in Disclosure Monitoring

**Workshop / conference oriented**
11. Native-Reader Validation of an LLM Monitor for Urdu Chain-of-Thought Disclosure
12. Translate-then-Monitor Under a Native Reference: An Urdu Case Study
13. Cross-Lingual Validity of Automated Disclosure Monitoring: Evidence from Urdu
14. Disclosure Monitoring Beyond English: A Same-Trace Native Validation in Urdu
15. Auditing an Automated Reasoning Monitor in a Lower-Resource Language

**Top 3**

| Title | What it signals |
|---|---|
| **#2** *Monitor or Model? …* | States the question; neutral on the answer. Fits any outcome branch |
| **#6** *Same Trace, Different Reader …* | Signals the key design move (same traces, different readers). Memorable for a workshop audience |
| **#4** *A Native-Reader Reference … : An Urdu Case Study* | Most conservative. "Case study" pre-empts the generalization criticism. Best if results are null or mixed |

**Avoid:** "Lost in Monitoring?" unless results actually show a monitor gap. **Choose
after results.**

---

## 3. Venue strategy (types; verify every specific call before acting)

### A. Realistic workshop venues

*Examples of the type:* multilingual/low-resource NLP workshops (e.g. LoResLM, verified to
exist in 2026); safety and responsible-LM workshops at ML conferences (e.g. SoLaR,
verified to exist in 2023); workshops on CoT/reasoning, evaluation or interpretability.

- **Fit:** high. Narrow, careful case study; measurement-validity framing.
- **Strengths:** native reference; clean design; transparency.
- **Weaknesses:** scope.
- **What would improve fit:** nothing required.
- **More languages/models needed?** No.
- **Preprint first:** usually compatible (check each workshop's policy).
- **Archival:** prefer **non-archival** workshops if a later expanded main-track version is
  planned.

### B. Specialized NLP or safety venues

*Examples of the type:* Findings tracks; special tracks on evaluation and resources; safety
or alignment workshops with archival proceedings.

- **Fit:** medium–high.
- **Strengths:** methodological contribution plus release.
- **Weaknesses:** one language.
- **What would improve fit:** a second language (ideally a different script or resource
  level) and an English human anchor.
- **More languages/models needed?** Likely.
- **Preprint first:** typically allowed under ACL-style anonymity rules (check the
  current policy).

### C. Main-track NLP venues

*Examples of the type:* ACL, EMNLP, NAACL, EACL via ACL Rolling Review.

- **Fit:** low–medium as is.
- **Weaknesses:** two small models, one language, descriptive statistics.
- **What would improve fit:** 3+ languages, 3+ models including a reasoning model, two
  judges, paraphrase control, English human anchor.
- **More languages/models needed?** Yes.

### D. Broader ML venues

*Examples of the type:* NeurIPS, ICLR, ICML main tracks.

- **Fit:** low as is. These need a generalizable method or result.
- **What would improve fit:** a general monitor-validation protocol with multi-language,
  multi-monitor evidence and a cost-effective validation recipe.
- **More languages/models needed?** Strongly.

### E. Journal extension

*Examples of the type:* TMLR (verified to exist as a venue); computational-linguistics or
language-resources journals.

- **Fit:** good for an **expanded** version: multiple languages, full release, extended
  reliability analysis.
- **Strength:** journals reward thoroughness and transparency, which this project
  already has.
- **Preprint first:** generally fine (check the policy).

---

## 4. CV / application wording (all states)

**Rule:** describe the state exactly. Never imply peer review that has not happened.

| State | Correct CV entry | Never write |
|---|---|---|
| A. In preparation | "[Name]. *[Title]*. Manuscript in preparation." | "forthcoming", "to appear", "under review" |
| B. Preprint posted | "[Name]. *[Title]*. arXiv:[ID], [year]. Preprint (not peer reviewed)." | Listing it under "Publications" without "preprint" |
| C. Submitted | "[Name]. *[Title]*. Submitted, [year]." Naming the venue is optional; follow the venue's anonymity norms | "accepted", "in press" |
| D. Under review | "[Name]. *[Title]*. Under review at [venue], [year]." Only when a review is actually in progress | Implying acceptance |
| E. Workshop accepted | "[Name]. *[Title]*. [Workshop name] at [Conference] [year] ([archival / non-archival])." | Listing it as a main-conference paper |
| F. Conference accepted | "[Name]. *[Title]*. In *Proceedings of [Conference] [year]*" (or "[Conference] [year], Findings") | Omitting "Findings"/"workshop" where applicable |

**Two-sentence research description**

- **CV:** "Investigated whether automated monitors of AI reasoning read lower-resource
  languages correctly, by comparing an LLM-based disclosure monitor against blinded
  native-Urdu readers on the same model-generated reasoning traces. Designed and executed
  a prespecified, fully provenance-tracked pipeline: 3,312 generations across two
  open-weight models, English and Urdu, direct and translated monitoring, and a
  312-trace human reference."
- **SOP:** "My recent project asks a measurement question that matters for AI oversight:
  when a reasoning monitor reports different results in Urdu than in English, is that
  the model or the monitor? I built a same-trace design with native-reader validation
  and prespecified analysis to separate the two, and I want to extend this toward
  validated multilingual oversight methods."
- **Professor outreach:** "I recently ran a prespecified study comparing an automated
  chain-of-thought disclosure monitor with native Urdu readers on the same traces, to
  separate monitor error from model behavior across languages. I'm interested in how
  your group's work on [topic] could inform validating oversight tools beyond English."

Use "ran" or "completed" only for stages actually completed at the time of writing.

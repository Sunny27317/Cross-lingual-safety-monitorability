# Workshop-v1 reviewer-proofing: three hostile reviews, defense matrix, red team

**2026-10-04. Pre-results.** Written from the manuscript and governance documents only. No
judge, translation or human output was opened. Any score-like language here is an
internal diagnostic, not a prediction of acceptance.

---

## Part 1 — Three hostile reviews

### Reviewer A — multilingual NLP

**Likely overall assessment.** "A careful, well-documented measurement study with a
sensible design. The scope (two small models, one language, one QA task) is too narrow
to say much about multilingual monitoring. It is a good workshop paper. A main-track
paper would need more languages."

**10 strongest criticisms**
1. Urdu is the only non-English language. There is no way to tell whether a gap is Urdu-
   specific, script-specific (Perso-Arabic) or general to lower-resource languages.
2. The Urdu items are translations, so translated text is confounded with language.
   "English vs Urdu" is really "original vs translated benchmark".
3. The prompt is not monolingual: the elicitation sentence and the `Final answer:`
   marker stay English inside the Urdu prompt.
4. Script share (≥ 0.50 Perso-Arabic characters) is a crude proxy for language
   compliance. It cannot tell Urdu from Arabic- or Persian-script output, or detect
   Hindi-like syntax.
5. One translator (IndicTrans2) with sentence-level segmentation may lose cross-sentence
   references, which is exactly where "as the reviewer said…" would be.
6. One judge, quantized to Q4_K_M. Quantization may hurt Urdu disproportionately.
7. The judge's instructions are English while the traces are Urdu, so `D_ur` measures
   cross-lingual reading, not monolingual Urdu monitoring.
8. Two raters is a thin human reference. There is no measure of how "native" each rater
   is, and no dialect or region information.
9. The UrduBench leaderboard score used to choose the judge measures task accuracy, not
   reading of reasoning or disclosure.
10. Code-switching is common in written Urdu, but no analysis treats it as a phenomenon
    rather than as noise.

**5 clarification questions**
1. How was the Urdu item translation produced (by machine, by humans, or both), and what
   did the native equivalence review check?
2. Does the judge see the Urdu question and options for Urdu traces, or English ones?
3. How are mixed-script segments handled in translation?
4. What were the raters' backgrounds (region, education in Urdu)?
5. Why OpenBookQA rather than a task with natively Urdu items?

**Claims they would object to.** Any "Urdu monitorability" generalization. Any statement
that a gap reflects "the Urdu language". Any implication that translate-then-monitor is
new.

**Missing controls they would mention.**
- A second non-English language, ideally one high-resource and one in a different
  script.
- Natively authored Urdu items.
- A second translator.
- An English human anchor.
- A paraphrase control.

**Strengths they would acknowledge.**
- Same-trace native reference.
- Native equivalence review of all 120 items.
- Identical inputs for judge and humans.
- Explicit no-truncation translation policy.
- Candid reporting of a mixed-language prompt.

**What would move them toward acceptance.**
- Wording that is careful about generalization.
- Reporting compliance distributions, not only the binary flag.
- Translation-audit counts.
- A clear statement that Urdu is a case study.

**What cannot be fixed without new experiments.** More languages, native items, a second
translator or judge, an English human reference, and a paraphrase control.

**What can be fixed now.**
- Scope wording.
- Making the prompt's mixed language explicit.
- Describing the compliance measure as script-based.
- Rater background reporting (from qualification records).
- Explicitly framing the study as a case study.

### Reviewer B — AI safety / interpretability

**Likely overall assessment.** "Asks the right question: is a monitoring gap the model or
the monitor? The construct is narrow (explicit acknowledgment of a hint), the models are
small, and the 'reasoning' is a prompted rationale, not a reasoning model's native
chain of thought. That limits the relevance to frontier monitoring."

**10 strongest criticisms**
1. These are prompted rationales from small instruction models, not native reasoning
   traces. Monitorability findings may not transfer to reasoning models.
2. The disclosure construct (explicit acknowledgment) is narrow. Safety-relevant
   monitoring targets intent, deception and reward hacking, not hint mentions.
3. Misleading-letter hints on science questions are artificial and low-stakes.
4. The monitor is a 7B open model, not the kind of frontier monitor actually deployed.
5. Without a paraphrase control, the translation results cannot show anything about
   monitor language limits.
6. Disclosure is not faithfulness. The paper must not imply that models "hide" anything.
7. The Cue-B subset is small (36 items), so source-dependent claims will be weak.
8. No analysis links disclosure to whether the answer actually followed the hint (the
   classic "conditional on switching" faithfulness score).
9. The judge sees the suggestion sentence, which could make it a keyword matcher.
10. The relevance of a 1.7B model's rationales to oversight of capable systems is
    unclear.

**5 clarification questions**
1. Is disclosure analysed conditional on the answer matching the suggestion?
2. How often do rationales mention the suggestion but get labelled `partial`?
3. Does the judge simply detect the suggestion's option letter?
4. Why not use Qwen's thinking mode, given its relevance to reasoning-model monitoring?
5. Would the conclusions change with a frontier-model judge?

**Claims they would object to.** "Monitorability" used without qualification.
"Unfaithful"/"hidden". Any safety-failure framing. Any extrapolation to frontier
monitors.

**Missing controls they would mention.**
- A conditional-on-adoption disclosure analysis.
- A stronger or frontier judge as comparison.
- A native-thinking condition.
- Higher-stakes cue types.

**Strengths they would acknowledge.**
- Clean separation of monitor validity from model behavior.
- Prespecified rules.
- Transparent governance, including documented failures.
- Native-reader reference.
- Honest decision not to claim mechanism.

**What would move them toward acceptance.**
- Framing as a measurement-validity case study.
- A clear statement of what "monitorability" means here.
- A discussion of the implications for monitor validation pipelines.
- An appendix of qualitative examples (carefully chosen and labelled).

**What cannot be fixed without new experiments.** Reasoning models with native thinking,
frontier judges, a richer construct, and higher-stakes cues.

**What can be fixed now.**
- Define "monitorability" operationally in the Introduction (done: verbalization plus
  monitor reading).
- Ban "hidden" and "faithfulness" language.
- The conditional-on-adoption breakdown. It is a cross-tab of existing variables, but
  it is not in the frozen plan, so it must be labelled exploratory if added after
  unsealing (see Part 2).

### Reviewer C — methods / statistics / reproducibility

**Likely overall assessment.** "Unusually transparent provenance and prespecification. The
statistics are descriptive by design, which is honest but limits what can be concluded.
Small cluster counts for Cue B and the human subset mean wide intervals. Generation code
was uncommitted at run time."

**10 strongest criticisms**
1. There are many intervals and no multiplicity handling. Some will exclude zero by
   chance.
2. A percentile bootstrap over 36 clusters (Cue B) may under-cover.
3. Complete-case G/R: excluding `partial`/`cannot_tell` changes the population across
   arms (selection on judge output).
4. k = 3 samples are not independent. Is item clustering enough when samples also share
   seeds across conditions?
5. The executed generation code was not committed at run time, so provenance relies on
   implementation hashes.
6. Metal non-determinism means outputs cannot be regenerated exactly.
7. A regenerated task after a crash: was the retry selective?
8. A timeout was retained as missing. Is missingness informative (long or looping
   outputs)?
9. Human κ with two raters on 312 items is fine, but the binary-subset κ depends on which
   items both raters made binary.
10. The decision trees and wording rules are helpful but complex. Was everything
    actually fixed before data? Dated evidence is needed.

**5 clarification questions**
1. What exactly is resampled in each bootstrap replicate (items only, or items and
   traces)?
2. How are undefined cells reported?
3. When were each governance decision and the analysis code frozen, relative to data
   access?
4. What fraction of traces are excluded from G by `partial`/`cannot_tell`, and do S1/S2
   change the conclusions?
5. Will raw outputs be released?

**Claims they would object to.** "Significant", "robust" or "no effect" language. Any
claim relying on an interval that excludes zero in a single cell.

**Missing controls they would mention.**
- A simulation check of interval coverage at these cluster counts.
- Sensitivity to the bootstrap method.

**Strengths they would acknowledge.**
- Prespecified estimands.
- Paired within-replicate contrasts.
- Explicit missingness cascade.
- No imputation.
- Hashes everywhere.
- Documented incidents with an outcome-independence argument.
- No post-hoc threshold choice (κ cutoff withdrawn).

**What would move them toward acceptance.**
- A full count table alongside every proportion.
- An explicit statement of how many intervals were computed.
- S1–S5 reported.
- A dated governance timeline in the appendix.
- Code and data release.

**What cannot be fixed without new work.** A coverage simulation (that is new analysis
work, not new experiments; it could be done as a supplementary, clearly labelled
methodological check), and exact output reproducibility.

**What can be fixed now.**
- Reporting templates with counts.
- A multiplicity statement.
- The dated timeline (Appendix J).
- Honest code-provenance wording (done).
- The retry and timeout justification (done in §4.8).

---

## Part 2 — Reviewer-defense matrix

**Severity:** H = could decide acceptance; M = needs a clear answer; L = minor.

| Reviewer concern | Severity | Already addressed? | Evidence / artifact | Best response | Paper change needed? | Future-work only? | Would require new experiment? |
|---|---|---|---|---|---|---|---|
| Only 2 models | H | Partly (scope stated) | Methods §4.4; Limitations | "Two configurations from different families test whether a pattern holds for more than one model; we report pattern consistency, not a model-general effect." | Keep scope wording strict; no pooling | Yes | Yes (more models) |
| Only 1 non-English language | H | Partly | Intro "Why Urdu"; Limitations | "A case study of one under-resourced, non-Latin-script language; we make no cross-language generalization." | Add "case study" wording to the abstract and conclusion | Yes | Yes |
| Urdu-specific generalization | H | Yes (ledger C26 prohibited) | Ledger; Limitations | As above; conclusions are conditional on Urdu | No | Yes | Yes |
| Monitor construct validity | H | Yes, by design (G vs native reference) | Methods §4.9/4.11; D-PG-4 parity | "This is precisely what G measures, against native readers with identical inputs." | Report the full confusion matrix | — | No |
| LLM judge reliability | H | Yes (this is the measured quantity) | Fu & Liu 2025; Doğruöz et al. 2026; Young 2026c | "We do not assume reliability; we estimate divergence from native readers." | No | — | No |
| Translation artifacts | M | Partly (audit, S4, no truncation) | D-PG-5; Methods §4.10 | Report audit counts beside R; R is descriptive only | Report audit counts in Table 8 | Second translator | Yes, for translator robustness |
| Human agreement | M | Yes (continuous κ + raw agreement + contingency) | AGREEMENT_REPORTING.md | "We report κ, raw agreement and disagreement location; the reference is adjudicated; S5 shows raw labels." | No | — | No |
| Cue artificiality | M | Partly | Methods §4.3; Limitations | "Controlled, low-stakes probe chosen for measurement clarity; not a model of real-world manipulation." | Add one sentence on low stakes (done in Limitations V2) | Yes | Yes (richer cues) |
| No paraphrase control | H for R; L for G | Yes (D-PG-3: R descriptive only) | Decision pack; ledger C22 prohibited | "We make no language-mechanism claim for R." | No | Yes | Yes |
| No confirmatory testing | M | Yes (by design) | Analysis plan §14; Methods §4.12 | "Descriptive by design for a first study; all planned comparisons reported; no selection." | Add the multiplicity sentence (done) | Confirmatory replication | Yes, for a confirmatory study |
| Multiple samples per item | M | Yes | D-PG-6 item-cluster bootstrap | "Samples are not treated as independent; items are resampled." | State it in captions | — | No |
| Dependence structure (shared seeds, cross-condition pairing) | M | Yes | Methods §4.12 (bookkeeping pairing) | "Item clustering captures within-item dependence; seed sharing creates no counterfactual pairing and is not used as such." | No | — | No |
| Missing timeout | L | Yes (D-PG-2) | §4.8; provenance | "1/3,312; retained as missing, not retried; worst-case bounds reported." | No | — | No |
| Judge language bias | M | Partly | Zhou et al. 2026 cited | "Detected directly by G/AG; any bias appears as divergence from native readers." | No | — | No |
| Dataset translation quality | M | Yes (120/120 native review) | §4.7; review packet | "All 120 items reviewed by a native speaker; translation vs language confound stated." | No | Native items | Yes |
| Dataset licence | M | Yes (no text redistribution) | §4.2 | "Licence unstated upstream; we release IDs and hashes only." | No | — | No |
| Model size limitations | M | Partly | Limitations | "Small open models chosen for local reproducibility; not representative of frontier systems." | No | Yes | Yes |
| External validity | H | Partly | Limitations; ledger | "Findings are conditional on this configuration; they are hypotheses for broader study." | No | Yes | Yes |
| Causal wording | H if violated | Yes (ledger tripwires) | Claim ledger | "No causal claims about the model; contrasts are descriptive." | Final overclaim scan | — | No |
| Hidden-CoT implications | H if violated | Yes (C24 prohibited) | Ledger; Intro | "Disclosure is a property of text; no claims about internal states." | No | — | No |
| Is "monitorability" operationalized appropriately? | H | Partly | Intro (two conditions) | "We operationalize only the second condition (monitor reading) for one construct (explicit acknowledgment of a suggestion)." | Use "disclosure monitoring" in place of bare "monitorability" (title and abstract) | — | No |
| Prompted rationale ≠ native reasoning | H (safety reviewers) | Yes (stated) | §4.5; Limitations | "Both models produce prompted rationales; native thinking was not usable in Urdu here (excluded pilot)." | No | Yes | Yes |
| Judge sees the suggestion (keyword-matching risk) | M | Partly | Judge V2 prompt: mention ≠ disclosure | "Raters see the same input (parity); `partial` captures mention-only. The confusion matrix shows whether the judge over-labels mentions." | Highlight the judge `disclosed` vs human `partial` cell in Table 7 | — | No |
| Disclosure conditional on adoption | M | **No** (not in the frozen plan) | — | "Not prespecified; if reported, labelled exploratory/post-hoc with its date." | Optional exploratory supplement | — | No |
| Small Cue-B and human subsets (interval width) | M | Yes (stated) | Limitations | "Intervals reported; differences narrower than them are unresolved." | No | — | Larger N = new experiment |
| Uncommitted generation code | M | Yes (honest wording) | §4.8; resume provenance | "Implementation hashes recorded; code archived after the run." | Archive the commit before posting | — | No |
| Bootstrap coverage with few clusters | M | Partly | Limitations | "Percentile intervals with 36 clusters may be anti-conservative; we state this." | Add a sentence (done in Limitations V2) | Coverage simulation | No (analysis only) |
| Complete-case selection in G/R | M | Yes (S1–S3, cascade) | Analysis plan | "S1/S2 recode partial; S3 bounds technical failures; the cascade is shown." | No | — | No |

---

## Part 3 — Red team

### Strongest rejection case

> "This submission studies whether a 7B open-weight judge's labels of 'explicit hint
> acknowledgment' in prompted rationales from two small models agree with two human
> raters in Urdu. Every element is narrow: one language, one benchmark (translated), one
> cue paradigm with two single wordings, one quantized judge, one translator, two small
> models without native reasoning. The construct is a textual mention-of-hint label far
> from the safety-relevant notion of chain-of-thought monitorability claimed in the
> framing. Translation results are uninterpretable without the paraphrase control the
> authors themselves deem necessary. Analyses are descriptive with many intervals and no
> error control, so any 'pattern' may be noise. The human reference (two raters, one of
> whom may be the author) is thin. The contribution reduces to a single measurement in a
> single configuration; the combination of known ingredients is not sufficient novelty
> for this venue."

### Evidence-based author response (non-defensive)

> "We agree the study is narrow, and we have scoped every claim accordingly. The paper's
> question is methodological: whether an apparent cross-lingual difference in automated
> disclosure labels is attributable to the monitor or to the text. Answering it requires
> a native reference on the *same* traces with *identical* inputs. Prior multilingual
> monitoring work relies on LLM judges validated by inspection (Onyame et al., 2026), and
> judge reliability is known to degrade and shift in lower-resource languages (Fu & Liu,
> 2025; Zhou et al., 2026). Our estimate, whichever direction it takes, is therefore
> informative for anyone interpreting such numbers.
>
> We do not claim mechanism for translation effects (no paraphrase control) or
> generality beyond this configuration. All rules, including the decision not to make
> those claims, were fixed and dated before any monitoring or human label was examined.
> We report every planned comparison with counts and intervals, and treat only patterns
> that replicate across both models as findings. We state clearly whether any author
> served as a rater. The design is cheap to replicate in other languages, and we release
> everything needed to do so."

### The 5 issues that genuinely determine publishability

1. **Whether G is estimable with useful precision.** The size of the complete-pair n after
   `partial`/`cannot_tell`, and of the κ interval. If G's intervals are uninformative,
   the main contribution is weak.
2. **Construct clarity.** "Disclosure monitoring" must be clearly distinguished from
   "monitorability" and "faithfulness". Overreach here is fatal with safety reviewers.
3. **Scope honesty versus contribution size.** A one-language, two-small-model case study
   suits a workshop. Main-track publication probably needs more languages and models.
4. **Human reference quality.** Rater independence (including any author-rater),
   qualification and agreement reporting.
5. **Discipline in reporting.** No cherry-picking among many intervals, prespecified
   wording applied as written, and translation results kept descriptive.

---

## Part 4 — Translation-arm red team (2026-10-04, model obtained; no translation run)

### ACL multilingual reviewer
1. Sentence-level MT of long, code-switched reasoning is a weak proxy for document
   translation.
2. Segment boundaries break discourse cues such as "so" and "therefore", which carry
   disclosure.
3. One translator.
4. No MT quality metric is reported.
5. Mixed-script pass-through leaves English fragments untranslated, so the input is
   mixed-language.

- **Defense:** the arm is a contrast, not an MT evaluation. The audit targets disclosure
  preservation specifically. Segmentation is natural-boundary-first and order-preserving.
  Pass-through is deliberate: those fragments are already English, and they are flagged.
- **Cannot defend:** translator-specific effects; document-level discourse loss.
- **Wording fix:** "translation by one sentence-level MT system" wherever T is
  interpreted.

### AI safety reviewer
1. Translate-then-monitor is how a deployed pipeline might "fix" multilingual
   monitoring, so a positive R will be over-read.
2. Translation may add explicitness, making the judge over-detect.
3. Without a paraphrase control, R is uninterpretable.
4. The judge still sees Urdu suggestion text in the T arm, so the input is mixed.
5. MT failures could cluster on long rationales, which are exactly the ones that matter.

- **Defense:** R is prespecified as descriptive (D-PG-3). The exploratory agreement
  diagnostic checks whether rate changes track native readers. The mixed input is
  deliberate: holding non-rationale inputs fixed isolates the rationale's language.
  Failures are reported by length and model, and P-MISS activates if they cluster.
- **Cannot defend:** any mechanism claim.
- **Wording fix:** never write "mitigation" or "recovery".

### Reproducibility reviewer
1. The tokenizer-usage bug shows the pipeline was not validated end to end.
2. Device and dtype nondeterminism (fp16 vs fp32) may change beam outputs.
3. The artifact hash and configuration hash are not yet recorded.
4. Which system translated each rationale must be traceable.
5. Segment-level records are needed to audit reassembly.

- **Defense:** the bug was caught by the synthetic validator before any scientific
  translation. That is the purpose of the gate. Methods will state the correction and the
  rerun validation if the engineering record supports it. Device and dtype are recorded,
  and outputs are hashed. Per-trace segment tables record system, source hash, output and
  overflow flags.
- **Cannot defend:** bitwise reproducibility across hardware.
- **Wording fix:** "deterministic given the recorded runtime; not guaranteed bitwise
  identical across devices or dtypes".

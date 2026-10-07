# Reviewer #2: strongest rejection and response strategy (outcome-blind; 2026-10-06)

## Part 1. The review

> **Summary.** The authors score Urdu rationales from two small models with one quantized
> LLM judge, an MT-then-judge variant and (eventually) two human raters, and call the
> difference a "monitor-validity gap". The question is reasonable but the evidence cannot
> carry the paper's implied claims.
>
> **1. Underpowered and ungeneralizable.** One language and two 2–4B models. Cue B rests on
> 36 items. Intervals will be wide; a null will be uninterpretable and a positive result
> fragile.
>
> **2. One judge.** G characterizes one 7B quantized model and one prompt. Nothing follows
> about "automated monitors".
>
> **3. Translation confound, no paraphrase control.** Any T–D difference mixes language with
> rewriting. The R analysis is uninterpretable.
>
> **4. Prompted rationales.** These are not reasoning traces. Disclosure in prompted text
> says little about monitoring real reasoning channels.
>
> **5. Human reference.** Two raters (one pair κ), and the adjudicator decides contested
> items. Is H any better than the judge? There is no English human anchor, so the core
> "model vs monitor" decomposition is one-sided.
>
> **6. Governance after the fact.** Key analysis decisions and the interpretation framework
> were written after generation. Code ran uncommitted. The translation procedure was
> amended mid-stage. This looks like a forking-paths garden.
>
> **7. Multiple intervals, no correction.** Dozens of intervals; some will exclude zero by
> chance.
>
> **8. Judge sees the suggestion.** Keyword matching could inflate `disclosed`.
>
> **9. Dataset licensing.** The Urdu dataset has no licence, which undermines reproducibility.
>
> **10. Causal overreach.** The title's "Monitor or Model?" promises a decomposition the
> design cannot deliver.
>
> **Recommendation:** reject; resubmit with more languages, more judges, a paraphrase
> control and an English human reference.

## Part 2. Point-by-point strategy

| # | Concede? | Mitigation already in the design | Manuscript change | Future work |
|---|---|---|---|---|
| 1 | **Yes, partly.** It is a case study | Descriptive intervals; replication-in-sign rule; precision stated from the design | State design-based precision in Limitations; scope the title and abstract ("an Urdu case study"); report every cell | More languages and models |
| 2 | **Yes** | G is defined for this monitor; the choice was made before data and is justified | "this monitor" throughout; no generalization | More judges |
| 3 | **Yes** | R is descriptive only (D-PG-3); translation audit and S4; exclude-six; the design isolates the reader, not the language | Keep R secondary; never use the word "recovery" without A > 0 and the exploratory label | A paraphrase control; a second translator |
| 4 | **Yes** | Stated construct: disclosure in visible prompted rationales | Construct paragraph early in §1 | Native reasoning channels in larger models |
| 5 | **Partly.** H is a reference, not truth; the English anchor is missing | Blind double annotation; independent adjudicator first label; κ with CIs and full tables; abstain/unresolved never imputed | Make the one-sided limit explicit (no English H; AG automated only) | More raters; an English human anchor |
| 6 | **Partly.** The timing is real, but the decisions were made before any result was seen | Full timeline (Appendix J): plan content final before generation; D-PG approvals after generation but before any label was examined; framework locked pre-unseal with exposure disclosed; amendment triggered by technical failure, before any success | Methods §4.17 states this exactly; never "preregistered" | Commit before running in future work |
| 7 | **Yes** | No tests; every interval reported; family sizes stated; weight only on cross-model replication | Family-size sentences in Results | Pre-specified equivalence margins |
| 8 | **Yes, as a threat** | Parity with human readers; `partial` label; the confusion cell | Report the judge-`disclosed` × reader-`partial` cell explicitly | A suggestion-masked judge arm |
| 9 | **Yes** | Release IDs and hashes, not text; licence stated as unknown | Data-availability text; **remediate the public PDF** before posting | Seek licence clarification |
| 10 | **Partly** | G does separate the monitor side on fixed text; the model side stays "consistent with" only | Title: prefer a case-study title, or add a subtitle | — |

**Do not invent** analyses, raters or evidence in response. Every reply must point to an
existing table, record or limitation.

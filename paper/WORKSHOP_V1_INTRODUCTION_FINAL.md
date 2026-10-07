<!-- Drop-in for §1 of paper/WORKSHOP_V1_PREPRINT.md. Outcome-blind; written 2026-10-06. Citations
are the preprint's verified references; re-check them on the upload date. -->

# 1 Introduction

Reading a model's written reasoning is one of the more practical ways to oversee it. A
monitor, usually another language model, inspects a rationale for evidence that something
other than the stated task shaped the answer (Korbak et al., 2025; Emmons et al., 2025).
For such monitoring to work, two links must hold. The model must state the relevant
information in its text, and the monitor must recognize the statement when it is there.

Much work examines the first link. Models given hints or biasing context often do not
mention influences that changed their answers (Turpin et al., 2023; Chen et al., 2025;
Young, 2026a, 2026b). The second link is examined less often, although being monitorable
and being monitored correctly are distinct properties (Yang et al., 2025), and measured
verbalization rates shift with the classifier used to score them (Young, 2026c).

Language is a natural place for the second link to weaken. LLM judges are less consistent
across languages, especially lower-resource ones (Fu & Liu, 2025), and their scores can be
biased by the language of the text they evaluate (Zhou et al., 2026). Multilingual
evaluations report that chain-of-thought monitoring becomes less reliable outside English
(Onyame et al., 2026). In such evaluations, however, the monitor is also the measuring
instrument. A detection rate that differs between languages can arise because the
rationales say something different, or because the monitor reads them differently. An
automated comparison cannot tell these apart.

We separate them by **holding the rationale fixed**. Each Urdu rationale is scored three
ways: by an automated monitor reading the Urdu, by the same monitor reading an English
machine translation, and by native readers of Urdu. Because all three scores refer to the
same text, any difference between them is a difference in reading, not in what the model
wrote. The native-reader labels serve as a reference for the monitor's Urdu judgments.
Comparing the two gives a monitor-validity gap (G) on identical inputs. The translation
arm shows whether changing only the language in which the monitor reads changes its
labels.

Urdu is an informative test case for three reasons. It is widely spoken but lower-resource
for current models. It is written in a right-to-left Perso-Arabic script. A strong,
item-aligned Urdu translation of a standard benchmark exists, so the same items can be
posed in both languages. We use a disclosure task: models answer multiple-choice science
questions with or without a misleading suggestion, and we ask whether their rationales
explicitly state that the suggestion influenced them.

The study is deliberately narrow:
- two small open models;
- one monitor;
- one translator;
- one language.

Every analysis was frozen before any monitor or human label was examined. All estimates
carry descriptive item-cluster intervals, and no hypothesis tests are performed.

**Contributions.**
1. **A same-rationale design for cross-lingual monitor validation.** One persisted
   rationale is scored directly, in translation and by native readers, separating monitor
   behavior from model behavior without regenerating text.
2. **A native-reader reference for automated disclosure monitoring in Urdu.** Blinded
   double annotation with adjudication, using the same inputs and label definitions as the
   monitor. Agreement is reported continuously, without thresholds.
3. **A measurement of this monitor's validity in Urdu** (G), together with a descriptive
   translate-then-monitor contrast (R), for two model configurations. [[R-INTRO-1: one
   sentence of results, after unseal]]
4. **A frozen, fully provenanced pipeline and analysis.** Hashed stages, retained failures,
   dated amendments and synthetic-validated estimators, released as code and identifiers.

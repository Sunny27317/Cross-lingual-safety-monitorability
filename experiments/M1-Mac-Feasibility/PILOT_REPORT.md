# Track-A English hint pilot report

**Status: complete descriptive pilot; no confirmatory inference.** This report was
generated after the completed run passed frozen integrity validation. It uses only the
existing `clsm.track_a_analyze` pipeline and frozen metric definitions.

## 1. Run identity

| Field | Observed value |
|---|---|
| Experiment | `track-a-en-hint-pilot` |
| Authorized commit | `605b9b71d1eb1bb616d331fd5a82db7ceaa163c1` |
| Scientific config hash | `e325114a6de5764e81011510272e42bd27310b614dd4f2c9de3740f33261740b` |
| Dataset content hash | `db93be51bc72ea852d50a816f835d5822e4241ddb5039102fa46e91a5c98d399` |
| Run start / finish | `2026-09-11T14:59:47.844788+00:00` / `2026-09-12T23:24:07.720740+00:00` |
| Planned / present / missing | 800 / 800 / 0 |
| Raw artifacts | 3,200 (4 per generation), manifest hash matched |
| Completion manifest | Present and valid |
| Working tree at run | Clean (`git_dirty: false`) |

## 2. Provenance and frozen design

The recorded model is `Qwen/Qwen3-1.7B`, revision
`90862c4b9d2787eaed51d12237eafdfe7c5f6077`, GGUF
`Qwen3-1.7B-Q8_0.gguf`, SHA-256
`061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`, size
1,834,426,016 bytes. The recorded llama.cpp identity is commit
`5266f24da75dc449bd56cbed7addb9c8e4a6a73e`, build `10809`, with verified identity.

Decoding was temperature 0.6, top-p 0.95, top-k 20, max-new-tokens 16,384, context
32,768, timeout 900 seconds, eight samples per condition, seeds 0–7, and an empty
extra-argument surface. No generation was rerun or replaced.

The dataset pin contains 50 items: 10 frozen subjects × 5 items, with 400 control and
400 treatment records. Every item has eight records per condition. Strict Latin A–D
extraction and the existing item-level majority rule were used; majority ties remain
ambiguous and are excluded where the metric requires a majority.

## 3. Completion and parsing

- Valid parsed generations: **787 / 800 (98.375%)**
- Parse-invalid generations: **13 / 800** — 5 `AMBIGUOUS`, 8 `NO_ANSWER`, 0 `PARSE_ERROR`
- Reasoning span: 799 `PRESENT`, 1 `MALFORMED`, 0 `EMPTY`, 0 `ABSENT`
- Stop reasons: `EOS` 0, `LENGTH` 0, `TIMEOUT` 0, `NONZERO_EXIT` 0, `UNKNOWN` 800
- Item-level majority ties: control 0, treatment 1
- Missing generation identities: 0

The 13 parse-invalid records and the `UNKNOWN` stop-reason limitation are retained and
reported. No invalid answer was imputed, and no tie was resolved by option letter.

## 4. Frozen behavioral metrics

The existing metric output uses item-level majority aggregation and deterministic
item-cluster percentile bootstrap intervals. These are descriptive intervals only.

| Metric | Numerator / denominator | Estimate | 95% descriptive CI |
|---|---:|---:|---:|
| Unhinted accuracy (supporting) | 36 / 50 items with a control majority | 0.7200 | [0.6000, 0.8400] |
| Hinted accuracy (supporting) | 29 / 49 items with a treatment majority | 0.5918 | [0.4490, 0.7347] |
| Control adoption (supporting) | 5 / 50 items with a control majority | 0.1000 | [0.0200, 0.1800] |
| Hinted adoption (supporting) | 13 / 49 items with a treatment majority | 0.2653 | [0.1429, 0.3878] |
| Adoption increase (supporting paired) | 8 / 49 paired-majority items | 0.1633 | [0.0612, 0.2653] |
| **Answer-switch rate** | **6 / 35 switch-eligible items with a treatment majority** | **0.1714** | **[0.0571, 0.3143]** |

Switch eligibility is the frozen set with a correct control majority and a wrong hint
target, with a treatment majority observed. Six of the 35 eligible items switched to
the hint target under the frozen majority rule.

The three disclosure-dependent pilot quantities are **not estimable in this stage**:

| Frozen quantity | Status and denominator |
|---|---|
| `disclosure_rate` | Not computed: requires disclosure labels from a validated judge/human reference; no denominator is defined by the English generator-only pipeline |
| `hidden_influence_rate` | Not computed: requires the same disclosure labels; no denominator is defined |
| `conditional_hidden_influence_rate` | Not computed: requires disclosure labels; no denominator is defined |

This is the preregistered stage boundary, not a zero estimate. No automated judge was run
and no human labels were created.

## 5. Descriptive interpretation

The frozen English run completed all 800 planned calls, preserved invalid records and
made the pipeline's item-level parsing, majority, tie and provenance behavior observable.
The observed answer-switch and adoption quantities provide a descriptive behavioral
signal and support proceeding to the separately gated judge-calibration/native-human
planning review, subject to supervisor approval.

This is a **pipeline/behavior feasibility conclusion**, not evidence for the Urdu
hypothesis, monitor validity, translation recovery, or a confirmatory effect.

## 6. Limitations and non-conclusions

The pilot uses one small quantized English model, one runtime, 50 MMLU items, stochastic
sampling and repeated generations clustered within items. All stop reasons are `UNKNOWN`
under the recorded runtime signal, and 13 generations are parse-invalid. The descriptive
intervals do not turn the pilot into a confirmatory test.

This pilot cannot establish the Monitor-Validity Gap, cross-lingual degradation, Urdu
monitor failure, translate-then-monitor recovery, causal faithfulness, or frontier-model
generalization. It does not select a judge, translator, SESOI or confirmatory sample
size. Those decisions remain separately human-gated.

## 7. Next stage

**STOP after this English descriptive report.** The next permitted activity is prospective
review and freeze of the native-human reference and judge-calibration protocol. Do not
run a judge, Urdu inference, translation experiment, human annotation or confirmatory
analysis automatically from this report.

# Prospective power plan — no N or SESOI selected

**ENGINEERING READY.** Confirmatory population, test, N, SESOI, alpha, target power,
nuisance parameters, ICC, multiplicity and missingness assumptions remain investigator
scientific decisions. No English pilot results were inspected to choose them. Conventional
alpha .05 and power .80 may be discussed as common choices; they are not project defaults
or decisions. Synthetic tests use explicit hypothetical values solely to verify arithmetic.

## Required inputs and estimand alignment

`PowerScenario` requires an investigator decision record, estimand, positive SESOI,
alpha, target power, paired outcome probabilities, missingness, its assumption, nuisance
justification, ICC, traces/item and null assumption. It rejects a missing SESOI,
incoherent probabilities, a scenario difference inconsistent with SESOI, and outcome
fields such as pilot switch rate. Each scenario hash binds all inputs. Code cannot
prove a human's justification is independent; retain a dated rationale/access history.

The paired positive/negative discordances must match the intended estimand:

- Native-minus-direct gap: positive = H=1,D=0; negative = H=0,D=1.
- Translated-minus-direct detection: positive = T=1,D=0; negative = T=0,D=1,
  on the prospectively specified common native/direct/translated population.
- Agreement recovery: compare the binary correctness indicators 1[T=H] and 1[D=H],
  not raw disclosure rates. Its nuisance probabilities are different inputs.

A language interaction or a difference of paired gaps is not automatically powered by
one of these simple scenarios. It needs an independently specified joint multi-arm model
and statistical review before confirmatory use. The utility does not silently substitute
a simpler test for the primary scientific question.

## Independent binary-pair calculation

`exact_paired_power(n_pairs, scenario)` is restricted to one trace per independent item
and ICC=0. It uses the exact two-sided McNemar/binomial null on discordances. If q is
P(positive discordance)+P(negative discordance), pairwise MCAR loss m gives discordance
count K ~ Binomial(N, q(1−m)). Conditional on K, positive discordances follow
Binomial(K, p_positive/q). Sum alternative probabilities in the two-sided rejection
region of Binomial(K, 1/2). This calculates power at supplied inputs, not a selected N.

The exact-test relationship is documented by [statsmodels' McNemar API](https://www.statsmodels.org/dev/generated/statsmodels.stats.contingency_tables.mcnemar.html)
and the [NIST McNemar reference](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm).
Our power integration is an explicit derivation using that test, not a source-reported
recommendation for this study. The independent calculation must not treat repeated
samples from one item as independent observations.

## Cluster simulation and sensitivity

`simulated_cluster_power` uses a fully declared synthetic generative assumption:
item-specific joint binary category probabilities follow a Dirichlet distribution with
mean the supplied joint probabilities and concentration (1/ICC − 1). Conditional traces
are multinomial draws. This gives the specified within-item correlation for category
indicators; it is **not** a universal language/model/annotator ICC. ICC=0 uses fixed
probabilities. Pairwise MCAR thins observed pairs. Item totals retain all traces together.

The test statistic is the absolute sum of item-level signed discordances. Whole-item
sign flips generate a Monte Carlo reference distribution with the +1 correction. Validity
requires the explicitly supplied within-item label-exchangeability/symmetry null and
independent items. It is not guaranteed by zero average difference alone. `SimulationPlan`
requires item count, simulations, sign-flip draws and seed. Reports include rejection
count, power, Monte Carlo standard error and assumptions. Numerical error is distinct
from scientific uncertainty about the assumptions.

`sensitivity_grid` runs the supplied scenarios/counts in deterministic order and returns
all results. It does not optimize, select or freeze N. Include an independently justified
range of nuisance/ICC/missingness inputs, and validate null error behaviour and sensitivity
to model misspecification before scientific design approval. The same seed across grid
rows is a reproducibility convention, not independent evidence across scenarios.

`ResamplingPlan` in the agreement/analysis code supplies item-cluster bootstrap for
future paired reports. It is separate from prospective power simulation. Bootstrap
precision on a pilot does not define a scientifically meaningful SESOI.

## Human gate

Complete [sample-size decision](SAMPLE_SIZE_DECISION_TEMPLATE.md) and
[preregistration](CONFIRMATORY_PREREG_TEMPLATE.md), obtain statistical/scientific review,
resolve governance/resources, freeze the plan before confirmatory outcomes, and obtain
separate authorization. If inputs remain unjustified, report sensitivity only and leave
N/SESOI unresolved. **No confirmatory calculation on scientific records is run here.**

# Synthetic clustered-method validation

This report is a prospective operating-characteristic check of a source-item
cluster sign-flip randomization test, with the percentile interval retained as a
diagnostic. It uses generated binary paired trace differences only; it does not
use pilot records and does not select a confirmatory sample size, SESOI, threshold,
or test. The committed 20-simulation
per-cell example is **smoke validation only**: its Monte Carlo error is too large
to establish calibrated type-I error or interval coverage and it is not
sufficient to freeze a confirmatory test.

The smoke simulation used 20 repetitions per scenario, 50 source-item bootstrap
replicates, nominal alpha 0.10, and seed `20260911`. Rejection is recorded when
the percentile interval excludes zero. Monte Carlo standard errors are shown so
the small synthetic run is not mistaken for a scientific result.

| scenario (items, traces/item, p+, p-, ICC, missing, informative missing) | true delta | defined | rejection | rejection MCSE | coverage | coverage MCSE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| (8, 3, .20, .20, 0, 0, 0) | 0.00 | 20 | 0.15 | 0.0798 | 0.85 | 0.0798 |
| (12, 4, .20, .10, .2, .1, .2) | 0.10 | 20 | 0.50 | 0.1118 | 0.80 | 0.0894 |
| (20, 5, .10, .10, .4, 0, 0) | 0.00 | 20 | 0.10 | 0.0671 | 0.90 | 0.0671 |

The informative-missingness row is a sensitivity mechanism: its interval
coverage is against the complete-case scenario delta and is not evidence that
missingness is ignorable. The implementation must therefore report missingness
and retain this sensitivity analysis rather than silently treating it as a
validated assumption.

The deterministic report artifact hash is
`b5d89f39888e461f9fb31bd615962cbae3161be17a828f91b3d6aafa2bcecacf`.

For a real methods review, run the same pure function with a pre-registered
scenario grid and thousands of simulations per cell, then have the investigator
and statistician decide whether the operating characteristics are adequate. That
larger run is intentionally not a project-data analysis and has not been used to
choose confirmatory N, SESOI, or an acceptance threshold.

## Larger synthetic-only check (not a freeze)

The following wider check was run after the smoke report with 2,000 simulations
per cell, 1,000 bootstrap replicates, alpha 0.05, and seed `20260912`. It is still
an engineering diagnostic, not evidence for the study's confirmatory design.

| scenario (items, traces/item, p+, p-, ICC, missing, informative missing) | true delta | rejection | coverage | rejection MCSE | coverage MCSE |
| --- | ---: | ---: | ---: | ---: | ---: |
| (8, 3, .20, .20, 0, 0, 0) | 0.00 | 0.1065 | 0.8935 | 0.0069 | 0.0069 |
| (16, 4, .15, .15, .2, .05, 0) | 0.00 | 0.0570 | 0.9430 | 0.0052 | 0.0052 |
| (32, 6, .20, .10, .4, .1, 0) | 0.10 | 0.3365 | 0.9285 | 0.0106 | 0.0058 |
| (32, 6, .10, .10, .4, .1, .2) | 0.00 | 0.0680 | 0.9320 | 0.0056 | 0.0056 |

All four cells had zero undefined/failure intervals. The sign-flip calibration
depends on the exchangeability/symmetry-under-the-null assumption documented in
`POWER_PLAN.md`; it is not a distribution-free guarantee. The null-cell
rejection rates were 0.0165, 0.0315, and 0.0495, with corresponding binomial
Monte Carlo standard errors 0.0028, 0.0052, and 0.0049. In particular, the
informative-missingness null cell is 0.0495 (MCSE approximately 0.00485; 95%
Monte Carlo interval approximately [0.0400, 0.0590]). These values are
compatible with nominal alpha within Monte Carlo uncertainty; they do not prove
that the procedure is conservative and still require human statistical
acceptance. The percentile interval remains an explicitly reported small-cluster
diagnostic.
The larger artifact hash is
`faa063db1b53b292dc3d59b530a0e7033bdfeb41b8fbac11e0ee7addc175de61`.

The sign-flip procedure is marked `READY_FOR_HUMAN_REVIEW` as an engineering
candidate only; final use still requires the protocol's human statistical
approval. The percentile interval remains a diagnostic and is not used as the
confirmatory test.

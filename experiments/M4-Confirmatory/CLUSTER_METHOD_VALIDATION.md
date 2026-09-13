# Synthetic clustered-method validation

This report is a prospective operating-characteristic check of the source-item
clustered percentile bootstrap implementation. It uses generated binary paired
trace differences only; it does not use pilot records and does not select a
confirmatory sample size, SESOI, threshold, or test. The committed 20-simulation
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

All four cells had zero undefined/failure intervals. The larger artifact hash is
`2cf0118bf0865535d1b1e43813d883d3023261f6c20fbfcabd7e17064b2eabb1`.

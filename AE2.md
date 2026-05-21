# Tier-A spec card — AE2: Black-hole ringdown deviates from Kerr

```
PID:                AE2
DOMAIN:             aerospace
ONE_LINER:          Black-hole ringdown deviates from Kerr by ~1e-3 at the
                    first overtone, pooled across high-SNR mergers.
SHARP_FORM:         Pooled |delta f_22 / f_22| across GWTC-3 high-SNR
                    ringdowns is consistent with 1e-3 and inconsistent
                    with 0 at the 90% credible level.
PREDICTED_EFFECT:   1e-3 dimensionless fractional
NULL_HYPOTHESIS:    GR/Kerr is exact; pooled |delta f / f| = 0.
DATA_SOURCE:        GWOSC GWTC-3 catalogue
                    https://www.gw-openscience.org/eventapi/
                    LVC ringdown-analysis posteriors
                    https://dcc.ligo.org/LIGO-T2100447/public
TEST_STATISTIC:     90% credible interval of pooled |delta f_22 / f_22|
                    from a hierarchical Bayesian fit (PyMC) across events.
DECISION_RULE:
  SUPPORTED   if 90% CI contains 1e-3 AND excludes 0.
  REFUTED     if 90% CI is fully below 3e-4 OR fully above 3e-3.
  INCONCLUSIVE otherwise.
RETROFIT_RISK:      low
```

## Background

The document's prediction AE2 (and the underlying cosmological P32) claims
that CCDR identifies black-hole formation as a local χ_4 → 1 dimensional
reduction, producing a small deviation from Kerr in the ringdown overtones
at the ~1e-3 level.

## Why this is testable on public data

LIGO/Virgo/KAGRA publish full posterior samples for ringdown analyses of
their high-SNR events. The pipeline (Isi & Farr 2021;
LIGO-Virgo-KAGRA ringdown papers) extracts (delta f_22, delta tau_22) as
free parameters; results are publicly downloadable as HDF5 files.

## Implementation outline

1. Use `gwosc.datasets.find_datasets(catalog="GWTC-3-confident")` to enumerate.
2. Filter to events with reported ringdown SNR > 8.
3. For each event, download the ringdown posterior samples from the LVC
   data release on DCC (LIGO-T2100447 or successor).
4. Build a hierarchical model:

   ```
   mu      ~ Normal(0, 0.1)            # population-level deviation
   sigma   ~ HalfNormal(0.1)
   for each event i:
       df_i ~ Normal(mu, sigma)
       observation_likelihood_i(df_i)  # use KDE of per-event posterior
   ```

5. Sample with NUTS, extract the 90 % CI on `mu / f_Kerr_22(M, chi)`.
6. Apply decision rule.

## Most likely outcome

**INCONCLUSIVE.** Current per-event ringdown posteriors have widths of
order 1e-1, so the population-level CI may not even reach 1e-3 sensitivity.
This is the honest report.

## Caveats to surface in the result

- Ringdown analyses depend on assumed start time; we use the LVC central
  choice. Sensitivity to this choice should be reported as a separate
  systematic.
- The hierarchical-model prior (`mu ~ N(0, 0.1)`) is weakly informative;
  results should be checked with a flat prior alternative.
- Frequency deviations alone are not a unique CCDR signature — any
  beyond-Kerr theory predicts something similar. A SUPPORTED verdict
  here would not be specific to CCDR.

## Decision-rule lock

After this spec is finalised, write the SHA-256 of the `DECISION_RULE`
string above into `AE2.lock`. The runner asserts the live module hash
matches the locked value at import time.

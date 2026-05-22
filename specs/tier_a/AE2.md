# AE2 spec card

```
PID:               AE2
DOMAIN:            aerospace
ONE_LINER:         Black-hole ringdown deviates from Kerr by ~1e-3 at first overtone.
SHARP_FORM:        Pooled |delta f_22 / f_22| consistent with 1e-3 and inconsistent with 0.
PREDICTED_EFFECT:  0.001 dimensionless fractional
NULL_HYPOTHESIS:   GR exact; |df/f| = 0.
FALSIFICATION:     Posterior 90% CI fully below 3e-4 or fully above 3e-3.
RETROFIT_RISK:     low
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if 90% CI of pooled |df/f| contains 1e-3 AND excludes 0; REFUTED if 90% CI fully below 3e-4 or fully above 3e-3; INCONCLUSIVE otherwise.
```

## Public sources

- https://gwosc.org/eventapi/json/GWTC-3-confident/
- LVK TGR catalogue papers (Abbott et al. 2021, 2023)

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `AE2.lock`; modifying the rule without re-locking will fail
the harness self-test.

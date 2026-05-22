# MAT3 spec card

```
PID:               MAT3
DOMAIN:            materials
ONE_LINER:         Nanocrystalline kappa(T) ~ T^{1/2} at T<=5 K.
SHARP_FORM:        Pooled log-log slope in [0.3, 0.7] at T<=5 K.
PREDICTED_EFFECT:  0.5 log-log slope
NULL_HYPOTHESIS:   Casimir T^3 (slope 3).
FALSIFICATION:     Pooled slope in [2.5, 3.5].
RETROFIT_RISK:     medium
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if pooled T<=5 K log-log slope in [0.3,0.7]; REFUTED if in [2.5,3.5]; INCONCLUSIVE otherwise.
```

## Public sources

- Same datasets as MAT1

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `MAT3.lock`; modifying the rule without re-locking will fail
the harness self-test.

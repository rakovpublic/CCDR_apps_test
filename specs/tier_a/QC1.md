# QC1 spec card

```
PID:               QC1
DOMAIN:            quantum_computing
ONE_LINER:         CDT holographic QEC code distance scales as d ~ N^{1/3}.
SHARP_FORM:        log d / log N slope is in [0.30, 0.36] vs surface-code 0.5.
PREDICTED_EFFECT:  (0.3, 0.36) dimensionless slope
NULL_HYPOTHESIS:   d ~ N^{1/2} (surface code).
FALSIFICATION:     Slope CI fully outside [0.20,0.45].
RETROFIT_RISK:     high
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if 95% CI of log-log slope ⊂ [0.30,0.36]; REFUTED if CI fully >0.45 or <0.20; INCONCLUSIVE otherwise.
```

## Public sources

- Stim simulation (in-process)

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `QC1.lock`; modifying the rule without re-locking will fail
the harness self-test.

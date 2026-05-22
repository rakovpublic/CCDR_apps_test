# QC2 spec card

```
PID:               QC2
DOMAIN:            quantum_computing
ONE_LINER:         CDT code outperforms surface code at N > 1e5.
SHARP_FORM:        p_L^CDT(N) < p_L^surface(N) for N=1e5 at p=0.5*p_th.
PREDICTED_EFFECT:  0.5 logical-error ratio CDT/surface
NULL_HYPOTHESIS:   No advantage (ratio >= 1).
FALSIFICATION:     Ratio >= 1 at N=1e5 with binomial p<0.05.
RETROFIT_RISK:     high
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if logical-error ratio CDT/surface < 1 with binomial p<0.05 (extrapolated to N=1e5); REFUTED if ratio>=1 with p<0.05; INCONCLUSIVE otherwise.
```

## Public sources

- Stim+PyMatching

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `QC2.lock`; modifying the rule without re-locking will fail
the harness self-test.

# QC4 spec card

```
PID:               QC4
DOMAIN:            quantum_computing
ONE_LINER:         CDT code superior under correlated burst errors.
SHARP_FORM:        P(logical fail | burst) is lower for CDT proxy than surface code.
PREDICTED_EFFECT:  0.5 ratio (CDT fails) / (surface fails)
NULL_HYPOTHESIS:   Same or worse.
FALSIFICATION:     Ratio >= 1 with p < 0.05.
RETROFIT_RISK:     high
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if Fisher exact p<0.05 with CDT-failures < surface-failures under burst injection at p=0.7*p_th; REFUTED if Fisher p<0.05 in opposite direction; INCONCLUSIVE otherwise.
```

## Public sources

- Stim+PyMatching

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `QC4.lock`; modifying the rule without re-locking will fail
the harness self-test.

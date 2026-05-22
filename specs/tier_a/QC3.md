# QC3 spec card

```
PID:               QC3
DOMAIN:            quantum_computing
ONE_LINER:         CDT threshold p_th ~ 1 %.
SHARP_FORM:        p_th in [0.005, 0.02] from finite-size scaling.
PREDICTED_EFFECT:  0.01 physical-error probability
NULL_HYPOTHESIS:   Surface-code p_th ~ 0.0057-0.011 (depends on circuit noise).
FALSIFICATION:     p_th outside [0.001, 0.05].
RETROFIT_RISK:     high
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if estimated p_th in [0.005,0.02]; REFUTED if <0.001 or >0.05; INCONCLUSIVE otherwise.
```

## Public sources

- Stim+PyMatching

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `QC3.lock`; modifying the rule without re-locking will fail
the harness self-test.

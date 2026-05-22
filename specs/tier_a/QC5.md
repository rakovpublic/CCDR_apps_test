# QC5 spec card

```
PID:               QC5
DOMAIN:            quantum_computing
ONE_LINER:         Phononic-crystal-substrate transmon T1 exceeds 1 ms.
SHARP_FORM:        max(reported T1) for this architecture > 1000 us.
PREDICTED_EFFECT:  1000.0 microseconds
NULL_HYPOTHESIS:   Plateau around 300 us (current SoTA).
FALSIFICATION:     No transmon meets >= 1 ms by execution date.
RETROFIT_RISK:     low
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if any published phononic-crystal-substrate transmon T1 >= 1 ms with independent replication; INCONCLUSIVE if best reported T1 < 1 ms (forward-looking prediction not yet met); REFUTED only if a publication explicitly bounds T1 below 1 ms in this architecture.
```

## Public sources

- https://export.arxiv.org/api/query
- SQuADDS database https://sqdlab.github.io/SQuADDS/

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `QC5.lock`; modifying the rule without re-locking will fail
the harness self-test.

# EN3 spec card

```
PID:               EN3
DOMAIN:            energy
ONE_LINER:         Cosmic-crystal photovoltaic enhancement above Shockley-Queisser.
SHARP_FORM:        Si single-junction eta exceeds 32.9% (SQ) by 5-10% absolute.
PREDICTED_EFFECT:  (0.345, 0.362) absolute efficiency (fraction)
NULL_HYPOTHESIS:   Si stays sub-SQ; current record ~ 27%.
FALSIFICATION:     No Si single-junction cell > 32.9% reported.
RETROFIT_RISK:     high
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if best Si single-junction eta > 32.9% (SQ); REFUTED if max < 32.9%; INCONCLUSIVE otherwise. Multi-junction reading downgraded to RETROFIT.
```

## Public sources

- https://www.nrel.gov/pv/cell-efficiency.html
- https://www.nrel.gov/pv/assets/pdfs/best-research-cell-efficiencies.pdf

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `EN3.lock`; modifying the rule without re-locking will fail
the harness self-test.

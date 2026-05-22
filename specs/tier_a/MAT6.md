# MAT6 spec card

```
PID:               MAT6
DOMAIN:            materials
ONE_LINER:         Isotopically pure diamond kappa caps at 3300 W/m/K (theoretical max).
SHARP_FORM:        No room-T peer-reviewed 12C-diamond report exceeds 3500 W/m/K.
PREDICTED_EFFECT:  3300.0 W/m/K
NULL_HYPOTHESIS:   Higher isotopic purity yields kappa > 3500 W/m/K.
FALSIFICATION:     Any peer-reviewed report >= 3500 W/m/K at 300 K.
RETROFIT_RISK:     high
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if max peer-reviewed RT kappa for 12C-enriched diamond in [3300, 3500] W/m/K; REFUTED if any value >= 3500; INCONCLUSIVE otherwise. HIGH retrofit risk forces SUPPORTED -> RETROFIT in summary.
```

## Public sources

- https://api.crossref.org/works?query=isotopically+pure+diamond+thermal+conductivity
- Wei et al. 1993 (PRL 70, 3764)
- Inyushkin et al. 2018 (PRB 97, 144305)

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `MAT6.lock`; modifying the rule without re-locking will fail
the harness self-test.

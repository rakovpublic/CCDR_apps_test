# FR7 spec card

```
PID:               FR7
DOMAIN:            fusion
ONE_LINER:         Tokamak M_KSS correlates negatively with energy-confinement time.
SHARP_FORM:        Spearman rho(M_KSS, tau_E) < -0.5 across machines.
PREDICTED_EFFECT:  -0.7 Spearman rho
NULL_HYPOTHESIS:   No significant negative correlation.
FALSIFICATION:     rho > +0.5 with p<0.05.
RETROFIT_RISK:     medium
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if Spearman rho(M_KSS, tau_E) < -0.5 with one-sided p<0.05; REFUTED if rho > +0.5 with p<0.05; INCONCLUSIVE otherwise.
```

## Public sources

- Doyle et al., Nucl. Fusion 47, S18 (2007) — IPB98(y,2) scaling.
- Wesson, Tokamaks (2011) edge-parameter compilations.
- ITPA H-mode confinement DB public summary tables.

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `FR7.lock`; modifying the rule without re-locking will fail
the harness self-test.

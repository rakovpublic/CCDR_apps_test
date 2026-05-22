# MAT1 spec card

```
PID:               MAT1
DOMAIN:            materials
ONE_LINER:         Grain-boundary kappa follows CCDR mu(x)=x/sqrt(1+x), not Casimir.
SHARP_FORM:        AIC_C - AIC_CCDR > 4 across >=5 materials.
PREDICTED_EFFECT:  4.0 delta-AIC (Casimir vs CCDR)
NULL_HYPOTHESIS:   Casimir kappa = alpha T^3 L_grain (1-beta exp(-Td/T)) suffices.
FALSIFICATION:     Sign test favors Casimir with p<0.05.
RETROFIT_RISK:     medium
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if sign-test p<0.05 with AIC_C - AIC_CCDR > 4 across >=5 materials; REFUTED if sign test favors Casimir with p<0.05; INCONCLUSIVE otherwise.
```

## Public sources

- Cahill et al., Appl. Phys. Rev. 1, 011305 (2014)
- Touloukian (NIST/CINDAS) thermal-conductivity tabulations

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `MAT1.lock`; modifying the rule without re-locking will fail
the harness self-test.

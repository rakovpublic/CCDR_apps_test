# EL1 spec card

```
PID:               EL1
DOMAIN:            electronics
ONE_LINER:         3D NAND throughput scales with area, not volume.
SHARP_FORM:        Spearman rho(N_layers, BW/bit) < 0 with p<0.05.
PREDICTED_EFFECT:  -0.5 Spearman rho
NULL_HYPOTHESIS:   rho >= 0; per-cell bandwidth is layer-agnostic.
FALSIFICATION:     rho > 0 with p<0.05.
RETROFIT_RISK:     low
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if Spearman rho(N_layers, BW_per_bit) < 0 with one-sided p<0.05; REFUTED if rho > 0 with two-sided p<0.05; INCONCLUSIVE otherwise.
```

## Public sources

- Samsung ISSCC V-NAND papers (2014-2024)
- Micron / SK Hynix product briefs and IMW proceedings

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `EL1.lock`; modifying the rule without re-locking will fail
the harness self-test.

# MAT10 spec card

```
PID:               MAT10
DOMAIN:            materials
ONE_LINER:         Solidification grain-size vs cooling-rate exponent ~ 0.277 (3D Ising KZ).
SHARP_FORM:        Pooled log-log slope (grain size vs quench time) in [0.20, 0.35].
PREDICTED_EFFECT:  0.277 dimensionless exponent
NULL_HYPOTHESIS:   Classical nucleation gives similar 0.25-0.33; no CCDR-specific evidence.
FALSIFICATION:     CI fully <0.10 or >0.50.
RETROFIT_RISK:     medium
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if pooled log-log exponent 95% CI subset [0.20, 0.35]; REFUTED if CI fully <0.10 or >0.50; INCONCLUSIVE otherwise.
```

## Public sources

- Jones, Rep. Prog. Phys. 36 (1973) — rapid solidification of Al
- Wang et al., Acta Mater. 2018 — LPBF Inconel 718 grain vs scan speed
- Mukherjee et al., Sci. Rep. 6, 19717 (2016) — SLM Ti-6Al-4V

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `MAT10.lock`; modifying the rule without re-locking will fail
the harness self-test.

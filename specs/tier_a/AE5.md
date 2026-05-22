# AE5 spec card

```
PID:               AE5
DOMAIN:            aerospace
ONE_LINER:         Pioneer 10/11 carries ~1e-10 m/s^2 residual after thermal recoil.
SHARP_FORM:        post-thermal-recoil residual acceleration ~ 1e-10 m/s^2.
PREDICTED_EFFECT:  1e-10 m/s^2
NULL_HYPOTHESIS:   Post-thermal residual is 0 within ~1e-11 m/s^2 uncertainty.
FALSIFICATION:     Upper bound on post-thermal residual < 3e-11 m/s^2.
RETROFIT_RISK:     low
TIER:              implementable_now
DECISION_RULE:
SUPPORTED if post-thermal Pioneer residual >= 5e-11 m/s^2 with 3-sigma signif; REFUTED if upper bound < 3e-11 m/s^2; INCONCLUSIVE otherwise.
```

## Public sources

- Turyshev & Toth 2010 (arXiv:1001.3686)
- Turyshev et al. 2012, PRL 108, 241101 (thermal-recoil resolution)
- Modenini & Tortora 2014 (A&A 562, A115) — independent confirmation

## Notes

Implementation lives in `src/ccdr_tests/tests/`. The decision-rule hash is
locked in `AE5.lock`; modifying the rule without re-locking will fail
the harness self-test.

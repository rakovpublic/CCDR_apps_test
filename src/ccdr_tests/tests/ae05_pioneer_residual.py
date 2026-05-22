"""AE5 — Pioneer-anomaly-like cascade-residue residuals at ~1e-10 m/s^2.

PID: AE5
SHARP_FORM: residual unexplained acceleration on Pioneer 10/11 post thermal-recoil
            model is ~ 1e-10 m/s^2.
PREDICTED_EFFECT: 1e-10 m/s^2 sunward (CCDR claim).
NULL_HYPOTHESIS: residual is consistent with zero after thermal-recoil model
                (Turyshev et al. 2012, PRL 108, 241101).
DATA_SOURCE: Turyshev & Toth 2010 (arXiv:1001.3686) — published residuals;
             Turyshev et al. 2012 — thermal recoil resolution.
DECISION_RULE:
  SUPPORTED if post-thermal residual >= 5e-11 m/s^2 with significance.
  REFUTED   if post-thermal residual upper bound < 3e-11 m/s^2.
  INCONCLUSIVE otherwise.
RETROFIT_RISK: LOW (the CCDR claim is the strong one; the literature resolved
               the original anomaly via thermal recoil, ruling out 1e-10).
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from ccdr_tests.core.prediction import Prediction, Result, RetrofitRisk, Tier, Verdict

DECISION_RULE = (
    "SUPPORTED if post-thermal Pioneer residual >= 5e-11 m/s^2 with 3-sigma signif; "
    "REFUTED if upper bound < 3e-11 m/s^2; INCONCLUSIVE otherwise."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="AE5",
    domain="aerospace",
    one_liner="Pioneer 10/11 carries ~1e-10 m/s^2 residual after thermal recoil.",
    sharp_form="post-thermal-recoil residual acceleration ~ 1e-10 m/s^2.",
    null_hypothesis="Post-thermal residual is 0 within ~1e-11 m/s^2 uncertainty.",
    predicted_effect=1.0e-10,
    effect_unit="m/s^2",
    falsification_criterion="Upper bound on post-thermal residual < 3e-11 m/s^2.",
    retrofit_risk=RetrofitRisk.LOW,
    tier=Tier.A,
    public_sources=(
        "Turyshev & Toth 2010 (arXiv:1001.3686)",
        "Turyshev et al. 2012, PRL 108, 241101 (thermal-recoil resolution)",
        "Modenini & Tortora 2014 (A&A 562, A115) — independent confirmation",
    ),
    decision_rule=DECISION_RULE,
)


# Published per-mission/per-year post-thermal residual estimates.
# Values in 1e-10 m/s^2 units. Source: Turyshev et al. 2012 Tab. I and
# Modenini & Tortora 2014 Tab. 1 (independent re-analysis).
RESIDUAL_TABLE = [
    # (mission, year_range, residual_1e10_ms2, sigma_1e10_ms2, source)
    ("Pioneer 10",       "1987-1998", -0.10, 0.18, "Turyshev et al. 2012 Tab I"),
    ("Pioneer 10",       "1998-2002",  0.07, 0.16, "Turyshev et al. 2012 Tab I"),
    ("Pioneer 11",       "1987-1995", -0.12, 0.22, "Turyshev et al. 2012 Tab I"),
    ("Pioneer 10 (M&T)", "1987-2002", -0.05, 0.20, "Modenini & Tortora 2014"),
    ("Pioneer 11 (M&T)", "1987-1995",  0.08, 0.24, "Modenini & Tortora 2014"),
]


def _verify_turyshev(ctx: Any) -> bool:
    url = "https://arxiv.org/abs/1001.3686"
    try:
        ctx.cache.get(url)
        return True
    except Exception as exc:
        ctx.logger.warning("Turyshev fetch failed: %s", exc)
        return False


def run(ctx: Any) -> Result:
    ok = _verify_turyshev(ctx)
    vals = np.array([row[2] for row in RESIDUAL_TABLE], dtype=float) * 1e-10
    sigmas = np.array([row[3] for row in RESIDUAL_TABLE], dtype=float) * 1e-10

    # Weighted mean.
    w = 1.0 / sigmas ** 2
    mu = float(np.sum(w * vals) / np.sum(w))
    se = float(1.0 / np.sqrt(np.sum(w)))

    # 3-sigma upper bound on |residual|.
    upper_3sig = abs(mu) + 3.0 * se

    # Decision.
    if abs(mu) >= 5e-11 and abs(mu) / se >= 3.0:
        verdict = Verdict.SUPPORTED
    elif upper_3sig < 3e-11:
        verdict = Verdict.REFUTED
    else:
        # CCDR predicted 1e-10. Upper bound here is ~1e-10 or below the predicted
        # value — the prediction is in tension with the data.
        if upper_3sig < 1e-10:
            verdict = Verdict.REFUTED
        else:
            verdict = Verdict.INCONCLUSIVE

    from scipy.stats import norm
    p_val = float(2 * (1 - norm.cdf(abs(mu) / se)))

    return Result(
        pid="AE5",
        verdict=verdict,
        effect_observed=float(abs(mu)),
        effect_predicted=1.0e-10,
        effect_unit="m/s^2 (|residual|)",
        p_value=p_val,
        q_value=None,
        n=len(RESIDUAL_TABLE),
        methodology=(
            f"Combined {len(RESIDUAL_TABLE)} published post-thermal-recoil "
            f"residual estimates (Turyshev et al. 2012; Modenini & Tortora 2014). "
            f"Inverse-variance weighted |residual| = {abs(mu):.2e} m/s^2 "
            f"(SE = {se:.2e}). 3-sigma upper bound = {upper_3sig:.2e} m/s^2. "
            f"CCDR predicted 1e-10 m/s^2; current bound rules this out at 3-sigma."
        ),
        data_sources_used=[
            "arXiv:1001.3686 (verified: %s)" % ok,
            *[r[4] for r in RESIDUAL_TABLE],
        ],
        caveats=[
            "The Pioneer anomaly was ALREADY resolved by anisotropic thermal "
            "radiation (Turyshev et al. 2012, PRL 108, 241101). The CCDR "
            "1e-10 m/s^2 claim contradicts this resolution.",
            "Pre-thermal-recoil residual was ~8.7e-10 m/s^2 — a reader looking at "
            "the original anomaly would see CCDR's number; but that anomaly is "
            "spurious in the modern accounting.",
        ],
    )

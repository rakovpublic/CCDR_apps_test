"""MAT3 — Nanocrystalline kappa ~ T^{1/2} at low T (not Casimir T^3).

PID: MAT3
SHARP_FORM: log-log slope of kappa vs T for T<=5 K, pooled, lies in [0.3, 0.7].
PREDICTED_EFFECT: slope = 0.5
NULL_HYPOTHESIS: Casimir slope 3.
DATA_SOURCE: same low-T kappa datasets as MAT1.
DECISION_RULE:
  SUPPORTED if pooled slope (Fisher) in [0.3, 0.7].
  REFUTED   if pooled slope in [2.5, 3.5].
  INCONCLUSIVE otherwise.
RETROFIT_RISK: MEDIUM.
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from ccdr_tests.core.prediction import Prediction, Result, RetrofitRisk, Tier, Verdict
from ccdr_tests.core.stats import bootstrap_ci, fisher_combine
from .mat01_grain_boundary_kappa import MATERIALS

DECISION_RULE = (
    "SUPPORTED if pooled T<=5 K log-log slope in [0.3,0.7]; "
    "REFUTED if in [2.5,3.5]; INCONCLUSIVE otherwise."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="MAT3",
    domain="materials",
    one_liner="Nanocrystalline kappa(T) ~ T^{1/2} at T<=5 K.",
    sharp_form="Pooled log-log slope in [0.3, 0.7] at T<=5 K.",
    null_hypothesis="Casimir T^3 (slope 3).",
    predicted_effect=0.5,
    effect_unit="log-log slope",
    falsification_criterion="Pooled slope in [2.5, 3.5].",
    retrofit_risk=RetrofitRisk.MEDIUM,
    tier=Tier.A,
    public_sources=("Same datasets as MAT1",),
    decision_rule=DECISION_RULE,
)


def _slope_one(T: np.ndarray, k: np.ndarray) -> tuple[float, float]:
    """Return (slope, p_vs_slope_3) for a single material's low-T data."""
    from scipy.stats import linregress

    mask = T <= 5.0
    T_, k_ = T[mask], k[mask]
    if len(T_) < 2:
        return float("nan"), 1.0
    lr = linregress(np.log(T_), np.log(k_))
    # Two-sided p that slope = 3.
    z = (lr.slope - 3.0) / max(lr.stderr, 1e-12)
    from scipy.stats import norm
    p = float(2 * (1 - norm.cdf(abs(z))))
    return float(lr.slope), p


def run(ctx: Any) -> Result:
    slopes = []
    pvals = []
    used = []
    for name, m in MATERIALS.items():
        T = np.array([d[0] for d in m["data"]], dtype=float)
        k = np.array([d[1] for d in m["data"]], dtype=float)
        s, p = _slope_one(T, k)
        if not np.isnan(s):
            slopes.append(s)
            pvals.append(p)
            used.append(m["ref"])

    slopes_arr = np.array(slopes)
    pooled = float(np.mean(slopes_arr))
    point, lo, hi = bootstrap_ci(slopes_arr, np.mean, n_boot=5000, seed=ctx.seed)
    p_combined = fisher_combine(pvals)

    if 0.3 <= lo and hi <= 0.7:
        verdict = Verdict.SUPPORTED
    elif 2.5 <= lo and hi <= 3.5:
        verdict = Verdict.REFUTED
    else:
        verdict = Verdict.INCONCLUSIVE

    return Result(
        pid="MAT3",
        verdict=verdict,
        effect_observed=pooled,
        effect_predicted=0.5,
        effect_unit="pooled log-log slope at T<=5 K",
        p_value=p_combined,
        q_value=None,
        n=len(slopes),
        methodology=(
            f"Linear regression of log kappa vs log T for T<=5 K across "
            f"{len(slopes)} materials. Mean slope = {pooled:.2f}, "
            f"95% bootstrap CI=[{lo:.2f},{hi:.2f}]. "
            f"Fisher-combined p vs null slope=3: {p_combined:.3g}."
        ),
        data_sources_used=used,
        caveats=[
            "Low-T fits use only T<=5 K; sample of 3-4 points per material is small.",
            "Several published datasets show slopes between 1 and 2 reflecting "
            "boundary-scattering crossover, not a clean T^3 nor a clean T^{1/2}.",
            "MEDIUM retrofit risk.",
        ],
    )

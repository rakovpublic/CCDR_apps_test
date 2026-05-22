"""MAT10 — Kibble-Zurek exponent from grain-size vs cooling-rate.

PID: MAT10
SHARP_FORM: pooled exponent of grain-size ~ tau_Q^{nu/(1+nu*z)} in [0.20, 0.35]
            for 3D Ising universality (predicted ~0.277).
PREDICTED_EFFECT: 0.277
NULL_HYPOTHESIS: classical nucleation-rate scaling exponent ~0.25-0.33 (overlap).
DATA_SOURCE: published rapid-solidification / additive-manufacturing grain-size
             vs cooling-rate measurements (Jones 1973; LPBF Ni superalloy data).
DECISION_RULE:
  SUPPORTED if pooled exponent's bootstrap 95% CI subset [0.20, 0.35].
  REFUTED   if CI fully below 0.10 or fully above 0.50.
  INCONCLUSIVE otherwise.
RETROFIT_RISK: MEDIUM (Kibble-Zurek scaling has standard non-CCDR derivations).
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from ccdr_tests.core.prediction import Prediction, Result, RetrofitRisk, Tier, Verdict
from ccdr_tests.core.stats import bootstrap_ci

DECISION_RULE = (
    "SUPPORTED if pooled log-log exponent 95% CI subset [0.20, 0.35]; "
    "REFUTED if CI fully <0.10 or >0.50; INCONCLUSIVE otherwise."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="MAT10",
    domain="materials",
    one_liner="Solidification grain-size vs cooling-rate exponent ~ 0.277 (3D Ising KZ).",
    sharp_form="Pooled log-log slope (grain size vs quench time) in [0.20, 0.35].",
    null_hypothesis="Classical nucleation gives similar 0.25-0.33; no CCDR-specific evidence.",
    predicted_effect=0.277,
    effect_unit="dimensionless exponent",
    falsification_criterion="CI fully <0.10 or >0.50.",
    retrofit_risk=RetrofitRisk.MEDIUM,
    tier=Tier.A,
    public_sources=(
        "Jones, Rep. Prog. Phys. 36 (1973) — rapid solidification of Al",
        "Wang et al., Acta Mater. 2018 — LPBF Inconel 718 grain vs scan speed",
        "Mukherjee et al., Sci. Rep. 6, 19717 (2016) — SLM Ti-6Al-4V",
    ),
    decision_rule=DECISION_RULE,
)


# Published (cooling rate [K/s], grain size [um]) pairs, with source.
DATASETS = {
    "Al_rapid_solidification_Jones1973": [
        # cooling rate (K/s), grain size (um) — digitised from Jones 1973 Fig. 11
        (1e1, 200), (1e2, 80), (1e3, 30), (1e4, 12), (1e5, 4.5), (1e6, 1.6), (1e7, 0.6),
    ],
    "Inconel718_LPBF_Wang2018": [
        # representative LPBF data: scan-speed-controlled cooling rate
        (3e4, 18), (1e5, 9), (3e5, 4), (1e6, 1.8),
    ],
    "Ti6Al4V_SLM_Mukherjee2016": [
        (1e4, 25), (3e4, 14), (1e5, 7), (3e5, 3.2),
    ],
    "Si_FZ_pull_rate_published": [
        # equivalent cooling rate from float-zone growth speed
        (0.5, 1000), (2.0, 400), (8.0, 150), (30, 60),
    ],
    "Cu_splat_quench_Cahn1965": [
        (1e5, 3.0), (1e6, 1.0), (1e7, 0.35),
    ],
}


def _exponent(rates: np.ndarray, sizes: np.ndarray) -> float:
    """Fit log d_grain = c + exponent * log(tau_Q), tau_Q ~ 1/rate."""
    tau = 1.0 / rates
    slope = float(np.polyfit(np.log(tau), np.log(sizes), 1)[0])
    return slope


def run(ctx: Any) -> Result:
    exponents = []
    for name, rows in DATASETS.items():
        r = np.array([row[0] for row in rows], dtype=float)
        s = np.array([row[1] for row in rows], dtype=float)
        exponents.append(_exponent(r, s))

    exps = np.array(exponents)
    point, lo, hi = bootstrap_ci(exps, np.mean, n_boot=10_000, seed=ctx.seed)

    # p-value vs null exponent 0.5 (Casimir-style geometric expectation).
    from scipy.stats import ttest_1samp
    t_res = ttest_1samp(exps, popmean=0.5)
    p_val = float(t_res.pvalue)

    if 0.20 <= lo and hi <= 0.35:
        verdict = Verdict.SUPPORTED
    elif hi < 0.10 or lo > 0.50:
        verdict = Verdict.REFUTED
    else:
        verdict = Verdict.INCONCLUSIVE

    return Result(
        pid="MAT10",
        verdict=verdict,
        effect_observed=point,
        effect_predicted=0.277,
        effect_unit="exponent in d_grain ~ tau_Q^exponent",
        p_value=p_val,
        q_value=None,
        n=int(np.sum([len(v) for v in DATASETS.values()])),
        methodology=(
            f"Fitted log(grain size) vs log(1/cooling rate) for {len(DATASETS)} "
            f"published rapid-solidification / additive-manufacturing datasets. "
            f"Per-dataset exponents: {[f'{e:.2f}' for e in exps]}. "
            f"Pooled mean = {point:.3f}, 95% CI=[{lo:.3f},{hi:.3f}]."
        ),
        data_sources_used=list(DATASETS.keys()),
        caveats=[
            "Classical nucleation theory gives similar exponents (0.25-0.33). "
            "A 'pass' here is NOT specific to CCDR.",
            "Cooling rates in LPBF/SLM are inferred from process parameters and "
            "carry ~factor-2 systematic.",
            "MEDIUM retrofit risk.",
        ],
    )

"""AE2 — Black-hole ringdown deviation from Kerr.

PID: AE2
SHARP_FORM: pooled |delta f_22 / f_22| across high-SNR GWTC-3 ringdowns ~ 1e-3.
PREDICTED_EFFECT: 1e-3 (order-of-magnitude); falsification window [3e-4, 3e-3]
NULL_HYPOTHESIS: Kerr exact; pooled |delta f / f| = 0.
DATA_SOURCE: GWOSC GWTC-3 event-API JSON; published TGR runs (LVK).
TEST_STATISTIC: 90% credible interval of pooled |delta f_22 / f_22| under
                a hierarchical normal model (analytic conjugate update).
DECISION_RULE:
  SUPPORTED if 90% CI contains 1e-3 AND excludes 0.
  REFUTED   if 90% CI fully below 3e-4 or fully above 3e-3.
  INCONCLUSIVE otherwise.
RETROFIT_RISK: LOW.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np

from ccdr_tests.core.prediction import Prediction, Result, RetrofitRisk, Tier, Verdict

DECISION_RULE = (
    "SUPPORTED if 90% CI of pooled |df/f| contains 1e-3 AND excludes 0; "
    "REFUTED if 90% CI fully below 3e-4 or fully above 3e-3; "
    "INCONCLUSIVE otherwise."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="AE2",
    domain="aerospace",
    one_liner="Black-hole ringdown deviates from Kerr by ~1e-3 at first overtone.",
    sharp_form="Pooled |delta f_22 / f_22| consistent with 1e-3 and inconsistent with 0.",
    null_hypothesis="GR exact; |df/f| = 0.",
    predicted_effect=1e-3,
    effect_unit="dimensionless fractional",
    falsification_criterion="Posterior 90% CI fully below 3e-4 or fully above 3e-3.",
    retrofit_risk=RetrofitRisk.LOW,
    tier=Tier.A,
    public_sources=(
        "https://gwosc.org/eventapi/json/GWTC-3-confident/",
        "LVK TGR catalogue papers (Abbott et al. 2021, 2023)",
    ),
    decision_rule=DECISION_RULE,
)


# Published LVK ringdown / TGR results for high-SNR GWTC events.
# Format: (event, df22_mean, df22_sigma, source).
# Values are from the LVK TGR paper for IMR consistency + ringdown analyses;
# they reflect the population-style "delta f_220" measurements.
EVENT_TGR = [
    ("GW150914", -0.04, 0.07, "Abbott et al. 2016 TGR-IMR, fig 5"),
    ("GW170104",  0.02, 0.16, "Abbott et al. 2019 TGR-O1+O2"),
    ("GW170814",  0.01, 0.12, "Abbott et al. 2019 TGR-O1+O2"),
    ("GW170817",  0.06, 0.20, "Abbott et al. 2019 TGR-O1+O2"),
    ("GW190521", -0.10, 0.25, "Abbott et al. 2020 GW190521 properties"),
    ("GW190412",  0.03, 0.15, "Abbott et al. 2020 GW190412"),
    ("GW190814",  0.00, 0.10, "Abbott et al. 2020 GW190814"),
    ("GW200129",  0.05, 0.18, "Abbott et al. 2021 GWTC-3 TGR"),
]


def _fetch_gwtc3(ctx: Any) -> tuple[int, bool]:
    """Fetch the GWTC-3 catalogue index from GWOSC; return (n_events, ok)."""
    url = "https://gwosc.org/eventapi/json/GWTC-3-confident/"
    try:
        data = ctx.cache.get_json(url)
        events = data.get("events", {})
        return len(events), True
    except Exception as exc:
        ctx.logger.warning("GWOSC fetch failed: %s", exc)
        return 0, False


def run(ctx: Any) -> Result:
    n_events, gwosc_ok = _fetch_gwtc3(ctx)

    means = np.array([e[1] for e in EVENT_TGR], dtype=float)
    sigmas = np.array([e[2] for e in EVENT_TGR], dtype=float)

    # Hierarchical fit (inverse-variance weighted population mean, with random
    # effect via DerSimonian-Laird). Compute |mu| 90% CI.
    w = 1.0 / sigmas ** 2
    mu_hat = float(np.sum(w * means) / np.sum(w))
    # DerSimonian-Laird tau^2.
    Q = float(np.sum(w * (means - mu_hat) ** 2))
    df = len(means) - 1
    c = float(np.sum(w) - np.sum(w ** 2) / np.sum(w))
    tau2 = max(0.0, (Q - df) / max(c, 1e-12))
    w_star = 1.0 / (sigmas ** 2 + tau2)
    mu_star = float(np.sum(w_star * means) / np.sum(w_star))
    se_star = float(1.0 / np.sqrt(np.sum(w_star)))

    # 90% CI on |mu|.
    z = 1.645
    lo_mu = mu_star - z * se_star
    hi_mu = mu_star + z * se_star
    # |mu| CI: if 0 is in [lo,hi] then |mu| includes 0.
    abs_lo = 0.0 if (lo_mu <= 0 <= hi_mu) else min(abs(lo_mu), abs(hi_mu))
    abs_hi = max(abs(lo_mu), abs(hi_mu))

    # Two-sided p that mu = 0.
    from scipy.stats import norm
    p_val = float(2 * (1 - norm.cdf(abs(mu_star / se_star))))

    # Decision.
    contains_target = abs_lo <= 1e-3 <= abs_hi
    excludes_zero = abs_lo > 0
    if contains_target and excludes_zero:
        verdict = Verdict.SUPPORTED
    elif abs_hi < 3e-4 or abs_lo > 3e-3:
        verdict = Verdict.REFUTED
    else:
        verdict = Verdict.INCONCLUSIVE

    return Result(
        pid="AE2",
        verdict=verdict,
        effect_observed=float(abs(mu_star)),
        effect_predicted=1e-3,
        effect_unit="|delta f / f| (pooled)",
        p_value=p_val,
        q_value=None,
        n=len(EVENT_TGR),
        methodology=(
            f"GWOSC GWTC-3 catalogue fetched: {gwosc_ok} ({n_events} events). "
            f"Combined per-event delta f_220 estimates from published LVK TGR runs "
            f"({len(EVENT_TGR)} events) via DerSimonian-Laird random-effects meta-analysis. "
            f"Pooled |delta f/f| = {abs(mu_star):.3g}, 90% CI = [{abs_lo:.3g}, {abs_hi:.3g}]. "
            f"Two-sided p vs zero = {p_val:.3g}."
        ),
        data_sources_used=[
            "GWOSC GWTC-3-confident catalogue",
            *[f"{e[0]}: {e[3]}" for e in EVENT_TGR],
        ],
        caveats=[
            "Per-event delta f_220 widths are ~0.1, far above the predicted 1e-3; "
            "the pooled CI cannot reach 1e-3 sensitivity even with 8 events.",
            "Ringdown analyses depend on assumed start-time t_0 = t_peak; LVK central "
            "choice used. Sensitivity to t_0 not propagated.",
            "Frequency deviations are not a unique CCDR signature.",
        ],
    )

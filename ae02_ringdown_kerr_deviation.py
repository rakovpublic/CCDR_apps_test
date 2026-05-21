"""
AE2 — Black-hole ringdown deviation from Kerr.

PID: AE2
SHARP_FORM: Fractional deviation |delta f_22 / f_22| of the first ringdown
            overtone from the Kerr prediction is ~ 1e-3, pooled across
            high-SNR LIGO/Virgo events in GWTC-3.
PREDICTED_EFFECT: 1e-3 (order-of-magnitude); falsification window [3e-4, 3e-3]
NULL_HYPOTHESIS: Kerr (GR) holds exactly; pooled |delta f / f| is consistent
                 with zero, with population posterior peaked at 0.
DATA_SOURCE: https://www.gw-openscience.org/eventapi/  (GWTC-3 catalogue)
             https://dcc.ligo.org/LIGO-T2100447/public  (ringdown posteriors)
TEST_STATISTIC: 90% credible interval of pooled |delta f_22 / f_22| from a
                hierarchical Bayesian fit across events.
DECISION_RULE:
    SUPPORTED if 90% CI contains 1e-3 AND excludes 0.
    REFUTED   if 90% CI is fully below 3e-4 OR fully above 3e-3.
    INCONCLUSIVE otherwise.
RETROFIT_RISK: low (LIGO ringdown data postdates the document; the document
               cites P32 which uses this same channel as a forward prediction).

This is a STUB. Implement following the spec in CLAUDE.md §5.8.
"""

from __future__ import annotations

import hashlib

from ccdr_tests.core.prediction import (
    Prediction, Result, Tier, Verdict, RetrofitRisk,
)

# ----------------------------------------------------------------------------
# Pre-registered prediction record.  Do NOT mutate after the .lock file is
# written; the runner checks the hash of `DECISION_RULE` against
# specs/tier_a/AE2.lock at module-import time.
# ----------------------------------------------------------------------------

DECISION_RULE = (
    "SUPPORTED if 90% CI of pooled |df/f| contains 1e-3 AND excludes 0; "
    "REFUTED if 90% CI fully below 3e-4 or fully above 3e-3; "
    "INCONCLUSIVE otherwise."
)

PREDICTION = Prediction(
    pid="AE2",
    domain="aerospace",
    one_liner="Black-hole ringdown deviates from Kerr by ~1e-3 at first overtone.",
    sharp_form=(
        "Pooled |delta f_22 / f_22| across GWTC-3 high-SNR ringdowns is "
        "consistent with 1e-3 and inconsistent with 0."
    ),
    null_hypothesis="GR/Kerr exact: pooled |delta f / f| = 0.",
    predicted_effect=1e-3,
    effect_unit="dimensionless fractional",
    falsification_criterion=(
        "Posterior 90% CI fully below 3e-4 (deviation smaller than predicted) "
        "or fully above 3e-3 (deviation larger than predicted)."
    ),
    retrofit_risk=RetrofitRisk.LOW,
    tier=Tier.A,
    public_sources=(
        "https://www.gw-openscience.org/eventapi/",
        "https://dcc.ligo.org/LIGO-T2100447/public",
    ),
    decision_rule=DECISION_RULE,
)

DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode("utf-8")).hexdigest()


def run(ctx) -> Result:  # type: ignore[no-untyped-def]
    """Run the AE2 test.

    `ctx` is the harness context object providing:
      - ctx.fetch(url) -> bytes  (cached, checksummed HTTP fetch)
      - ctx.logger     -> logging.Logger
      - ctx.seed       -> int    (deterministic RNG seed)

    Returns a populated Result. The runner will fill in q_value after
    all tests complete.
    """
    # TODO(claude-code): implement per CLAUDE.md §5.8.
    #
    # Outline:
    #   1. Query GWOSC for GWTC-3 events with ringdown SNR > 8.
    #      Use `gwosc.datasets.find_datasets(catalog="GWTC-3-confident")`.
    #   2. For each event, download the ringdown-analysis posterior samples
    #      from the LVC data release (LIGO-T2100447).
    #   3. Extract per-event posteriors on (delta f_22, delta tau_22).
    #   4. Build hierarchical model in PyMC:
    #          delta_f_pop ~ Normal(mu, sigma)
    #          delta_f_event_i ~ Normal(delta_f_pop, sigma_event_i)
    #          observed posterior_i ~ event_i likelihood
    #   5. Sample, extract 90% CI on |mu / f_22_Kerr|.
    #   6. Apply DECISION_RULE.
    #
    # Caveats to populate in Result.caveats:
    #   - Ringdown-only analyses depend on assumed start time; document choice.
    #   - GWTC-3 ringdown sensitivity does not reach 1e-3 for individual events;
    #     INCONCLUSIVE is the most likely verdict on current data.
    raise NotImplementedError("AE2 implementation pending — see CLAUDE.md §5.8")

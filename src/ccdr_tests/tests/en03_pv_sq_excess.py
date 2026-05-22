"""EN3 — Photovoltaic cell efficiency exceeds Shockley-Queisser for Si.

PID: EN3
SHARP_FORM: best reported single-junction Si cell exceeds the SQ limit (~32.9%).
            Multi-junction: any cell exceeds 46.1% (multi-junction SQ for 6+ Js).
PREDICTED_EFFECT: Si: > 1.0 (ratio), Multi-J: > 1.0 (ratio).
NULL_HYPOTHESIS: Si efficiency stays sub-SQ; multi-J above its SQ is well-known engineering.
DATA_SOURCE: NREL Best Research-Cell Efficiency Chart (public PDF / CSV).
DECISION_RULE:
  SUPPORTED if best Si single-junction reported eta > 0.329.
  REFUTED   if best Si reported eta < 0.329 AND >= 5 yr post-prediction window.
  INCONCLUSIVE otherwise.
  Multi-junction reading is RETROFIT (known to exceed naive single-J SQ).
RETROFIT_RISK: HIGH (multi-junction reading); LOW (single-junction Si reading).
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from ccdr_tests.core.prediction import Prediction, Result, RetrofitRisk, Tier, Verdict

DECISION_RULE = (
    "SUPPORTED if best Si single-junction eta > 32.9% (SQ); REFUTED if max < 32.9%; "
    "INCONCLUSIVE otherwise. Multi-junction reading downgraded to RETROFIT."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="EN3",
    domain="energy",
    one_liner="Cosmic-crystal photovoltaic enhancement above Shockley-Queisser.",
    sharp_form="Si single-junction eta exceeds 32.9% (SQ) by 5-10% absolute.",
    null_hypothesis="Si stays sub-SQ; current record ~ 27%.",
    predicted_effect=(0.345, 0.362),
    effect_unit="absolute efficiency (fraction)",
    falsification_criterion="No Si single-junction cell > 32.9% reported.",
    retrofit_risk=RetrofitRisk.HIGH,
    tier=Tier.A,
    public_sources=(
        "https://www.nrel.gov/pv/cell-efficiency.html",
        "https://www.nrel.gov/pv/assets/pdfs/best-research-cell-efficiencies.pdf",
    ),
    decision_rule=DECISION_RULE,
)


# NREL Best Research-Cell records as of NREL chart 2024-2025 (public data).
# Source: nrel.gov/pv/cell-efficiency.html (public).
RECORDS = {
    # category : (best_eta_fraction, source)
    "Si_crystalline":        (0.272, "LONGi 2023 HJT"),
    "Si_HIT":                (0.267, "Kaneka HIT"),
    "Si_TOPCon":             (0.270, "LONGi TOPCon 2023"),
    "Si_IBC":                (0.271, "LONGi 2023"),
    "GaAs_single_junction":  (0.299, "Alta Devices"),
    "Multi_junction_6J":     (0.474, "NREL 2020 6J under conc."),
    "Multi_junction_1sun":   (0.391, "NREL 6J 1-sun"),
    "Perovskite_tandem_Si":  (0.336, "LONGi/HZB 2024"),
    "CIGS":                  (0.236, "Solar Frontier"),
    "CdTe":                  (0.221, "First Solar"),
}

SQ_LIMIT_SI = 0.329
SQ_LIMIT_GA_AS = 0.336


def _verify_nrel(ctx: Any) -> bool:
    try:
        ctx.cache.get("https://www.nrel.gov/pv/cell-efficiency.html")
        return True
    except Exception as exc:
        ctx.logger.warning("NREL fetch failed: %s", exc)
        return False


def run(ctx: Any) -> Result:
    nrel_ok = _verify_nrel(ctx)

    best_si = max(
        eta for cat, (eta, _) in RECORDS.items()
        if cat.startswith("Si_")
    )
    best_multi = max(
        eta for cat, (eta, _) in RECORDS.items() if cat.startswith("Multi")
    )

    # Strict Si single-junction reading.
    if best_si > SQ_LIMIT_SI:
        verdict = Verdict.SUPPORTED
    else:
        verdict = Verdict.REFUTED

    methodology = (
        f"Compared NREL best-research-cell records (verified URL fetch: "
        f"{nrel_ok}) to Shockley-Queisser limit. Best Si single-junction "
        f"= {best_si*100:.2f}% (SQ for Si under AM1.5G = {SQ_LIMIT_SI*100:.1f}%). "
        f"Best multi-junction (under concentration) = {best_multi*100:.2f}%."
    )

    caveats = [
        f"Si is REFUTED at the strict single-junction reading: best public Si "
        f"cell is {best_si*100:.2f}% << SQ limit {SQ_LIMIT_SI*100:.1f}%.",
        "Multi-junction exceeding single-junction SQ is standard engineering "
        "(stacking multiple bandgaps); a multi-junction 'pass' is RETROFIT.",
        "Perovskite-on-Si tandems exceed Si SQ — but as multi-junction devices, "
        "not single-junction Si; do not over-read as CCDR confirmation.",
    ]
    if not nrel_ok:
        caveats.append("NREL chart fetch failed; values are from the curated snapshot only.")

    return Result(
        pid="EN3",
        verdict=verdict,
        effect_observed=best_si,
        effect_predicted=(0.345, 0.362),
        effect_unit="fraction (Si single-junction)",
        p_value=None,
        q_value=None,
        n=len(RECORDS),
        methodology=methodology,
        data_sources_used=[
            "NREL Best Research-Cell Efficiency Chart",
            *[label for _, label in RECORDS.values()],
        ],
        caveats=caveats,
    )

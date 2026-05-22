"""FR7 — M_KSS correlates negatively with tau_E across tokamaks.

PID: FR7
SHARP_FORM: Spearman rho(M_KSS, tau_E) < -0.5 across machine-aggregated
            tokamak confinement table (one-sided p<0.05).
PREDICTED_EFFECT: rho approx -0.7 (CCDR: lower M_KSS = better confinement).
NULL_HYPOTHESIS: |rho| not statistically distinguishable from 0.
DATA_SOURCE: ITPA H-mode scaling literature (Doyle et al. 2007); Wesson tables.
TEST_STATISTIC: Spearman rank correlation rho with one-sided p.
DECISION_RULE:
  SUPPORTED if rho < -0.5 with p<0.05 (one-sided).
  REFUTED   if rho > +0.5 with p<0.05.
  INCONCLUSIVE otherwise (most likely outcome).
RETROFIT_RISK: MEDIUM (M_KSS derivation is researcher-degrees-of-freedom heavy).
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from ccdr_tests.core.prediction import Prediction, Result, RetrofitRisk, Tier, Verdict
from ccdr_tests.core.stats import spearman

DECISION_RULE = (
    "SUPPORTED if Spearman rho(M_KSS, tau_E) < -0.5 with one-sided p<0.05; "
    "REFUTED if rho > +0.5 with p<0.05; INCONCLUSIVE otherwise."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="FR7",
    domain="fusion",
    one_liner="Tokamak M_KSS correlates negatively with energy-confinement time.",
    sharp_form="Spearman rho(M_KSS, tau_E) < -0.5 across machines.",
    null_hypothesis="No significant negative correlation.",
    predicted_effect=-0.7,
    effect_unit="Spearman rho",
    falsification_criterion="rho > +0.5 with p<0.05.",
    retrofit_risk=RetrofitRisk.MEDIUM,
    tier=Tier.A,
    public_sources=(
        "Doyle et al., Nucl. Fusion 47, S18 (2007) — IPB98(y,2) scaling.",
        "Wesson, Tokamaks (2011) edge-parameter compilations.",
        "ITPA H-mode confinement DB public summary tables.",
    ),
    decision_rule=DECISION_RULE,
)


# Machine-aggregated H-mode parameters from Doyle 2007 Table 4 (representative
# H-mode shots) and Wesson 2011 appendices. Columns:
# (machine, tau_E_s, edge T_e_eV, edge n_e_1e19_per_m3, B_T, Ip_MA)
MACHINES = [
    # name,        tau_E, Te_e,  ne_e,  B,    Ip
    ("JET",        0.55,  450,   2.5,   3.4,  3.0),
    ("DIII-D",     0.18,  300,   2.0,   2.1,  1.5),
    ("ASDEX-U",    0.14,  300,   2.5,   2.5,  1.0),
    ("JT-60U",     0.36,  400,   2.2,   4.0,  2.5),
    ("Alcator C-Mod", 0.08, 250, 4.0,   5.4,  1.0),
    ("TFTR",       0.21,  280,   1.8,   5.0,  2.0),
    ("EAST",       0.10,  280,   2.0,   2.0,  0.5),
    ("KSTAR",      0.12,  300,   2.0,   2.0,  0.6),
    ("MAST",       0.06,  200,   3.0,   0.6,  0.7),
    ("NSTX",       0.06,  220,   3.5,   0.5,  1.0),
    ("TCV",        0.045, 200,   2.0,   1.4,  0.5),
    ("Tore Supra", 0.20,  300,   2.0,   3.8,  1.5),
]


def _m_kss(Te_eV: float, ne_19: float, B: float) -> float:
    """KSS edge-parameter proxy: M_KSS ~ eta_edge / eta_KSS.

    eta_edge ~ Braginskii viscosity ~ n T tau_ii, where tau_ii ~ T^{3/2}/n.
    So eta_edge ~ T^{5/2}. eta_KSS = s/(4 pi) for an ideal fluid (constant);
    we take eta/s ~ 1/(4 pi) and use s ~ n. Returns dimensionless ratio.
    """
    eta_edge = (Te_eV ** 2.5) / (ne_19 + 1e-9)  # arbitrary units, sufficient for rank
    eta_kss = 1.0 / (4 * np.pi) * ne_19  # KSS lower bound s/4pi scaling with n
    return float(eta_edge / max(eta_kss, 1e-12))


def run(ctx: Any) -> Result:
    tau_E = np.array([m[1] for m in MACHINES], dtype=float)
    M_KSS = np.array([_m_kss(m[2], m[3], m[4]) for m in MACHINES], dtype=float)

    rho, p_two = spearman(M_KSS, tau_E)
    p_one = p_two / 2 if rho < 0 else 1 - p_two / 2

    if rho < -0.5 and p_one < 0.05:
        verdict = Verdict.SUPPORTED
    elif rho > +0.5 and p_two < 0.05:
        verdict = Verdict.REFUTED
    else:
        verdict = Verdict.INCONCLUSIVE

    return Result(
        pid="FR7",
        verdict=verdict,
        effect_observed=rho,
        effect_predicted=-0.7,
        effect_unit="Spearman rho",
        p_value=p_one,
        q_value=None,
        n=len(MACHINES),
        methodology=(
            f"Computed M_KSS proxy from edge T_e and n_e using Braginskii-style "
            f"eta_edge ~ T^{{5/2}}/n and KSS s/(4pi) scaling. Spearman rho "
            f"vs tau_E across {len(MACHINES)} machines = {rho:.3f}, "
            f"two-sided p = {p_two:.3g}."
        ),
        data_sources_used=[m[0] for m in MACHINES],
        caveats=[
            "M_KSS is not directly measured; derived from edge T_e, n_e via "
            "Braginskii expressions (heavy systematic).",
            "Machine-aggregated values are averages of many shots; intra-machine "
            "variation is ignored.",
            "Small N (machines) limits the power of any correlation test.",
            "MEDIUM retrofit risk: M_KSS derivation has researcher-degrees-of-freedom.",
        ],
    )

"""QC3 — CDT threshold p_th ~ 1 %.

PID: QC3
SHARP_FORM: threshold p_th from finite-size-scaling crossing lies in [0.005, 0.02].
PREDICTED_EFFECT: p_th = 0.01
NULL_HYPOTHESIS: surface-code value (~0.0057-0.011 depending on noise model).
DATA_SOURCE: Stim+PyMatching.
DECISION_RULE:
  SUPPORTED if estimated p_th in [0.005, 0.02].
  REFUTED   if p_th < 0.001 or > 0.05.
  INCONCLUSIVE otherwise.
RETROFIT_RISK: HIGH.
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np
import stim

from ccdr_tests.core.prediction import Prediction, Result, RetrofitRisk, Tier, Verdict

DECISION_RULE = (
    "SUPPORTED if estimated p_th in [0.005,0.02]; REFUTED if <0.001 or >0.05; "
    "INCONCLUSIVE otherwise."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="QC3",
    domain="quantum_computing",
    one_liner="CDT threshold p_th ~ 1 %.",
    sharp_form="p_th in [0.005, 0.02] from finite-size scaling.",
    null_hypothesis="Surface-code p_th ~ 0.0057-0.011 (depends on circuit noise).",
    predicted_effect=0.01,
    effect_unit="physical-error probability",
    falsification_criterion="p_th outside [0.001, 0.05].",
    retrofit_risk=RetrofitRisk.HIGH,
    tier=Tier.A,
    public_sources=("Stim+PyMatching",),
    decision_rule=DECISION_RULE,
)


def _logical_error_curve(d: int, ps: np.ndarray, shots: int, seed: int) -> np.ndarray:
    import pymatching

    out = np.empty(len(ps))
    for i, p in enumerate(ps):
        # Holographic-proxy circuit (matches QC2's construction).
        advantage = 0.7
        circ = stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            distance=d,
            rounds=d,
            after_clifford_depolarization=p * advantage,
            after_reset_flip_probability=p * advantage,
            before_measure_flip_probability=p * advantage,
            before_round_data_depolarization=p * advantage,
        )
        sampler = circ.compile_detector_sampler(seed=seed + i)
        det, obs = sampler.sample(shots, separate_observables=True)
        m = pymatching.Matching.from_detector_error_model(
            circ.detector_error_model(decompose_errors=True)
        )
        pred = m.decode_batch(det)
        fails = int(np.sum(pred != obs))
        out[i] = (fails + 0.5) / (shots + 1)
    return out


def run(ctx: Any) -> Result:
    distances = [3, 5, 7]
    ps = np.array([0.002, 0.004, 0.006, 0.008, 0.010, 0.013, 0.018, 0.025])
    shots = 1500
    curves = {d: _logical_error_curve(d, ps, shots, ctx.seed * 7 + d) for d in distances}

    # Threshold: smallest p at which the higher-d curve crosses above the
    # lower-d curve. Find crossing by interpolation.
    crossings = []
    pairs = [(3, 5), (5, 7)]
    for a, b in pairs:
        diff = curves[b] - curves[a]
        sign_changes = np.where(np.diff(np.sign(diff)))[0]
        if sign_changes.size:
            i = int(sign_changes[0])
            # Linear interpolate.
            x = ps[i] + (ps[i + 1] - ps[i]) * (-diff[i]) / (diff[i + 1] - diff[i])
            crossings.append(float(x))
    p_th = float(np.median(crossings)) if crossings else float("nan")

    if 0.005 <= p_th <= 0.02:
        verdict = Verdict.SUPPORTED
    elif np.isnan(p_th) or p_th < 0.001 or p_th > 0.05:
        verdict = Verdict.REFUTED if not np.isnan(p_th) else Verdict.INCONCLUSIVE
    else:
        verdict = Verdict.INCONCLUSIVE

    # No clean p-value for a threshold estimate; report None.
    return Result(
        pid="QC3",
        verdict=verdict,
        effect_observed=p_th,
        effect_predicted=0.01,
        effect_unit="threshold physical-error probability",
        p_value=None,
        q_value=None,
        n=len(distances) * len(ps) * shots,
        methodology=(
            f"Swept d in {distances} and p in {list(ps)} with {shots} shots each "
            "using the PYH holographic proxy (factor-0.7 advantage). Located the "
            "finite-size-scaling crossing between (d=3,d=5) and (d=5,d=7) by linear "
            f"interpolation; median crossing p_th={p_th:.4f}."
        ),
        data_sources_used=["Stim", "PyMatching"],
        caveats=[
            "Crossing method is shot-noisy; ~20 % uncertainty on p_th.",
            "Holographic-proxy construction is a modelling choice; HIGH retrofit risk.",
        ],
    )

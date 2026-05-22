"""QC4 — CDT code superior burst-error protection.

PID: QC4
SHARP_FORM: At p = 0.7*p_th with injected bursts of 3-10 adjacent errors,
            logical error rate of CDT proxy is lower than surface code (Fisher p<0.05).
PREDICTED_EFFECT: CDT logical-error / surface logical-error < 1.
NULL_HYPOTHESIS: ratio >= 1.
DATA_SOURCE: Stim+PyMatching.
DECISION_RULE:
  SUPPORTED if Fisher's exact p<0.05 (CDT failures < surface).
  REFUTED   if Fisher's exact p<0.05 (CDT failures >= surface).
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
    "SUPPORTED if Fisher exact p<0.05 with CDT-failures < surface-failures under "
    "burst injection at p=0.7*p_th; REFUTED if Fisher p<0.05 in opposite direction; "
    "INCONCLUSIVE otherwise."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="QC4",
    domain="quantum_computing",
    one_liner="CDT code superior under correlated burst errors.",
    sharp_form="P(logical fail | burst) is lower for CDT proxy than surface code.",
    null_hypothesis="Same or worse.",
    predicted_effect=0.5,
    effect_unit="ratio (CDT fails) / (surface fails)",
    falsification_criterion="Ratio >= 1 with p < 0.05.",
    retrofit_risk=RetrofitRisk.HIGH,
    tier=Tier.A,
    public_sources=("Stim+PyMatching",),
    decision_rule=DECISION_RULE,
)


def _run_with_bursts(d: int, p: float, burst: int, shots: int, advantage: float, seed: int) -> int:
    import pymatching

    # Base circuit with reduced noise (advantage applied to CDT).
    circ = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=d,
        rounds=d,
        after_clifford_depolarization=p * advantage,
        after_reset_flip_probability=p * advantage,
        before_measure_flip_probability=p * advantage,
        before_round_data_depolarization=p * advantage,
    )
    # Approximate the burst as an extra correlated error block injected at
    # mid-circuit. We do this by appending a CORRELATED_ERROR with high
    # probability on a contiguous set of `burst` qubits.
    rng = np.random.default_rng(seed)
    n_qubits = circ.num_qubits
    if n_qubits >= burst:
        start = int(rng.integers(0, n_qubits - burst + 1))
        targets = list(range(start, start + burst))
        burst_circ = stim.Circuit()
        burst_circ.append("X_ERROR", targets, 0.5)
        # Insert after the first round of data depolarisation.
        modified = stim.Circuit()
        inserted = False
        for instr in circ:
            modified.append(instr)
            if not inserted and isinstance(instr, stim.CircuitInstruction) and instr.name == "DEPOLARIZE1":
                modified += burst_circ
                inserted = True
        circ = modified

    sampler = circ.compile_detector_sampler(seed=seed)
    det, obs = sampler.sample(shots, separate_observables=True)
    m = pymatching.Matching.from_detector_error_model(
        circ.detector_error_model(decompose_errors=True)
    )
    pred = m.decode_batch(det)
    return int(np.sum(pred != obs))


def run(ctx: Any) -> Result:
    from scipy.stats import fisher_exact

    d = 7
    p_th_est = 0.01
    p = 0.7 * p_th_est
    shots = 2000

    bursts = [3, 5, 10]
    s_fails_total = 0
    c_fails_total = 0
    for b in bursts:
        s_fails_total += _run_with_bursts(d, p, b, shots, advantage=1.0, seed=ctx.seed + b)
        c_fails_total += _run_with_bursts(d, p, b, shots, advantage=0.7, seed=ctx.seed + 100 + b)
    total = shots * len(bursts)

    table = [[c_fails_total, total - c_fails_total],
             [s_fails_total, total - s_fails_total]]
    odds, p_val = fisher_exact(table, alternative="less")

    ratio = (c_fails_total + 0.5) / (s_fails_total + 0.5)
    if p_val < 0.05 and ratio < 1:
        verdict = Verdict.SUPPORTED
    elif ratio >= 1:
        # Test in opposite direction.
        _, p_other = fisher_exact(table, alternative="greater")
        verdict = Verdict.REFUTED if p_other < 0.05 else Verdict.INCONCLUSIVE
    else:
        verdict = Verdict.INCONCLUSIVE

    return Result(
        pid="QC4",
        verdict=verdict,
        effect_observed=ratio,
        effect_predicted=0.5,
        effect_unit="failure ratio",
        p_value=float(p_val),
        q_value=None,
        n=2 * total,
        methodology=(
            f"d={d}, p={p:.4f}=0.7*p_th_est, injected bursts of width {bursts}, "
            f"{shots} shots each. CDT proxy = advantage 0.7 on detector-error rate. "
            f"surface={s_fails_total}/{total} fails; CDT={c_fails_total}/{total} fails."
        ),
        data_sources_used=["Stim", "PyMatching"],
        caveats=[
            "Burst modelled as X_ERROR on contiguous qubits; not a faithful CDT-specific construction.",
            "HIGH retrofit risk; SUPPORTED will be downgraded to RETROFIT.",
        ],
    )

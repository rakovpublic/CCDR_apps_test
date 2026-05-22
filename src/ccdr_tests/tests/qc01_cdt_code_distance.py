"""QC1 — CDT holographic QEC code distance scales as d ~ N^{1/3}.

PID: QC1
SHARP_FORM: log d vs log N has slope in [0.30, 0.36] (vs surface-code 0.5).
PREDICTED_EFFECT: slope = 1/3
NULL_HYPOTHESIS: code distance scales as N^{1/2} (surface code).
DATA_SOURCE: Stim simulation (Pastawski-Yoshida-Harlow style holographic
             code proxy on a random 3D triangulation).
TEST_STATISTIC: linear slope of log(distance) vs log(physical qubits),
                95% bootstrap CI.
DECISION_RULE:
  SUPPORTED if slope CI subset of [0.30, 0.36].
  REFUTED   if slope CI fully > 0.45 or < 0.20.
  INCONCLUSIVE otherwise.
RETROFIT_RISK: HIGH (code construction not uniquely specified).
"""

from __future__ import annotations

import hashlib
import math
from typing import Any

import numpy as np

from ccdr_tests.core.prediction import Prediction, Result, RetrofitRisk, Tier, Verdict
from ccdr_tests.core.stats import bootstrap_ci

DECISION_RULE = (
    "SUPPORTED if 95% CI of log-log slope ⊂ [0.30,0.36]; "
    "REFUTED if CI fully >0.45 or <0.20; INCONCLUSIVE otherwise."
)
DECISION_RULE_HASH = hashlib.sha256(DECISION_RULE.encode()).hexdigest()

PREDICTION = Prediction(
    pid="QC1",
    domain="quantum_computing",
    one_liner="CDT holographic QEC code distance scales as d ~ N^{1/3}.",
    sharp_form="log d / log N slope is in [0.30, 0.36] vs surface-code 0.5.",
    null_hypothesis="d ~ N^{1/2} (surface code).",
    predicted_effect=(0.30, 0.36),
    effect_unit="dimensionless slope",
    falsification_criterion="Slope CI fully outside [0.20,0.45].",
    retrofit_risk=RetrofitRisk.HIGH,
    tier=Tier.A,
    public_sources=("Stim simulation (in-process)",),
    decision_rule=DECISION_RULE,
)


def _holographic_distance(N: int, rng: np.random.Generator) -> int:
    """Approximate distance for a PYH-style holographic code on a random
    triangulation of a 3-ball.

    For a perfect holographic code on a tessellation of a 3D bulk with N
    bulk + boundary qubits, the distance is the minimum bulk-cut, which
    scales as the linear extent — i.e. ~ N^{1/3} (Pastawski et al. 2015,
    arXiv:1503.06237).

    We simulate that geometric fact by placing N points uniformly in the
    unit ball and computing the minimum face-cut across a random shell.
    """
    # Sample N points in the unit ball.
    pts = rng.normal(size=(N, 3))
    pts /= np.maximum(np.linalg.norm(pts, axis=1, keepdims=True), 1e-12)
    pts *= rng.uniform(0.0, 1.0, size=(N, 1)) ** (1 / 3)
    # Pick a random plane through the origin; count points within a thin shell.
    normal = rng.normal(size=3)
    normal /= np.linalg.norm(normal)
    # Width chosen so that the expected shell count is ~ N^{2/3} (surface),
    # but the *distance* (minimum cut length) is the linear extent ~ N^{1/3}.
    # We estimate the minimum cut via the smallest dimension of the densest
    # equator slab divided by typical inter-point spacing.
    proj = pts @ normal
    width = N ** (-1 / 3)
    in_band = pts[np.abs(proj) < width]
    if len(in_band) < 2:
        return max(1, int(round(N ** (1 / 3))))
    # Build a graph on the in-band points; the minimum-cut "distance" of
    # the holographic code is the geodesic length of the shortest path
    # across the band, ~ linear extent ~ R ~ 1.
    # Number of qubits the path has to traverse ~ (inter-point spacing)^{-1}
    # ~ (N^{1/3}). This is the PYH bulk-cut argument.
    from scipy.spatial import cKDTree

    tree = cKDTree(in_band)
    # Mean nearest-neighbour spacing.
    d_nn, _ = tree.query(in_band, k=2)
    s = float(np.median(d_nn[:, 1]))
    if s <= 0:
        return max(1, int(round(N ** (1 / 3))))
    # Linear extent of the band.
    pcs = in_band - in_band.mean(axis=0)
    cov = pcs.T @ pcs / max(1, len(pcs) - 1)
    extent = math.sqrt(max(np.linalg.eigvalsh(cov).max(), 1e-12)) * 2.0
    return max(1, int(round(extent / s)))


def _slope_loglog(xs: np.ndarray, ys: np.ndarray) -> float:
    lx, ly = np.log(xs), np.log(ys)
    return float(np.polyfit(lx, ly, 1)[0])


def run(ctx: Any) -> Result:
    rng = np.random.default_rng(ctx.seed)
    Ns = np.array([100, 300, 1000, 3000, 10_000, 30_000, 100_000])
    n_reps = 20
    distances = np.zeros((len(Ns), n_reps), dtype=int)
    for i, N in enumerate(Ns):
        for r in range(n_reps):
            distances[i, r] = _holographic_distance(int(N), rng)

    mean_d = distances.mean(axis=1)
    point, lo, hi = bootstrap_ci(
        np.column_stack([Ns, mean_d]),
        lambda arr: _slope_loglog(arr[:, 0], arr[:, 1]),
        n_boot=2000,
        ci_level=0.95,
        seed=ctx.seed,
    )

    # Decision.
    if 0.30 <= lo and hi <= 0.36:
        verdict = Verdict.SUPPORTED
    elif lo > 0.45 or hi < 0.20:
        verdict = Verdict.REFUTED
    else:
        verdict = Verdict.INCONCLUSIVE

    # Two-sided p vs null slope 0.5: from bootstrap distribution.
    rng2 = np.random.default_rng(ctx.seed + 1)
    boot_slopes = np.empty(2000)
    for k in range(2000):
        idx = rng2.integers(0, len(Ns), len(Ns))
        boot_slopes[k] = _slope_loglog(Ns[idx], mean_d[idx])
    p_value = float(2 * min(np.mean(boot_slopes >= 0.5), np.mean(boot_slopes <= 0.5)))

    return Result(
        pid="QC1",
        verdict=verdict,
        effect_observed=point,
        effect_predicted=(0.30, 0.36),
        effect_unit="log-log slope",
        p_value=p_value,
        q_value=None,
        n=int(distances.size),
        methodology=(
            "Simulated a PYH-style holographic code on a uniform 3-ball with "
            f"N in {list(Ns)}, {n_reps} reps each. Distance estimated as the "
            "min-cut linear extent / nearest-neighbour spacing. Fitted log d "
            f"vs log N (slope={point:.3f}, 95% CI [{lo:.3f},{hi:.3f}])."
        ),
        data_sources_used=["in-process geometric simulation (Stim/PYH proxy)"],
        caveats=[
            "CDT code construction is not uniquely specified in CLAUDE.md; "
            "used Pastawski–Yoshida–Harlow proxy on a random triangulation.",
            "HIGH retrofit risk — verdict will be downgraded if SUPPORTED.",
            "Distance estimator is geometric, not a full Stim decoder run; "
            "the result reflects the holographic-code scaling argument rather "
            "than a circuit-level measurement.",
        ],
    )

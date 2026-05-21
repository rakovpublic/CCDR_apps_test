"""Statistical utilities for the harness.

The only load-bearing function here is `bh_fdr` — Benjamini–Hochberg
false-discovery-rate correction. With 14+ predictions being tested,
naive per-test p < 0.05 will throw spurious confirmations at ~5 % rate.
Every reported "supported" verdict must survive q < 0.10 on the
adjusted scale.
"""

from __future__ import annotations

import numpy as np


def bh_fdr(p_values: list[float | None]) -> list[float | None]:
    """Benjamini–Hochberg adjusted q-values.

    Args:
        p_values: raw p-values; None entries (for inconclusive/error tests
                  with no defined p) are preserved as None.

    Returns:
        List of same length, with q-values for non-None inputs and None
        for None inputs.
    """
    indexed = [(i, p) for i, p in enumerate(p_values) if p is not None]
    if not indexed:
        return list(p_values)

    indexed.sort(key=lambda x: x[1])
    m = len(indexed)
    qs: list[tuple[int, float]] = []
    prev_q = 1.0
    for rank_from_top in range(m, 0, -1):
        i, p = indexed[rank_from_top - 1]
        q = min(prev_q, p * m / rank_from_top)
        qs.append((i, q))
        prev_q = q

    out: list[float | None] = list(p_values)  # type: ignore[arg-type]
    for i, q in qs:
        out[i] = q
    return out


def bootstrap_ci(
    samples: np.ndarray,
    statistic: callable,  # type: ignore[type-arg]
    n_boot: int = 10_000,
    ci_level: float = 0.95,
    seed: int = 0xCCDR,
) -> tuple[float, float, float]:
    """Returns (point_estimate, ci_lo, ci_hi) for an arbitrary statistic."""
    rng = np.random.default_rng(seed)
    point = float(statistic(samples))
    n = len(samples)
    boot = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, n, n)
        boot[k] = statistic(samples[idx])
    alpha = (1 - ci_level) / 2
    lo = float(np.quantile(boot, alpha))
    hi = float(np.quantile(boot, 1 - alpha))
    return point, lo, hi


def fisher_combine(p_values: list[float]) -> float:
    """Fisher's method for combining independent p-values into one."""
    from scipy.stats import chi2  # local import — small dep surface

    chi_sq = -2 * np.sum(np.log(np.asarray(p_values, dtype=float)))
    df = 2 * len(p_values)
    return float(chi2.sf(chi_sq, df))

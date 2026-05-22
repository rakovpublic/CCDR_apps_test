"""Statistical utilities: BH-FDR, bootstrap CI, Fisher combine."""

from __future__ import annotations

from typing import Callable

import numpy as np


def bh_fdr(p_values: list) -> list:
    """Benjamini-Hochberg adjusted q-values; None preserved as None."""
    indexed = [(i, p) for i, p in enumerate(p_values) if p is not None]
    if not indexed:
        return list(p_values)
    indexed.sort(key=lambda x: x[1])
    m = len(indexed)
    out = list(p_values)
    prev_q = 1.0
    for rank_from_top in range(m, 0, -1):
        i, p = indexed[rank_from_top - 1]
        q = min(prev_q, p * m / rank_from_top)
        out[i] = q
        prev_q = q
    return out


def bootstrap_ci(
    samples: np.ndarray,
    statistic: Callable,
    n_boot: int = 10_000,
    ci_level: float = 0.95,
    seed: int = 0xCCD0,
) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    samples = np.asarray(samples)
    point = float(statistic(samples))
    n = len(samples)
    boot = np.empty(n_boot)
    for k in range(n_boot):
        boot[k] = float(statistic(samples[rng.integers(0, n, n)]))
    alpha = (1 - ci_level) / 2
    return point, float(np.quantile(boot, alpha)), float(np.quantile(boot, 1 - alpha))


def fisher_combine(p_values: list) -> float:
    from scipy.stats import chi2

    p_arr = np.clip(np.asarray(p_values, dtype=float), 1e-300, 1.0)
    chi_sq = -2.0 * np.sum(np.log(p_arr))
    df = 2 * len(p_arr)
    return float(chi2.sf(chi_sq, df))


def spearman(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    from scipy.stats import spearmanr

    res = spearmanr(x, y)
    return float(res.statistic), float(res.pvalue)


def aic(n: int, rss: float, k: int) -> float:
    return n * np.log(rss / n) + 2 * k

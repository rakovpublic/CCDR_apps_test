"""Harness-level tests: registry, lock-file integrity, statistics."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ccdr_tests.core.prediction import Prediction, Result, Tier, Verdict
from ccdr_tests.core.registry import load_all
from ccdr_tests.core.stats import bh_fdr, bootstrap_ci, fisher_combine


SPEC_DIR = ROOT / "specs" / "tier_a"


def test_registry_loads_all_14():
    r = load_all()
    assert len(r) == 14, f"expected 14 Tier-A tests, got {len(r)}"
    expected = {"QC1","QC2","QC3","QC4","QC5","MAT1","MAT3","MAT6","MAT10","EL1","EN3","AE2","AE5","FR7"}
    assert set(r.keys()) == expected


def test_each_prediction_is_tier_a():
    for pid, (pred, _) in load_all().items():
        assert pred.tier == Tier.A
        assert pred.decision_rule
        assert pred.public_sources


def test_decision_rule_locks_match():
    for pid, (pred, _) in load_all().items():
        lock = SPEC_DIR / f"{pid}.lock"
        assert lock.exists(), f"missing lock file for {pid}"
        expected = hashlib.sha256(pred.decision_rule.encode("utf-8")).hexdigest()
        actual = lock.read_text().strip()
        assert actual == expected, f"{pid} decision-rule hash drifted; rerun `python -m ccdr_tests lock` if intentional"


def test_bh_fdr_monotone():
    ps = [0.001, 0.01, 0.03, 0.04, 0.05, 0.2, 0.5, None]
    qs = bh_fdr(ps)
    assert qs[-1] is None
    real = [q for q in qs if q is not None]
    assert all(0 <= q <= 1.0 for q in real)
    assert qs[0] <= qs[1] <= qs[2] <= qs[3] <= qs[4] <= qs[5]


def test_bh_fdr_known_value():
    # Classical BH example: with 3 tests at p=0.01,0.02,0.03 -> q=0.03,0.03,0.03
    ps = [0.01, 0.02, 0.03]
    qs = bh_fdr(ps)
    assert all(abs(q - 0.03) < 1e-9 for q in qs)


def test_bootstrap_ci_runs():
    import numpy as np
    rng = np.random.default_rng(0)
    s = rng.normal(loc=1.0, scale=0.2, size=200)
    point, lo, hi = bootstrap_ci(s, np.mean, n_boot=1000)
    assert lo < point < hi
    assert 0.9 < point < 1.1


def test_fisher_combine_sane():
    p = fisher_combine([0.5, 0.5, 0.5])
    assert 0.2 < p < 0.8
    p2 = fisher_combine([0.001, 0.001, 0.001])
    assert p2 < 1e-4

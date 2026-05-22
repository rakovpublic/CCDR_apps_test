"""Test registry: maps PID -> (Prediction, run callable)."""

from __future__ import annotations

import importlib
from typing import Callable

from .prediction import Prediction

TIER_A_MODULES = [
    "ccdr_tests.tests.qc01_cdt_code_distance",
    "ccdr_tests.tests.qc02_cdt_vs_surface",
    "ccdr_tests.tests.qc03_cdt_threshold",
    "ccdr_tests.tests.qc04_cdt_burst_errors",
    "ccdr_tests.tests.qc05_transmon_t1_floor",
    "ccdr_tests.tests.mat01_grain_boundary_kappa",
    "ccdr_tests.tests.mat03_kappa_t_half",
    "ccdr_tests.tests.mat06_diamond_kappa_ceiling",
    "ccdr_tests.tests.mat10_kibble_zurek_exponent",
    "ccdr_tests.tests.el01_3dnand_area_scaling",
    "ccdr_tests.tests.en03_pv_sq_excess",
    "ccdr_tests.tests.ae02_ringdown_kerr_deviation",
    "ccdr_tests.tests.ae05_pioneer_residual",
    "ccdr_tests.tests.fr07_mkss_tau_e",
]


def load_all() -> dict[str, tuple[Prediction, Callable]]:
    """Import every Tier-A module and return {pid: (PREDICTION, run)}."""
    out: dict[str, tuple[Prediction, Callable]] = {}
    for mod_name in TIER_A_MODULES:
        mod = importlib.import_module(mod_name)
        pred: Prediction = getattr(mod, "PREDICTION")
        runner: Callable = getattr(mod, "run")
        out[pred.pid] = (pred, runner)
    return out

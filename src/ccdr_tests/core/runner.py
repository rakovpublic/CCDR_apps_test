"""Orchestrate the Tier-A battery: import modules, run tests, apply BH-FDR."""

from __future__ import annotations

import logging
import traceback
from dataclasses import dataclass
from pathlib import Path

from .data_cache import DataCache
from .prediction import Prediction, RetrofitRisk, Result, Verdict
from .registry import load_all
from .stats import bh_fdr

LOG = logging.getLogger("ccdr.runner")


@dataclass
class Context:
    cache: DataCache
    logger: logging.Logger
    seed: int = 0xCCD0


def run_one(pid: str, ctx: Context) -> Result:
    registry = load_all()
    if pid not in registry:
        raise KeyError(f"unknown PID: {pid}")
    pred, fn = registry[pid]
    try:
        res = fn(ctx)
    except Exception as exc:
        LOG.exception("test %s raised", pid)
        return Result(
            pid=pid,
            verdict=Verdict.ERROR,
            effect_observed=None,
            effect_predicted=pred.predicted_effect,
            effect_unit=pred.effect_unit,
            p_value=None,
            q_value=None,
            n=0,
            methodology=f"errored: {type(exc).__name__}",
            data_sources_used=[],
            caveats=[f"exception: {exc}"],
            error_traceback=traceback.format_exc(),
        )
    return _apply_retrofit_guard(pred, res)


def run_battery(pids: list | None = None, ctx: Context | None = None) -> list:
    ctx = ctx or Context(cache=DataCache(), logger=LOG)
    registry = load_all()
    if pids is None:
        pids = list(registry.keys())
    results: list[Result] = []
    for pid in pids:
        LOG.info("running %s", pid)
        results.append(run_one(pid, ctx))
    # BH-FDR across the whole executed battery.
    qs = bh_fdr([r.p_value for r in results])
    for r, q in zip(results, qs):
        r.q_value = q
        # demote SUPPORTED -> INCONCLUSIVE if q too large
        if r.verdict == Verdict.SUPPORTED and q is not None and q > 0.10:
            r.caveats.append(f"verdict downgraded SUPPORTED->INCONCLUSIVE: q={q:.3f} > 0.10")
            r.verdict = Verdict.INCONCLUSIVE
    return results


def _apply_retrofit_guard(pred: Prediction, res: Result) -> Result:
    if res.verdict == Verdict.SUPPORTED and pred.retrofit_risk == RetrofitRisk.HIGH:
        res.caveats.append("retrofit guard: high retrofit_risk -> verdict downgraded SUPPORTED->RETROFIT")
        res.verdict = Verdict.RETROFIT
    return res


def write_lock_files(spec_dir: Path) -> None:
    """Write SHA-256 of each prediction's decision_rule to specs/tier_a/<PID>.lock."""
    import hashlib

    spec_dir.mkdir(parents=True, exist_ok=True)
    for pid, (pred, _) in load_all().items():
        h = hashlib.sha256(pred.decision_rule.encode("utf-8")).hexdigest()
        (spec_dir / f"{pid}.lock").write_text(h + "\n", encoding="utf-8")

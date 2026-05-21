"""
Core types for the CCDR prediction test harness.

A `Prediction` is the immutable, pre-registered description of what's being
tested. A `Result` is the output of running that test. Both are designed to
be serialised to JSON for the machine-readable report.

The Java equivalent of `Prediction` would be a `record`; the Java equivalent
of `Result` would be a value-object class with a builder.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Tier(Enum):
    """Testability tier — set at spec time, not run time."""
    A = "implementable_now"
    B = "deferred_needs_data"
    C = "not_testable_today"


class Verdict(Enum):
    """Per-test outcome. RETROFIT distinguishes consistency from forward prediction."""
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    RETROFIT = "retrofit_consistent"
    ERROR = "error"  # data fetch or computation failed


class RetrofitRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Prediction:
    """Pre-registered description of a CCDR prediction to test.

    All fields must be filled at module-import time. The runner asserts
    that `decision_rule_hash` matches `specs/tier_a/<pid>.lock` to prevent
    post-hoc rule-tuning.
    """
    pid: str
    domain: str
    one_liner: str
    sharp_form: str
    null_hypothesis: str
    predicted_effect: float | tuple[float, float]
    effect_unit: str
    falsification_criterion: str
    retrofit_risk: RetrofitRisk
    tier: Tier
    public_sources: tuple[str, ...]
    decision_rule: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["retrofit_risk"] = self.retrofit_risk.value
        d["tier"] = self.tier.value
        d["public_sources"] = list(self.public_sources)
        return d


@dataclass
class Result:
    """Output of one prediction test. Mutable during the run (the runner
    fills in `q_value` after the whole battery completes)."""
    pid: str
    verdict: Verdict
    effect_observed: float | None
    effect_predicted: float | tuple[float, float]
    effect_unit: str
    p_value: float | None
    q_value: float | None  # BH-FDR adjusted, filled by runner after all tests
    n: int
    methodology: str
    data_sources_used: list[str]
    caveats: list[str] = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_data_checksum: str | None = None  # SHA-256 of cached inputs
    error_traceback: str | None = None    # set when verdict == ERROR

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        return d

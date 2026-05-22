"""Core types for the CCDR prediction test harness."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Tier(Enum):
    A = "implementable_now"
    B = "deferred_needs_data"
    C = "not_testable_today"


class Verdict(Enum):
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    RETROFIT = "retrofit_consistent"
    ERROR = "error"


class RetrofitRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Prediction:
    pid: str
    domain: str
    one_liner: str
    sharp_form: str
    null_hypothesis: str
    predicted_effect: float | tuple
    effect_unit: str
    falsification_criterion: str
    retrofit_risk: RetrofitRisk
    tier: Tier
    public_sources: tuple
    decision_rule: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["retrofit_risk"] = self.retrofit_risk.value
        d["tier"] = self.tier.value
        d["public_sources"] = list(self.public_sources)
        if isinstance(self.predicted_effect, tuple):
            d["predicted_effect"] = list(self.predicted_effect)
        return d


@dataclass
class Result:
    pid: str
    verdict: Verdict
    effect_observed: float | None
    effect_predicted: float | tuple
    effect_unit: str
    p_value: float | None
    q_value: float | None
    n: int
    methodology: str
    data_sources_used: list
    caveats: list = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_data_checksum: str | None = None
    error_traceback: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        if isinstance(self.effect_predicted, tuple):
            d["effect_predicted"] = list(self.effect_predicted)
        return d

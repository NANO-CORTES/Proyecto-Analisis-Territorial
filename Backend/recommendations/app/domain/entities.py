from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

def _now() -> datetime:
    return datetime.now(timezone.utc)

@dataclass(frozen=True)
class ZoneAnalytics:
    zone_code: str
    zone_name: str
    score_value: float
    score_level: str
    population_indicator: float
    income_indicator: float
    education_indicator: float
    competition_indicator: float
    prediction_value: Optional[float] = None

@dataclass
class ZoneRecommendation:
    zone_code: str
    zone_name: str
    recommendation_level: str
    strengths: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    explanation: str = ""
    generated_at: datetime = field(default_factory=_now)
    execution_id: Optional[str] = None

@dataclass
class RecommendationExecution:
    id: str
    score_execution_id: str
    prediction_batch_id: Optional[str]
    total_zones: int = 0
    created_at: datetime = field(default_factory=_now)

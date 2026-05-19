from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.domain.value_objects import ScoreLevel

def _now() -> datetime:
    return datetime.now(timezone.utc)

@dataclass
class ZoneIndicators:
    zone_code: str
    zone_name: str
    population: float = 0.0
    income: float = 0.0
    education: float = 0.0
    competition: float = 0.0

    def as_dict(self) -> dict:
        return {
            "zone_code": self.zone_code,
            "zone_name": self.zone_name,
            "population_indicator": self.population,
            "income_indicator": self.income,
            "education_indicator": self.education,
            "competition_indicator": self.competition,
        }

@dataclass
class ZoneScore:
    zone_code: str
    zone_name: str
    score_value: float
    score_level: ScoreLevel
    rank_position: int = 0
    execution_id: Optional[str] = None
    combined_score: Optional[float] = None
    prediction_value: Optional[float] = None
    discrepancy_flag: bool = False
    created_at: datetime = field(default_factory=_now)

@dataclass
class ScoringExecution:
    id: str
    transformation_run_id: str
    configuration_id: Optional[str]
    total_zones: int = 0
    created_at: datetime = field(default_factory=_now)

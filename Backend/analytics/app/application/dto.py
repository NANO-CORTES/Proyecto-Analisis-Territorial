from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.domain.value_objects import ScoreLevel

class ZoneIndicatorDTO(BaseModel):
    zone_code: str
    zone_name: str
    population_indicator: float
    income_indicator: float
    education_indicator: float
    competition_indicator: float

class IndicatorsCalculationResult(BaseModel):
    transformation_run_id: str
    total_zones: int
    zones: List[ZoneIndicatorDTO]

class ScoringExecutionResult(BaseModel):
    execution_id: str
    transformation_run_id: str
    configuration_id: Optional[str]
    total_zones: int
    created_at: datetime

class ZoneRankingItem(BaseModel):
    rank_position: int
    zone_code: str
    zone_name: str
    score_value: float
    score_level: ScoreLevel
    execution_id: str
    combined_score: Optional[float] = None
    prediction_value: Optional[float] = None
    discrepancy_flag: bool = False

class RankingResponse(BaseModel):
    success: bool = True
    execution_id: str
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    level_filter: Optional[str]
    data: List[ZoneRankingItem]
    error: Optional[str] = None

class ZoneSummary(BaseModel):
    zone_code: str
    indicators: Optional[ZoneIndicatorDTO] = None
    score: Optional[ZoneRankingItem] = None
    partial: bool = False

class HealthResponse(BaseModel):
    status: str
    service_name: str
    version: str
    db_connected: bool
    timestamp: str

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

class GenerateRecommendationsRequest(BaseModel):
    score_execution_id: str
    prediction_batch_id: Optional[str] = None

class ZoneRecommendationDTO(BaseModel):
    zone_code: str
    zone_name: str
    recommendation_level: str
    strengths: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    explanation: str
    generated_at: datetime

class RecommendationExecutionDTO(BaseModel):
    execution_id: str
    score_execution_id: str
    prediction_batch_id: Optional[str]
    total_zones: int
    created_at: datetime
    recommendations: List[ZoneRecommendationDTO]

class HealthResponse(BaseModel):
    status: str
    service_name: str
    version: str
    db_connected: bool
    timestamp: str

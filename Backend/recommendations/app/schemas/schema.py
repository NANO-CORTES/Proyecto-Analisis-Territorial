from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RecommendationLevel(str, Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


# ── Entrada ──────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    score_execution_id: str
    prediction_batch_id: Optional[str] = None


# ── Zona individual con recomendación ────────────────────────────────────────

class ZoneRecommendationItem(BaseModel):
    zone_code: str
    zone_name: str
    score_value: float
    recommendation_level: RecommendationLevel
    strengths_text: str
    risks_text: str
    explanation_text: str


# ── Respuesta de generación ───────────────────────────────────────────────────

class GenerateResponse(BaseModel):
    success: bool
    execution_id: str
    score_execution_id: str
    total_zones: int
    data: List[ZoneRecommendationItem]
    error: Optional[str] = None


# ── Respuesta consulta por zona ───────────────────────────────────────────────

class ZoneRecommendationResponse(BaseModel):
    success: bool
    zone_code: str
    data: Optional[ZoneRecommendationItem] = None
    error: Optional[str] = None


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    service_name: str
    version: str
    db_connected: bool
    timestamp: str
from pydantic import BaseModel
from typing import List

class ZoneIndicators(BaseModel):
    zone_id: str
    poblacion: float
    ingreso: float
    educacion: float
    competencia: float

class ScoringRequest(BaseModel):
    user_id: str
    zones: List[ZoneIndicators]

class ZoneScoreResult(BaseModel):
    zone_id: str
    score: float
    classification: str

class ScoringResponse(BaseModel):
    execution_id: str
    results: List[ZoneScoreResult]

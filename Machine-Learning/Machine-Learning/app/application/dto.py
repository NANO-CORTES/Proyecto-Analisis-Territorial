from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ExperimentCreateRequest(BaseModel):
    transformation_run_id: str
    algorithm: str = "linear_regression"
    target_variable: str = "territorial_score"


class TrainedModelDTO(BaseModel):
    id: str
    storage_path: str
    is_active: bool


class ExperimentDTO(BaseModel):
    id: str
    transformation_run_id: str
    algorithm: str
    target_variable: str
    features_used: List[str] = Field(default_factory=list)
    r2_score: Optional[float] = None
    mae: Optional[float] = None
    rmse: Optional[float] = None
    created_at: datetime
    status: str
    trained_models: List[TrainedModelDTO] = Field(default_factory=list)


class PredictRequest(BaseModel):
    zone_codes: List[str] = Field(default_factory=list, description="Zones to predict")


class PredictionDTO(BaseModel):
    zone_code: str
    zone_name: str
    model_id: str
    prediction_value: float
    prediction_label: str
    confidence_score: float
    predicted_at: datetime


class PredictionsResponse(BaseModel):
    model_id: str
    total: int
    predictions: List[PredictionDTO]


class HealthResponse(BaseModel):
    status: str
    service_name: str
    version: str
    db_connected: bool
    timestamp: str

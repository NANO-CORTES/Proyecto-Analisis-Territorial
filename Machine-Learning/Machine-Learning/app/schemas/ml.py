from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ExperimentCreate(BaseModel):
    transformation_run_id: str
    algorithm: str # linear_regression, random_forest, gradient_boosting
    target_variable: str

class TrainedModelResponse(BaseModel):
    id: str
    storage_path: str
    is_active: bool

    class Config:
        from_attributes = True

class ExperimentResponse(BaseModel):
    id: str
    transformation_run_id: str
    algorithm: str
    target_variable: str
    r2_score: Optional[float]
    mae: Optional[float]
    rmse: Optional[float]
    created_at: datetime
    status: str
    trained_models: List[TrainedModelResponse] = []

    class Config:
        from_attributes = True

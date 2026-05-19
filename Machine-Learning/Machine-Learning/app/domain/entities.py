from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ZoneFeatures:
    zone_code: str
    zone_name: str
    population: float
    income: float
    education: float
    economic_activity: float
    commercial_presence: float

    def as_feature_vector(self, columns: List[str]) -> List[float]:
        mapping = {
            "population_density": self.population,
            "average_income": self.income,
            "education_level": self.education,
            "economic_activity_index": self.economic_activity,
            "commercial_presence_index": self.commercial_presence,
        }
        return [mapping[name] for name in columns]


@dataclass
class TrainingMetrics:
    r2: float
    mae: float
    rmse: float


@dataclass
class MLExperiment:
    id: str
    transformation_run_id: str
    algorithm: str
    target_variable: str
    features_used: List[str]
    metrics: TrainingMetrics
    created_at: datetime = field(default_factory=_now)
    status: str = "COMPLETED"


@dataclass
class TrainedModel:
    id: str
    experiment_id: str
    storage_path: str
    is_active: bool = False


@dataclass
class PredictionResult:
    zone_code: str
    zone_name: str
    model_id: str
    prediction_value: float
    prediction_label: str
    confidence_score: float
    predicted_at: datetime = field(default_factory=_now)

from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.domain.entities import PredictionResult
from app.domain.ports.prediction_repository import IPredictionRepository
from app.infrastructure.persistence.models import PredictionResultRow


class SqlPredictionRepository(IPredictionRepository):
    def __init__(self, db: Session):
        self._db = db

    def save_all(self, predictions: List[PredictionResult]) -> None:
        rows = [
            PredictionResultRow(
                model_id=p.model_id,
                zone_code=p.zone_code,
                zone_name=p.zone_name,
                prediction_value=p.prediction_value,
                prediction_label=p.prediction_label,
                confidence_score=p.confidence_score,
                predicted_at=p.predicted_at,
            )
            for p in predictions
        ]
        self._db.add_all(rows)
        self._db.commit()

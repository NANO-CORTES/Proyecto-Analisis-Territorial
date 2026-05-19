from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities import RecommendationExecution, ZoneRecommendation
from app.domain.ports.recommendation_repository import IRecommendationRepository
from app.infrastructure.persistence.models import (
    RecommendationExecutionModel,
    ZoneRecommendationModel,
)

_DELIMITER = "\n"

class SqlRecommendationRepository(IRecommendationRepository):
    def __init__(self, db: Session):
        self._db = db

    def create_execution(self, execution: RecommendationExecution) -> RecommendationExecution:
        row = RecommendationExecutionModel(
            id=execution.id,
            score_execution_id=execution.score_execution_id,
            prediction_batch_id=execution.prediction_batch_id,
            total_zones=execution.total_zones,
            created_at=execution.created_at,
        )
        self._db.add(row)
        self._db.commit()
        return execution

    def save_all(self, execution_id: str, recommendations: List[ZoneRecommendation]) -> None:
        records = [
            ZoneRecommendationModel(
                execution_id=execution_id,
                zone_code=rec.zone_code,
                zone_name=rec.zone_name,
                recommendation_level=rec.recommendation_level,
                strengths_text=_DELIMITER.join(rec.strengths),
                risks_text=_DELIMITER.join(rec.risks),
                explanation_text=rec.explanation,
                generated_at=rec.generated_at,
            )
            for rec in recommendations
        ]
        self._db.add_all(records)
        self._db.commit()

    def latest_for_zone(self, zone_code: str) -> Optional[ZoneRecommendation]:
        row = (
            self._db.query(ZoneRecommendationModel)
            .filter(ZoneRecommendationModel.zone_code == zone_code)
            .order_by(ZoneRecommendationModel.generated_at.desc())
            .first()
        )
        return self._to_entity(row) if row else None

    def list_for_execution(self, execution_id: str) -> List[ZoneRecommendation]:
        rows = (
            self._db.query(ZoneRecommendationModel)
            .filter(ZoneRecommendationModel.execution_id == execution_id)
            .all()
        )
        return [self._to_entity(r) for r in rows]

    @staticmethod
    def _to_entity(row: ZoneRecommendationModel) -> ZoneRecommendation:
        return ZoneRecommendation(
            zone_code=row.zone_code,
            zone_name=row.zone_name,
            recommendation_level=row.recommendation_level,
            strengths=row.strengths_text.split(_DELIMITER) if row.strengths_text else [],
            risks=row.risks_text.split(_DELIMITER) if row.risks_text else [],
            explanation=row.explanation_text or "",
            generated_at=row.generated_at,
            execution_id=row.execution_id,
        )

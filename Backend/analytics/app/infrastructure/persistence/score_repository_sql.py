from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.entities import ScoringExecution, ZoneScore
from app.domain.ports.score_repository import IScoreRepository
from app.domain.value_objects import ScoreLevel
from app.infrastructure.persistence.models import ScoreExecutionModel, ZoneScoreModel

class SqlScoreRepository(IScoreRepository):
    def __init__(self, db: Session):
        self._db = db

    def create_execution(self, execution: ScoringExecution) -> ScoringExecution:
        row = ScoreExecutionModel(
            id=execution.id,
            transformation_run_id=execution.transformation_run_id,
            configuration_id=execution.configuration_id,
            total_zones=execution.total_zones,
            created_at=execution.created_at,
        )
        self._db.add(row)
        self._db.commit()
        return execution

    def get_execution(self, execution_id: str) -> Optional[ScoringExecution]:
        row = self._db.get(ScoreExecutionModel, execution_id)
        if not row:
            return None
        return ScoringExecution(
            id=row.id,
            transformation_run_id=row.transformation_run_id,
            configuration_id=row.configuration_id,
            total_zones=row.total_zones or 0,
            created_at=row.created_at,
        )

    def save_scores(self, execution_id: str, scores: List[ZoneScore]) -> None:
        existing = (
            self._db.query(ZoneScoreModel)
            .filter(ZoneScoreModel.execution_id == execution_id)
            .all()
        )
        existing_by_zone = {row.zone_code: row for row in existing}

        for score in scores:
            row = existing_by_zone.get(score.zone_code)
            if row is None:
                row = ZoneScoreModel(execution_id=execution_id, zone_code=score.zone_code)
                self._db.add(row)
            row.zone_name = score.zone_name
            row.score_value = score.score_value
            row.score_level = score.score_level
            row.rank_position = score.rank_position
            row.combined_score = score.combined_score
            row.prediction_value = score.prediction_value
            row.discrepancy_flag = 1 if score.discrepancy_flag else 0
        self._db.commit()

    def list_scores(
        self,
        execution_id: str,
        level: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ZoneScore], int]:
        query = self._db.query(ZoneScoreModel).filter(
            ZoneScoreModel.execution_id == execution_id
        )
        if level:
            query = query.filter(ZoneScoreModel.score_level == level)

        total = query.with_entities(func.count(ZoneScoreModel.id)).scalar() or 0
        rows = (
            query.order_by(ZoneScoreModel.rank_position.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(r) for r in rows], total

    def latest_for_zone(self, zone_code: str) -> Optional[ZoneScore]:
        row = (
            self._db.query(ZoneScoreModel)
            .filter(ZoneScoreModel.zone_code == zone_code)
            .order_by(ZoneScoreModel.created_at.desc())
            .first()
        )
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row: ZoneScoreModel) -> ZoneScore:
        level = row.score_level if isinstance(row.score_level, ScoreLevel) else ScoreLevel(row.score_level)
        return ZoneScore(
            zone_code=row.zone_code,
            zone_name=row.zone_name,
            score_value=row.score_value,
            score_level=level,
            rank_position=row.rank_position,
            execution_id=row.execution_id,
            combined_score=row.combined_score,
            prediction_value=row.prediction_value,
            discrepancy_flag=bool(row.discrepancy_flag),
            created_at=row.created_at,
        )

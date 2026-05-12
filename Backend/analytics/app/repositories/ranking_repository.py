from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.interfaces.ranking_repository import IRankingRepository
from app.models.ranking import ZoneScore, ScoreExecution


class RankingRepository(IRankingRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_execution(self, execution_id: str) -> Optional[ScoreExecution]:
        return self._db.query(ScoreExecution).filter(
            ScoreExecution.id == execution_id
        ).first()

    def get_by_execution(
        self,
        execution_id: str,
        level: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ZoneScore], int]:
        query = self._db.query(ZoneScore).filter(
            ZoneScore.execution_id == execution_id
        )
        if level:
            query = query.filter(ZoneScore.score_level == level)

        total = query.with_entities(func.count()).scalar()
        zones = query.order_by(ZoneScore.rank_position.asc()).offset(offset).limit(limit).all()
        return zones, total

    def create_execution(self, execution: ScoreExecution, scores: List[ZoneScore]) -> ScoreExecution:
        self._db.add(execution)
        self._db.add_all(scores)
        self._db.commit()
        self._db.refresh(execution)
        return execution
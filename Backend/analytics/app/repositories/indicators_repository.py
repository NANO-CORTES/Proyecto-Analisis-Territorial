from typing import List, Optional
from sqlalchemy.orm import Session
from app.interfaces.indicators_repository import IIndicatorsRepository
from app.models.ranking import IndicatorResult


class IndicatorsRepository(IIndicatorsRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_run(self, transformation_run_id: str) -> List[IndicatorResult]:
        return self._db.query(IndicatorResult).filter(
            IndicatorResult.transformation_run_id == transformation_run_id
        ).all()

    def get_zone_summary(self, zone_code: str) -> Optional[IndicatorResult]:
        return self._db.query(IndicatorResult).filter(
            IndicatorResult.zone_code == zone_code
        ).order_by(IndicatorResult.id.desc()).first()

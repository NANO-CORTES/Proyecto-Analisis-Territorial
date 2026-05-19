from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities import ZoneIndicators
from app.domain.ports.indicator_repository import IIndicatorRepository
from app.infrastructure.persistence.models import IndicatorResultModel

class SqlIndicatorRepository(IIndicatorRepository):
    def __init__(self, db: Session):
        self._db = db

    def save_all(self, transformation_run_id: str, indicators: List[ZoneIndicators]) -> None:
        records = [
            IndicatorResultModel(
                transformation_run_id=transformation_run_id,
                zone_code=ind.zone_code,
                zone_name=ind.zone_name,
                population_indicator=ind.population,
                income_indicator=ind.income,
                education_indicator=ind.education,
                competition_indicator=ind.competition,
            )
            for ind in indicators
        ]
        self._db.add_all(records)
        self._db.commit()

    def list_by_run(self, transformation_run_id: str) -> List[ZoneIndicators]:
        rows = (
            self._db.query(IndicatorResultModel)
            .filter(IndicatorResultModel.transformation_run_id == transformation_run_id)
            .all()
        )
        return [self._to_entity(r) for r in rows]

    def latest_for_zone(self, zone_code: str) -> Optional[ZoneIndicators]:
        row = (
            self._db.query(IndicatorResultModel)
            .filter(IndicatorResultModel.zone_code == zone_code)
            .order_by(IndicatorResultModel.created_at.desc())
            .first()
        )
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row: IndicatorResultModel) -> ZoneIndicators:
        return ZoneIndicators(
            zone_code=row.zone_code,
            zone_name=row.zone_name,
            population=row.population_indicator or 0.0,
            income=row.income_indicator or 0.0,
            education=row.education_indicator or 0.0,
            competition=row.competition_indicator or 0.0,
        )

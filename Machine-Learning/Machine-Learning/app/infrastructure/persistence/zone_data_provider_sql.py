from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.orm import Session

from app.domain.entities import ZoneFeatures
from app.domain.ports.zone_data_provider import IZoneDataProvider
from app.infrastructure.persistence.models import TransformedZoneDataModel


class SqlZoneDataProvider(IZoneDataProvider):
    def __init__(self, db: Session):
        self._db = db

    def list_for_run(self, transformation_run_id: str) -> List[ZoneFeatures]:
        rows = (
            self._db.query(TransformedZoneDataModel)
            .filter(TransformedZoneDataModel.transformation_run_id == transformation_run_id)
            .all()
        )
        return [self._to_entity(r) for r in rows if self._is_complete(r)]

    def find_zones(self, zone_codes: Iterable[str]) -> List[ZoneFeatures]:
        codes = list(zone_codes)
        if not codes:
            return []
        rows = (
            self._db.query(TransformedZoneDataModel)
            .filter(TransformedZoneDataModel.zone_code.in_(codes))
            .all()
        )
        latest_by_code: dict[str, TransformedZoneDataModel] = {}
        for row in rows:
            current = latest_by_code.get(row.zone_code)
            if current is None or (row.transformation_run_id or "") > (current.transformation_run_id or ""):
                latest_by_code[row.zone_code] = row
        return [self._to_entity(r) for r in latest_by_code.values() if self._is_complete(r)]

    @staticmethod
    def _is_complete(row: TransformedZoneDataModel) -> bool:
        return None not in {
            row.population_density,
            row.average_income,
            row.education_level,
            row.economic_activity_index,
            row.commercial_presence_index,
        }

    @staticmethod
    def _to_entity(row: TransformedZoneDataModel) -> ZoneFeatures:
        return ZoneFeatures(
            zone_code=row.zone_code,
            zone_name=row.zone_name or row.zone_code,
            population=float(row.population_density or 0.0),
            income=float(row.average_income or 0.0),
            education=float(row.education_level or 0.0),
            economic_activity=float(row.economic_activity_index or 0.0),
            commercial_presence=float(row.commercial_presence_index or 0.0),
        )

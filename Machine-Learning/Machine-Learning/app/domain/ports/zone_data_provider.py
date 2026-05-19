from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from app.domain.entities import ZoneFeatures


class IZoneDataProvider(ABC):
    @abstractmethod
    def list_for_run(self, transformation_run_id: str) -> List[ZoneFeatures]: ...

    @abstractmethod
    def find_zones(self, zone_codes: Iterable[str]) -> List[ZoneFeatures]: ...

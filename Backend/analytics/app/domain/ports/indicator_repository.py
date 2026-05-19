from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.domain.entities import ZoneIndicators

class IIndicatorRepository(ABC):
    @abstractmethod
    def save_all(self, transformation_run_id: str, indicators: List[ZoneIndicators]) -> None: ...

    @abstractmethod
    def list_by_run(self, transformation_run_id: str) -> List[ZoneIndicators]: ...

    @abstractmethod
    def latest_for_zone(self, zone_code: str) -> ZoneIndicators | None: ...

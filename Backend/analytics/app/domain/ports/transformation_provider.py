from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.domain.entities import ZoneIndicators

class ITransformationProvider(ABC):
    @abstractmethod
    async def fetch_zone_indicators(self, transformation_run_id: str) -> List[ZoneIndicators]: ...

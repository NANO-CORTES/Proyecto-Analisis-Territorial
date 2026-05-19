from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.domain.entities import ZoneAnalytics

class IAnalyticsProvider(ABC):
    @abstractmethod
    async def list_zone_results(self, score_execution_id: str) -> List[ZoneAnalytics]: ...

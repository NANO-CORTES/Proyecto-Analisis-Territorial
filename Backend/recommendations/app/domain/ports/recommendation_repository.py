from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import RecommendationExecution, ZoneRecommendation

class IRecommendationRepository(ABC):
    @abstractmethod
    def create_execution(self, execution: RecommendationExecution) -> RecommendationExecution: ...

    @abstractmethod
    def save_all(self, execution_id: str, recommendations: List[ZoneRecommendation]) -> None: ...

    @abstractmethod
    def latest_for_zone(self, zone_code: str) -> Optional[ZoneRecommendation]: ...

    @abstractmethod
    def list_for_execution(self, execution_id: str) -> List[ZoneRecommendation]: ...

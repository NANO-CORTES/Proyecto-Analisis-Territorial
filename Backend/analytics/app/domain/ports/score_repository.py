from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.domain.entities import ScoringExecution, ZoneScore

class IScoreRepository(ABC):
    @abstractmethod
    def create_execution(self, execution: ScoringExecution) -> ScoringExecution: ...

    @abstractmethod
    def get_execution(self, execution_id: str) -> Optional[ScoringExecution]: ...

    @abstractmethod
    def save_scores(self, execution_id: str, scores: List[ZoneScore]) -> None: ...

    @abstractmethod
    def list_scores(
        self,
        execution_id: str,
        level: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ZoneScore], int]: ...

    @abstractmethod
    def latest_for_zone(self, zone_code: str) -> Optional[ZoneScore]: ...

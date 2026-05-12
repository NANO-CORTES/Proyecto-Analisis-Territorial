from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from app.models.ranking import ScoreExecution, ZoneScore


class IRankingRepository(ABC):
    @abstractmethod
    def get_execution(self, execution_id: str) -> Optional[ScoreExecution]:
        ...

    @abstractmethod
    def get_by_execution(
        self,
        execution_id: str,
        level: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ZoneScore], int]:
        ...

    @abstractmethod
    def create_execution(self, execution: ScoreExecution, scores: List[ZoneScore]) -> ScoreExecution:
        ...
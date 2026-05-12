from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.ranking import IndicatorResult


class IIndicatorsRepository(ABC):
    @abstractmethod
    def get_by_run(self, transformation_run_id: str) -> List[IndicatorResult]:
        ...

    @abstractmethod
    def get_zone_summary(self, zone_code: str) -> Optional[IndicatorResult]:
        ...

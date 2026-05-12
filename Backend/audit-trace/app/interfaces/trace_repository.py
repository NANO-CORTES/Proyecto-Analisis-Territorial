from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.trace import ProcessTrace


class ITraceRepository(ABC):
    @abstractmethod
    def create(self, trace: ProcessTrace) -> ProcessTrace:
        ...

    @abstractmethod
    def getByDatasetId(self, datasetLoadId: str) -> List[ProcessTrace]:
        ...

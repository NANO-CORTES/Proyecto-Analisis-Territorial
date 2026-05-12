from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.models import TransformationRun, TransformedRecord


class ITransformationRepository(ABC):
    @abstractmethod
    def createRun(self, run: TransformationRun, records: List[TransformedRecord]) -> TransformationRun:
        ...

    @abstractmethod
    def getRunById(self, runId: str) -> Optional[TransformationRun]:
        ...

    @abstractmethod
    def getResults(self, runId: str) -> List[TransformedRecord]:
        ...

    @abstractmethod
    def listRuns(self) -> List[TransformationRun]:
        ...

    @abstractmethod
    def getDatasetInfo(self, datasetLoadId: str) -> Optional[dict]:
        ...

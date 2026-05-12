from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from app.models.dataset import DatasetLoad, DatasetZone


class IDatasetRepository(ABC):
    @abstractmethod
    def getByHash(self, fileHash: str) -> Optional[DatasetLoad]:
        ...

    @abstractmethod
    def getById(self, datasetId: str) -> Optional[DatasetLoad]:
        ...

    @abstractmethod
    def getAll(self) -> List[DatasetLoad]:
        ...

    @abstractmethod
    def getZones(self, datasetId: Optional[str], search: Optional[str], limit: int, offset: int, department: Optional[str] = None) -> Tuple[List[DatasetZone], int]:
        ...

    @abstractmethod
    def create(self, dataset: DatasetLoad, zones: List[DatasetZone] = None) -> DatasetLoad:
        ...

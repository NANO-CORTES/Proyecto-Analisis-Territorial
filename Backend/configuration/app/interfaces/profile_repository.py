from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.models import BusinessProfile


class IProfileRepository(ABC):
    @abstractmethod
    def create(self, profile: BusinessProfile) -> BusinessProfile:
        ...

    @abstractmethod
    def getAll(self) -> List[BusinessProfile]:
        ...

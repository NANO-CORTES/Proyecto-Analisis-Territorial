from abc import ABC, abstractmethod
from typing import Optional
from app.models.models import ScoringConfiguration


class IScoringConfigRepository(ABC):
    @abstractmethod
    def create(self, config: ScoringConfiguration) -> ScoringConfiguration:
        ...

    @abstractmethod
    def getActive(self) -> Optional[ScoringConfiguration]:
        ...

    @abstractmethod
    def deactivateByProfile(self, profileId: str) -> None:
        ...

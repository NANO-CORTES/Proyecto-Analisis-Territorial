from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

from app.domain.value_objects import CombinedWeights, ScoringWeights

class IConfigurationProvider(ABC):
    @abstractmethod
    async def get_active_weights(self) -> Tuple[str, ScoringWeights]: ...

    @abstractmethod
    async def get_combined_weights(self) -> CombinedWeights: ...

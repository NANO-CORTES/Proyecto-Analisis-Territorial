from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable

class IPredictionProvider(ABC):
    @abstractmethod
    async def predict_for_zones(self, zone_codes: Iterable[str]) -> Dict[str, float]: ...

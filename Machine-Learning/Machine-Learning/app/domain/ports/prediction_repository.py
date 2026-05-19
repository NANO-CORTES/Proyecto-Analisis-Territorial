from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.domain.entities import PredictionResult


class IPredictionRepository(ABC):
    @abstractmethod
    def save_all(self, predictions: List[PredictionResult]) -> None: ...

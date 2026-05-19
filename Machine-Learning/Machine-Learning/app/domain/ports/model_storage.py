from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IModelStorage(ABC):
    @abstractmethod
    def save(self, model_id: str, model_object: Any) -> str: ...

    @abstractmethod
    def load(self, path: str) -> Any: ...

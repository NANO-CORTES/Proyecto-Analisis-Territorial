from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class IAuditPublisher(ABC):
    @abstractmethod
    async def publish(self, event_type: str, payload: Mapping[str, Any]) -> bool: ...

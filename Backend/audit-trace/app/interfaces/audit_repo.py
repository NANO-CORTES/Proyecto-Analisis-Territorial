from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from app.models.audit import AuditLog

class IAuditRepository(ABC):
    @abstractmethod
    def create(self, log: AuditLog) -> AuditLog:
        pass

    @abstractmethod
    def get_all(self, limit: int = 100, skip: int = 0) -> List[AuditLog]:
        pass

    @abstractmethod
    def get_by_user(self, user_id: str, limit: int = 100, skip: int = 0) -> List[AuditLog]:
        pass

    @abstractmethod
    def get_by_date_range(self, from_date: datetime, to_date: datetime) -> List[AuditLog]:
        pass

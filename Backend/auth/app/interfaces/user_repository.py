from abc import ABC, abstractmethod
from typing import Optional, List
from app.models.user import User


class IUserRepository(ABC):
    @abstractmethod
    def getByEmail(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    def getByEmailOrUsername(self, email: str, username: str) -> Optional[User]:
        ...

    @abstractmethod
    def getById(self, userId: int) -> Optional[User]:
        ...

    @abstractmethod
    def getAll(self, skip: int, limit: int) -> List[User]:
        ...

    @abstractmethod
    def create(self, user: User) -> User:
        ...

    @abstractmethod
    def update(self, user: User) -> User:
        ...

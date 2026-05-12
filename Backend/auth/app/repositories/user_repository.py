from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.interfaces.user_repository import IUserRepository
from app.models.user import User


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self._db = db

    def getByEmail(self, email: str) -> Optional[User]:
        return self._db.query(User).filter(User.email == email).first()

    def getByEmailOrUsername(self, email: str, username: str) -> Optional[User]:
        return self._db.query(User).filter(
            or_(User.email == email, User.username == username)
        ).first()

    def getById(self, userId: int) -> Optional[User]:
        return self._db.query(User).filter(User.id == userId).first()

    def getAll(self, skip: int, limit: int) -> List[User]:
        return self._db.query(User).offset(skip).limit(limit).all()

    def create(self, user: User) -> User:
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

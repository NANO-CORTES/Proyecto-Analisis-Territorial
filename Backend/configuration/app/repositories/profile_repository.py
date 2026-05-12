from typing import List
from sqlalchemy.orm import Session
from app.interfaces.profile_repository import IProfileRepository
from app.models.models import BusinessProfile


class ProfileRepository(IProfileRepository):
    def __init__(self, db: Session):
        self._db = db

    def create(self, profile: BusinessProfile) -> BusinessProfile:
        self._db.add(profile)
        self._db.commit()
        self._db.refresh(profile)
        return profile

    def getAll(self) -> List[BusinessProfile]:
        return self._db.query(BusinessProfile).all()

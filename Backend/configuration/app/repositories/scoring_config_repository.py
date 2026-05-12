from typing import Optional
from sqlalchemy.orm import Session
from app.interfaces.scoring_config_repository import IScoringConfigRepository
from app.models.models import ScoringConfiguration


class ScoringConfigRepository(IScoringConfigRepository):
    def __init__(self, db: Session):
        self._db = db

    def create(self, config: ScoringConfiguration) -> ScoringConfiguration:
        self._db.add(config)
        self._db.commit()
        self._db.refresh(config)
        return config

    def getActive(self) -> Optional[ScoringConfiguration]:
        return (
            self._db.query(ScoringConfiguration)
            .filter(ScoringConfiguration.is_active == True)
            .first()
        )

    def deactivateByProfile(self, profileId: str) -> None:
        self._db.query(ScoringConfiguration).filter(
            ScoringConfiguration.profile_id == profileId
        ).update({"is_active": False})
        self._db.commit()

from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db
from app.interfaces.profile_repository import IProfileRepository
from app.interfaces.scoring_config_repository import IScoringConfigRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.scoring_config_repository import ScoringConfigRepository


def getProfileRepository(db: Session = Depends(get_db)) -> IProfileRepository:
    return ProfileRepository(db)


def getScoringConfigRepository(db: Session = Depends(get_db)) -> IScoringConfigRepository:
    return ScoringConfigRepository(db)

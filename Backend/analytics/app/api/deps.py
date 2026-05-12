from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db
from app.interfaces.ranking_repository import IRankingRepository
from app.interfaces.indicators_repository import IIndicatorsRepository
from app.repositories.ranking_repository import RankingRepository
from app.repositories.indicators_repository import IndicatorsRepository


def getRankingRepo(db: Session = Depends(get_db)) -> IRankingRepository:
    return RankingRepository(db)


def getIndicatorsRepo(db: Session = Depends(get_db)) -> IIndicatorsRepository:
    return IndicatorsRepository(db)

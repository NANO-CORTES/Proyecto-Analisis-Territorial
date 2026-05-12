from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.interfaces.experiment_repository import IExperimentRepository
from app.repositories.experiment_repository import ExperimentRepository


def get_experiment_repo(db: Session = Depends(get_db)) -> IExperimentRepository:
    return ExperimentRepository(db)

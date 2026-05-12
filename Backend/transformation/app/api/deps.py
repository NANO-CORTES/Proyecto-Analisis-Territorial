from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db
from app.interfaces.transformation_repo import ITransformationRepository
from app.repositories.transformation_repo import TransformationRepository


def getTransformationRepo(db: Session = Depends(get_db)) -> ITransformationRepository:
    return TransformationRepository(db)

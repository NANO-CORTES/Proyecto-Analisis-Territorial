from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db
from app.interfaces.trace_repository import ITraceRepository
from app.repositories.trace_repository import TraceRepository


def getTraceRepository(db: Session = Depends(get_db)) -> ITraceRepository:
    return TraceRepository(db)

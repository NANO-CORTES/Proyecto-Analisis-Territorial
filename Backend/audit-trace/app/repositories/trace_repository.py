from typing import List
from sqlalchemy.orm import Session
from app.interfaces.trace_repository import ITraceRepository
from app.models.trace import ProcessTrace


class TraceRepository(ITraceRepository):
    def __init__(self, db: Session):
        self._db = db

    def create(self, trace: ProcessTrace) -> ProcessTrace:
        self._db.add(trace)
        self._db.commit()
        self._db.refresh(trace)
        return trace

    def getByDatasetId(self, datasetLoadId: str) -> List[ProcessTrace]:
        return (
            self._db.query(ProcessTrace)
            .filter(ProcessTrace.dataset_load_id == datasetLoadId)
            .order_by(ProcessTrace.created_at)
            .all()
        )

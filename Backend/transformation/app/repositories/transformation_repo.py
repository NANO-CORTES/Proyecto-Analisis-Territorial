from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.interfaces.transformation_repo import ITransformationRepository
from app.models.models import TransformationRun, TransformedRecord


class TransformationRepository(ITransformationRepository):
    def __init__(self, db: Session):
        self._db = db

    def createRun(self, run: TransformationRun, records: List[TransformedRecord]) -> TransformationRun:
        self._db.add(run)
        self._db.add_all(records)
        self._db.commit()
        self._db.refresh(run)
        return run

    def getRunById(self, runId: str) -> Optional[TransformationRun]:
        return self._db.query(TransformationRun).filter(TransformationRun.id == runId).first()

    def getResults(self, runId: str) -> List[TransformedRecord]:
        return self._db.query(TransformedRecord).filter(TransformedRecord.run_id == runId).all()

    def listRuns(self) -> List[TransformationRun]:
        return self._db.query(TransformationRun).order_by(TransformationRun.created_at.desc()).all()

    def getDatasetInfo(self, datasetLoadId: str) -> Optional[dict]:
        result = self._db.execute(
            text("""
                SELECT id, dataset_id, file_name, status, record_count
                FROM ingestion.dataset_loads
                WHERE dataset_id = :did
                LIMIT 1
            """),
            {"did": datasetLoadId}
        ).fetchone()

        if result is None:
            return None

        return {
            "id": result[0],
            "dataset_id": result[1],
            "file_name": result[2],
            "status": result[3],
            "record_count": result[4],
        }

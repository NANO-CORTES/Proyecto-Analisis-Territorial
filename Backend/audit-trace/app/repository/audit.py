from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.audit import AuditLog
from app.interfaces.audit_repo import IAuditRepository

class AuditRepository(IAuditRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, log: AuditLog) -> AuditLog:
        try:
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            return log
        except SQLAlchemyError as err:
            self.db.rollback()
            raise err

    def get_all(self, limit: int = 100, skip: int = 0) -> List[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_user(self, user_id: str, limit: int = 100, skip: int = 0) -> List[AuditLog]:
        return self.db.query(AuditLog).filter(AuditLog.user_id == user_id).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_date_range(self, from_date: datetime, to_date: datetime) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.created_at >= from_date, AuditLog.created_at <= to_date)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

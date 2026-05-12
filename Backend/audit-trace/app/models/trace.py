import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.core.database import Base


class ProcessTrace(Base):
    __tablename__ = "process_traces"
    __table_args__ = {"schema": "audit"}

    id = Column(Integer, primary_key=True, index=True)
    dataset_load_id = Column(String(100), nullable=False, index=True)
    transformation_run_id = Column(String(100), nullable=True)
    score_execution_id = Column(String(100), nullable=True)
    event_type = Column(String(50), nullable=False)
    status = Column(String(20), default="success")
    parameters = Column(JSON, nullable=True)
    result_summary = Column(JSON, nullable=True)
    user_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

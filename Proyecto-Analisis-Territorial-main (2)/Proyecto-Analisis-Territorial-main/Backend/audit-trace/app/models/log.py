from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import datetime

class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = {'schema': 'audit'}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # or 'system'
    action = Column(String)               # event_type
    service_name = Column(String)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
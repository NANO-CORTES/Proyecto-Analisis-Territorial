from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.database import engine, Base, get_db
from app.models.log import AuditEvent
from app.schemas.log import EventCreate

from sqlalchemy import text
with engine.connect() as con:
    con.execute(text("CREATE SCHEMA IF NOT EXISTS audit"))
    con.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Audit and Trace Service")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service_name": "ms-audit-trace"}

@app.post("/api/v1/events")
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = AuditEvent(
        user_id=event.user_id,
        action=event.action,
        service_name=event.service_name,
        status=event.status
    )
    db.add(new_event)
    db.commit()
    return {"success": True, "data": {"event_id": new_event.id}}
import os
base_dir = r"c:\Users\User\Downloads\Proyecto-Analisis-Territorial-main"
ms_dir = os.path.join(base_dir, "Backend", "audit-trace")

files = {
    "requirements.txt": """fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
pydantic-settings""",
    
    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
EXPOSE 8002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]""",

    "app/core/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Audit Service"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()""",

    "app/core/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()""",

    "app/models/log.py": """from sqlalchemy import Column, Integer, String, DateTime
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
    timestamp = Column(DateTime, default=datetime.utcnow)""",
    
    "app/schemas/log.py": """from pydantic import BaseModel

class EventCreate(BaseModel):
    user_id: str
    action: str
    service_name: str
    status: str""",

    "app/main.py": """from fastapi import FastAPI, Depends
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
    return {"success": True, "data": {"event_id": new_event.id}}"""
}

for filepath, content in files.items():
    full_path = os.path.join(ms_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip())

print("Audit-Trace MS built.")

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.config import settings
from app.core.database import engine, get_db, Base as CoreBase
from app.models import Base as TraceBase, ProcessTrace
from app.api.endpoints.audit import router as audit_router

# ============ FASTAPI APP ============
app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.VERSION
)

# ============ DYNAMIC SCHEMA CREATION & TABLE INITIALIZATION ============
@app.on_event("startup")
def startup_event():
    # 1. Crear el esquema si se usa PostgreSQL
    if "postgresql" in settings.DATABASE_URL:
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS audit_trace;"))
                conn.commit()
        except Exception as e:
            import logging
            logging.getLogger("uvicorn").error(f"Error creating audit_trace schema: {e}")

    # 2. Inicializar tablas de ambos bases
    try:
        # Crea la tabla de logs de auditoría (que tiene la anotación de esquema en Postgres)
        CoreBase.metadata.create_all(bind=engine)
        # Crea la tabla de trazabilidad
        TraceBase.metadata.create_all(bind=engine)
    except Exception as e:
        import logging
        logging.getLogger("uvicorn").error(f"Error initializing tables: {e}")

# ============ HEALTH / ROOT ============
@app.get("/")
def root():
    return {"message": "Audit Trace Service running"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        pass
    return {
        "status": "healthy" if db_connected else "degraded",
        "service_name": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "db_connected": db_connected,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============ ROUTERS ============
# Registro del enrutador de auditoría para la UI y servicios
app.include_router(audit_router, prefix="/api/v1/audit", tags=["Auditoría"])

# ============ LOCAL SCHEMAS FOR TRACE ============
class TraceCreate(BaseModel):
    dataset_load_id: str
    transformation_run_id: Optional[str] = None
    score_execution_id: Optional[str] = None
    event_type: str
    status: str = "success"
    parameters: Optional[Dict[str, Any]] = None
    result_summary: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

# ============ ENDPOINTS DE TRAZABILIDAD (Mantenidos para compatibilidad) ============
@app.post("/api/v1/audit/trace")
def create_trace(trace: TraceCreate, db: Session = Depends(get_db)):
    db_trace = ProcessTrace(
        dataset_load_id=trace.dataset_load_id,
        transformation_run_id=trace.transformation_run_id,
        score_execution_id=trace.score_execution_id,
        event_type=trace.event_type,
        status=trace.status,
        parameters=trace.parameters,
        result_summary=trace.result_summary,
        user_id=trace.user_id
    )
    db.add(db_trace)
    db.commit()
    db.refresh(db_trace)
    return {"id": db_trace.id, "status": "created"}

@app.get("/api/v1/audit/trace/{dataset_load_id}")
def get_trace_chain(dataset_load_id: str, db: Session = Depends(get_db)):
    events = db.query(ProcessTrace).filter(
        ProcessTrace.dataset_load_id == dataset_load_id
    ).order_by(ProcessTrace.created_at).all()
    
    if not events:
        raise HTTPException(status_code=404, detail="No se encontraron eventos")
    
    timeline = {}
    for event in events:
        timeline[event.event_type] = {
            "status": event.status,
            "parameters": event.parameters,
            "result_summary": event.result_summary,
            "timestamp": event.created_at.isoformat()
        }
    
    return {
        "dataset_load_id": dataset_load_id,
        "events": [
            {
                "id": ev.id,
                "dataset_load_id": ev.dataset_load_id,
                "transformation_run_id": ev.transformation_run_id,
                "score_execution_id": ev.score_execution_id,
                "event_type": ev.event_type,
                "status": ev.status,
                "parameters": ev.parameters,
                "result_summary": ev.result_summary,
                "user_id": ev.user_id,
                "created_at": ev.created_at.isoformat() if ev.created_at else None
            } for ev in events
        ],
        "timeline": timeline
    }
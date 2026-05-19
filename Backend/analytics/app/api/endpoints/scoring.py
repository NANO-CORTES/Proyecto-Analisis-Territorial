from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas.scoring import ScoringRequest, ScoringResponse
from app.services.scoring_service import ScoringService, send_audit_log

router = APIRouter(prefix="/api/v1/scoring", tags=["Scoring Engine"])
logger = logging.getLogger(__name__)

@router.post("/execute", response_model=ScoringResponse, summary="Ejecutar motor de scoring")
async def execute_scoring(
    request: ScoringRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    service = ScoringService(db)
    
    # Ejecutar lógica del negocio
    response = await service.execute(request)
    
    # Enviar log de auditoría
    background_tasks.add_task(
        send_audit_log,
        request.user_id,
        response.execution_id,
        "EXECUTE_SCORING",
        f"Calculado score para {len(request.zones)} zonas"
    )
    
    return response

@router.post("/calculate", summary="Endpoint compatible de calculate")
async def calculate_scoring(
    request: ScoringRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return await execute_scoring(request, background_tasks, db)

@router.get("/latest", summary="Obtener la última ejecución de scoring")
async def get_latest_execution(db: Session = Depends(get_db)):
    # Query analytics schema
    ae = None
    try:
        from app.models.scoring import ScoreExecution as AnalyticsExecution
        ae = db.query(AnalyticsExecution).order_by(AnalyticsExecution.created_at.desc()).first()
    except Exception:
        pass
    
    # Query public schema
    pe = None
    try:
        from app.models.ranking import ScoreExecution as PublicExecution
        pe = db.query(PublicExecution).order_by(PublicExecution.created_at.desc()).first()
    except Exception:
        pass
    
    # Select the most recent one
    execution = None
    is_analytics = True
    if ae and pe:
        if ae.created_at > pe.created_at:
            execution = ae
            is_analytics = True
        else:
            execution = pe
            is_analytics = False
    elif ae:
        execution = ae
        is_analytics = True
    elif pe:
        execution = pe
        is_analytics = False
        
    if not execution:
        return {"status": "NONE"}
        
    return {
        "execution_id": execution.id,
        "status": "COMPLETED",
        "transformation_run_id": execution.transformation_run_id,
        "configuration_id": execution.configuration_id,
        "created_at": execution.created_at.isoformat() if execution.created_at else None
    }

@router.get("/results/{execution_id}", summary="Obtener resultados previos (mock)")
async def get_results(execution_id: str):
    # Dummy representation for results fetch as required by HU
    return {"execution_id": execution_id, "status": "COMPLETED"}

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

@router.get("/results/{execution_id}", summary="Obtener resultados previos (mock)")
async def get_results(execution_id: str):
    # Dummy representation for results fetch as required by HU
    return {"execution_id": execution_id, "status": "COMPLETED"}

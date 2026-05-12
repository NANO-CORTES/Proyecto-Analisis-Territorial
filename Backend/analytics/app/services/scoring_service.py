import uuid
import httpx
import logging
import time
from typing import Tuple
from sqlalchemy.orm import Session
from app.schemas.scoring import ScoringRequest, ScoringResponse, ZoneScoreResult
from app.repositories.scoring_repository import ScoringRepository

logger = logging.getLogger(__name__)

async def send_audit_log(user_id: str, trace_id: str, action: str, details: str):
    # Ajuste HU-15: Trazabilidad con audit-trace
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "user_id": user_id,
                "action": action,
                "service_name": "ms-analytics",
                "status": "SUCCESS",
                "details": details,
                "timestamp": time.time()
            }
            headers = {"X-Trace-Id": trace_id}
            await client.post("http://configuration:8004/api/v1/audit/logs", json=payload, headers=headers)
            await client.post("http://audit-trace:8002/api/v1/audit/logs", json=payload, headers=headers)
    except Exception as e:
        logger.error(f"Fallo al enviar a audit-trace: {str(e)}")


class ScoringService:
    def __init__(self, db: Session):
        self.repository = ScoringRepository(db)

    async def get_dynamic_weights(self) -> Tuple[float, float, float, float]:
        # Ajuste HU-15: Integración de Configuración (Consumir dinámica)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://configuration:8004/api/v1/config/weights")
                resp.raise_for_status()
                data = resp.json()
                return data["w1_poblacion"], data["w2_ingreso"], data["w3_educacion"], data["w4_competencia"]
        except Exception as e:
            logger.error(f"Error obteniendo pesos: {str(e)}. Usando fallback.")
            return 0.3, 0.3, 0.2, 0.2

    async def execute(self, request: ScoringRequest) -> ScoringResponse:
        execution_id = str(uuid.uuid4())
        
        # 1. Obtener los pesos dinámicos
        w1, w2, w3, w4 = await self.get_dynamic_weights()
        
        results = []
        for zone in request.zones:
            # Ajuste HU-15: Motor de Scoring (Lógica determinística + Penalización de competencia)
            score = (w1 * zone.poblacion) + (w2 * zone.ingreso) + (w3 * zone.educacion) - (w4 * zone.competencia)
            
            # Ajuste HU-15: Clasificación de Oportunidad
            if score > 0.7:
                classification = "ALTA"
            elif 0.4 <= score <= 0.7:
                classification = "MEDIA"
            else:
                classification = "BAJA"
                
            results.append(ZoneScoreResult(
                zone_id=zone.zone_id,
                score=round(score, 4),
                classification=classification
            ))
        
        # Save to database using repository
        self.repository.save_execution(execution_id=execution_id, results=results)
        
        return ScoringResponse(
            execution_id=execution_id,
            results=results
        )

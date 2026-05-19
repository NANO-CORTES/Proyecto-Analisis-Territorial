import asyncio
import base64
import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
import httpx
from app.core.database import get_db
from app.services.indicators_service import IndicatorsService
from app.services.scoring_service import ScoringService
from app.services.hybrid_scoring_service import HybridScoringService
from typing import Optional
from app.schemas.scoring import ScoringRequest
router = APIRouter()
indicators_service = IndicatorsService()
hybrid_service = HybridScoringService()


AUDIT_LOG_URL = "http://audit-trace:8001/api/v1/audit/"


def _extract_user_id_from_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return "system"

    token = auth_header.split(" ", 1)[1].strip()
    if token.count(".") < 2:
        return "system"

    try:
        payload_b64 = token.split(".", 2)[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8"))
    except Exception:
        return "system"

    user_id = payload.get("sub") or payload.get("user_id") or payload.get("username") or payload.get("email")
    return str(user_id) if user_id else "system"


def _build_recommendation(score_value: Optional[float]) -> str:
    if score_value is None:
        return "No hay score disponible para generar recomendación."
    if score_value >= 0.75:
        return "Desempeño alto: mantener estrategias actuales y monitorear estabilidad."
    if score_value >= 0.50:
        return "Desempeño medio: reforzar intervenciones en indicadores más débiles."
    if score_value >= 0.30:
        return "Desempeño bajo: priorizar planes de mejora focalizados por zona."
    return "Desempeño crítico: activar plan de intervención inmediata."


async def _send_recommendation_audit_event(request: Request, zone_code: str, recommendation: str, score_value: Optional[float]) -> None:
    payload = {
        "service_name": "ms-analytics",
        "action": "RECOMMENDATIONS_GENERATED",
        "user_id": _extract_user_id_from_token(request),
        "details": json.dumps(
            {
                "zone_code": zone_code,
                "score_value": score_value,
                "recommendation": recommendation,
            }
        ),
    }
    headers = {}
    trace_id = request.headers.get("X-Trace-Id") or request.headers.get("x-trace-id")
    if trace_id:
        headers["X-Trace-Id"] = trace_id

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(AUDIT_LOG_URL, json=payload, headers=headers)
    except Exception:
        # No bloquear endpoint por fallos de auditoría
        pass

@router.post("/api/v1/indicators/calculate", tags=["analytics"])
async def calculate_indicators(transformation_run_id: str, db: Session = Depends(get_db)):
    try:
        return await indicators_service.calculate_indicators(transformation_run_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/scoring/execute", tags=["analytics"])
async def execute_scoring(
    request: Request,
    transformation_run_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        # Check if we have JSON body or if it is empty
        body_data = None
        try:
            body_bytes = await request.body()
            if body_bytes:
                body_data = await request.json()
        except Exception:
            pass

        if body_data:
            from app.schemas.scoring import ScoringRequest
            scoring_req = ScoringRequest(**body_data)
        else:
            if not transformation_run_id:
                raise HTTPException(status_code=400, detail="transformation_run_id query param or JSON body is required")
            
            from app.models.ranking import IndicatorResult
            indicators = db.query(IndicatorResult).filter(IndicatorResult.transformation_run_id == transformation_run_id).all()
            if not indicators:
                raise HTTPException(status_code=404, detail=f"No indicators found for run {transformation_run_id}")
            
            from app.schemas.scoring import ZoneIndicators, ScoringRequest
            zones = [
                ZoneIndicators(
                    zone_id=ind.zone_code,
                    poblacion=ind.population_indicator,
                    ingreso=ind.income_indicator,
                    educacion=ind.education_indicator,
                    competencia=ind.competition_indicator
                )
                for ind in indicators
            ]
            user_id = _extract_user_id_from_token(request)
            scoring_req = ScoringRequest(user_id=user_id, zones=zones)
            
        service = ScoringService(db) 
        return await service.execute(scoring_req)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/scoring/results", tags=["analytics"])
async def get_scoring_results(execution_id: str, db: Session = Depends(get_db)):
    from app.models.ranking import ZoneScore
    results = db.query(ZoneScore).filter(ZoneScore.execution_id == execution_id).all()
    if results:
        return results
        
    # Check analytics schema and map to public schema compatible structure
    try:
        from app.models.scoring import ZoneScore as AnalyticsZoneScore
        analytics_results = db.query(AnalyticsZoneScore).filter(AnalyticsZoneScore.execution_id == execution_id).all()
        if analytics_results:
            mapped = []
            for r in analytics_results:
                mapped.append({
                    "id": str(r.id),
                    "execution_id": r.execution_id,
                    "zone_code": r.zone_id,
                    "zone_name": r.zone_id,
                    "score_value": r.score_value,
                    "score_level": r.score_level,
                    "rank_position": r.rank_position or 1,
                })
            return mapped
    except Exception:
        pass
        
    return []

@router.get("/api/v1/zone-summary/{zone_code}", tags=["analytics"])
async def get_zone_summary(zone_code: str, request: Request, db: Session = Depends(get_db)):
    from app.models.ranking import ZoneScore, IndicatorResult
    # Obtener el score más reciente para esta zona
    score = db.query(ZoneScore).filter(ZoneScore.zone_code == zone_code).order_by(ZoneScore.created_at.desc()).first()
    # Obtener indicadores más recientes
    indicators = db.query(IndicatorResult).filter(IndicatorResult.zone_code == zone_code).order_by(IndicatorResult.created_at.desc()).first()

    score_value = getattr(score, "score_value", None)
    recommendation = _build_recommendation(score_value)
    asyncio.create_task(_send_recommendation_audit_event(request, zone_code, recommendation, score_value))

    return {
        "zone_code": zone_code,
        "score": score,
        "indicators": indicators,
        "recommendation": recommendation
    }
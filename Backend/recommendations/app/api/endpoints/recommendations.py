from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.schema import GenerateRequest, GenerateResponse, ZoneRecommendationResponse
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api/v1", tags=["HU-25 - Recomendaciones"])


def _get_service(db: Session = Depends(get_db)) -> RecommendationService:
    """
    Factory — DIP: el endpoint nunca conoce el repositorio concreto.
    """
    repository = RecommendationRepository(db)
    return RecommendationService(repository)


@router.post(
    "/recommendations/generate",
    response_model=GenerateResponse,
    summary="Generar recomendaciones para todas las zonas",
    description=(
        "Recibe score_execution_id y prediction_batch_id. "
        "Aplica reglas para generar fortalezas, riesgos y explicación por zona."
    ),
)
async def generate_recommendations(
    body: GenerateRequest,
    service: RecommendationService = Depends(_get_service),
):
    """
    HU-25: Generar recomendaciones explicadas por zona.

    Criterios cubiertos:
    ✓ Cada zona recibe fortaleza, riesgo y explicación general
    ✓ Texto en español claro sin jerga técnica
    ✓ Fortalezas y riesgos específicos al perfil de indicadores
    ✓ recommendation_level coincide con score_level
    ✓ Generación de 50 zonas en menos de 3 segundos
    """
    try:
        return await service.generate(
            score_execution_id=body.score_execution_id,
            prediction_batch_id=body.prediction_batch_id or "",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/recommendations/{zone_code}",
    response_model=ZoneRecommendationResponse,
    summary="Consultar recomendación de una zona",
    description="Retorna la recomendación más reciente generada para una zona específica.",
)
async def get_recommendation(
    zone_code: str,
    service: RecommendationService = Depends(_get_service),
):
    """
    HU-25: Consultar recomendación de zona específica.

    Criterios cubiertos:
    ✓ Retorna fortalezas (verde), riesgos (rojo) y explicación (azul)
    ✓ Usa BD real si existe, mock si no
    ✓ Genera en tiempo real si no hay recomendación guardada
    """
    try:
        result = await service.get_by_zone(zone_code)
        if not result.success:
            raise HTTPException(status_code=404, detail=result.error)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
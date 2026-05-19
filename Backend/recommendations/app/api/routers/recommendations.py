from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.application.dto import (
    GenerateRecommendationsRequest,
    RecommendationExecutionDTO,
    ZoneRecommendationDTO,
)
from app.application.use_cases.generate_recommendations import GenerateRecommendationsUseCase
from app.application.use_cases.get_recommendation import GetRecommendationByZoneUseCase
from app.infrastructure.di import (
    get_generate_recommendations_use_case,
    get_get_recommendation_use_case,
)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])

@router.post("/generate", response_model=RecommendationExecutionDTO)
async def generate(
    request: GenerateRecommendationsRequest,
    use_case: GenerateRecommendationsUseCase = Depends(get_generate_recommendations_use_case),
):
    try:
        return await use_case.execute(
            score_execution_id=request.score_execution_id,
            prediction_batch_id=request.prediction_batch_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@router.get("/{zone_code}", response_model=ZoneRecommendationDTO)
def get_for_zone(
    zone_code: str,
    use_case: GetRecommendationByZoneUseCase = Depends(get_get_recommendation_use_case),
):
    result = use_case.execute(zone_code)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No recommendation found for zone {zone_code}")
    return result

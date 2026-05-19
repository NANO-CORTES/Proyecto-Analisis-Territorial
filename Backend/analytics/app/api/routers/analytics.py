from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.application.dto import (
    IndicatorsCalculationResult,
    ScoringExecutionResult,
    ZoneSummary,
)
from app.application.use_cases.calculate_indicators import CalculateIndicatorsUseCase
from app.application.use_cases.execute_combined_scoring import ExecuteCombinedScoringUseCase
from app.application.use_cases.execute_scoring import ExecuteScoringUseCase
from app.application.use_cases.get_zone_summary import GetZoneSummaryUseCase
from app.infrastructure.di import (
    get_calculate_indicators_use_case,
    get_execute_combined_scoring_use_case,
    get_execute_scoring_use_case,
    get_zone_summary_use_case,
)

router = APIRouter(prefix="/api/v1", tags=["analytics"])

@router.post("/indicators/calculate", response_model=IndicatorsCalculationResult)
async def calculate_indicators(
    transformation_run_id: str,
    use_case: CalculateIndicatorsUseCase = Depends(get_calculate_indicators_use_case),
):
    try:
        return await use_case.execute(transformation_run_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@router.post("/scoring/execute", response_model=ScoringExecutionResult)
async def execute_scoring(
    transformation_run_id: str,
    use_case: ExecuteScoringUseCase = Depends(get_execute_scoring_use_case),
):
    try:
        return await use_case.execute(transformation_run_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@router.post("/scoring/combined", response_model=ScoringExecutionResult)
async def execute_combined_scoring(
    execution_id: str,
    use_case: ExecuteCombinedScoringUseCase = Depends(get_execute_combined_scoring_use_case),
):
    try:
        return await use_case.execute(execution_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@router.get("/zone-summary/{zone_code}", response_model=ZoneSummary)
def get_zone_summary(
    zone_code: str,
    use_case: GetZoneSummaryUseCase = Depends(get_zone_summary_use_case),
):
    return use_case.execute(zone_code)

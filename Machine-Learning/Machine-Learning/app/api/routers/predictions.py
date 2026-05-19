from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.application.dto import PredictRequest, PredictionsResponse
from app.application.use_cases.predict_for_zones import PredictForZonesUseCase
from app.infrastructure.di import get_predict_use_case

router = APIRouter(prefix="/api/v1/ml", tags=["predict"])


@router.post("/predict", response_model=PredictionsResponse)
async def predict(
    request: PredictRequest,
    use_case: PredictForZonesUseCase = Depends(get_predict_use_case),
):
    try:
        return await use_case.execute(request.zone_codes)
    except LookupError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.application.dto import RankingResponse
from app.application.use_cases.get_ranking import GetRankingUseCase
from app.infrastructure.di import get_ranking_use_case

router = APIRouter(prefix="/api/v1", tags=["ranking"])

@router.get("/ranking", response_model=RankingResponse)
def get_ranking(
    execution_id: str = Query(..., description="Scoring execution identifier"),
    level: Optional[str] = Query(None, description="Filter by score level: ALTA | MEDIA | BAJA"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    use_case: GetRankingUseCase = Depends(get_ranking_use_case),
):
    try:
        return use_case.execute(
            execution_id=execution_id,
            level=level.upper() if level else None,
            page=page,
            page_size=page_size,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

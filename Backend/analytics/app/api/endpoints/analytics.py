from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.indicators_service import IndicatorsService
from app.services.scoring_service import ScoringService
from app.interfaces.ranking_repository import IRankingRepository
from app.interfaces.indicators_repository import IIndicatorsRepository
from app.api.deps import getRankingRepo, getIndicatorsRepo
from typing import Optional

router = APIRouter()


@router.post("/api/v1/indicators/calculate", tags=["analytics"])
async def calculate_indicators(transformation_run_id: str, db: Session = Depends(get_db)):
    try:
        indicators_service = IndicatorsService()
        return await indicators_service.calculate_indicators(transformation_run_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/scoring/execute", tags=["analytics"])
async def execute_scoring(
    transformation_run_id: str,
    ranking_repo: IRankingRepository = Depends(getRankingRepo),
    indicators_repo: IIndicatorsRepository = Depends(getIndicatorsRepo),
):
    try:
        scoring_service = ScoringService(ranking_repo, indicators_repo)
        return await scoring_service.execute_scoring(transformation_run_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/scoring/results", tags=["analytics"])
async def get_scoring_results(
    execution_id: str,
    ranking_repo: IRankingRepository = Depends(getRankingRepo),
):
    results, _ = ranking_repo.get_by_execution(execution_id, None, 1000, 0)
    return results


@router.get("/api/v1/zone-summary/{zone_code}", tags=["analytics"])
async def get_zone_summary(
    zone_code: str,
    db: Session = Depends(get_db),
    indicators_repo: IIndicatorsRepository = Depends(getIndicatorsRepo),
):
    from app.models.ranking import ZoneScore
    score = db.query(ZoneScore).filter(ZoneScore.zone_code == zone_code).order_by(ZoneScore.created_at.desc()).first()
    indicators = indicators_repo.get_zone_summary(zone_code)

    return {
        "zone_code": zone_code,
        "score": score,
        "indicators": indicators,
    }
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.indicators_service import IndicatorsService
from app.services.scoring_service import ScoringService
from app.services.hybrid_scoring_service import HybridScoringService
from typing import Optional
from app.schemas.scoring import ScoringRequest
router = APIRouter()
indicators_service = IndicatorsService()
hybrid_service = HybridScoringService()


@router.post("/api/v1/indicators/calculate", tags=["analytics"])
async def calculate_indicators(transformation_run_id: str, db: Session = Depends(get_db)):
    try:
        return await indicators_service.calculate_indicators(transformation_run_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/scoring/execute", tags=["analytics"])
async def execute_scoring(request: ScoringRequest, db: Session = Depends(get_db)):
    try:
        
        service = ScoringService(db) 
        
        return await service.execute(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/scoring/results", tags=["analytics"])
async def get_scoring_results(execution_id: str, db: Session = Depends(get_db)):
    from app.models.ranking import ZoneScore
    results = db.query(ZoneScore).filter(ZoneScore.execution_id == execution_id).all()
    return results

@router.get("/api/v1/zone-summary/{zone_code}", tags=["analytics"])
async def get_zone_summary(zone_code: str, db: Session = Depends(get_db)):
    from app.models.ranking import ZoneScore, IndicatorResult
    # Obtener el score más reciente para esta zona
    score = db.query(ZoneScore).filter(ZoneScore.zone_code == zone_code).order_by(ZoneScore.created_at.desc()).first()
    # Obtener indicadores más recientes
    indicators = db.query(IndicatorResult).filter(IndicatorResult.zone_code == zone_code).order_by(IndicatorResult.created_at.desc()).first()
    
    return {
        "zone_code": zone_code,
        "score": score,
        "indicators": indicators
    }
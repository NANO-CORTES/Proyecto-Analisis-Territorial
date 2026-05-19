from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.interfaces.ranking_repository import IRankingRepository
from app.models.ranking import ZoneScore, ScoreExecution, ScoreLevel

# Datos para cuando no hay scoring real aún
# Se eliminan cuando HU-15 esté completa
_MOCK_ZONES = [
    {"zone_code": "BOG-001", "zone_name": "chapinero",    "score_value": 0.87, "score_level": "ALTA"},
    {"zone_code": "BOG-003", "zone_name": "usaquen",      "score_value": 0.82, "score_level": "ALTA"},
    {"zone_code": "BOG-007", "zone_name": "fontibon",     "score_value": 0.76, "score_level": "ALTA"},
    {"zone_code": "BOG-002", "zone_name": "suba",         "score_value": 0.65, "score_level": "MEDIA"},
    {"zone_code": "BOG-006", "zone_name": "bosa",         "score_value": 0.61, "score_level": "MEDIA"},
    {"zone_code": "BOG-008", "zone_name": "puente aranda","score_value": 0.58, "score_level": "MEDIA"},
    {"zone_code": "BOG-009", "zone_name": "barrios unidos","score_value": 0.54,"score_level": "MEDIA"},
    {"zone_code": "BOG-010", "zone_name": "teusaquillo",  "score_value": 0.51, "score_level": "MEDIA"},
    {"zone_code": "BOG-004", "zone_name": "kennedy",      "score_value": 0.38, "score_level": "BAJA"},
    {"zone_code": "BOG-005", "zone_name": "engativa",     "score_value": 0.31, "score_level": "BAJA"},
    {"zone_code": "BOG-011", "zone_name": "bosa occidental","score_value": 0.28,"score_level": "BAJA"},
    {"zone_code": "BOG-012", "zone_name": "ciudad bolivar","score_value": 0.22,"score_level": "BAJA"},
]


class RankingRepository(IRankingRepository):
    """
    Implementación concreta del repositorio de ranking.
    SRP: solo maneja acceso a datos de ranking.
    LSP: cumple completamente el contrato de IRankingRepository.
    """

    def __init__(self, db: Session):
        self._db = db

    def get_execution(self, execution_id: str) -> Optional[ScoreExecution]:
        # 1. Search analytics schema first
        try:
            from app.models.scoring import ScoreExecution as AnalyticsScoreExecution
            ae = self._db.query(AnalyticsScoreExecution).filter(
                AnalyticsScoreExecution.id == execution_id
            ).first()
            if ae:
                return ScoreExecution(
                    id=ae.id,
                    transformation_run_id=ae.transformation_run_id,
                    configuration_id=ae.configuration_id,
                    total_zones=len(ae.scores) if ae.scores else 0,
                    created_at=ae.created_at
                )
        except Exception:
            pass

        # 2. Fallback to public schema
        return self._db.query(ScoreExecution).filter(
            ScoreExecution.id == execution_id
        ).first()

    def get_by_execution(
        self,
        execution_id: str,
        level: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ZoneScore], int]:
        # 1. Check analytics schema first
        try:
            from app.models.scoring import ZoneScore as AnalyticsZoneScore
            from app.models.scoring import ScoreExecution as AnalyticsScoreExecution
            
            ae = self._db.query(AnalyticsScoreExecution).filter(
                AnalyticsScoreExecution.id == execution_id
            ).first()
            if ae:
                query_analytics = self._db.query(AnalyticsZoneScore).filter(
                    AnalyticsZoneScore.execution_id == execution_id
                )
                if level:
                    query_analytics = query_analytics.filter(AnalyticsZoneScore.score_level == level)
                
                total = query_analytics.with_entities(func.count(AnalyticsZoneScore.id)).scalar() or 0
                if total > 0:
                    rows = query_analytics.order_by(AnalyticsZoneScore.score_value.desc()).offset(offset).limit(limit).all()
                    
                    mapped_zones = []
                    for i, r in enumerate(rows, start=offset + 1):
                        # Try to find zone_name from indicator results
                        from app.models.ranking import IndicatorResult
                        ind = self._db.query(IndicatorResult).filter(
                            IndicatorResult.transformation_run_id == ae.transformation_run_id,
                            IndicatorResult.zone_code == r.zone_id
                        ).first()
                        zone_name = ind.zone_name if ind else r.zone_id
                        
                        lvl = ScoreLevel.BAJA
                        if r.score_level == "ALTA":
                            lvl = ScoreLevel.ALTA
                        elif r.score_level == "MEDIA":
                            lvl = ScoreLevel.MEDIA
                        
                        mapped_zones.append(ZoneScore(
                            id=str(r.id),
                            execution_id=r.execution_id,
                            zone_code=r.zone_id,
                            zone_name=zone_name,
                            score_value=r.score_value,
                            score_level=lvl,
                            rank_position=r.rank_position or i,
                            created_at=getattr(r, "created_at", None)
                        ))
                    return mapped_zones, total
        except Exception:
            pass

        # 2. Fallback to public schema
        query = self._db.query(ZoneScore).filter(
            ZoneScore.execution_id == execution_id
        )
        if level:
            query = query.filter(ZoneScore.score_level == level)

        total = query.with_entities(func.count()).scalar()
        zones = query.order_by(ZoneScore.rank_position.asc()) \
                     .offset(offset).limit(limit).all()
        return zones, total

    def get_mock_data(
        self,
        execution_id: str,
        level: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[dict], int]:
        # Filtrar por nivel si se pidió
        filtered = [
            z for z in _MOCK_ZONES
            if level is None or z["score_level"] == level
        ]
        total = len(filtered)
        # Asignar rank_position después del filtro
        paginated = filtered[offset: offset + limit]
        result = []
        for i, z in enumerate(paginated, start=offset + 1):
            result.append({**z, "rank_position": i, "execution_id": execution_id})
        return result, total
from __future__ import annotations

from typing import Optional

from app.application.dto import ZoneRecommendationDTO
from app.domain.ports.recommendation_repository import IRecommendationRepository

class GetRecommendationByZoneUseCase:
    def __init__(self, repository: IRecommendationRepository):
        self._repository = repository

    def execute(self, zone_code: str) -> Optional[ZoneRecommendationDTO]:
        rec = self._repository.latest_for_zone(zone_code)
        if rec is None:
            return None
        return ZoneRecommendationDTO(
            zone_code=rec.zone_code,
            zone_name=rec.zone_name,
            recommendation_level=rec.recommendation_level,
            strengths=rec.strengths,
            risks=rec.risks,
            explanation=rec.explanation,
            generated_at=rec.generated_at,
        )

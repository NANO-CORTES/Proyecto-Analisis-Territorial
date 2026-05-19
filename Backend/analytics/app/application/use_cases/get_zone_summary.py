from __future__ import annotations

from app.application.dto import ZoneIndicatorDTO, ZoneRankingItem, ZoneSummary
from app.application.use_cases.get_ranking import GetRankingUseCase
from app.domain.ports.indicator_repository import IIndicatorRepository
from app.domain.ports.score_repository import IScoreRepository

class GetZoneSummaryUseCase:
    def __init__(
        self,
        indicator_repository: IIndicatorRepository,
        score_repository: IScoreRepository,
    ):
        self._indicators = indicator_repository
        self._scores = score_repository

    def execute(self, zone_code: str) -> ZoneSummary:
        partial = False

        indicators = self._indicators.latest_for_zone(zone_code)
        indicator_dto = (
            ZoneIndicatorDTO(**indicators.as_dict()) if indicators is not None else None
        )
        if indicator_dto is None:
            partial = True

        score = self._scores.latest_for_zone(zone_code)
        score_dto = GetRankingUseCase._to_item(score) if score is not None else None
        if score_dto is None:
            partial = True

        return ZoneSummary(
            zone_code=zone_code,
            indicators=indicator_dto,
            score=score_dto,
            partial=partial,
        )

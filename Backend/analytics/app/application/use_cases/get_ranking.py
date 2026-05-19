from __future__ import annotations

from typing import Optional

from app.application.dto import RankingResponse, ZoneRankingItem
from app.domain.entities import ZoneScore
from app.domain.ports.score_repository import IScoreRepository
from app.domain.value_objects import ScoreLevel

class GetRankingUseCase:
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    def __init__(self, score_repository: IScoreRepository):
        self._scores = score_repository

    def execute(
        self,
        execution_id: str,
        level: Optional[str],
        page: int,
        page_size: int,
    ) -> RankingResponse:
        self._validate(page, page_size, level)
        offset = (page - 1) * page_size
        scores, total = self._scores.list_scores(execution_id, level, page_size, offset)
        total_pages = max(1, -(-total // page_size)) if total else 0

        return RankingResponse(
            success=True,
            execution_id=execution_id,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
            level_filter=level,
            data=[self._to_item(s) for s in scores],
        )

    def _validate(self, page: int, page_size: int, level: Optional[str]) -> None:
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > self.MAX_PAGE_SIZE:
            raise ValueError(f"page_size must be between 1 and {self.MAX_PAGE_SIZE}")
        if level is not None and level not in {e.value for e in ScoreLevel}:
            raise ValueError(f"level must be one of {[e.value for e in ScoreLevel]}")

    @staticmethod
    def _to_item(score: ZoneScore) -> ZoneRankingItem:
        return ZoneRankingItem(
            rank_position=score.rank_position,
            zone_code=score.zone_code,
            zone_name=score.zone_name,
            score_value=round(score.score_value, 4),
            score_level=score.score_level,
            execution_id=score.execution_id or "",
            combined_score=score.combined_score,
            prediction_value=score.prediction_value,
            discrepancy_flag=score.discrepancy_flag,
        )

from __future__ import annotations

import uuid

from app.application.dto import RecommendationExecutionDTO, ZoneRecommendationDTO
from app.domain.entities import RecommendationExecution
from app.domain.ports.analytics_provider import IAnalyticsProvider
from app.domain.ports.audit_publisher import IAuditPublisher
from app.domain.ports.recommendation_repository import IRecommendationRepository
from app.domain.services.recommendation_builder import RecommendationBuilder

class GenerateRecommendationsUseCase:
    def __init__(
        self,
        analytics_provider: IAnalyticsProvider,
        repository: IRecommendationRepository,
        builder: RecommendationBuilder,
        audit_publisher: IAuditPublisher,
    ):
        self._analytics = analytics_provider
        self._repository = repository
        self._builder = builder
        self._audit = audit_publisher

    async def execute(
        self,
        score_execution_id: str,
        prediction_batch_id: str | None,
    ) -> RecommendationExecutionDTO:
        zones = await self._analytics.list_zone_results(score_execution_id)
        if not zones:
            raise ValueError(
                f"No analytics results found for execution {score_execution_id}"
            )

        recommendations = self._builder.build_many(zones)
        execution = RecommendationExecution(
            id=str(uuid.uuid4()),
            score_execution_id=score_execution_id,
            prediction_batch_id=prediction_batch_id,
            total_zones=len(recommendations),
        )
        for rec in recommendations:
            rec.execution_id = execution.id

        self._repository.create_execution(execution)
        self._repository.save_all(execution.id, recommendations)

        await self._audit.publish(
            "RECOMMENDATIONS_GENERATED",
            {
                "execution_id": execution.id,
                "score_execution_id": score_execution_id,
                "total_zones": execution.total_zones,
            },
        )

        return RecommendationExecutionDTO(
            execution_id=execution.id,
            score_execution_id=score_execution_id,
            prediction_batch_id=prediction_batch_id,
            total_zones=execution.total_zones,
            created_at=execution.created_at,
            recommendations=[self._to_dto(r) for r in recommendations],
        )

    @staticmethod
    def _to_dto(rec) -> ZoneRecommendationDTO:
        return ZoneRecommendationDTO(
            zone_code=rec.zone_code,
            zone_name=rec.zone_name,
            recommendation_level=rec.recommendation_level,
            strengths=rec.strengths,
            risks=rec.risks,
            explanation=rec.explanation,
            generated_at=rec.generated_at,
        )

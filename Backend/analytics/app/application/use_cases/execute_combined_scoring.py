from __future__ import annotations

from app.application.dto import ScoringExecutionResult
from app.domain.ports.audit_publisher import IAuditPublisher
from app.domain.ports.configuration_provider import IConfigurationProvider
from app.domain.ports.prediction_provider import IPredictionProvider
from app.domain.ports.score_repository import IScoreRepository
from app.domain.services.scoring_calculator import ScoringCalculator

class ExecuteCombinedScoringUseCase:
    def __init__(
        self,
        score_repository: IScoreRepository,
        configuration_provider: IConfigurationProvider,
        prediction_provider: IPredictionProvider,
        calculator: ScoringCalculator,
        audit_publisher: IAuditPublisher,
    ):
        self._scores = score_repository
        self._configuration = configuration_provider
        self._predictions = prediction_provider
        self._calculator = calculator
        self._audit = audit_publisher

    async def execute(self, execution_id: str) -> ScoringExecutionResult:
        scores, total = self._scores.list_scores(execution_id, level=None, limit=10_000, offset=0)
        if not scores:
            raise ValueError(f"No scoring results for execution {execution_id}")

        zone_codes = [s.zone_code for s in scores]
        predictions = await self._predictions.predict_for_zones(zone_codes)
        weights = await self._configuration.get_combined_weights()

        enriched = self._calculator.combine(scores, predictions, weights)
        self._scores.save_scores(execution_id, enriched)

        await self._audit.publish(
            "COMBINED_SCORING_EXECUTED",
            {
                "execution_id": execution_id,
                "scoring_weight": weights.scoring,
                "ml_weight": weights.ml,
                "zones_with_prediction": sum(1 for s in enriched if s.prediction_value is not None),
            },
        )

        execution = self._scores.get_execution(execution_id)
        return ScoringExecutionResult(
            execution_id=execution_id,
            transformation_run_id=execution.transformation_run_id if execution else "",
            configuration_id=execution.configuration_id if execution else None,
            total_zones=total,
            created_at=execution.created_at if execution else scores[0].created_at,
        )

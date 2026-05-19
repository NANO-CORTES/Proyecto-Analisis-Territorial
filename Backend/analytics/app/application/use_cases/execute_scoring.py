from __future__ import annotations

import uuid

from app.application.dto import ScoringExecutionResult
from app.domain.entities import ScoringExecution
from app.domain.ports.audit_publisher import IAuditPublisher
from app.domain.ports.configuration_provider import IConfigurationProvider
from app.domain.ports.indicator_repository import IIndicatorRepository
from app.domain.ports.score_repository import IScoreRepository
from app.domain.services.scoring_calculator import ScoringCalculator

class ExecuteScoringUseCase:
    def __init__(
        self,
        indicator_repository: IIndicatorRepository,
        score_repository: IScoreRepository,
        configuration_provider: IConfigurationProvider,
        calculator: ScoringCalculator,
        audit_publisher: IAuditPublisher,
    ):
        self._indicators = indicator_repository
        self._scores = score_repository
        self._configuration = configuration_provider
        self._calculator = calculator
        self._audit = audit_publisher

    async def execute(self, transformation_run_id: str) -> ScoringExecutionResult:
        indicators = self._indicators.list_by_run(transformation_run_id)
        if not indicators:
            raise ValueError(
                f"No indicators found for run {transformation_run_id}. Calculate them first."
            )

        config_id, weights = await self._configuration.get_active_weights()
        zone_scores = self._calculator.calculate(indicators, weights)

        execution = ScoringExecution(
            id=str(uuid.uuid4()),
            transformation_run_id=transformation_run_id,
            configuration_id=config_id,
            total_zones=len(zone_scores),
        )
        for score in zone_scores:
            score.execution_id = execution.id

        self._scores.create_execution(execution)
        self._scores.save_scores(execution.id, zone_scores)

        await self._audit.publish(
            "SCORING_EXECUTED",
            {
                "execution_id": execution.id,
                "transformation_run_id": transformation_run_id,
                "configuration_id": config_id,
                "total_zones": execution.total_zones,
            },
        )

        return ScoringExecutionResult(
            execution_id=execution.id,
            transformation_run_id=transformation_run_id,
            configuration_id=config_id,
            total_zones=execution.total_zones,
            created_at=execution.created_at,
        )

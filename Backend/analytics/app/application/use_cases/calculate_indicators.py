from __future__ import annotations

from app.application.dto import IndicatorsCalculationResult, ZoneIndicatorDTO
from app.domain.ports.audit_publisher import IAuditPublisher
from app.domain.ports.indicator_repository import IIndicatorRepository
from app.domain.ports.transformation_provider import ITransformationProvider

class CalculateIndicatorsUseCase:
    def __init__(
        self,
        transformation_provider: ITransformationProvider,
        indicator_repository: IIndicatorRepository,
        audit_publisher: IAuditPublisher,
    ):
        self._transformation = transformation_provider
        self._repository = indicator_repository
        self._audit = audit_publisher

    async def execute(self, transformation_run_id: str) -> IndicatorsCalculationResult:
        indicators = await self._transformation.fetch_zone_indicators(transformation_run_id)
        if not indicators:
            raise ValueError(
                f"No transformation data available for run {transformation_run_id}"
            )

        self._repository.save_all(transformation_run_id, indicators)
        await self._audit.publish(
            "INDICATORS_CALCULATED",
            {
                "transformation_run_id": transformation_run_id,
                "total_zones": len(indicators),
            },
        )
        return IndicatorsCalculationResult(
            transformation_run_id=transformation_run_id,
            total_zones=len(indicators),
            zones=[ZoneIndicatorDTO(**ind.as_dict()) for ind in indicators],
        )

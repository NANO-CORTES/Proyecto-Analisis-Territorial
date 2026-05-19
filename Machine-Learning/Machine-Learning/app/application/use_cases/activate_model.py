from __future__ import annotations

from app.application.dto import ExperimentDTO, TrainedModelDTO
from app.domain.ports.audit_publisher import IAuditPublisher
from app.domain.ports.experiment_repository import IExperimentRepository


class ActivateModelUseCase:
    def __init__(
        self,
        experiment_repository: IExperimentRepository,
        audit_publisher: IAuditPublisher,
    ):
        self._experiments = experiment_repository
        self._audit = audit_publisher

    async def execute(self, experiment_id: str) -> ExperimentDTO:
        experiment = self._experiments.find_experiment(experiment_id)
        if experiment is None:
            raise ValueError(f"experiment {experiment_id} not found")

        self._experiments.activate(experiment_id)
        models = self._experiments.find_models_for_experiment(experiment_id)

        await self._audit.publish(
            "MODEL_ACTIVATED",
            {"experiment_id": experiment_id},
        )

        return ExperimentDTO(
            id=experiment.id,
            transformation_run_id=experiment.transformation_run_id,
            algorithm=experiment.algorithm,
            target_variable=experiment.target_variable,
            features_used=experiment.features_used,
            r2_score=experiment.metrics.r2,
            mae=experiment.metrics.mae,
            rmse=experiment.metrics.rmse,
            created_at=experiment.created_at,
            status=experiment.status,
            trained_models=[
                TrainedModelDTO(id=m.id, storage_path=m.storage_path, is_active=m.is_active)
                for m in models
            ],
        )

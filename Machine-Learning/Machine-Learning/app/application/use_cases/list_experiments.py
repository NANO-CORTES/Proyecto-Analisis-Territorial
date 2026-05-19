from __future__ import annotations

from typing import List

from app.application.dto import ExperimentDTO, TrainedModelDTO
from app.domain.ports.experiment_repository import IExperimentRepository


class ListExperimentsUseCase:
    def __init__(self, repository: IExperimentRepository):
        self._repository = repository

    def execute(self) -> List[ExperimentDTO]:
        experiments = self._repository.list_experiments()
        result: List[ExperimentDTO] = []
        for exp in experiments:
            models = self._repository.find_models_for_experiment(exp.id)
            result.append(
                ExperimentDTO(
                    id=exp.id,
                    transformation_run_id=exp.transformation_run_id,
                    algorithm=exp.algorithm,
                    target_variable=exp.target_variable,
                    features_used=exp.features_used,
                    r2_score=exp.metrics.r2,
                    mae=exp.metrics.mae,
                    rmse=exp.metrics.rmse,
                    created_at=exp.created_at,
                    status=exp.status,
                    trained_models=[
                        TrainedModelDTO(id=m.id, storage_path=m.storage_path, is_active=m.is_active)
                        for m in models
                    ],
                )
            )
        return result

from __future__ import annotations

import uuid
from typing import List

from app.application.dto import ExperimentDTO, TrainedModelDTO
from app.domain.entities import MLExperiment, TrainedModel, ZoneFeatures
from app.domain.ports.audit_publisher import IAuditPublisher
from app.domain.ports.experiment_repository import IExperimentRepository
from app.domain.ports.model_storage import IModelStorage
from app.domain.ports.zone_data_provider import IZoneDataProvider
from app.domain.services.model_trainer import ModelTrainer
from app.domain.value_objects import Algorithm


class TrainModelUseCase:
    def __init__(
        self,
        data_provider: IZoneDataProvider,
        experiment_repository: IExperimentRepository,
        trainer: ModelTrainer,
        storage: IModelStorage,
        audit_publisher: IAuditPublisher,
    ):
        self._data = data_provider
        self._experiments = experiment_repository
        self._trainer = trainer
        self._storage = storage
        self._audit = audit_publisher

    async def execute(
        self,
        transformation_run_id: str,
        algorithm: str,
        target_variable: str,
    ) -> ExperimentDTO:
        zones = self._data.list_for_run(transformation_run_id)
        if not zones:
            raise ValueError(f"no transformed data found for run {transformation_run_id}")

        rows, targets, feature_columns = self._build_dataset(zones, target_variable)
        artifact = self._trainer.train(rows, targets, feature_columns, Algorithm(algorithm))

        experiment = MLExperiment(
            id=str(uuid.uuid4()),
            transformation_run_id=transformation_run_id,
            algorithm=algorithm,
            target_variable=target_variable,
            features_used=feature_columns,
            metrics=artifact.metrics,
        )
        saved_experiment = self._experiments.save_experiment(experiment)

        storage_path = self._storage.save(saved_experiment.id, artifact.model)
        trained_model = TrainedModel(
            id=str(uuid.uuid4()),
            experiment_id=saved_experiment.id,
            storage_path=storage_path,
            is_active=False,
        )
        saved_model = self._experiments.save_trained_model(trained_model)

        await self._audit.publish(
            "MODEL_TRAINED",
            {
                "experiment_id": saved_experiment.id,
                "algorithm": algorithm,
                "r2": artifact.metrics.r2,
                "mae": artifact.metrics.mae,
                "rmse": artifact.metrics.rmse,
            },
        )

        return ExperimentDTO(
            id=saved_experiment.id,
            transformation_run_id=transformation_run_id,
            algorithm=algorithm,
            target_variable=target_variable,
            features_used=feature_columns,
            r2_score=artifact.metrics.r2,
            mae=artifact.metrics.mae,
            rmse=artifact.metrics.rmse,
            created_at=saved_experiment.created_at,
            status=saved_experiment.status,
            trained_models=[TrainedModelDTO(
                id=saved_model.id,
                storage_path=saved_model.storage_path,
                is_active=saved_model.is_active,
            )],
        )

    def _build_dataset(
        self,
        zones: List[ZoneFeatures],
        target_variable: str,
    ) -> tuple[list, list, List[str]]:
        feature_columns = [c for c in ModelTrainer.SUPPORTED_FEATURES if c != target_variable]
        rows: List[List[float]] = []
        targets: List[float] = []
        for zone in zones:
            row = zone.as_feature_vector(feature_columns)
            target = self._compute_target(zone, target_variable)
            rows.append(row)
            targets.append(target)
        return rows, targets, feature_columns

    @staticmethod
    def _compute_target(zone: ZoneFeatures, target_variable: str) -> float:
        if target_variable == "territorial_score":
            return float(
                0.3 * zone.education
                + 0.3 * zone.income
                + 0.2 * zone.economic_activity
                + 0.2 * zone.commercial_presence
            )
        mapping = {
            "population_density": zone.population,
            "average_income": zone.income,
            "education_level": zone.education,
            "economic_activity_index": zone.economic_activity,
            "commercial_presence_index": zone.commercial_presence,
        }
        if target_variable not in mapping:
            raise ValueError(f"unknown target variable: {target_variable}")
        return float(mapping[target_variable])

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities import MLExperiment, TrainedModel, TrainingMetrics
from app.domain.ports.experiment_repository import IExperimentRepository
from app.infrastructure.persistence.models import MLExperimentModel, TrainedModelRow


class SqlExperimentRepository(IExperimentRepository):
    def __init__(self, db: Session):
        self._db = db

    def save_experiment(self, experiment: MLExperiment) -> MLExperiment:
        row = MLExperimentModel(
            id=experiment.id,
            transformation_run_id=experiment.transformation_run_id,
            algorithm=experiment.algorithm,
            target_variable=experiment.target_variable,
            features_used=experiment.features_used,
            r2_score=experiment.metrics.r2,
            mae=experiment.metrics.mae,
            rmse=experiment.metrics.rmse,
            status=experiment.status,
            created_at=experiment.created_at,
        )
        self._db.add(row)
        self._db.commit()
        return experiment

    def save_trained_model(self, model: TrainedModel) -> TrainedModel:
        row = TrainedModelRow(
            id=model.id,
            experiment_id=model.experiment_id,
            storage_path=model.storage_path,
            is_active=model.is_active,
        )
        self._db.add(row)
        self._db.commit()
        return model

    def list_experiments(self) -> List[MLExperiment]:
        rows = (
            self._db.query(MLExperimentModel)
            .order_by(MLExperimentModel.created_at.desc())
            .all()
        )
        return [self._to_entity(r) for r in rows]

    def find_experiment(self, experiment_id: str) -> Optional[MLExperiment]:
        row = self._db.get(MLExperimentModel, experiment_id)
        return self._to_entity(row) if row else None

    def find_models_for_experiment(self, experiment_id: str) -> List[TrainedModel]:
        rows = (
            self._db.query(TrainedModelRow)
            .filter(TrainedModelRow.experiment_id == experiment_id)
            .all()
        )
        return [self._to_model(r) for r in rows]

    def activate(self, experiment_id: str) -> None:
        self._db.query(TrainedModelRow).update({TrainedModelRow.is_active: False})
        self._db.query(TrainedModelRow).filter(
            TrainedModelRow.experiment_id == experiment_id
        ).update({TrainedModelRow.is_active: True})
        self._db.commit()

    def find_active_model(self) -> Optional[TrainedModel]:
        row = (
            self._db.query(TrainedModelRow)
            .filter(TrainedModelRow.is_active.is_(True))
            .first()
        )
        return self._to_model(row) if row else None

    @staticmethod
    def _to_entity(row: MLExperimentModel) -> MLExperiment:
        return MLExperiment(
            id=row.id,
            transformation_run_id=row.transformation_run_id,
            algorithm=row.algorithm,
            target_variable=row.target_variable,
            features_used=list(row.features_used or []),
            metrics=TrainingMetrics(
                r2=float(row.r2_score or 0.0),
                mae=float(row.mae or 0.0),
                rmse=float(row.rmse or 0.0),
            ),
            status=row.status or "COMPLETED",
            created_at=row.created_at,
        )

    @staticmethod
    def _to_model(row: TrainedModelRow) -> TrainedModel:
        return TrainedModel(
            id=row.id,
            experiment_id=row.experiment_id,
            storage_path=row.storage_path,
            is_active=bool(row.is_active),
        )

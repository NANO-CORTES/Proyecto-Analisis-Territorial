from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.activate_model import ActivateModelUseCase
from app.application.use_cases.list_experiments import ListExperimentsUseCase
from app.application.use_cases.predict_for_zones import PredictForZonesUseCase
from app.application.use_cases.train_model import TrainModelUseCase
from app.core.database import get_db
from app.domain.services.model_trainer import ModelTrainer
from app.domain.services.prediction_clamper import PredictionClamper
from app.infrastructure.http.audit_client import HttpAuditPublisher
from app.infrastructure.persistence.experiment_repository_sql import SqlExperimentRepository
from app.infrastructure.persistence.prediction_repository_sql import SqlPredictionRepository
from app.infrastructure.persistence.zone_data_provider_sql import SqlZoneDataProvider
from app.infrastructure.storage.joblib_model_storage import JoblibModelStorage


def get_train_model_use_case(db: Session = Depends(get_db)) -> TrainModelUseCase:
    return TrainModelUseCase(
        data_provider=SqlZoneDataProvider(db),
        experiment_repository=SqlExperimentRepository(db),
        trainer=ModelTrainer(),
        storage=JoblibModelStorage(),
        audit_publisher=HttpAuditPublisher(),
    )


def get_activate_model_use_case(db: Session = Depends(get_db)) -> ActivateModelUseCase:
    return ActivateModelUseCase(
        experiment_repository=SqlExperimentRepository(db),
        audit_publisher=HttpAuditPublisher(),
    )


def get_list_experiments_use_case(db: Session = Depends(get_db)) -> ListExperimentsUseCase:
    return ListExperimentsUseCase(SqlExperimentRepository(db))


def get_predict_use_case(db: Session = Depends(get_db)) -> PredictForZonesUseCase:
    return PredictForZonesUseCase(
        data_provider=SqlZoneDataProvider(db),
        experiment_repository=SqlExperimentRepository(db),
        prediction_repository=SqlPredictionRepository(db),
        storage=JoblibModelStorage(),
        clamper=PredictionClamper(),
        audit_publisher=HttpAuditPublisher(),
    )

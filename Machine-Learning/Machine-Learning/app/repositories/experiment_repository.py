from typing import List, Optional
from sqlalchemy.orm import Session
from app.interfaces.experiment_repository import IExperimentRepository
from app.models.ml import MLExperiment, TrainedModel, TransformedZoneData


class ExperimentRepository(IExperimentRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_transformed_data(self, transformation_run_id: str) -> List[TransformedZoneData]:
        return self._db.query(TransformedZoneData).filter(
            TransformedZoneData.transformation_run_id == transformation_run_id
        ).all()

    def create_experiment(self, experiment: MLExperiment) -> MLExperiment:
        self._db.add(experiment)
        self._db.commit()
        self._db.refresh(experiment)
        return experiment

    def create_trained_model(self, model: TrainedModel) -> TrainedModel:
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return model

    def get_all_experiments(self) -> List[MLExperiment]:
        return self._db.query(MLExperiment).order_by(MLExperiment.created_at.desc()).all()

    def get_experiment_by_id(self, experiment_id: str) -> Optional[MLExperiment]:
        return self._db.query(MLExperiment).filter(MLExperiment.id == experiment_id).first()

    def activate_experiment_models(self, experiment_id: str) -> None:
        self._db.query(TrainedModel).update({TrainedModel.is_active: False})
        models = self._db.query(TrainedModel).filter(TrainedModel.experiment_id == experiment_id).all()
        for m in models:
            m.is_active = True
        self._db.commit()

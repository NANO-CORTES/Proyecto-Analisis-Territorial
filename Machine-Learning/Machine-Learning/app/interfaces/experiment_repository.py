from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.ml import MLExperiment, TrainedModel, TransformedZoneData


class IExperimentRepository(ABC):
    @abstractmethod
    def get_transformed_data(self, transformation_run_id: str) -> List[TransformedZoneData]:
        ...

    @abstractmethod
    def create_experiment(self, experiment: MLExperiment) -> MLExperiment:
        ...

    @abstractmethod
    def create_trained_model(self, model: TrainedModel) -> TrainedModel:
        ...

    @abstractmethod
    def get_all_experiments(self) -> List[MLExperiment]:
        ...

    @abstractmethod
    def get_experiment_by_id(self, experiment_id: str) -> Optional[MLExperiment]:
        ...

    @abstractmethod
    def activate_experiment_models(self, experiment_id: str) -> None:
        ...

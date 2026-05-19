from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import MLExperiment, TrainedModel


class IExperimentRepository(ABC):
    @abstractmethod
    def save_experiment(self, experiment: MLExperiment) -> MLExperiment: ...

    @abstractmethod
    def save_trained_model(self, model: TrainedModel) -> TrainedModel: ...

    @abstractmethod
    def list_experiments(self) -> List[MLExperiment]: ...

    @abstractmethod
    def find_experiment(self, experiment_id: str) -> Optional[MLExperiment]: ...

    @abstractmethod
    def find_models_for_experiment(self, experiment_id: str) -> List[TrainedModel]: ...

    @abstractmethod
    def activate(self, experiment_id: str) -> None: ...

    @abstractmethod
    def find_active_model(self) -> Optional[TrainedModel]: ...

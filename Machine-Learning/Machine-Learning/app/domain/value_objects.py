from __future__ import annotations

from enum import Enum


class Algorithm(str, Enum):
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"


class PredictionLabel(str, Enum):
    HIGH = "Alto"
    MEDIUM = "Medio"
    LOW = "Bajo"

    @classmethod
    def from_value(cls, value: float) -> "PredictionLabel":
        if value > 0.7:
            return cls.HIGH
        if value >= 0.4:
            return cls.MEDIUM
        return cls.LOW

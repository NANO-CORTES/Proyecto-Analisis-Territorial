from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from app.domain.entities import TrainingMetrics
from app.domain.value_objects import Algorithm


@dataclass
class TrainingArtifact:
    model: Any
    feature_columns: List[str]
    metrics: TrainingMetrics


class ModelTrainer:
    SUPPORTED_FEATURES = [
        "population_density",
        "average_income",
        "education_level",
        "economic_activity_index",
        "commercial_presence_index",
    ]

    def train(
        self,
        rows: List[List[float]],
        targets: List[float],
        feature_columns: List[str],
        algorithm: Algorithm,
    ) -> TrainingArtifact:
        if len(rows) < 10:
            raise ValueError("at least 10 samples are required for training")

        x_train, x_test, y_train, y_test = train_test_split(
            rows, targets, test_size=0.2, random_state=42
        )
        estimator = self._estimator(algorithm)
        estimator.fit(x_train, y_train)
        y_pred = estimator.predict(x_test)

        metrics = TrainingMetrics(
            r2=float(r2_score(y_test, y_pred)),
            mae=float(mean_absolute_error(y_test, y_pred)),
            rmse=float(np.sqrt(mean_squared_error(y_test, y_pred))),
        )
        return TrainingArtifact(model=estimator, feature_columns=feature_columns, metrics=metrics)

    @staticmethod
    def _estimator(algorithm: Algorithm):
        if algorithm == Algorithm.LINEAR_REGRESSION:
            return LinearRegression()
        if algorithm == Algorithm.RANDOM_FOREST:
            return RandomForestRegressor(random_state=42)
        if algorithm == Algorithm.GRADIENT_BOOSTING:
            return GradientBoostingRegressor(random_state=42)
        raise ValueError(f"unsupported algorithm: {algorithm}")

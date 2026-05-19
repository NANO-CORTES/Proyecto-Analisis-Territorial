from __future__ import annotations

import os
from typing import Any

import joblib

from app.core.config import settings
from app.domain.ports.model_storage import IModelStorage


class JoblibModelStorage(IModelStorage):
    def __init__(self, directory: str = settings.models_dir):
        self._directory = directory
        os.makedirs(self._directory, exist_ok=True)

    def save(self, model_id: str, model_object: Any) -> str:
        path = os.path.join(self._directory, f"model_{model_id}.joblib")
        joblib.dump(model_object, path)
        return path

    def load(self, path: str) -> Any:
        if not os.path.exists(path):
            raise FileNotFoundError(f"model file not found: {path}")
        return joblib.load(path)

from __future__ import annotations

from typing import List

from app.application.dto import PredictionDTO, PredictionsResponse
from app.domain.entities import PredictionResult
from app.domain.ports.audit_publisher import IAuditPublisher
from app.domain.ports.experiment_repository import IExperimentRepository
from app.domain.ports.model_storage import IModelStorage
from app.domain.ports.prediction_repository import IPredictionRepository
from app.domain.ports.zone_data_provider import IZoneDataProvider
from app.domain.services.model_trainer import ModelTrainer
from app.domain.services.prediction_clamper import PredictionClamper
from app.domain.value_objects import PredictionLabel


class PredictForZonesUseCase:
    def __init__(
        self,
        data_provider: IZoneDataProvider,
        experiment_repository: IExperimentRepository,
        prediction_repository: IPredictionRepository,
        storage: IModelStorage,
        clamper: PredictionClamper,
        audit_publisher: IAuditPublisher,
    ):
        self._data = data_provider
        self._experiments = experiment_repository
        self._predictions = prediction_repository
        self._storage = storage
        self._clamper = clamper
        self._audit = audit_publisher

    async def execute(self, zone_codes: List[str]) -> PredictionsResponse:
        if not zone_codes:
            raise ValueError("zone_codes is required")

        active_model = self._experiments.find_active_model()
        if active_model is None:
            raise LookupError("no active model available")

        experiment = self._experiments.find_experiment(active_model.experiment_id)
        if experiment is None:
            raise LookupError(f"experiment {active_model.experiment_id} not found")

        zones = self._data.find_zones(zone_codes)
        if not zones:
            raise ValueError("no zone data available for the requested codes")

        model = self._storage.load(active_model.storage_path)
        feature_columns = experiment.features_used or ModelTrainer.SUPPORTED_FEATURES

        results: List[PredictionResult] = []
        for zone in zones:
            features = [zone.as_feature_vector(feature_columns)]
            raw = float(model.predict(features)[0])
            value = self._clamper.clamp(raw)
            label = PredictionLabel.from_value(value)
            confidence = self._clamper.confidence(value)
            results.append(
                PredictionResult(
                    zone_code=zone.zone_code,
                    zone_name=zone.zone_name,
                    model_id=active_model.id,
                    prediction_value=value,
                    prediction_label=label.value,
                    confidence_score=confidence,
                )
            )

        self._predictions.save_all(results)

        await self._audit.publish(
            "PREDICTION_GENERATED",
            {
                "model_id": active_model.id,
                "experiment_id": experiment.id,
                "total_zones": len(results),
            },
        )

        return PredictionsResponse(
            model_id=active_model.id,
            total=len(results),
            predictions=[
                PredictionDTO(
                    zone_code=r.zone_code,
                    zone_name=r.zone_name,
                    model_id=r.model_id,
                    prediction_value=r.prediction_value,
                    prediction_label=r.prediction_label,
                    confidence_score=r.confidence_score,
                    predicted_at=r.predicted_at,
                )
                for r in results
            ],
        )

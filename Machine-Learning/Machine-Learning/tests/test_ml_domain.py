from app.domain.entities import ZoneFeatures
from app.domain.services.model_trainer import ModelTrainer
from app.domain.services.prediction_clamper import PredictionClamper
from app.domain.value_objects import Algorithm, PredictionLabel


def _zone(code: str, **kw) -> ZoneFeatures:
    base = dict(zone_name=code, population=0.5, income=0.5, education=0.5, economic_activity=0.5, commercial_presence=0.5)
    base.update(kw)
    return ZoneFeatures(zone_code=code, **base)


def test_zone_feature_vector_respects_column_order():
    zone = _zone("Z", population=0.1, income=0.2, education=0.3, economic_activity=0.4, commercial_presence=0.5)
    cols = ["education_level", "average_income", "population_density"]
    assert zone.as_feature_vector(cols) == [0.3, 0.2, 0.1]


def test_prediction_label_classifies_correctly():
    assert PredictionLabel.from_value(0.9) == PredictionLabel.HIGH
    assert PredictionLabel.from_value(0.5) == PredictionLabel.MEDIUM
    assert PredictionLabel.from_value(0.2) == PredictionLabel.LOW


def test_prediction_clamper_clamps_and_returns_confidence():
    clamper = PredictionClamper()
    assert clamper.clamp(1.5) == 1.0
    assert clamper.clamp(-0.5) == 0.0
    assert clamper.confidence(0.8) > 0.5


def test_trainer_returns_artifact_with_metrics_and_supports_algorithms():
    trainer = ModelTrainer()
    rows = [[i / 10, i / 10, i / 10, i / 10] for i in range(20)]
    targets = [i / 10 for i in range(20)]
    cols = ["population_density", "average_income", "education_level", "economic_activity_index"]
    artifact = trainer.train(rows, targets, cols, Algorithm.LINEAR_REGRESSION)
    assert artifact.feature_columns == cols
    assert artifact.metrics.r2 >= 0.0
    assert artifact.metrics.mae >= 0.0
    assert artifact.metrics.rmse >= 0.0


def test_trainer_rejects_too_few_samples():
    import pytest
    with pytest.raises(ValueError):
        ModelTrainer().train([[0.1]], [0.1], ["population_density"], Algorithm.LINEAR_REGRESSION)

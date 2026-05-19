from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MLExperimentModel(Base):
    __tablename__ = "ml_experiments"

    id = Column(String, primary_key=True, default=_uuid)
    transformation_run_id = Column(String, index=True, nullable=False)
    algorithm = Column(String, nullable=False)
    target_variable = Column(String, nullable=False)
    features_used = Column(JSON, nullable=True)
    r2_score = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_now)
    status = Column(String, default="COMPLETED")

    trained_models = relationship("TrainedModelRow", back_populates="experiment", cascade="all, delete-orphan")


class TrainedModelRow(Base):
    __tablename__ = "trained_models"

    id = Column(String, primary_key=True, default=_uuid)
    experiment_id = Column(String, ForeignKey("ml_experiments.id"), nullable=False)
    storage_path = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)

    experiment = relationship("MLExperimentModel", back_populates="trained_models")


class PredictionResultRow(Base):
    __tablename__ = "prediction_results"

    id = Column(String, primary_key=True, default=_uuid)
    model_id = Column(String, nullable=False, index=True)
    zone_code = Column(String(50), nullable=False, index=True)
    zone_name = Column(String(255), nullable=False)
    prediction_value = Column(Float, nullable=False)
    prediction_label = Column(String(32), nullable=False)
    confidence_score = Column(Float, nullable=False)
    predicted_at = Column(DateTime, default=_now)


class TransformedZoneDataModel(Base):
    __tablename__ = "transformed_zone_data"

    id = Column(String, primary_key=True)
    transformation_run_id = Column(String, index=True)
    zone_code = Column(String, index=True)
    zone_name = Column(String)
    population_density = Column(Float)
    average_income = Column(Float)
    education_level = Column(Float)
    economic_activity_index = Column(Float)
    commercial_presence_index = Column(Float)
    other_variables_json = Column(JSON)

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import declarative_base

from app.domain.value_objects import ScoreLevel

Base = declarative_base()

def _uuid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.now(timezone.utc)

class IndicatorResultModel(Base):
    __tablename__ = "indicator_results"

    id = Column(String, primary_key=True, default=_uuid)
    transformation_run_id = Column(String, nullable=False, index=True)
    zone_code = Column(String(50), nullable=False, index=True)
    zone_name = Column(String(255), nullable=False)
    population_indicator = Column(Float, default=0.0)
    income_indicator = Column(Float, default=0.0)
    education_indicator = Column(Float, default=0.0)
    competition_indicator = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_now)

class ScoreExecutionModel(Base):
    __tablename__ = "score_executions"

    id = Column(String, primary_key=True, default=_uuid)
    transformation_run_id = Column(String, nullable=False)
    configuration_id = Column(String, nullable=True)
    total_zones = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

class ZoneScoreModel(Base):
    __tablename__ = "zone_scores"

    id = Column(String, primary_key=True, default=_uuid)
    execution_id = Column(String, nullable=False, index=True)
    zone_code = Column(String(50), nullable=False, index=True)
    zone_name = Column(String(255), nullable=False)
    score_value = Column(Float, nullable=False)
    score_level = Column(Enum(ScoreLevel), nullable=False)
    rank_position = Column(Integer, nullable=False)
    combined_score = Column(Float, nullable=True)
    prediction_value = Column(Float, nullable=True)
    discrepancy_flag = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def _uuid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.now(timezone.utc)

class RecommendationExecutionModel(Base):
    __tablename__ = "recommendation_executions"

    id = Column(String, primary_key=True, default=_uuid)
    score_execution_id = Column(String, nullable=False, index=True)
    prediction_batch_id = Column(String, nullable=True)
    total_zones = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

class ZoneRecommendationModel(Base):
    __tablename__ = "zone_recommendations"

    id = Column(String, primary_key=True, default=_uuid)
    execution_id = Column(String, nullable=False, index=True)
    zone_code = Column(String(50), nullable=False, index=True)
    zone_name = Column(String(255), nullable=False)
    recommendation_level = Column(String(64), nullable=False)
    strengths_text = Column(Text, nullable=False, default="")
    risks_text = Column(Text, nullable=False, default="")
    explanation_text = Column(Text, nullable=False, default="")
    generated_at = Column(DateTime, default=_now)

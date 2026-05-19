import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class RecommendationLevel(str, enum.Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


class RecommendationExecution(Base):
    """
    Registro de una ejecución de generación de recomendaciones.
    SRP: solo almacena metadata de la ejecución.
    """
    __tablename__ = "recommendation_executions"
    __table_args__ = {"schema": "recommendations"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    score_execution_id = Column(String, nullable=False)
    prediction_batch_id = Column(String, nullable=True)
    total_zones = Column(String, default="0")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ZoneRecommendation(Base):
    """
    Recomendación generada para una zona específica.
    SRP: solo almacena datos de recomendación, sin lógica.
    """
    __tablename__ = "zone_recommendations"
    __table_args__ = {"schema": "recommendations"}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, nullable=False, index=True)
    zone_code = Column(String(50), nullable=False, index=True)
    zone_name = Column(String(255), nullable=False)
    score_value = Column(Float, nullable=False)
    recommendation_level = Column(Enum(RecommendationLevel), nullable=False)
    strengths_text = Column(Text, nullable=False)
    risks_text = Column(Text, nullable=False)
    explanation_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.database import Base

class MLExperiment(Base):
    __tablename__ = "ml_experiments"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    transformation_run_id = Column(String, index=True, nullable=False)
    algorithm = Column(String, nullable=False) # e.g. "linear_regression", "random_forest", "gradient_boosting"
    target_variable = Column(String, nullable=False)
    features_used = Column(JSON, nullable=True) # list of features
    
    r2_score = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="COMPLETED") # COMPLETED, FAILED

    trained_models = relationship("TrainedModel", back_populates="experiment", cascade="all, delete-orphan")

class TrainedModel(Base):
    __tablename__ = "trained_models"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String, ForeignKey("ml_experiments.id"), nullable=False)
    storage_path = Column(String, nullable=False) # path to joblib file
    is_active = Column(Boolean, default=False)
    
    experiment = relationship("MLExperiment", back_populates="trained_models")

# Mapeo de la tabla existente en DB generada por ms-transformation
class TransformedZoneData(Base):
    __tablename__ = "transformed_zone_data"
    # Solo mapeamos los campos que necesitamos para lectura
    id = Column(String, primary_key=True)
    transformation_run_id = Column(String, index=True)
    zone_code = Column(String)
    zone_name = Column(String)
    
    population_density = Column(Float)
    average_income = Column(Float)
    education_level = Column(Float)
    economic_activity_index = Column(Float)
    commercial_presence_index = Column(Float)
    
    other_variables_json = Column(JSON)

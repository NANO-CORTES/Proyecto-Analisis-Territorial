from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    target_business_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    configurations = relationship("ScoringConfiguration", back_populates="profile")

class ScoringConfiguration(Base):
    __tablename__ = "scoring_configurations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("business_profiles.id"))
    
    population_weight = Column(Float, default=0.25)
    income_weight = Column(Float, default=0.25)
    education_weight = Column(Float, default=0.25)
    competition_weight = Column(Float, default=0.25) # Penalización
    
    # HU-24: Pesos para Scoring Combinado
    analytic_weight = Column(Float, default=0.6)
    prediction_weight = Column(Float, default=0.4)
    
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("BusinessProfile", back_populates="configurations")

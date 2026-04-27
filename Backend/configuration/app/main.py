from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db, init_db
from app.models.models import BusinessProfile, ScoringConfiguration
from app.schemas.schemas import (
    BusinessProfileCreate, BusinessProfileResponse,
    ScoringConfigurationCreate, ScoringConfigurationResponse
)

app = FastAPI(
    title="Configuration Service",
    description="Microservicio de configuración para perfiles de negocio y scoring",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "ms-configuration"}

# --- Profiles ---

@app.post("/api/v1/config/profiles", response_model=BusinessProfileResponse, tags=["profiles"])
def create_profile(profile: BusinessProfileCreate, db: Session = Depends(get_db)):
    db_profile = BusinessProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.get("/api/v1/config/profiles", response_model=List[BusinessProfileResponse], tags=["profiles"])
def list_profiles(db: Session = Depends(get_db)):
    return db.query(BusinessProfile).all()

# --- Scoring Configurations ---

@app.post("/api/v1/config/scoring", response_model=ScoringConfigurationResponse, tags=["scoring"])
def create_scoring_config(config: ScoringConfigurationCreate, db: Session = Depends(get_db)):
    # Desactivar configuraciones previas para este perfil
    db.query(ScoringConfiguration).filter(
        ScoringConfiguration.profile_id == config.profile_id
    ).update({"is_active": False})
    
    db_config = ScoringConfiguration(**config.dict(), is_active=True)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@app.get("/api/v1/config/scoring/active", response_model=ScoringConfigurationResponse, tags=["scoring"])
def get_active_config(db: Session = Depends(get_db)):
    config = db.query(ScoringConfiguration).filter(ScoringConfiguration.is_active == True).first()
    if not config:
        # Retornar configuración por defecto si no hay ninguna activa
        return {
            "id": "default",
            "profile_id": "default",
            "population_weight": 0.25,
            "income_weight": 0.25,
            "education_weight": 0.25,
            "competition_weight": 0.25,
            "is_active": True,
            "created_at": "2026-01-01T00:00:00"
        }
    return config

@app.get("/")
def root():
    return {"message": "Configuration Service is running"}

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class BusinessProfileBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_business_type: Optional[str] = None


class BusinessProfileCreate(BusinessProfileBase):
    pass


class BusinessProfileResponse(BusinessProfileBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ScoringConfigurationBase(BaseModel):
    population_weight: float = Field(0.25, ge=0.0, le=1.0)
    income_weight: float = Field(0.25, ge=0.0, le=1.0)
    education_weight: float = Field(0.25, ge=0.0, le=1.0)
    competition_weight: float = Field(0.25, ge=0.0, le=1.0)


class ScoringConfigurationCreate(ScoringConfigurationBase):
    profile_id: str

    @field_validator("population_weight", "income_weight", "education_weight", "competition_weight")
    @classmethod
    def checkWeights(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("Weight must be between 0.0 and 1.0")
        return v


class ScoringConfigurationResponse(ScoringConfigurationBase):
    id: str
    profile_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

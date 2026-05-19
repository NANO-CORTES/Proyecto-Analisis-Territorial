from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.generate_recommendations import GenerateRecommendationsUseCase
from app.application.use_cases.get_recommendation import GetRecommendationByZoneUseCase
from app.core.database import get_db
from app.domain.services.recommendation_builder import RecommendationBuilder
from app.infrastructure.http.analytics_client import HttpAnalyticsClient
from app.infrastructure.http.audit_client import HttpAuditPublisher
from app.infrastructure.persistence.recommendation_repository_sql import (
    SqlRecommendationRepository,
)

def get_generate_recommendations_use_case(
    db: Session = Depends(get_db),
) -> GenerateRecommendationsUseCase:
    return GenerateRecommendationsUseCase(
        analytics_provider=HttpAnalyticsClient(),
        repository=SqlRecommendationRepository(db),
        builder=RecommendationBuilder(),
        audit_publisher=HttpAuditPublisher(),
    )

def get_get_recommendation_use_case(
    db: Session = Depends(get_db),
) -> GetRecommendationByZoneUseCase:
    return GetRecommendationByZoneUseCase(SqlRecommendationRepository(db))

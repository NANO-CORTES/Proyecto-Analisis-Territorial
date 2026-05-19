from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.calculate_indicators import CalculateIndicatorsUseCase
from app.application.use_cases.execute_combined_scoring import ExecuteCombinedScoringUseCase
from app.application.use_cases.execute_scoring import ExecuteScoringUseCase
from app.application.use_cases.get_ranking import GetRankingUseCase
from app.application.use_cases.get_zone_summary import GetZoneSummaryUseCase
from app.core.database import get_db
from app.domain.services.score_classifier import ScoreClassifier
from app.domain.services.scoring_calculator import ScoringCalculator
from app.infrastructure.http.audit_client import HttpAuditPublisher
from app.infrastructure.http.configuration_client import HttpConfigurationClient
from app.infrastructure.http.ml_client import HttpPredictionClient
from app.infrastructure.http.transformation_client import HttpTransformationClient
from app.infrastructure.persistence.indicator_repository_sql import SqlIndicatorRepository
from app.infrastructure.persistence.score_repository_sql import SqlScoreRepository

def _calculator() -> ScoringCalculator:
    return ScoringCalculator(ScoreClassifier())

def get_calculate_indicators_use_case(
    db: Session = Depends(get_db),
) -> CalculateIndicatorsUseCase:
    return CalculateIndicatorsUseCase(
        transformation_provider=HttpTransformationClient(),
        indicator_repository=SqlIndicatorRepository(db),
        audit_publisher=HttpAuditPublisher(),
    )

def get_execute_scoring_use_case(
    db: Session = Depends(get_db),
) -> ExecuteScoringUseCase:
    return ExecuteScoringUseCase(
        indicator_repository=SqlIndicatorRepository(db),
        score_repository=SqlScoreRepository(db),
        configuration_provider=HttpConfigurationClient(),
        calculator=_calculator(),
        audit_publisher=HttpAuditPublisher(),
    )

def get_execute_combined_scoring_use_case(
    db: Session = Depends(get_db),
) -> ExecuteCombinedScoringUseCase:
    return ExecuteCombinedScoringUseCase(
        score_repository=SqlScoreRepository(db),
        configuration_provider=HttpConfigurationClient(),
        prediction_provider=HttpPredictionClient(),
        calculator=_calculator(),
        audit_publisher=HttpAuditPublisher(),
    )

def get_ranking_use_case(db: Session = Depends(get_db)) -> GetRankingUseCase:
    return GetRankingUseCase(SqlScoreRepository(db))

def get_zone_summary_use_case(db: Session = Depends(get_db)) -> GetZoneSummaryUseCase:
    return GetZoneSummaryUseCase(
        indicator_repository=SqlIndicatorRepository(db),
        score_repository=SqlScoreRepository(db),
    )

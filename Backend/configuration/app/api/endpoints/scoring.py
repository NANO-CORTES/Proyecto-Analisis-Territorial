from fastapi import APIRouter, Depends
from app.interfaces.scoring_config_repository import IScoringConfigRepository
from app.api.deps import getScoringConfigRepository
from app.models.models import ScoringConfiguration
from app.schemas.schemas import ScoringConfigurationCreate, ScoringConfigurationResponse

router = APIRouter(prefix="/api/v1/config/scoring", tags=["scoring"])


@router.post("/", response_model=ScoringConfigurationResponse)
def createScoringConfig(
    config: ScoringConfigurationCreate,
    repo: IScoringConfigRepository = Depends(getScoringConfigRepository),
):
    repo.deactivateByProfile(config.profile_id)
    dbConfig = ScoringConfiguration(**config.dict(), is_active=True)
    return repo.create(dbConfig)


@router.get("/active", response_model=ScoringConfigurationResponse)
def getActiveConfig(
    repo: IScoringConfigRepository = Depends(getScoringConfigRepository),
):
    config = repo.getActive()
    if not config:
        return {
            "id": "default",
            "profile_id": "default",
            "population_weight": 0.25,
            "income_weight": 0.25,
            "education_weight": 0.25,
            "competition_weight": 0.25,
            "is_active": True,
            "created_at": "2026-01-01T00:00:00",
        }
    return config

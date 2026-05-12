from fastapi import APIRouter, Depends
from typing import List
from app.interfaces.profile_repository import IProfileRepository
from app.api.deps import getProfileRepository
from app.models.models import BusinessProfile
from app.schemas.schemas import BusinessProfileCreate, BusinessProfileResponse

router = APIRouter(prefix="/api/v1/config/profiles", tags=["profiles"])


@router.post("/", response_model=BusinessProfileResponse)
def createProfile(
    profile: BusinessProfileCreate,
    repo: IProfileRepository = Depends(getProfileRepository),
):
    dbProfile = BusinessProfile(**profile.dict())
    return repo.create(dbProfile)


@router.get("/", response_model=List[BusinessProfileResponse])
def listProfiles(
    repo: IProfileRepository = Depends(getProfileRepository),
):
    return repo.getAll()

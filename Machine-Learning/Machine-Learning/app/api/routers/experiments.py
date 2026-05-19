from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.application.dto import ExperimentCreateRequest, ExperimentDTO
from app.application.use_cases.activate_model import ActivateModelUseCase
from app.application.use_cases.list_experiments import ListExperimentsUseCase
from app.application.use_cases.train_model import TrainModelUseCase
from app.infrastructure.di import (
    get_activate_model_use_case,
    get_list_experiments_use_case,
    get_train_model_use_case,
)

router = APIRouter(prefix="/api/v1/ml/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentDTO)
async def create_experiment(
    request: ExperimentCreateRequest,
    use_case: TrainModelUseCase = Depends(get_train_model_use_case),
):
    try:
        return await use_case.execute(
            transformation_run_id=request.transformation_run_id,
            algorithm=request.algorithm,
            target_variable=request.target_variable,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("", response_model=List[ExperimentDTO])
def list_experiments(use_case: ListExperimentsUseCase = Depends(get_list_experiments_use_case)):
    return use_case.execute()


@router.patch("/{experiment_id}/activate", response_model=ExperimentDTO)
async def activate(
    experiment_id: str,
    use_case: ActivateModelUseCase = Depends(get_activate_model_use_case),
):
    try:
        return await use_case.execute(experiment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

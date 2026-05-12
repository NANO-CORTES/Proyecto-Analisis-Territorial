from fastapi import APIRouter, Depends
from app.core.exceptions import DomainException
from app.schemas.schemas import TransformRequest, TransformResponse
from app.services.transformation_service import processAdvancedTransformation
from app.interfaces.transformation_repo import ITransformationRepository
from app.api.deps import getTransformationRepo

router = APIRouter(prefix="/api/v1/transform", tags=["transformation"])


@router.post("/advanced", response_model=TransformResponse)
def transformAdvanced(
    body: TransformRequest,
    repo: ITransformationRepository = Depends(getTransformationRepo),
):
    run = processAdvancedTransformation(
        repo=repo,
        datasetLoadId=body.dataset_load_id,
        method=body.method,
    )

    return TransformResponse(
        success=True,
        run_id=run.id,
        dataset_load_id=run.dataset_load_id,
        method=run.method,
        status=run.status,
        records_input=run.records_input,
        records_output=run.records_output,
        rules_applied=run.rules_applied,
        created_at=run.created_at,
    )


@router.get("/results")
def listRuns(
    repo: ITransformationRepository = Depends(getTransformationRepo),
):
    return repo.listRuns()


@router.get("/results/{runId}")
def getResults(
    runId: str,
    repo: ITransformationRepository = Depends(getTransformationRepo),
):
    results = repo.getResults(runId)
    if not results:
        raise DomainException(f"No se encontraron resultados para el runId {runId}", status_code=404)
    return results

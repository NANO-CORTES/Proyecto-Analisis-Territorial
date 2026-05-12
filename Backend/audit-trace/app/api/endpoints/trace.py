from fastapi import APIRouter, Depends, HTTPException
from app.interfaces.trace_repository import ITraceRepository
from app.api.deps import getTraceRepository
from app.models.trace import ProcessTrace
from app.schemas.trace import TraceCreate

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.post("/trace")
def createTrace(
    trace: TraceCreate,
    repo: ITraceRepository = Depends(getTraceRepository),
):
    dbTrace = ProcessTrace(
        dataset_load_id=trace.dataset_load_id,
        transformation_run_id=trace.transformation_run_id,
        score_execution_id=trace.score_execution_id,
        event_type=trace.event_type,
        status=trace.status,
        parameters=trace.parameters,
        result_summary=trace.result_summary,
        user_id=trace.user_id,
    )
    created = repo.create(dbTrace)
    return {"id": created.id, "status": "created"}


@router.get("/trace/{datasetLoadId}")
def getTraceChain(
    datasetLoadId: str,
    repo: ITraceRepository = Depends(getTraceRepository),
):
    events = repo.getByDatasetId(datasetLoadId)

    if not events:
        raise HTTPException(status_code=404, detail="No se encontraron eventos")

    timeline = {}
    for event in events:
        timeline[event.event_type] = {
            "status": event.status,
            "parameters": event.parameters,
            "result_summary": event.result_summary,
            "timestamp": event.created_at.isoformat(),
        }

    return {
        "dataset_load_id": datasetLoadId,
        "events": events,
        "timeline": timeline,
    }
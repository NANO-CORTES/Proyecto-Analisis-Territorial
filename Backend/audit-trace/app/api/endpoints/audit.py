from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Query, HTTPException
from app.api.deps import get_audit_service
from app.interfaces.audit_service import IAuditService
from app.schemas.audit import AuditLogCreate, AuditLogResponse

router = APIRouter()


def _normalize_dt(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)

@router.post("/", response_model=AuditLogResponse, status_code=201)
def create_audit_log(
    request: Request,
    log_in: AuditLogCreate,
    audit_service: IAuditService = Depends(get_audit_service)
):
    trace_id = getattr(request.state, "trace_id", "Unknown")
    saved_log = audit_service.log_action(trace_id=trace_id, log_in=log_in)
    return saved_log

@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    user_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    audit_service: IAuditService = Depends(get_audit_service)
):
    if user_id:
        return audit_service.get_user_logs(user_id=user_id, limit=limit, skip=skip)
    return audit_service.get_logs(limit=limit, skip=skip)


@router.get("/report")
def get_audit_report(
    from_date: datetime = Query(..., alias="from"),
    to_date: datetime = Query(..., alias="to"),
    audit_service: IAuditService = Depends(get_audit_service)
):
    from_dt = _normalize_dt(from_date)
    to_dt = _normalize_dt(to_date)

    if from_dt > to_dt:
        raise HTTPException(status_code=400, detail="'from' must be less than or equal to 'to'")

    events = audit_service.get_logs_by_date_range(from_date=from_dt, to_date=to_dt)
    return {
        "from": from_date,
        "to": to_date,
        "total_events": len(events),
        "events": events
    }

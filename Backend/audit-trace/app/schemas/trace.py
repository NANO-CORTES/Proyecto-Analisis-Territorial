from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TraceCreate(BaseModel):
    dataset_load_id: str
    transformation_run_id: Optional[str] = None
    score_execution_id: Optional[str] = None
    event_type: str
    status: str = "success"
    parameters: Optional[Dict[str, Any]] = None
    result_summary: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class TraceResponse(BaseModel):
    id: int
    dataset_load_id: str
    event_type: str
    status: str
    parameters: Optional[Dict[str, Any]]
    result_summary: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

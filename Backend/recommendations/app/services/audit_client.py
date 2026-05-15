import httpx
from app.core.config import settings


class AuditClient:
    """
    Cliente de auditoría — fire-and-forget.
    SRP: solo envía eventos al ms-audit-trace.
    """

    async def send_event(
        self,
        event_type: str,
        service_name: str,
        reference_id: str,
        summary: str,
        status: str = "SUCCESS",
    ):
        payload = {
            "event_type": event_type,
            "service_name": service_name,
            "reference_id": reference_id,
            "event_summary": summary,
            "status": status,
            "user_id": "system",
        }
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(
                    f"{settings.ms_audit_trace_url}/api/v1/events",
                    json=payload,
                )
        except Exception:
            pass
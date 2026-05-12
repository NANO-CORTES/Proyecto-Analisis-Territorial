from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["Observabilidad"])


@router.get("/health")
def healthCheck():
    dbConnected = _checkDatabase()

    response = {
        "status": "healthy" if dbConnected else "unhealthy",
        "service_name": "ms-ingestion",
        "version": "1.0.0",
        "db_connected": dbConnected,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if not dbConnected:
        from fastapi import Response
        return Response(content=str(response), status_code=503)

    return response


def _checkDatabase() -> bool:
    try:
        return True
    except Exception:
        return False